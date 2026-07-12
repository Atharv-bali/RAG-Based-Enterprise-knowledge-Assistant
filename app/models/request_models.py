from pydantic import BaseModel, Field, validator

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="The query question to ask the RAG assistant")

    @validator('question')
    def validate_question(cls, v):
        if not v or not v.strip():
            raise ValueError("Question cannot be empty or whitespace only")
        return v.strip()