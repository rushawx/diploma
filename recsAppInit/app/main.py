"""
Data and Embeddings Initialization Service

This service loads project data and generates embeddings
for the recommendation system on Docker startup.
"""
import logging
import os
import pickle
import uuid

import numpy as np
import pandas as pd
import sqlalchemy as sa
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


from config import settings
from models import Project, User


logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

load_dotenv()


def load_data_from_excel(file_path: str) -> pd.DataFrame:
    """Load and validate project data from Excel file"""
    try:
        logger.info(f"Loading data from: {file_path}")

        if not os.path.exists(file_path):
            logger.error(f"Data file not found: {file_path}")
            return pd.DataFrame()

        df = pd.read_excel(file_path, header=0)
        df = df.fillna('')
        df = df.drop_duplicates(subset=['title_rus'])

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

        text_data = df['title_rus'].fillna('') + ' ' + df['annotation'].fillna('') + ' '+ df['description'].fillna('')
        text_data = text_data.replace("\n", " ")
        text_data = text_data.replace("\r", " ")
        text_data = text_data.replace("\t", " ")

        embeddings = model.encode(
            text_data.tolist(),
            show_progress_bar=True,
            batch_size=settings.BATCH_SIZE
        )

        logger.info(f"Generated {len(embeddings)} embeddings with shape {embeddings.shape}")
        return embeddings

    except Exception as e:
        logger.error(f"Failed to generate embeddings: {str(e)}")
        if settings.STOP_ON_ERROR:
            raise
        return np.array([])


def insert_projects_to_database(
    df: pd.DataFrame,
    embeddings: np.ndarray,
    session: sessionmaker
) -> int:
    """Insert projects and embeddings into database"""
    try:
        logger.info(f"Inserting {len(df)} projects into database")

        admin_user = session.query(User).filter(
            User.nick_name == settings.ADMIN_USERNAME
        ).first()

        if not admin_user:
            logger.error(f"Admin user '{settings.ADMIN_USERNAME}' not found")
            return 0

        logger.info(f"Using admin user: {admin_user.nick_name} (id: {admin_user.id})")

        inserted_count = 0
        skipped_count = 0
        error_count = 0

        for idx, project_data in enumerate(df.to_dict(orient="records")):
            try:
                project = Project(
                    id=uuid.uuid4(),
                    title_rus=project_data.get("title_rus"),
                    title_eng=project_data.get("title_eng"),
                    annotation=project_data.get("annotation"),
                    description=project_data.get("description"),
                    modified_by=admin_user.id,
                )
                project.embedding = embeddings[idx].astype("float32").tolist()

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
    df: pd.DataFrame,
    model: SentenceTransformer,
    embeddings_path: str
) -> np.ndarray:
    """Load existing embeddings or generate new ones"""
    try:
        if not settings.SKIP_EMBEDDING and os.path.exists(embeddings_path):
            logger.info(f"Loading existing embeddings from: {embeddings_path}")
            with open(embeddings_path, 'rb') as f:
                embeddings = pickle.load(f)
            logger.info(f"Loaded {len(embeddings)} existing embeddings")
            return embeddings
        else:
            logger.info("Generating new embeddings (SKIP_EMBEDDING=false or embeddings not found)")
            return generate_embeddings(df, model)

    except Exception as e:
        logger.error(f"Failed to load/generate embeddings: {str(e)}")
        if settings.STOP_ON_ERROR:
            raise
        return np.array([])


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

        logger.info(f"Initialization complete! {inserted_count} projects ready")

    except Exception as e:
        logger.error(f"Initialization service failed: {str(e)}")
        if settings.STOP_ON_ERROR:
            raise


if __name__ == "__main__":
    main()
