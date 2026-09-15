"""Request and response schemas for the HTTP API."""

from pydantic import BaseModel, field_validator


class ConversationCreated(BaseModel):
    conversation_id: str


class ConversationMessage(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        content = value.strip()
        if content == "":
            raise ValueError("content cannot be empty")
        return content
