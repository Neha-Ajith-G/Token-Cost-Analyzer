from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, description="Input text to analyze")
    model: str = Field(min_length=1, description="Model name")
class AnalyzeResult(BaseModel):
    text: str
    token_count: int
    estimated_cost: float

class CompleteResponse(BaseModel):
    original: AnalyzeResult
    optimized: AnalyzeResult

