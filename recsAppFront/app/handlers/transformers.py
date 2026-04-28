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
