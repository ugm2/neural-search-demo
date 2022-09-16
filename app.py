import streamlit as st

st.set_page_config(
    page_title="Neural Search",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "https://github.com/ugm2/neural-search-demo"},
)

from streamlit_option_menu import option_menu
from interface.config import session_state_variables, pages
from interface.components import component_select_pipeline

# Initialization of session state
for key, value in session_state_variables.items():
    if key not in st.session_state:
        st.session_state[key] = value


def run_demo():

    main_page = st.container()

    st.sidebar.title("🧠 Neural Search 🔎")

    navigation = st.sidebar.container()

    with navigation:

        selected_page = option_menu(
            menu_title="Navigation",
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
