from pydantic import BaseModel


# states
class State(BaseModel):
    """
    Default state.
    """

    notes: dict[str, str] = {"notes": "This is the default note"}
