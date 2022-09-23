import streamlit as st
from interface.utils import (
    get_pipelines,
    extract_text_from_url,
    extract_text_from_file,
    reset_vars_data,
)
from interface.draw_pipelines import get_pipeline_graph


def component_select_pipeline(container):
    pipeline_names, pipeline_funcs, pipeline_func_parameters = get_pipelines()
    with container:
        selected_pipeline = st.selectbox(
            "Select pipeline",
            pipeline_names,
            index=pipeline_names.index("Keyword Search")
            if "Keyword Search" in pipeline_names
            else 0,
        )
        index_pipe = pipeline_names.index(selected_pipeline)
        st.write("---")
        st.header("Pipeline Parameters")
        for parameter, value in pipeline_func_parameters[index_pipe].items():
            if isinstance(value, str):
                value = st.text_input(parameter, value)
            elif isinstance(value, bool):
                value = st.checkbox(parameter, value)
            elif isinstance(value, int):
                value = int(st.number_input(parameter, value=value))
            elif isinstance(value, float):
                value = float(st.number_input(parameter, value=value))
            pipeline_func_parameters[index_pipe][parameter] = value
        if (
            st.session_state["pipeline"] is None
            or st.session_state["pipeline"]["name"] != selected_pipeline
            or list(st.session_state["pipeline_func_parameters"][index_pipe].values())
            != list(pipeline_func_parameters[index_pipe].values())
        ):
            st.session_state["pipeline_func_parameters"] = pipeline_func_parameters
            (search_pipeline, index_pipeline,) = pipeline_funcs[
                index_pipe
            ](**pipeline_func_parameters[index_pipe])
            st.session_state["pipeline"] = {
                "name": selected_pipeline,
                "search_pipeline": search_pipeline,
                "index_pipeline": index_pipeline,
                "doc": pipeline_funcs[index_pipe].__doc__,
            }
            reset_vars_data()


def component_show_pipeline(pipeline, pipeline_name):
    """Draw the pipeline"""
    expander_text = "Show pipeline"
    if pipeline["doc"] is not None and "BUG" in pipeline["doc"]:
        expander_text += "  ⚠️"
    with st.expander(expander_text):
        if pipeline["doc"] is not None:
            st.markdown(pipeline["doc"])
        fig = get_pipeline_graph(pipeline[pipeline_name])
        st.plotly_chart(fig, use_container_width=True)


def component_show_search_result(container, results):
    with container:
        for idx, document in enumerate(results):
            st.markdown(f"### Match {idx+1}")
            st.markdown(f"**Text**: {document['text']}")
            st.markdown(f"**Document**: {document['id']}")
            if "_split_id" in document["meta"]:
                st.markdown(f"**Document Chunk**: {document['meta']['_split_id']}")
            if "score" in document:
                st.markdown(f"**Score**: {document['score']:.3f}")
            if "content_audio" in document:
                st.audio(str(document["content_audio"]))
            st.markdown("---")


def component_text_input(container, doc_id):
    """Draw the Text Input widget"""
    with container:
        texts = []
        with st.expander("Enter documents"):
            while True:
                text = st.text_input(f"Document {doc_id}", key=doc_id)
                if text != "":
                    texts.append({"text": text, "doc_id": doc_id})
                    doc_id += 1
                    st.markdown("---")
                else:
                    break
        corpus = [{"text": doc["text"], "id": doc["doc_id"]} for doc in texts]
        return corpus, doc_id


def component_article_url(container, doc_id):
    """Draw the Article URL widget"""
    with container:
        urls = []
        with st.expander("Enter URLs"):
            while True:
                url = st.text_input(f"URL {doc_id}", key=doc_id)
                if url != "":
                    urls.append({"text": extract_text_from_url(url), "doc_id": doc_id})
                    doc_id += 1
                    st.markdown("---")
                else:
                    break

        for idx, doc in enumerate(urls):
            with st.expander(f"Preview URL {idx}"):
                st.write(doc["text"])

        corpus = [{"text": doc["text"], "id": doc["doc_id"]} for doc in urls]
        return corpus, doc_id


def component_file_input(container, doc_id):
    """Draw the extract text from file widget"""
    with container:
        files = []
        with st.expander("Enter Files"):
            while True:
                file = st.file_uploader(
                    "Upload a .txt, .pdf, .csv, image file", key=doc_id
                )
                if file != None:
                    extracted_text = extract_text_from_file(file)
                    if extracted_text != None:
                        files.append({"text": extracted_text, "doc_id": doc_id})
                        doc_id += 1
                        st.markdown("---")
                    else:
                        break
                else:
                    break

        for idx, doc in enumerate(files):
            with st.expander(f"Preview File {idx}"):
                st.write(doc["text"])

        corpus = [{"text": doc["text"], "id": doc["doc_id"]} for doc in files]
        return corpus, doc_id
