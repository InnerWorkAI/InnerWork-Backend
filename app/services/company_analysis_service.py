from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.weekly_burnout_form_model import WeeklyBurnoutFormModel
from app.models.employee_model import EmployeeModel


HIGH_THRESHOLD = 7.0
MEDIUM_THRESHOLD = 4.0


async def collect_company_data(company_id: int, db: Session):

    four_weeks_ago = datetime.utcnow() - timedelta(weeks=4)

    forms = (
        db.query(WeeklyBurnoutFormModel)
        .join(EmployeeModel, EmployeeModel.id == WeeklyBurnoutFormModel.employee_id)
        .filter(EmployeeModel.company_id == company_id)
        .filter(WeeklyBurnoutFormModel.created_at >= four_weeks_ago)
        .all()
    )

    if not forms:
        return {
            "average_burnout": 0,
            "high_risk_percentage": 0,
            "medium_risk_percentage": 0,
            "employees_high_risk": [],
            "trend": "stable"
        }

    total_score = sum(f.burnout_score for f in forms if f.burnout_score)
    average_burnout = total_score / len(forms)

    high_risk_forms = [f for f in forms if f.burnout_score >= HIGH_THRESHOLD]
    medium_risk_forms = [
        f for f in forms
        if MEDIUM_THRESHOLD <= f.burnout_score < HIGH_THRESHOLD
    ]

    high_risk_percentage = (len(high_risk_forms) / len(forms)) * 100
    medium_risk_percentage = (len(medium_risk_forms) / len(forms)) * 100

    # Empleados únicos en alto riesgo
    employees_high_risk = list({
        f.employee_id for f in high_risk_forms
    })

    trend = calculate_trend(company_id, db)

    return {
        "average_burnout": round(average_burnout, 2),
        "high_risk_percentage": round(high_risk_percentage, 2),
        "medium_risk_percentage": round(medium_risk_percentage, 2),
        "employees_high_risk": employees_high_risk,
        "trend": trend
    }


def calculate_trend(company_id: int, db: Session):

    now = datetime.utcnow()
    two_weeks_ago = now - timedelta(weeks=2)
    four_weeks_ago = now - timedelta(weeks=4)

    recent_avg = (
        db.query(func.avg(WeeklyBurnoutFormModel.burnout_score))
        .join(EmployeeModel)
        .filter(EmployeeModel.company_id == company_id)
        .filter(WeeklyBurnoutFormModel.created_at >= two_weeks_ago)
        .scalar()
    )

    older_avg = (
        db.query(func.avg(WeeklyBurnoutFormModel.burnout_score))
        .join(EmployeeModel)
        .filter(EmployeeModel.company_id == company_id)
        .filter(
            WeeklyBurnoutFormModel.created_at >= four_weeks_ago,
            WeeklyBurnoutFormModel.created_at < two_weeks_ago
        )
        .scalar()
    )

    if not recent_avg or not older_avg:
        return "stable"

    if recent_avg > older_avg + 0.5:
        return "increasing"
    elif recent_avg < older_avg - 0.5:
        return "decreasing"
    else:
        return "stable"