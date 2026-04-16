import pickle
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


@st.cache_data(ttl="10m", show_spinner="Загрузка данных...")
def get_data():
    df = pd.read_excel("app/resources/data.xlsx", header=0)
    df = df.fillna("")
    df.drop_duplicates(inplace=True)
    return df

@st.cache_data(ttl="10m", show_spinner="Загрузка векторных представлений...")
def get_item_embeddings():
    with open("app/resources/item_embeddings.pkl", "rb") as f:
        return pickle.load(f)

@st.cache_resource(ttl="10m", show_spinner="Загрузка трансформера...")
def get_model():
    return SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

def transformer_search(df, model, item_embeddings, query: str, top_k: int = 5):
    q_emb = model.encode([query], normalize_embeddings=True)
    sims = cosine_similarity(q_emb, item_embeddings).ravel()
    top_idx = np.argsort(-sims)[:top_k]
    return pd.DataFrame(
        data=zip(
            df.iloc[top_idx]["title_rus"].to_list(),
            sims[top_idx],
            ["transformer"] * top_k,
        ),
        columns=["title", "score", "algo"],
    )
