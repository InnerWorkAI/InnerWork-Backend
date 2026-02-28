import logging
from typing import Dict, Any, Optional

from app.services.report_generation_service import ReportGenerationService
from app.services.email_service import EmailService
from app.repositories.intervention_repository import InterventionRepository
from app.models.company_admin_model import CompanyAdminModel
from app.models.user_model import UserModel
from app.models.employee_model import EmployeeModel
from app.services.company_service import CompanyService
from app.services.employee_analysis_service import EmployeeAnalysisService
from app.core.config import settings
from app.schemas.agent_schema import AgentActionItem, ActionType

logger = logging.getLogger("uvicorn")

async def _handle_send_company_report(
    action_item: AgentActionItem, company_id: int, db, company_data: Optional[Dict[str, Any]], risk_level: str
):
    company = CompanyService.get_company_by_id(db, company_id)
    primary_admin = db.query(CompanyAdminModel).filter(
        CompanyAdminModel.company_id == company_id,
        CompanyAdminModel.is_primary_admin.is_(True)
    ).first()

    if not primary_admin:
        logger.warning(f"No primary admin found for company {company_id}")
        return

    user = db.query(UserModel).filter(UserModel.id == primary_admin.user_id).first()
    admin_email = user.email

    avg_burnout = company_data.get("average_burnout", 0) if company_data else 0

    await EmailService.send_company_report_email(
        recipient_email=admin_email,
        company_name=company.name,
        average_burnout=avg_burnout,
        risk_level=risk_level,
        executive_summary=action_item.reasoning,
        dashboard_url=f"{settings.FRONTEND_URL}/company/{company_id}/dashboard",
        company_data=company_data
    )


async def _handle_notify_hr_about_employees(
    action_item: AgentActionItem, company_id: int, db, company_data: Optional[Dict[str, Any]], risk_level: str
):
    company = CompanyService.get_company_by_id(db, company_id)

    hr_users = db.query(UserModel).join(CompanyAdminModel).filter(
        CompanyAdminModel.company_id == company_id,
        CompanyAdminModel.is_primary_admin.is_(False)
    ).all()

    hr_emails = [u.email for u in hr_users]
    employees_data = []

    for emp_id in action_item.target_employees:
        analysis = await EmployeeAnalysisService.analyze_employee(emp_id, db)

        if not analysis.get("is_high_risk", False):
            continue

        emp = db.query(EmployeeModel).filter(
            EmployeeModel.id == emp_id
        ).first()

        if not emp:
            continue

        employees_data.append({
            "id": emp.id,
            "name": f"{emp.first_name} {emp.last_name}",
            "average": analysis.get("average", 0),
            "trend": analysis.get("trend", "stable")
        })

        await InterventionRepository.save_employee_intervention(
            employee_id=emp.id,
            action_taken=ActionType.NOTIFY_HR_ABOUT_EMPLOYEES.value,
            reasoning=action_item.reasoning,
            db=db
        )

    if not employees_data:
        logger.info("No real high-risk employees. Email not sent.")
        return

    enriched_report = await ReportGenerationService.generate_hr_report(
        company_name=company.name,
        employees_data=employees_data,
        dashboard_url=f"{settings.FRONTEND_URL}/company/{company_id}/dashboard"
    )

    for email in hr_emails:
        await EmailService.send_hr_risk_report_email(
            recipient_email=email,
            report=enriched_report
        )


async def _handle_notify_employee_support(
    action_item: AgentActionItem, company_id: int, db, company_data: Optional[Dict[str, Any]], risk_level: str
):
    for employee_id in action_item.target_employees:
        emp = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
        if not emp:
            continue
            
        # Get real metrics to generate empathetic content
        analysis = await EmployeeAnalysisService.analyze_employee(employee_id, db)
        
        support_recommendations = await ReportGenerationService.generate_employee_support_content(
            employee_name=emp.first_name,
            metrics=analysis
        )

        await EmailService.send_employee_support_email(
            recipient_email=emp.user.email,
            employee_name=f"{emp.first_name} {emp.last_name}",
            support_recommendations=support_recommendations
        )

        await InterventionRepository.save_employee_intervention(
            employee_id=employee_id,
            action_taken=ActionType.NOTIFY_EMPLOYEE_SUPPORT.value,
            reasoning=action_item.reasoning,
            db=db
        )


async def _handle_no_action(
    action_item: AgentActionItem, company_id: int, db, company_data: Optional[Dict[str, Any]], risk_level: str
):
    logger.info(f"No action required for company {company_id}: {action_item.reasoning}")



ACTION_HANDLERS = {
    ActionType.SEND_COMPANY_REPORT: _handle_send_company_report,
    ActionType.NOTIFY_HR_ABOUT_EMPLOYEES: _handle_notify_hr_about_employees,
    ActionType.NOTIFY_EMPLOYEE_SUPPORT: _handle_notify_employee_support,
    ActionType.NO_ACTION: _handle_no_action,
}

async def execute_action(
    action_item: AgentActionItem, 
    company_id: int, 
    db, 
    company_data: Optional[Dict[str, Any]] = None, 
    risk_level: str = "LOW"
):
    """
    Orchestrates the execution of a specific agent action using the unified
    Strategy pattern mapping to its corresponding handler.

    Args:
        action_item (AgentActionItem): The specific action model step determined by the agent.
        company_id (int): The ID of the company involved.
        db: The database active session.
        company_data (Optional[Dict]): Additional context about the company metrics.
        risk_level (str): The calculated risk level for the overall company context.
    """
    action_type = action_item.action
    handler = ACTION_HANDLERS.get(action_type)

    if not handler:
        logger.warning(f"Unknown ActionType '{action_type}' for company {company_id}")
        return

    logger.info(f"Executing '{action_type.value}' handler for company {company_id}.")
    await handler(
        action_item=action_item,
        company_id=company_id,
        db=db,
        company_data=company_data,
        risk_level=risk_level,
    )