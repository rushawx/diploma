import pickle

import numpy as np
import pandas as pd
import streamlit as st
from app.config import Settings
from handlers.transformers_config import configure_device, get_torch_device
from handlers.auth_helpers import make_authenticated_request
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

settings = Settings()

_device = configure_device()


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
        return sorted(list(tags_set))  # Return as sorted list for consistent display
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
        embedding = project.get('embedding', [])
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
        results.append({
            'title_rus': project.get('title_rus', 'Untitled'),
            'score': sims[i],
            'algo': 'transformer',
            'project': project
        })

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

    # Get projects with tags from backend
    projects = get_backend_projects_with_tags()
    if not projects:
        return pd.DataFrame(columns=["title_rus", "score", "algo"])

    # Calculate similarity scores for all projects
    similarities = []
    for project in projects:
        project_tags = project.get('tags', [])
        if project_tags:
            similarity = cosine_similarity_tags(tags_vector, project_tags)
            similarities.append({
                'title_rus': project.get('title_rus', 'Untitled'),
                'score': similarity,
                'algo': 'tags',
                'project': project
            })

    if not similarities:
        return pd.DataFrame(columns=["title_rus", "score", "algo"])

    # Convert to DataFrame and sort by similarity score
    results_df = pd.DataFrame(similarities)
    results_df = results_df.sort_values('score', ascending=False)

    # Filter by minimum similarity threshold
    results_df = results_df[results_df['score'] >= settings.MIN_SIMILARITY_THRESHOLD]

    # Return top_k results
    return results_df.head(top_k)
