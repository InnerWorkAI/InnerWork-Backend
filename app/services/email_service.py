from app.services.report_generation_service import ReportGenerationService
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings
from typing import List, Optional

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

class EmailService:

    @staticmethod
    async def send_email(
        recipient_email: str,
        subject: str,
        title: str,
        body_text: str,
        button_text: Optional[str] = None,
        button_url: Optional[str] = None
    ):

        button_html = ""
        if button_text and button_url:
            button_html = f"""
            <table width="100%" cellspacing="0" cellpadding="0">
                <tr>
                    <td align="center" style="padding:30px 0;">
                        <a href="{button_url}" target="_blank"
                           style="
                                background-color:#9333ea;
                                color:#ffffff;
                                padding:14px 28px;
                                text-decoration:none;
                                font-weight:bold;
                                border-radius:6px;
                                display:inline-block;
                                font-size:15px;
                           ">
                            {button_text}
                        </a>
                    </td>
                </tr>
            </table>
            """

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
        </head>
        <body style="margin:0;padding:0;font-family:Arial,sans-serif;background:#f4f4f4;">
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0"
                               style="background:#ffffff;
                                      margin:50px 0;
                                      padding:40px;
                                      border-radius:8px;
                                      box-shadow:0 4px 10px rgba(0,0,0,0.05);">

                            <tr>
                                <td align="center" style="padding-bottom:25px;">
                                    <h1 style="color:#9333ea;margin:0;">
                                        {title}
                                    </h1>
                                </td>
                            </tr>

                            <tr>
                                <td style="font-size:15px;line-height:1.6;color:#333;">
                                    {body_text}
                                </td>
                            </tr>

                            <tr>
                                <td>
                                    {button_html}
                                </td>
                            </tr>

                            <tr>
                                <td style="padding-top:30px;
                                           font-size:12px;
                                           color:#999;
                                           text-align:center;">
                                    &copy; {settings.FRONTEND_URL.split('//')[-1]} - All rights reserved
                                </td>
                            </tr>

                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        message = MessageSchema(
            subject=subject,
            recipients=[recipient_email],
            body=html_content,
            subtype="html"
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        

        
    @staticmethod
    async def send_company_report_email(
        recipient_email: str,
        company_name: str,
        average_burnout: float,
        risk_level: str,
        executive_summary: str,
        dashboard_url: str,
        company_data: Optional[dict] = None
    ):
        subject = f"Organizational Burnout Report – {company_name}"

        department_section = ""
        if company_data and "department_burnout" in company_data:
            dept_scores_html = "".join([
                f"<li>{d['name']}: {d['average']}%</li>" for d in company_data["department_burnout"]
            ])
            
            critical_depts_html = ""
            if company_data.get("critical_departments"):
                critical_lines = "".join([
                    f"<li><strong>{d['name']}</strong>: {d['average']}%</li>" for d in company_data["critical_departments"]
                ])
                critical_depts_html = f"""
                <strong style='color:#e11d48;'>Critical Departments (Action Required):</strong>
                <ul style='color:#e11d48;'>
                    {critical_lines}
                </ul>
                """

            if dept_scores_html:
                department_section = f"""
                <strong>Department Breakdown:</strong>
                <ul>
                    {dept_scores_html}
                </ul>
                {critical_depts_html}
                <br>
                """

        body = f"""
        Dear Administrator,<br><br>

        The latest organizational burnout analysis for <strong>{company_name}</strong> has been completed.<br><br>

        <strong>Average Burnout Level:</strong> {average_burnout:.2f}%<br>
        <strong>Organizational Risk Level:</strong> {risk_level}<br><br>

        {department_section}

        <strong>Executive Summary:</strong><br>
        {executive_summary}<br><br>

        We recommend reviewing the full dashboard for detailed department insights,
        risk trends, and suggested interventions.
        """

        await EmailService.send_email(
            recipient_email=recipient_email,
            subject=subject,
            title="Organizational Burnout Report",
            body_text=body,
            button_text="View Dashboard",
            button_url=dashboard_url
        )

    @staticmethod
    async def send_hr_risk_report_email(
        recipient_email: str,
        report: dict
    ):

        subject = f"Burnout Risk Alert – {report['company_name']}"

        await EmailService.send_email(
            recipient_email=recipient_email,
            subject=subject,
            title="HR Burnout Risk Report",
            body_text=report["analysis_text"],
            button_text="View Full Dashboard",
            button_url=report["dashboard_url"]
        )



    @staticmethod
    async def send_employee_support_email(
        recipient_email: str,
        employee_name: str,
        support_recommendations: str,
        meeting_url: Optional[str] = None
    ):
        subject = "Confidential Wellbeing Support"

        meeting_section = ""
        if meeting_url:
            meeting_section = f"""
            You may schedule a confidential meeting here:
            <br><br>
            """

        body = f"""
        Dear {employee_name},<br><br>

        We continuously monitor workplace wellbeing to ensure a healthy and sustainable work environment.

        Based on recent feedback, we would like to proactively offer support resources that may help you maintain balance and performance.<br><br>

        <strong>Recommended Actions:</strong><br>
        {support_recommendations}<br><br>

        {meeting_section}

        Please remember that this message is confidential and intended solely as a supportive initiative.
        Your wellbeing is important to us.
        """

        await EmailService.send_email(
            recipient_email=recipient_email,
            subject=subject,
            title="We’re Here to Support You",
            body_text=body,
            button_text="Schedule a Confidential Meeting" if meeting_url else None,
            button_url=meeting_url if meeting_url else None
        )