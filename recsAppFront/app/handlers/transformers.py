import pickle

import implicit
import numpy as np
import pandas as pd
import streamlit as st
from app.config import Settings
from handlers.transformers_config import get_torch_device
from handlers.auth_helpers import make_authenticated_request
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

settings = Settings()


def cosine_similarity_tags(tags_vector1: list, tags_vector2: list) -> float:
    """
    Calculate cosine similarity between two tags vectors.

    Args:
        tags_vector1: First tags vector (list of floats)
        tags_vector2: Second tags vector (list of floats)

    Returns:
        Cosine similarity score between 0 and 1
    """
    vec1 = np.array(tags_vector1).reshape(1, -1)
    vec2 = np.array(tags_vector2).reshape(1, -1)
    similarity = cosine_similarity(vec1, vec2)[0][0]
    return float(similarity)


@st.cache_data(ttl="1h", show_spinner="Loading tags set...")
def get_tags_set():
    """Load the complete set of available tags from pickle file"""
    try:
        with open(settings.TAGS_SET_FILE, "rb") as f:
            tags_set = pickle.load(f)
        return sorted(list(tags_set))
    except Exception as e:
        st.error(f"Error loading tags set: {str(e)}")
        return []


def compile_tags_vector(selected_tags: list) -> list:
    """
    Compile a tags vector from selected tags.

    Args:
        selected_tags: List of selected tag names

    Returns:
        Tags vector as a list of 0s and 1s
    """
    tags_set = get_tags_set()
    tags_idx_dict = {tag: idx for idx, tag in enumerate(tags_set)}

    output = [0] * len(tags_set)
    for tag in selected_tags:
        if tag in tags_idx_dict:
            output[tags_idx_dict[tag]] = 1
        else:
            st.warning(f"Tag '{tag}' not found in tags set")

    return output


@st.cache_data(ttl="10m", show_spinner="Loading data...")
def get_data():
    df = pd.read_excel(settings.DATA_FILE, header=0)
    df = df.fillna("")
    df.drop_duplicates(inplace=True)
    return df


@st.cache_data(ttl="10m", show_spinner="Loading vector representations...")
def get_item_embeddings():
    with open(settings.EMBEDDINGS_FILE, "rb") as f:
        return pickle.load(f)


@st.cache_resource(ttl="10m", show_spinner="Loading transformer...")
def get_model():
    """Load transformer model and move to configured device."""
    model = SentenceTransformer(settings.TRANSFORMER_MODEL)

    device = get_torch_device()
    model = model.to(device)

    st.info(f"🔧 Model loaded on: {device}")

    return model


def get_backend_projects_with_embeddings():
    """Fetch projects with embeddings from backend API"""
    try:
        response = make_authenticated_request("GET", "/projects/with-embeddings")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch projects: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching backend projects: {str(e)}")
        return []


def get_backend_projects_with_tags():
    """Fetch projects with tags vectors from backend API"""
    try:
        response = make_authenticated_request("GET", "/projects/with-tags")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch projects: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching backend projects: {str(e)}")
        return []


def transformer_search(model, query: str, top_k: int = None):
    """Search for similar projects using backend data"""
    if top_k is None:
        top_k = settings.DEFAULT_TOP_K

    projects = get_backend_projects_with_embeddings()
    if not projects:
        return pd.DataFrame(columns=["title_rus", "score", "algo"])

    embeddings = []
    titles = []
    for project in projects:
        embedding = project.get("embedding", [])
        if embedding:
            embeddings.append(embedding)
            titles.append(project)

    if not embeddings:
        return pd.DataFrame(columns=["title_rus", "score", "algo"])

    item_embeddings = np.array(embeddings)

    q_emb = model.encode([query], normalize_embeddings=True)

    q_emb_cpu = q_emb.cpu().numpy() if hasattr(q_emb, "cpu") else q_emb

    sims = cosine_similarity(q_emb_cpu, item_embeddings).ravel()
    top_idx = np.argsort(-sims)[:top_k]

    valid_indices = [i for i in top_idx if sims[i] >= settings.MIN_SIMILARITY_THRESHOLD]
    if not valid_indices:
        return pd.DataFrame(columns=["title_rus", "score", "algo"])

    results = []
    for i in valid_indices:
        project = titles[i]
        results.append(
            {
                "title_rus": project.get("title_rus", "Untitled"),
                "score": sims[i],
                "algo": "transformer",
                "project": project,
            }
        )

    return pd.DataFrame(results)


