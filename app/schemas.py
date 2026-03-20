from pydantic import BaseModel, Field, field_validator


class HealthResponse(BaseModel):
    status: str = "healthy"


class MessageResponse(BaseModel):
    id: int
    text: str

    model_config = {"from_attributes": True}


class ProcessRequest(BaseModel):
    data: str = Field(..., min_length=1, max_length=10_000)

    @field_validator("data")
    @classmethod
    def sanitize_data(cls, v: str) -> str:
        """Strip whitespace and reject blank input (OWASP input validation)."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Data must not be empty or whitespace-only")
        return stripped


class ProcessResponse(BaseModel):
    received: str
    status: str = "processed"
