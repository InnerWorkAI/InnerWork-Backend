from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.weekly_burnout_form_model import WeeklyBurnoutFormModel



class EmployeeAnalysisService:

    HIGH_THRESHOLD = 75.0

    @staticmethod
    async def analyze_employee(employee_id: int, db: Session):

        four_weeks_ago = datetime.now() - timedelta(weeks=4)

        forms = (
            db.query(WeeklyBurnoutFormModel)
            .filter(WeeklyBurnoutFormModel.employee_id == employee_id)
            .filter(WeeklyBurnoutFormModel.created_at >= four_weeks_ago)
            .order_by(WeeklyBurnoutFormModel.created_at.desc())
            .all()
        )

        if not forms:
            return {
                "average": 0,
                "trend": "stable",
                "is_high_risk": False
            }

        average = sum(f.final_burnout_score for f in forms) / len(forms)

        trend = EmployeeAnalysisService.calculate_employee_trend(employee_id, db)

        return {
            "average": round(average, 2),
            "trend": trend,
            "is_high_risk": average >= EmployeeAnalysisService.HIGH_THRESHOLD
        }

    @staticmethod
    def calculate_employee_trend(employee_id: int, db: Session):

        now = datetime.now()
        two_weeks_ago = now - timedelta(weeks=2)
        four_weeks_ago = now - timedelta(weeks=4)

        recent_avg = (
            db.query(func.avg(WeeklyBurnoutFormModel.final_burnout_score))
            .filter(
                WeeklyBurnoutFormModel.employee_id == employee_id,
                WeeklyBurnoutFormModel.created_at >= two_weeks_ago
            )
            .scalar()
        )

        older_avg = (
            db.query(func.avg(WeeklyBurnoutFormModel.final_burnout_score))
            .filter(
                WeeklyBurnoutFormModel.employee_id == employee_id,
                WeeklyBurnoutFormModel.created_at >= four_weeks_ago,
                WeeklyBurnoutFormModel.created_at < two_weeks_ago
            )
            .scalar()
        )

        if not recent_avg or not older_avg:
            return "stable"

        if recent_avg > older_avg + 5.0:
            return "increasing"
        elif recent_avg < older_avg - 5.0:
            return "decreasing"
        else:
            return "stable"