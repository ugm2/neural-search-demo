from io import StringIO
import core.pipelines as pipelines_functions
from inspect import getmembers, isfunction
from newspaper import Article
from PyPDF2 import PdfFileReader
import streamlit as st
import pandas as pd


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
        string_columns = csv.select_dtypes(include=['object']).columns
        # get data from columns and join it together
        file_text = ""
        for row in csv[string_columns].values.tolist():
            # remove NaNs
            row = [x for x in row if str(x) != 'nan']
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

    else:
        st.warning(f"File type {file.type} not supported")
        return None

