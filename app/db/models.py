from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    time = Column(DateTime, default=datetime.datetime.utcnow)
    name = Column(String, index=True)

    results = relationship("Result", back_populates="scan", cascade="all, delete-orphan")

class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    x = Column(Integer)
    y = Column(Integer)
    status = Column(String)
    hollow_classification = Column(JSON, nullable=True)
    cracked_classification = Column(JSON, nullable=True)
    image_file_path = Column(String, nullable=True)
    audio_file_path = Column(String, nullable=True)

    scan = relationship("Scan", back_populates="results")