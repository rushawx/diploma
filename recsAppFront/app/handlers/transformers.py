import pickle

import numpy as np
import pandas as pd
import streamlit as st
from app.config import Settings
from handlers.transformers_config import configure_device, get_torch_device
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize settings
settings = Settings()

# Configure PyTorch device on module load
_device = configure_device()


# Use simple strings in decorators to avoid settings access issues
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

    # Explicitly move model to configured device
    device = get_torch_device()
    model = model.to(device)

    st.info(f"🔧 Model loaded on: {device}")

    return model


def transformer_search(df, model, item_embeddings, query: str, top_k: int = None):
    if top_k is None:
        top_k = settings.DEFAULT_TOP_K

    # Encode query using model (automatically uses configured device)
    q_emb = model.encode([query], normalize_embeddings=True)

    # Calculate cosine similarity (both embeddings should be on CPU for sklearn)
    # Convert to numpy for sklearn compatibility
    q_emb_cpu = q_emb.cpu().numpy() if hasattr(q_emb, "cpu") else q_emb
    item_embeddings_cpu = (
        item_embeddings.cpu().numpy()
        if hasattr(item_embeddings, "cpu")
        else item_embeddings
    )

    sims = cosine_similarity(q_emb_cpu, item_embeddings_cpu).ravel()
    top_idx = np.argsort(-sims)[:top_k]

    # Filter by minimum similarity threshold
    valid_indices = [i for i in top_idx if sims[i] >= settings.MIN_SIMILARITY_THRESHOLD]
    if not valid_indices:
        return pd.DataFrame(columns=["title", "score", "algo"])

    return pd.DataFrame(
        data=zip(
            df.iloc[valid_indices]["title_rus"].to_list(),
            sims[valid_indices],
            ["transformer"] * len(valid_indices),
        ),
        columns=["title", "score", "algo"],
    )
