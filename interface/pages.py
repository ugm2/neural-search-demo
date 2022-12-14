import streamlit as st
from streamlit_option_menu import option_menu
from core.search_index import index, search
from interface.components import (
    component_file_input,
    component_show_pipeline,
    component_show_search_result,
    component_text_input,
    component_article_url,
)


def page_landing_page(container):
    with container:
        st.header("Neural Search V2.1")

        st.markdown(
            "This is a tool to allow indexing & search content using neural capabilities"
        )
        st.markdown(
            "It uses the [Haystack](https://haystack.deepset.ai/overview/intro) open-source framework for building search systems"
        )
        st.markdown(
            "In this second version you can:"
            "\n  - Index raw text, URLs, CSVs, PDFs, Images and even audio!"
            "\n  - Use Dense Passage Retrieval, Keyword Search pipeline and DPR Ranker pipelines"
            "\n  - Search the indexed documents"
            "\n  - Read your responses out loud using the `audio_output` option!"
        )
        st.markdown(
            "TODO list:"
            "\n  - File type classification and converter nodes"
            "\n  - Build other pipelines"
        )
        st.markdown(
            "Follow development of the tool [here](https://github.com/ugm2/neural-search-demo)"
            "\n\nDeveloped with 💚 by [@ugm2](https://github.com/ugm2)"
        )


def page_search(container):
    with container:
        st.title("Query me!")

        ## SEARCH ##
        query = st.text_input("Query")

        component_show_pipeline(st.session_state["pipeline"], "search_pipeline")

        if st.button("Search"):
            with st.spinner("Searching..."):
                st.session_state["search_results"] = search(
                    queries=[query],
                    pipeline=st.session_state["pipeline"]["search_pipeline"],
                )
        if st.session_state["search_results"] is not None:
            component_show_search_result(
                container=container, results=st.session_state["search_results"][0]
            )


def page_index(container):
    with container:
        st.title("Index time!")

        component_show_pipeline(st.session_state["pipeline"], "index_pipeline")

        input_funcs = {
            "Raw Text": (component_text_input, "card-text"),
            "URL": (component_article_url, "link"),
            "File": (component_file_input, "file-text"),
        }
        selected_input = option_menu(
            None,
            list(input_funcs.keys()),
            icons=[f[1] for f in input_funcs.values()],
            menu_icon="list",
            default_index=0,
            orientation="horizontal",
        )

        clear_index = st.sidebar.checkbox("Clear Index", True)

        doc_id = st.session_state["doc_id"]
        corpus, doc_id = input_funcs[selected_input][0](container, doc_id)

        if len(corpus) > 0:
            index_results = None
            if st.button("Index"):
                with st.spinner("Indexing..."):
                    index_results = index(
                        documents=corpus,
                        pipeline=st.session_state["pipeline"]["index_pipeline"],
                        clear_index=clear_index,
                    )
                    st.session_state["doc_id"] = doc_id
                st.success(f"{len(index_results)} documents indexed successfully!")
