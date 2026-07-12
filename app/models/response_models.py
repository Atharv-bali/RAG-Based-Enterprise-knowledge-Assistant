from pydantic import BaseModel

class AnswerResponse(BaseModel):
    status: str
    answer: str