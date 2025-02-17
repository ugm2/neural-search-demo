import os
import shutil
from inspect import getmembers, isfunction, signature
from io import StringIO

import pandas as pd
import pytesseract
import streamlit as st
from newspaper import Article
from PIL import Image
from PyPDF2 import PdfFileReader

import core.pipelines as pipelines_functions
from core.audio import audio_to_text, load_model
from core.pipelines import data_path


def get_pipelines():
    pipeline_names, pipeline_funcs = list(
        zip(*getmembers(pipelines_functions, isfunction))
    )
    pipeline_names = [
        " ".join([n.capitalize() for n in name.split("_")]) for name in pipeline_names
    ]
    pipeline_func_parameters = [
        {key: value.default for key, value in signature(pipe_func).parameters.items()}
        for pipe_func in pipeline_funcs
    ]
    return pipeline_names, pipeline_funcs, pipeline_func_parameters


def reset_vars_data():
    st.session_state["doc_id"] = 0
    st.session_state["search_results"] = None
    # Delete data files
    shutil.rmtree(data_path)
    os.makedirs(data_path, exist_ok=True)


@st.cache_data
def extract_text_from_url(url: str):
    article = Article(url)
    article.download()
    article.parse()

    return article.text


@st.cache_data
def extract_text_from_file(file):
    # read text file
    if file.type == "text/plain":
        # To convert to a string based IO:
        stringio = StringIO(file.getvalue().decode("utf-8"))

        # To read file as string:
        file_text = stringio.read()

        return file_text

    # read pdf file
    elif file.type == "application/pdf":
        pdfReader = PdfFileReader(file)
        count = pdfReader.numPages
        all_text = ""

        for i in range(count):
            try:
                page = pdfReader.getPage(i)
                all_text += page.extractText()
            except:
                continue
        file_text = all_text

        return file_text

    # read csv file
    elif file.type == "text/csv":
        csv = pd.read_csv(file)
        # get columns of type string
        string_columns = csv.select_dtypes(include=["object"]).columns
        # get data from columns and join it together
        file_text = ""
        for row in csv[string_columns].values.tolist():
            # remove NaNs
            row = [x for x in row if str(x) != "nan"]
            for column in row:
                txt = ""
                if isinstance(column, list):
                    try:
                        txt = " ".join(column)
                    except:
                        continue
                elif isinstance(column, str):
                    txt = column
                else:
                    continue
                file_text += " " + txt
        return file_text

    # read image file (OCR)
    elif file.type in ["image/jpeg", "image/png"]:
        return pytesseract.image_to_string(Image.open(file))

    # read audio file (AudoToText)
    elif file.type in ["audio/mpeg", "audio/wav", "audio/aac", "audio/x-m4a"]:
        text = audio_to_text(st.session_state["audio_model"], file)
        return text

    else:
        st.warning(f"File type {file.type} not supported")
        return None


@st.cache_resource
def load_audio_model():
    return load_model()
