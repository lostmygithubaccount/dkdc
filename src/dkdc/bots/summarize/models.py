from marvin import ai_model

from pydantic import BaseModel, Field


@ai_model
class Summary(BaseModel):
    """Summarizes input text"""

    title: str = Field(..., description="The title of the page")
    date: str = Field(..., description="The date of the page")
    authors: list[str] = Field(..., description="A list of authors")
    one_liner: str = Field(..., description="A one-line summary of the text")
    summary: str = Field(..., description="The summary of the input text")
    key_points: list[str] = Field(..., description="A list of key points")
    paragraphs: str = Field(
        ..., description="A few paragraphs summary or as short as needed"
    )
    links: str = Field(..., description="A list of links to related resources")
    references: str = Field(..., description="A list of references")
