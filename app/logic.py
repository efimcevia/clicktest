from database import SessionLocal, Base
from app.models import Scenario, TestRun
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime
import json

db = SessionLocal()

def save_scenario(name: str, steps: list):
    try:
        scenario = Scenario(name=name, steps_json=json.dumps(steps))
        db.add(scenario)
        db.commit()
        return True, None

    except IntegrityError:
        db.rollback()
        return False, "Сценарий с таким именем уже существует!"

    except SQLAlchemyError as e:
        db.rollback()
        return False, f"Ошибка базы данных: {str(e)}"

def get_all_scenarios():
    return db.query(Scenario).order_by(Scenario.created_at.desc()).all()

def get_scenario_by_name(name: str):
    return db.query(Scenario).filter_by(name=name).first()

def save_run(scenario_id: int, status: str):
    run = TestRun(scenario_id=scenario_id, status=status, timestamp=datetime.utcnow())
    db.add(run)
    db.commit()

def get_runs(scenario_id: int):
    return db.query(TestRun).filter_by(scenario_id=scenario_id).order_by(TestRun.timestamp.desc()).all()