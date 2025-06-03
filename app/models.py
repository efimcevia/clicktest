from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
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
    tester_name = Column(String, default=None)

    scenario = relationship("Scenario", back_populates="runs")
    test_cases = relationship("TestCaseResult", back_populates="run", cascade="all, delete-orphan")

class TestCaseResult(Base):
    __tablename__ = "test_case_results"

    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("testruns.id"))
    title = Column(String)
    description = Column(String)
    status = Column(String)
    duration = Column(Float)

    run = relationship("TestRun", back_populates="test_cases")



class Screenshot(Base):
    __tablename__ = "screenshots"
    id = Column(Integer, primary_key=True)
    object_id = Column(Integer, nullable=False)
    object_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
