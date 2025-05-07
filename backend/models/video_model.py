from pydantic import BaseModel

class VideoRequest(BaseModel):
    topic: str
    duration: int
    level: str
