from fastapi import FastAPI, Depends, HTTPException
from app.backend_services import (
    load_pricings,
    count_tokens,
    calculate_cost,
    compress_text,
    generate_analysis)
from app.schemas import AnalyzeRequest, CompleteResponse, AnalysisResponse,AnalysisUpdate
from sqlalchemy.orm import Session
from app.db import engine, get_db
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
    try:
       response= generate_analysis(req.text, req.model)
       return response
    except ValueError as e:
        raise HTTPException( status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.post("/analyzedtexts", response_model=AnalysisResponse)
def save_analysis(req: AnalyzeRequest, db: Session = Depends(get_db)):
    pricings = load_pricings()
    compressed = compress_text(req.text)
    _,original_token_count = count_tokens(req.text, req.model, pricings)
    original_cost = calculate_cost(req.model, original_token_count, pricings)
    _,compressed_token_count = count_tokens(compressed, req.model, pricings)
    compressed_cost = calculate_cost(req.model, compressed_token_count, pricings)

    record = AnalysisRecord(
        text=req.text,
        model=req.model,
        original_token_count=original_token_count,
        original_cost=original_cost,
        optimized_text=compressed,
        optimized_token_count=compressed_token_count,
        optimized_cost=compressed_cost
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return record

#gets all
# @app.get("/analyzedtexts",response_model=list[AnalysisResponse])
# def get_analyzedtexts(db: Session = Depends(get_db)):
#     records = db.query(AnalysisRecord).all()
#     return records
@app.get("/analyzedtexts",response_model=list[AnalysisResponse])
def get_analyzedtexts(id: int | None = None, model: str | None = None, db: Session = Depends(get_db)):
    query = db.query(AnalysisRecord)
    if id is not None:
        #filters by id
        query = query.filter(AnalysisRecord.id == id)
    if model is not None:
        #filters by model
        query = query.filter(AnalysisRecord.model == model)
    #returns all records if no filters applied
    return query.all()

@app.get("/analyzedtexts/{id}", response_model = AnalysisResponse)
def get_save_by_id( id: int, db: Session = Depends(get_db)):
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

#Update record,allows to modify prompt or model assoc with a saved analysis record
@app.put("/analyzedtexts/{id}", response_model = AnalysisResponse)
def update_saved(id: int, req: AnalysisUpdate, db: Session = Depends(get_db)):
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    if req.text:
        record.text = req.text
    if req.model is not None:
        record.model = req.model
    #recalculate
    pricings = load_pricings()
    record.optimized_text = compress_text(record.text)
    record.original_token_count = count_tokens(record.text, record.model, pricings)[1]
    record.original_cost = calculate_cost(record.model, record.original_token_count, pricings)
    record.optimized_token_count = count_tokens(record.optimized_text, record.model, pricings)[1]
    record.optimized_cost = calculate_cost(record.model, record.optimized_token_count, pricings)
    db.commit()
    db.refresh(record)
    return record

@app.delete("/analyzedtexts/{id}")
def delete_save(id: int,db: Session = Depends(get_db)):
    record = (db.query(AnalysisRecord).filter(AnalysisRecord.id == id).first())
    if not record:
        raise HTTPException(
            status_code=404,
            detail="Record not found"
        )

    db.delete(record)
    db.commit()
    return {
        "message": f"Record {id} deleted successfully"
    }