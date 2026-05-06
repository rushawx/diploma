"""
Data and Embeddings Initialization Service

This service loads project data and generates embeddings
for the recommendation system on Docker startup.
"""

import logging
import os
import json
import pickle
import random
import string
import uuid
from typing import List

import numpy as np
import pandas as pd
import sqlalchemy as sa
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


from config import settings
from models import Project, User, Rating, Tag, UserTag, ProjectTag

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv()


def generate_random_password(length: int = 12) -> str:
    """Generate a random password"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(alphabet) for _ in range(length))


with open(settings.TITLES_WITH_TAGS_PATH, "rb") as f:
    titles_with_tags_dict = pickle.load(f)

with open(settings.TAGS_SET_PATH, "rb") as f:
    tags_idx_dict = {tag: idx for idx, tag in enumerate(sorted(pickle.load(f)))}


def compile_tags(tags: List[str]) -> List[int]:
    output = [0 for _ in range(len(tags_idx_dict))]
    for tag in tags:
        if tag in tags_idx_dict:
            output[tags_idx_dict[tag]] = 1
        else:
            logger.warning(f"Tag '{tag}' not found in tags_idx_dict")
    return output


def load_data_from_excel(file_path: str) -> pd.DataFrame:
    """Load and validate project data from Excel file"""
    try:
        logger.info(f"Loading data from: {file_path}")

        if not os.path.exists(file_path):
            logger.error(f"Data file not found: {file_path}")
            return pd.DataFrame()

        df = pd.read_excel(file_path, header=0)
        df = df.fillna("")
        df = df.drop_duplicates(subset=["title_rus"])

        logger.info(f"Loaded {len(df)} projects from Excel file")
        return df

    except Exception as e:
        logger.error(f"Failed to load data from Excel: {str(e)}")
        if settings.STOP_ON_ERROR:
            raise
        return pd.DataFrame()


def generate_embeddings(df: pd.DataFrame, model: SentenceTransformer) -> np.ndarray:
    """Generate embeddings for project descriptions"""
    try:
        logger.info(f"Generating embeddings for {len(df)} projects")

        if df.empty:
            logger.warning("No data to generate embeddings for")
            return np.array([])

        text_data = (
            df["title_rus"].fillna("")
            + " "
            + df["annotation"].fillna("")
            + " "
            + df["description"].fillna("")
        )
        text_data = text_data.replace("\n", " ")
        text_data = text_data.replace("\r", " ")
        text_data = text_data.replace("\t", " ")

        embeddings = model.encode(
            text_data.tolist(), show_progress_bar=True, batch_size=settings.BATCH_SIZE
        )

        logger.info(
            f"Generated {len(embeddings)} embeddings with shape {embeddings.shape}"
        )
        return embeddings

    except Exception as e:
        logger.error(f"Failed to generate embeddings: {str(e)}")
        if settings.STOP_ON_ERROR:
            raise
        return np.array([])


def insert_projects_to_database(
    df: pd.DataFrame, embeddings: np.ndarray, session: sessionmaker
) -> int:
    """Insert projects and embeddings into database"""
    try:
        logger.info(f"Inserting {len(df)} projects into database")

        admin_user = (
            session.query(User)
            .filter(User.nick_name == settings.ADMIN_USERNAME)
            .first()
        )

        if not admin_user:
            logger.error(f"Admin user '{settings.ADMIN_USERNAME}' not found")
            return 0

        logger.info(f"Using admin user: {admin_user.nick_name} (id: {admin_user.id})")

        inserted_count = 0
        skipped_count = 0
        error_count = 0

        for idx, project_data in enumerate(df.to_dict(orient="records")):
            try:
                title_rus = project_data.get("title_rus")
                project = Project(
                    id=uuid.uuid4(),
                    title_rus=title_rus,
                    title_eng=project_data.get("title_eng"),
                    annotation=project_data.get("annotation"),
                    description=project_data.get("description"),
                    modified_by=admin_user.id,
                )
                project.embedding = embeddings[idx].astype("float32").tolist()

                project_tags = titles_with_tags_dict.get(title_rus, [])
                if not project_tags:
                    logger.warning(f"No tags found for project: {title_rus}")
                project.tags = compile_tags(project_tags)

                session.add(project)
                session.commit()
                session.refresh(project)
                inserted_count += 1

            except Exception as e:
                error_count += 1
                logger.error(f"Failed to insert project: {str(e)}")
                session.rollback()

        logger.info(f"Inserted {inserted_count} projects successfully")
        if skipped_count > 0:
            logger.info(f"Skipped {skipped_count} projects")
        if error_count > 0:
            logger.warning(f"Encountered {error_count} errors during insertion")

        return inserted_count

    except Exception as e:
        logger.error(f"Database insertion failed: {str(e)}")
        if settings.STOP_ON_ERROR:
            raise
        return 0


def load_or_generate_embeddings(
    df: pd.DataFrame, model: SentenceTransformer, embeddings_path: str
) -> np.ndarray:
    """Load existing embeddings or generate new ones"""
    try:
        if not settings.SKIP_EMBEDDING and os.path.exists(embeddings_path):
            logger.info(f"Loading existing embeddings from: {embeddings_path}")
            with open(embeddings_path, "rb") as f:
                embeddings = pickle.load(f)
            logger.info(f"Loaded {len(embeddings)} existing embeddings")
            return embeddings
        else:
            logger.info(
                "Generating new embeddings (SKIP_EMBEDDING=false or embeddings not found)"
            )
            return generate_embeddings(df, model)

    except Exception as e:
        logger.error(f"Failed to load/generate embeddings: {str(e)}")
        if settings.STOP_ON_ERROR:
            raise
        return np.array([])


def load_artificial_profiles() -> dict:
    """Load artificial profiles with project ratings"""
    try:
        logger.info(
            f"Loading artificial profiles from: {settings.ARTIFICIAL_PROFILES_PATH}"
        )
        with open(settings.ARTIFICIAL_PROFILES_PATH, "rb") as f:
            profiles = pickle.load(f)
        logger.info(f"Loaded {len(profiles)} artificial profiles")
        return profiles
    except Exception as e:
        logger.error(f"Failed to load artificial profiles: {str(e)}")
        if settings.STOP_ON_ERROR:
            raise
        return {}


def create_artificial_users_and_ratings(
    profiles: dict, session: sessionmaker, projects_map: dict
) -> int:
    """Create artificial users and their ratings from profiles"""
    try:
        logger.info(
            f"Creating artificial users and ratings from {len(profiles)} profiles"
        )

        created_count = 0
        error_count = 0

        with open(settings.PROFILES_PATH, "r") as f:
            profiles_with_bio = json.load(f)

        for profile_name, profile_ratings in profiles.items():
            try:
                existing_user = (
                    session.query(User).filter(User.nick_name == profile_name).first()
                )
                if existing_user:
                    logger.info(f"User '{profile_name}' already exists, skipping")
                    continue

                profile_data = profiles_with_bio.get(profile_name, {})
                bio_text = (
                    profile_data.get("bio", "")
                    if isinstance(profile_data, dict)
                    else str(profile_data)
                )

                new_user = User(
                    id=uuid.uuid4(),
                    nick_name=profile_name,
                    password=generate_random_password(),
                    user_type="avatar",
                    self_bio=bio_text,
                )
                session.add(new_user)
                session.commit()
                session.refresh(new_user)

                ratings_count = 0
                for project_key, rating in profile_ratings.items():
                    if rating is None:
                        continue

                    # Parse project_key - it may be a JSON string or a plain title
                    try:
                        project_data = json.loads(project_key)
                        project_title = project_data.get("title", project_key)
                    except (json.JSONDecodeError, AttributeError):
                        project_title = project_key

                    project = projects_map.get(project_title)
                    if not project:
                        logger.warning(
                            f"Project '{project_title}' not found for user '{profile_name}'"
                        )
                        continue

                    new_rating = Rating(
                        id=uuid.uuid4(),
                        user_id=new_user.id,
                        project_id=project.id,
                        rating=rating,
                    )
                    session.add(new_rating)

                    ratings_count += 1

                session.commit()
                created_count += 1
                logger.info(
                    f"Created user '{profile_name}' with {ratings_count} ratings"
                )

            except Exception as e:
                error_count += 1
                logger.error(
                    f"Failed to create user/ratings for profile '{profile_name}': {str(e)}"
                )
                session.rollback()

        logger.info(f"Created {created_count} artificial users with ratings")
        if error_count > 0:
            logger.warning(
                f"Encountered {error_count} errors during user/rating creation"
            )

        return created_count

    except Exception as e:
        logger.error(f"Failed to create artificial users and ratings: {str(e)}")
        if settings.STOP_ON_ERROR:
            raise
        return 0


def insert_tags(session: sessionmaker) -> int:
    """Insert tags from tags_set.pkl into database"""
    try:
        logger.info("Loading tags from tags_set.pkl")
        with open(settings.TAGS_SET_PATH, "rb") as f:
            tags_set = pickle.load(f)
        logger.info(f"Loaded {len(tags_set)} tags")

        tags_map = {}
        inserted_count = 0
        skipped_count = 0

        for tag_name in sorted(tags_set):
            existing_tag = session.query(Tag).filter(Tag.name == tag_name).first()
            if existing_tag:
                tags_map[tag_name] = existing_tag
                skipped_count += 1
                continue

            new_tag = Tag(id=uuid.uuid4(), name=tag_name)
            session.add(new_tag)
            session.commit()
            session.refresh(new_tag)
            tags_map[tag_name] = new_tag
            inserted_count += 1

        logger.info(
            f"Inserted {inserted_count} tags, skipped {skipped_count} existing tags"
        )
        return tags_map

    except Exception as e:
        logger.error(f"Failed to insert tags: {str(e)}")
        if settings.STOP_ON_ERROR:
            raise
        return {}


def insert_project_tags(
    session: sessionmaker, projects_map: dict, tags_map: dict
) -> int:
    """Insert project-tag associations from titles_with_tags_dict.pkl"""
    try:
        logger.info("Loading project tags from titles_with_tags_dict.pkl")
        with open(settings.TITLES_WITH_TAGS_PATH, "rb") as f:
            titles_with_tags_dict = pickle.load(f)
        logger.info(f"Loaded tags for {len(titles_with_tags_dict)} projects")

        inserted_count = 0
        skipped_count = 0
        error_count = 0

        for project_title, tag_names in titles_with_tags_dict.items():
            project = projects_map.get(project_title)
            if not project:
                logger.warning(f"Project '{project_title}' not found for tags")
                skipped_count += len(tag_names)
                continue

            for tag_name in tag_names:
                tag = tags_map.get(tag_name)
                if not tag:
                    logger.warning(f"Tag '{tag_name}' not found in tags_map")
                    skipped_count += 1
                    continue

                existing_project_tag = (
                    session.query(ProjectTag)
                    .filter(
                        ProjectTag.project_id == project.id,
                        ProjectTag.tag_id == tag.id,
                    )
                    .first()
                )
                if existing_project_tag:
                    skipped_count += 1
                    continue

                new_project_tag = ProjectTag(
                    id=uuid.uuid4(), project_id=project.id, tag_id=tag.id
                )
                session.add(new_project_tag)
                inserted_count += 1

            session.commit()

        logger.info(
            f"Inserted {inserted_count} project tags, skipped {skipped_count}, errors: {error_count}"
        )
        return inserted_count

    except Exception as e:
        logger.error(f"Failed to insert project tags: {str(e)}")
        if settings.STOP_ON_ERROR:
            raise
        return 0


def insert_user_tags(session: sessionmaker, users_map: dict, tags_map: dict) -> int:
    """Insert user-tag associations from artificial_profiles.json"""
    try:
        logger.info("Loading user tags from artificial_profiles.json")
        with open(settings.PROFILES_PATH, "r") as f:
            profiles_with_bio = json.load(f)
        logger.info(f"Loaded tags for {len(profiles_with_bio)} users")

        inserted_count = 0
        skipped_count = 0
        error_count = 0

        for profile_name, profile_data in profiles_with_bio.items():
            user = users_map.get(profile_name)
            if not user:
                logger.warning(f"User '{profile_name}' not found for tags")
                skipped_count += len(profile_data.get("tags", []))
                continue

            tag_names = profile_data.get("tags", [])
            for tag_name in tag_names:
                tag = tags_map.get(tag_name)
                if not tag:
                    logger.warning(f"Tag '{tag_name}' not found in tags_map")
                    skipped_count += 1
                    continue

                existing_user_tag = (
                    session.query(UserTag)
                    .filter(
                        UserTag.user_id == user.id,
                        UserTag.tag_id == tag.id,
                    )
                    .first()
                )
                if existing_user_tag:
                    skipped_count += 1
                    continue

                new_user_tag = UserTag(id=uuid.uuid4(), user_id=user.id, tag_id=tag.id)
                session.add(new_user_tag)
                inserted_count += 1

            session.commit()

        logger.info(
            f"Inserted {inserted_count} user tags, skipped {skipped_count}, errors: {error_count}"
        )
        return inserted_count

    except Exception as e:
        logger.error(f"Failed to insert user tags: {str(e)}")
        if settings.STOP_ON_ERROR:
            raise
        return 0


def main():
    """Main initialization function"""
    logger.info("Starting Data and Embeddings Initialization Service")

    try:
        df = load_data_from_excel(settings.DATA_PATH)

        if df.empty:
            logger.error("No data loaded, stopping initialization")
            return

        logger.info(f"Loading ML model: {settings.TRANSFORMER_MODEL}")
        model = SentenceTransformer(settings.TRANSFORMER_MODEL)
        logger.info("ML model loaded successfully")

        embeddings = load_or_generate_embeddings(df, model, settings.EMBEDDINGS_PATH)

        if embeddings.size == 0:
            logger.error("No embeddings available, stopping initialization")
            return

        engine = sa.create_engine(
            settings.DATABASE_URL,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE,
            echo=settings.DB_ECHO,
        )
        Session = sessionmaker(bind=engine)

        with Session() as session:
            inserted_count = insert_projects_to_database(df, embeddings, session)

            projects = session.query(Project).all()
            projects_map = {project.title_rus: project for project in projects}

            profiles = load_artificial_profiles()
            users_map = {}
            if profiles:
                users_created = create_artificial_users_and_ratings(
                    profiles, session, projects_map
                )
                users = session.query(User).filter(User.user_type == "avatar").all()
                users_map = {user.nick_name: user for user in users}

            tags_map = insert_tags(session)
            if tags_map:
                project_tags_count = insert_project_tags(
                    session, projects_map, tags_map
                )
                if users_map:
                    user_tags_count = insert_user_tags(session, users_map, tags_map)

        logger.info(f"Initialization complete! {inserted_count} projects ready")

    except Exception as e:
        logger.error(f"Initialization service failed: {str(e)}")
        if settings.STOP_ON_ERROR:
            raise


if __name__ == "__main__":
    main()
