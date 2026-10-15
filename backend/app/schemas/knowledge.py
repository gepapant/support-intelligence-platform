from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    model_validator,
)


class KnowledgeArticleCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )
    content: str = Field(min_length=1)
    source_url: HttpUrl | None = None


class KnowledgeArticleUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    content: str | None = Field(
        default=None,
        min_length=1,
    )
    source_url: HttpUrl | None = None
    is_active: bool | None = None

    @model_validator(mode="after")
    def validate_update(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")

        required_if_provided = {
            "title",
            "content",
            "is_active",
        }

        for field_name in required_if_provided:
            if (
                field_name in self.model_fields_set
                and getattr(self, field_name) is None
            ):
                raise ValueError(f"{field_name} cannot be null")

        return self


class KnowledgeArticleRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    title: str
    content: str
    source_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
