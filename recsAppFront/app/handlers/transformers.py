import pickle

import numpy as np
import pandas as pd
import streamlit as st
import torch
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
    """Load transformer model from local pickle file or from HuggingFace and move to configured device."""
    # Load model from local pickle file if available
    import os

    model_path = settings.TRANSFORMER_MODEL_FILE
    if os.path.exists(model_path):
        st.info(f"📦 Loading transformer from local file: {model_path}")
        with open(model_path, "rb") as f:
            model = torch.load(f, map_location="cpu", weights_only=False)
    else:
        st.info(
            f"🌐 Loading transformer from HuggingFace: {settings.TRANSFORMER_MODEL}"
        )
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


@st.cache_resource(ttl="1h", show_spinner="Loading LightFM model...")
def get_lightfm_model():
    """Load LightFM model for avatar-based recommendations"""
    try:
        # Register the LightFM4Rec class so pickle can find it
        # The pickle file was saved with the class in __main__ namespace
        import sys

        if "__main__" not in sys.modules:
            sys.modules["__main__"] = type(sys)("__main__")
        sys.modules["__main__"].LightFM4Rec = LightFM4Rec

        with open(settings.LIGHTFM_MODEL_FILE, "rb") as f:
            model_wrapper = pickle.load(f)

        st.info("🎯 LightFM model loaded successfully")
        return model_wrapper
    except Exception as e:
        st.error(f"Error loading LightFM model: {str(e)}")
        return None


class LightFM4Rec:
    def __init__(
        self,
        model,
        user_mapping,
        item_mapping,
        inv_user_mapping,
        inv_item_mapping,
        user_col,
        item_col,
        rating_col,
    ):
        self.model = model
        self.user_mapping = user_mapping
        self.item_mapping = item_mapping
        self.inv_user_mapping = inv_user_mapping
        self.inv_item_mapping = inv_item_mapping
        self.user_col = user_col
        self.item_col = item_col
        self.rating_col = rating_col

    def fit(
        self,
        rating_matrix,
        train_interactions,
        user_features=None,
        item_features=None,
        epochs=16,
    ):
        self.user_features = user_features
        self.item_features = item_features
        self.train_interactions = train_interactions
        self.model.fit(
            rating_matrix,
            user_features=self.user_features,
            item_features=self.item_features,
            epochs=epochs,
        )

    def _get_lfm_pred(self, user_id):
        pred = self.model.predict(
            user_ids=user_id,
            item_ids=self.item_ids,
            user_features=self.user_features,
            item_features=self.item_features,
        )
        return pred

    def predict(self, test, interaction_matrix, user_col, filter_seen=True, k=10):
        user_ids = test[self.user_col].map(self.user_mapping).unique()
        self.item_ids = list(self.item_mapping.values())

        pred = pd.DataFrame(user_ids, columns=[user_col])
        scores = np.vstack(pred[user_col].apply(self._get_lfm_pred).values)

        if filter_seen:
            scores += np.nan_to_num(interaction_matrix.todense()[user_ids] * -np.inf)

        ind_part = np.argpartition(scores, -k)[:, -k:].copy()
        scores_not_sorted = np.take_along_axis(scores, ind_part, axis=1)
        ind_sorted = np.argsort(scores_not_sorted, axis=1)
        scores_sorted = np.sort(scores_not_sorted, axis=1)
        indices = np.take_along_axis(ind_part, ind_sorted, axis=1)

        preds = pd.DataFrame(
            {
                self.user_col: user_ids,
                self.item_col: np.flip(indices, axis=1).tolist(),
                self.rating_col: np.flip(scores_sorted, axis=1).tolist(),
            }
        ).explode([self.item_col, self.rating_col])
        preds[self.user_col] = preds[self.user_col].map(self.inv_user_mapping)
        preds[self.item_col] = preds[self.item_col].map(self.inv_item_mapping)

        return preds


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


def get_lightfm_recommendations(
    lightfm_model, avatar_nick_name: str, real_user_id: str, top_k: int = None
):
    """
    Get LightFM-based recommendations using the user's avatar.

    Args:
        lightfm_model: Trained LightFM model wrapper
        avatar_nick_name: Nickname of the avatar to use for recommendations
        real_user_id: Real user ID to filter out seen/rated projects
        top_k: Number of recommendations to return (defaults to settings.DEFAULT_TOP_K)

    Returns:
        DataFrame with recommended projects sorted by predicted score
    """
    if top_k is None:
        top_k = settings.DEFAULT_TOP_K

    try:
        if lightfm_model is None:
            return pd.DataFrame(columns=["title_rus", "score", "algo", "project"])

        # Get real user's rated projects to filter out
        rated_project_ids = set()
        response = make_authenticated_request("GET", "/projects/ratings/all")
        if response.status_code == 200:
            all_ratings = response.json()
            for rating in all_ratings:
                if rating["user_id"] == real_user_id:
                    rated_project_ids.add(rating["project_id"])

        # Get projects from backend
        projects = get_backend_projects_with_embeddings()
        if not projects:
            return pd.DataFrame(columns=["title_rus", "score", "algo", "project"])

        projects_map_by_title = {p["title_rus"]: p for p in projects}

        # Check if avatar is in the model
        if avatar_nick_name not in lightfm_model.user_mapping:
            st.warning(f"Avatar '{avatar_nick_name}' not found in model")
            return get_highly_rated_projects(top_k)

        # Get predictions for all items using the avatar
        predictions = lightfm_model.predict(
            test=pd.DataFrame({"user_name": [avatar_nick_name]}),
            interaction_matrix=lightfm_model.train_interactions,
            user_col="user_name",
            filter_seen=False,
        )

        # Convert predictions to list and filter out real user's rated projects
        results = []
        for _, row in predictions.iterrows():
            project_title = row["item_title"]
            if project_title in projects_map_by_title:
                project = projects_map_by_title[project_title]
                if project["id"] not in rated_project_ids:
                    results.append(
                        {
                            "project": project,
                            "score": row["rating"],
                            "algo": "lightfm",
                        }
                    )

        if not results:
            st.info("No new recommendations available")
            return pd.DataFrame(columns=["title_rus", "score", "algo", "project"])

        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values("score", ascending=False)
        results_df["title_rus"] = results_df["project"].apply(
            lambda p: p.get("title_rus", "Untitled")
        )

        return results_df.head(top_k)

    except Exception as e:
        st.error(f"Error generating LightFM recommendations: {str(e)}")
        return pd.DataFrame(columns=["title_rus", "score", "algo", "project"])
