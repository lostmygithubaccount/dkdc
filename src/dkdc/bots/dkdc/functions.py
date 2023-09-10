from marvin import ai_fn


# functions
@ai_fn
def create_function(task: str = "", name: str = "fn", language: str = "Python") -> str:
    """
    Creates a simple, typed function to accomplish
    the specified task in the specified language
    of the specified name.
    """
    task, name, language = task, name, language
    return ""


@ai_fn
def summarize_html_str(html_str: str = "") -> str:
    """
    Summarizes the HTML string.
    """
    html_str = html_str
    return ""
