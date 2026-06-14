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
class AnalysisResponse(BaseModel):
    id: int
    text: str
    model: str
    original_token_count: int
    original_cost: float
    optimized_text: str
    optimized_token_count: int
    optimized_cost: float
    class Config:
        from_attributes = True

class AnalysisUpdate(BaseModel):
    text: str | None = None
    model: str | None = None