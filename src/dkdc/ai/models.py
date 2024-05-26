# imports
from pydantic import BaseModel, Field


# classes
class File(BaseModel):
    """A file object."""

    filename: str = Field(
        ...,
        description="The name of the file. Defaults to `temp.<ext>` if not provided.",
    )
    content: str = Field(..., description="The content of the file.")
