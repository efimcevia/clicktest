from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    steps_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    runs = relationship("TestRun", back_populates="scenario")


class TestRun(Base):
    __tablename__ = "testruns"

    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"))
    status = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    scenario = relationship("Scenario", back_populates="runs")