def tags_search(tags_vector: list, top_k: int = None):
    """
    Search for similar projects based on tags vectors using cosine similarity.

    Args:
        tags_vector: Tags vector to use for similarity search
        top_k: Number of similar projects to return (defaults to settings.DEFAULT_TOP_K)

    Returns:
        DataFrame with similar projects sorted by similarity score
    """
    if top_k is None:
        top_k = settings.DEFAULT_TOP_K

    if not tags_vector:
        st.error("Tags vector must be provided")
        return pd.DataFrame(columns=["title_rus", "score", "algo"])

    projects = get_backend_projects_with_tags()
    if not projects:
        return pd.DataFrame(columns=["title_rus", "score", "algo"])

    similarities = []
    for project in projects:
        project_tags = project.get("tags", [])
        if project_tags:
            similarity = cosine_similarity_tags(tags_vector, project_tags)
            similarities.append(
                {
                    "title_rus": project.get("title_rus", "Untitled"),
                    "score": similarity,
                    "algo": "tags",
                    "project": project,
                }
            )

    if not similarities:
        return pd.DataFrame(columns=["title_rus", "score", "algo"])

    results_df = pd.DataFrame(similarities)
    results_df = results_df.sort_values("score", ascending=False)

    results_df = results_df[results_df["score"] >= settings.MIN_SIMILARITY_THRESHOLD]

    return results_df.head(top_k)


@st.cache_resource(ttl="1h", show_spinner="Loading ALS model...")
def get_als_model():
    """Load ALS model for collaborative filtering recommendations"""
    try:
        with open(settings.ALS_MODEL_FILE, "rb") as f:
            model_data = pickle.load(f)

        if isinstance(model_data, dict):
            als_model = model_data["model"]
            als_model.user_ids = model_data["user_ids"]
            als_model.item_ids = model_data["item_ids"]
            als_model.user_ratings = model_data.get("user_ratings", {})
            als_model.model_params = model_data.get("model_params", {})
            als_model.performance = model_data.get("performance", {})
        else:
            als_model = model_data

        st.info("🎯 ALS model loaded successfully")
        return als_model
    except Exception as e:
        st.error(f"Error loading ALS model: {str(e)}")
        return None


def get_user_ratings(user_id: str) -> dict:
    """Get all ratings for a specific user"""
    try:
        response = make_authenticated_request("GET", "/projects/ratings/all")
        if response.status_code == 200:
            all_ratings = response.json()
            user_ratings = {}
            for rating in all_ratings:
                if rating["user_id"] == user_id:
                    user_ratings[rating["project_id"]] = rating["rating"]
            return user_ratings
    except Exception as e:
        st.error(f"Error fetching user ratings: {str(e)}")
    return {}


def get_highly_rated_projects(top_k: int = None) -> pd.DataFrame:
    """Get top-k highly rated projects globally"""
    if top_k is None:
        top_k = settings.DEFAULT_TOP_K

    try:
        response = make_authenticated_request("GET", "/projects/ratings/all")
        if response.status_code != 200:
            return pd.DataFrame(columns=["title_rus", "score", "algo", "project"])

        all_ratings = response.json()
        if not all_ratings:
            return pd.DataFrame(columns=["title_rus", "score", "algo", "project"])

        projects = get_backend_projects_with_embeddings()
        if not projects:
            return pd.DataFrame(columns=["title_rus", "score", "algo", "project"])

        projects_map = {p["id"]: p for p in projects}

        project_ratings = {}
        for rating in all_ratings:
            project_id = rating["project_id"]
            if project_id in project_ratings:
                project_ratings[project_id].append(rating["rating"])
            else:
                project_ratings[project_id] = [rating["rating"]]

        project_avg_scores = []
        for project_id, ratings in project_ratings.items():
            if project_id in projects_map:
                avg_rating = np.mean(ratings)
                project_avg_scores.append(
                    {
                        "project": projects_map[project_id],
                        "score": avg_rating,
                        "algo": "popular",
                    }
                )

        if not project_avg_scores:
            return pd.DataFrame(columns=["title_rus", "score", "algo", "project"])

        results_df = pd.DataFrame(project_avg_scores)
        results_df = results_df.sort_values("score", ascending=False)
        results_df["title_rus"] = results_df["project"].apply(
            lambda p: p.get("title_rus", "Untitled")
        )

        return results_df.head(top_k)

    except Exception as e:
        st.error(f"Error fetching highly rated projects: {str(e)}")
        return pd.DataFrame(columns=["title_rus", "score", "algo", "project"])


