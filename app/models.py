from pydantic import BaseModel, HttpUrl, field_validator

class CompareRequest(BaseModel):
    input1: HttpUrl
    input2: HttpUrl
    method: str = "orb"

    @field_validator("method")
    def validate_method(cls, value):
        if value not in ["orb", "hist", "phash"]:
            raise ValueError("Invalid method. Use 'orb', 'hist', or 'phash'")
        return value
