import streamlit as st
import core.pipelines as pipelines_functions
from inspect import getmembers, isfunction
from networkx.drawing.nx_agraph import to_agraph


def component_select_pipeline(container):
    pipeline_names, pipeline_funcs = list(
        zip(*getmembers(pipelines_functions, isfunction))
    )
    pipeline_names = [
        " ".join([n.capitalize() for n in name.split("_")]) for name in pipeline_names
    ]
    with container:
        selected_pipeline = st.selectbox(
            "Select pipeline",
            pipeline_names,
            index=pipeline_names.index("Keyword Search")
            if "Keyword Search" in pipeline_names
            else 0,
        )
        (
            st.session_state["search_pipeline"],
            st.session_state["index_pipeline"],
        ) = pipeline_funcs[pipeline_names.index(selected_pipeline)]()


def component_show_pipeline(container, pipeline):
    """Draw the pipeline"""
    with st.expander("Show pipeline"):
        graphviz = to_agraph(pipeline.graph)
        graphviz.layout("dot")
        st.graphviz_chart(graphviz.string())


def component_show_search_result(container, results):
    with container:
        for idx, document in enumerate(results):
            st.markdown(f"### Match {idx+1}")
            st.markdown(f"**Text**: {document['text']}")
            st.markdown(f"**Document**: {document['id']}")
            if document["score"] is not None:
                st.markdown(f"**Score**: {document['score']:.3f}")
            st.markdown("---")


def component_text_input(container):
    """Draw the Text Input widget"""
    with container:
        texts = []
        doc_id = 1
        with st.expander("Enter documents"):
            while True:
                text = st.text_input(f"Document {doc_id}", key=doc_id)
                if text != "":
                    texts.append({"text": text})
                    doc_id += 1
                    st.markdown("---")
                else:
                    break
        corpus = [
            {"text": doc["text"], "id": doc_id} for doc_id, doc in enumerate(texts)
        ]
        return corpus
