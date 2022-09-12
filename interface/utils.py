import core.pipelines as pipelines_functions
from inspect import getmembers, isfunction
from newspaper import Article
import streamlit as st


def get_pipelines():
    pipeline_names, pipeline_funcs = list(
        zip(*getmembers(pipelines_functions, isfunction))
    )
    pipeline_names = [
        " ".join([n.capitalize() for n in name.split("_")]) for name in pipeline_names
    ]
    return pipeline_names, pipeline_funcs


@st.experimental_memo
def extract_text_from_url(url: str):
    article = Article(url)
    article.download()
    article.parse()

    return article.text
