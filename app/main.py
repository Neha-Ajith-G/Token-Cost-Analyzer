from fastapi import FastAPI
from app.backend_services import (
    load_pricings,
    count_tokens,
    calculate_cost,
    compress_text)
from app.schemas import AnalyzeRequest, AnalyzeResult, CompleteResponse
from app.db import engine
from app.models import AnalysisRecord
from app.db import Base

Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to the Token Cost Analyzer."}

@app.get("/models")
def models():
    pricings = load_pricings()
    return {"models": list(pricings.keys())}

@app.post("/analyze", response_model = CompleteResponse)
def analyze(req: AnalyzeRequest):
    pricings = load_pricings()
    compressed = compress_text(req.text)
    original_tokens, original_token_count = count_tokens(req.text, req.model, pricings)
    original_cost = calculate_cost(req.model, original_token_count, pricings)
    compressed_tokens, compressed_token_count = count_tokens(compressed, req.model, pricings)
    compressed_cost = calculate_cost(req.model, compressed_token_count, pricings)
    return CompleteResponse(
        original=AnalyzeResult(text=req.text, token_count=original_token_count, estimated_cost=original_cost),
        optimized=AnalyzeResult(text=compressed, token_count=compressed_token_count, estimated_cost=compressed_cost)
    )
