import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.employee_model import EmployeeModel
from app.models.user_model import UserModel
from app.repositories.weekly_burnout_form_repository import WeeklyBurnoutFormRepository
from app.services.email_service import EmailService
from app.core.config import settings

scheduler = AsyncIOScheduler()

async def _send_reminders_to_pending():
    db: Session = SessionLocal()
    try:
        employees = (
            db.query(EmployeeModel)
            .join(UserModel, EmployeeModel.user_id == UserModel.id)
            .filter(UserModel.is_active == True)
            .all()
        )

        for emp in employees:
            if not WeeklyBurnoutFormRepository.exists_this_week(db, emp.id):

                form_url = f"{settings.FRONTEND_URL}/weekly-burnout-form"
                await EmailService.send_email(
                    recipient_email=emp.user.email,
                    subject="Reminder: Complete Your Weekly Burnout Form",
                    title="Weekly Burnout Form Reminder",
                    body_text=f"Hello {emp.first_name},<br><br>This is a friendly reminder to complete your <strong>weekly burnout form</strong>.",
                    button_text="Fill Out Form",
                    button_url=form_url
                )
                            
                print(f"📧 Remainder sent to {emp.first_name} ({emp.user.email})")
    finally:
        db.close()


def start_scheduler():
    """
    Start the APScheduler to run the reminder task at specified intervals.
    - For testing: every 5 minutes
    - For production: every Friday at 9 AM
    """

    # scheduler.add_job(
    #     _send_reminders_to_pending,
    #     trigger='interval', 
    #     minutes=2,
    #     id='weekly_form_reminder',
    #     replace_existing=True
    # )

    scheduler.add_job(
        _send_reminders_to_pending,
        trigger='cron',
        day_of_week='fri',
        hour=9,
        minute=0,
        id='weekly_form_reminder_weekly',
        replace_existing=True
    )

    scheduler.start()
    print("🕒 Scheduler started successfully")