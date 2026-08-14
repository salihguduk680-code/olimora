from pydantic import BaseModel


class CompatibilityAspectResponse(BaseModel):
    person_a_body: str
    person_b_body: str
    aspect_type: str
    orb: float
    tone: str


class CompatibilityResponse(BaseModel):
    friend_name: str
    communication: int
    emotional: int
    attraction: int
    stability: int
    highlights: list[CompatibilityAspectResponse]
    disclaimer: str
