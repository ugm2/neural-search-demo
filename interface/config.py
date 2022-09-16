from interface.pages import page_landing_page, page_search, page_index

# Define default Session Variables over the whole session.
session_state_variables = {"pipeline": None, "pipeline_func_parameters": []}

# Define Pages for the demo
pages = {
    "Introduction": (page_landing_page, "house-fill"),
    "Search": (page_search, "search"),
    "Index": (page_index, "files"),
}
