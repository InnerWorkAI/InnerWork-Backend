from sqlalchemy.orm import Session
from app.models.company_burnout_report_model import CompanyBurnoutReportModel


class BurnoutReportRepository:

    @staticmethod
    async def get_last_company_report(company_id: int, db: Session):

        report = (
            db.query(CompanyBurnoutReportModel)
            .filter(CompanyBurnoutReportModel.company_id == company_id)
            .order_by(CompanyBurnoutReportModel.created_at.desc())
            .first()
        )

        if not report:
            return None

        return {
            "average_burnout": report.average_burnout,
            "risk_level": report.risk_level,
            "decision_taken": report.decision_taken,
            "reasoning": report.reasoning,
            "created_at": report.created_at.isoformat()
        }

    @staticmethod
    async def has_report_been_sent_this_week(company_id: int, db: Session) -> bool:
        """
        Check if a company report was already sent this week.
        """
        from datetime import datetime, timedelta
        
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        
        report_count = (
            db.query(CompanyBurnoutReportModel)
            .filter(
                CompanyBurnoutReportModel.company_id == company_id,
                CompanyBurnoutReportModel.decision_taken.ilike("%send_company_report%"),
                CompanyBurnoutReportModel.created_at >= one_week_ago
            )
            .count()
        )
        
        return report_count > 0

    @staticmethod
    async def save_company_report(
        company_id: int,
        average_burnout: float,
        risk_level: str,
        decision_taken: str,
        reasoning: str,
        db: Session
    ):

        report = CompanyBurnoutReportModel(
            company_id=company_id,
            average_burnout=average_burnout,
            risk_level=risk_level,
            decision_taken=decision_taken,
            reasoning=reasoning
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        return report