def get_als_recommendations(als_model, user_id: str, top_k: int = None):
    """
    Get ALS-based collaborative filtering recommendations for a user.

    Args:
        als_model: Trained ALS model (implicit.als.AlternatingLeastSquares instance)
        user_id: User ID to get recommendations for
        top_k: Number of recommendations to return (defaults to settings.DEFAULT_TOP_K)

    Returns:
        DataFrame with recommended projects sorted by predicted rating
    """
    if top_k is None:
        top_k = settings.DEFAULT_TOP_K

    try:
        if als_model is None or not hasattr(als_model, "item_factors"):
            return pd.DataFrame(columns=["title_rus", "score", "algo", "project"])

        response = make_authenticated_request("GET", "/projects/ratings/all")
        if response.status_code != 200:
            return pd.DataFrame(columns=["title_rus", "score", "algo", "project"])

        all_ratings = response.json()
        if not all_ratings:
            return pd.DataFrame(columns=["title_rus", "score", "algo", "project"])

        user_ratings = {}
        for rating in all_ratings:
            if rating["user_id"] == user_id:
                user_ratings[rating["project_id"]] = rating["rating"]

        if not user_ratings:
            return get_highly_rated_projects(top_k)

        if len(user_ratings) < 3:
            st.info(
                f"ℹ️ Need at least 3 ratings for personalized ALS recommendations "
                f"(current: {len(user_ratings)})"
            )
            return get_highly_rated_projects(top_k)

        projects = get_backend_projects_with_embeddings()
        if not projects:
            return pd.DataFrame(columns=["title_rus", "score", "algo", "project"])

        projects_map_by_title = {p["title_rus"]: p for p in projects}
        projects_map_by_id = {p["id"]: p for p in projects}

        user_ratings_by_item_idx = {}
        for project_id, rating in user_ratings.items():
            project = projects_map_by_id.get(project_id)
            if project and project["title_rus"] in als_model.item_ids:
                item_idx = als_model.item_ids.index(project["title_rus"])
                user_ratings_by_item_idx[item_idx] = rating

        if not user_ratings_by_item_idx:
            return get_highly_rated_projects(top_k)

        from scipy.sparse import csr_matrix

        row_indices = [0] * len(user_ratings_by_item_idx)
        col_indices = list(user_ratings_by_item_idx.keys())
        data = list(user_ratings_by_item_idx.values())

        user_items = csr_matrix(
            (data, (row_indices, col_indices)),
            shape=(1, len(als_model.item_ids))
        )

        from handlers.auth_helpers import get_user_profile
        user_profile = get_user_profile()
        user_nick_name = user_profile.get("nick_name") if user_profile else None
        user_in_model = user_nick_name in als_model.user_ids if user_nick_name else False

        if user_in_model:
            # Use existing user factors for artificial users in model
            user_idx = als_model.user_ids.index(user_nick_name)

            # Use actual training ratings from user_ratings
            if user_idx in als_model.user_ratings:
                original_ratings = als_model.user_ratings[user_idx]
                row_indices = [0] * len(original_ratings)
                col_indices = list(original_ratings.keys())
                data = list(original_ratings.values())

                original_user_items = csr_matrix(
                    (data, (row_indices, col_indices)),
                    shape=(1, len(als_model.item_ids))
                )
            else:
                # Fallback: create user_items from DB ratings
                original_user_items = user_items

            recommendations = als_model.recommend(
                userid=user_idx,
                user_items=original_user_items,
                N=top_k,
                filter_already_liked_items=True,
                recalculate_user=False
            )
        else:
            recommendations = als_model.recommend(
                userid=0,
                user_items=user_items,
                N=top_k,
                filter_already_liked_items=True,
                recalculate_user=True
            )

        results = []
        for item_idx, score in zip(recommendations[0], recommendations[1]):
            project_title = als_model.item_ids[item_idx]
            if project_title in projects_map_by_title:
                project = projects_map_by_title[project_title]
                results.append({"project": project, "score": float(score), "algo": "als"})

        if not results:
            return get_highly_rated_projects(top_k)

        results_df = pd.DataFrame(results)
        results_df["title_rus"] = results_df["project"].apply(
            lambda p: p.get("title_rus", "Untitled")
        )

        return results_df

    except Exception as e:
        st.error(f"Error generating ALS recommendations: {str(e)}")
        return pd.DataFrame(columns=["title_rus", "score", "algo", "project"])
