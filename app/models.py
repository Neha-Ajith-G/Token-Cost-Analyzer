from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float

from app.db import Base

class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id = Column(Integer, primary_key=True, index=True)

    text = Column(String, nullable=False)
    model = Column(String, nullable=False)

    original_token_count = Column(Integer, nullable=False)
    original_cost = Column(Float, nullable=False)

    optimized_text = Column(String, nullable=False)
    optimized_token_count = Column(Integer, nullable=False)
    optimized_cost = Column(Float, nullable=False)
