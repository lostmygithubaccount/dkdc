from pydantic import BaseModel


# states
class State(BaseModel):
    """
    Default state.
    """

    info: dict = {"me": "dkdc.ai", "creator": "dkdc.dev", "version": "infinity"}
    notes: dict = {"notes": "this is a default note"}
