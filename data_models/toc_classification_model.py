from typing import List
from pydantic import BaseModel, Field

class TableOfContentsClassifier(BaseModel):
    is_table_of_contents: bool = Field(False, description="Indicates whether the page is classified as a table of contents.")
