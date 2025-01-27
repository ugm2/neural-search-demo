import streamlit as st

st.set_page_config(
    page_title="Neural Search",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "https://github.com/ugm2/neural-search-demo"},
)

import nltk
from streamlit_option_menu import option_menu

from interface.components import component_select_pipeline
from interface.config import pages, session_state_variables
from interface.utils import load_audio_model

nltk.download("punkt_tab")
nltk.download("averaged_perceptron_tagger_eng")

# Initialization of session state
for key, value in session_state_variables.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Init audio model
st.session_state["audio_model"] = load_audio_model()


def run_demo():

    main_page = st.container()

    st.sidebar.title("🧠 Neural Search 🔎")

    navigation = st.sidebar.container()

    with navigation:

        selected_page = option_menu(
            menu_title=None,
            options=list(pages.keys()),
            icons=[f[1] for f in pages.values()],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"border": "2px solid #818494"},
                "icon": {"font-size": "22px"},
                "nav-link": {"font-size": "20px", "text-align": "left"},
            },
        )
        component_select_pipeline(navigation)

    # Draw the correct page
    pages[selected_page][0](main_page)


run_demo()
