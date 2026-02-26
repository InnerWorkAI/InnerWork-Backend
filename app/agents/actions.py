import logging
from sqlalchemy import func
from app.services.email_service import EmailService
from app.repositories.intervention_repository import InterventionRepository
from app.models.company_admin_model import CompanyAdminModel
from app.models.user_model import UserModel
from app.models.employee_model import EmployeeModel
from app.models.weekly_burnout_form_model import WeeklyBurnoutFormModel
from app.services.company_service import CompanyService
from app.core.config import settings

logger = logging.getLogger("uvicorn")


async def execute_action(decision: dict, company_id: int, db):
    action = decision.get("action")
    target_employees = decision.get("target_employees", [])
    reasoning = decision.get("reasoning", "")

    if action == "send_company_report":
        company = CompanyService.get_company_by_id(db, company_id)

        # Obtener admin principal
        primary_admin = db.query(CompanyAdminModel).filter(
            CompanyAdminModel.company_id == company_id,
            CompanyAdminModel.is_primary_admin.is_(True)
        ).first()

        if not primary_admin:
            logger.warning(f"No primary admin found for company {company_id}")
            return

        user = db.query(UserModel).filter(UserModel.id == primary_admin.user_id).first()
        admin_email = user.email

        await EmailService.send_company_report_email(
            recipient_email=admin_email,
            company_name=company.name,
            average_burnout=decision.get("average_burnout", 0),
            risk_level=decision.get("risk_level", "LOW"),
            executive_summary=reasoning,
            dashboard_url=f"{settings.FRONTEND_URL}/company/{company_id}/dashboard"
        )

    elif action == "notify_hr_about_employees":
        company = CompanyService.get_company_by_id(db, company_id)

        # Obtener HR (admins secundarios)
        hr_users = db.query(UserModel).join(CompanyAdminModel).filter(
            CompanyAdminModel.company_id == company_id,
            CompanyAdminModel.is_primary_admin.is_(False)
        ).all()
        hr_emails = [u.email for u in hr_users]

        # Preparar lista de empleados en riesgo con su burnout promedio
        employees_data = []
        for emp_id in target_employees:
            emp = db.query(EmployeeModel).filter(EmployeeModel.id == emp_id).first()
            if not emp:
                continue

            # Calcular burnout promedio desde WeeklyBurnoutFormModel
            avg_burnout = db.query(func.avg(WeeklyBurnoutFormModel.burnout_score)).filter(
                WeeklyBurnoutFormModel.employee_id == emp.id
            ).scalar() or 0

            employees_data.append({
                "name": f"{emp.first_name} {emp.last_name}",
                "burnout_score": round(avg_burnout, 2)
            })

            # Guardar intervención
            await InterventionRepository.save_employee_intervention(
                employee_id=emp.id,
                action_taken="notify_hr",
                reasoning=reasoning,
                db=db
            )

        # Enviar email a cada HR
        for email in hr_emails:
            await EmailService.send_hr_risk_report_email(
                recipient_email=email,
                company_name=company.name,
                at_risk_employees=employees_data,
                recommendations=reasoning,
                dashboard_url=f"{settings.FRONTEND_URL}/company/{company_id}/dashboard"
            )

    elif action == "notify_employee_support":
        for employee_id in target_employees:
            emp = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
            if not emp:
                continue

            await EmailService.send_employee_support_email(
                recipient_email=emp.user.email,
                employee_name=f"{emp.first_name} {emp.last_name}",
                support_recommendations=reasoning
            )

            await InterventionRepository.save_employee_intervention(
                employee_id=employee_id,
                action_taken="notify_employee_support",
                reasoning=reasoning,
                db=db
            )

    elif action == "no_action":
        logger.info(f"No action required for company {company_id}")
        return

    else:
        logger.warning(f"Unknown action '{action}' for company {company_id}")
        return