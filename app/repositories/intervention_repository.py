from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.employee_intervention_model import EmployeeInterventionModel

class InterventionRepository:

    @staticmethod
    async def save_employee_intervention(
        employee_id: int,
        action_taken: str,
        reasoning: str,
        db: Session
    ):

        intervention = EmployeeInterventionModel(
            employee_id=employee_id,
            burnout_score=None,
            action_taken=action_taken,
            reasoning=reasoning
        )

        db.add(intervention)
        db.commit()
        db.refresh(intervention)

        return intervention

    @staticmethod
    async def get_last_intervention(employee_id: int, db: Session):

        return (
            db.query(EmployeeInterventionModel)
            .filter(EmployeeInterventionModel.employee_id == employee_id)
            .order_by(EmployeeInterventionModel.created_at.desc())
            .first()
        )

    @staticmethod
    async def intervention_recently_sent(employee_id: int, db: Session, days: int = 7):

        last = await InterventionRepository.get_last_intervention(employee_id, db)

        if not last:
            return False

        return last.created_at >= datetime.now() - timedelta(days=days)