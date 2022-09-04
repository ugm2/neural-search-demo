import streamlit as st
from streamlit_option_menu import option_menu
from core.search_index import index, search
from interface.components import component_show_search_result, component_text_input

def page_landing_page(container):
    with container:
        st.header("Neural Search V1.0")

        st.markdown(
            "This is a tool to allow indexing & search content using neural capabilities"
        )
        st.markdown(
            "In this first version you can:"/
            "  - Index raw text as documents"/
            "  - Use Dense Passage Retrieval pipeline"/
            "  - Search the indexed documents"
        )
        
def page_search(container):
    with container:
        st.title("Query me!")
        
        ## SEARCH ##
        query = st.text_input("Query")
        
        if st.button("Search"):
            st.session_state['search_results'] = search(
                queries=[query],
                pipeline=st.session_state['search_pipeline'],
            )
        if 'search_results' in st.session_state:
            component_show_search_result(
                container=container,
                results=st.session_state['search_results'][0]
            )
        
def page_index(container):
    with container:
        st.title("Index time!")
        
        input_funcs = {
            "Raw Text": (component_text_input, "card-text"),
        }
        selected_input = option_menu(
            "Input Text",
            list(input_funcs.keys()),
            icons=[f[1] for f in input_funcs.values()],
            menu_icon="list",
            default_index=0,
            orientation="horizontal",
        )
        
        corpus = input_funcs[selected_input][0](container)
        
        if len(corpus) > 0:
            index_results = None
            if st.button("Index"):
                index_results = index(
                    corpus,
                    st.session_state['index_pipeline'],
                )
            if index_results:
                st.write(index_results)