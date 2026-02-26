from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings
from typing import List

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
        button_text: str = None,
        button_url: str = None
    ):
        """
        Send a stylized HTML email with optional button.
        - recipient_email: The email address of the recipient
        - subject: The subject of the email
        - title: The main title/header of the email
        - body_text: The main content of the email (can include HTML)
        - button_text: (Optional) The text to display on the button
        - button_url: (Optional) The URL the button should link to
        """

        button_html = ""
        if button_text and button_url:
            button_html = f"""
            <table width="100%" cellspacing="0" cellpadding="0">
                <tr>
                    <td align="center" style="padding:20px 0;">
                        <a href="{button_url}" target="_blank" 
                            style="
                                background-color:#9333ea;
                                color:#ffffff;
                                padding:12px 24px;
                                text-decoration:none;
                                font-weight:bold;
                                border-radius:6px;
                                display:inline-block;
                            ">
                            {button_text}
                        </a>
                    </td>
                </tr>
            </table>
            """

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
        </head>
        <body style="margin:0; padding:0; font-family: Arial, sans-serif; background-color:#f4f4f4;">
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:10px; padding:30px; margin:50px 0; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
                            <tr>
                                <td align="center" style="padding-bottom:20px;">
                                    <h1 style="color:#9333ea; margin:0;">{title}</h1>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <p style="color:#333333; font-size:16px; line-height:1.5;">
                                        {body_text}
                                    </p>
                                    {button_html}
                                    <p style="color:#888888; font-size:12px; text-align:center; margin-top:30px;">
                                        &copy; {settings.FRONTEND_URL.split('//')[-1]} - All rights reserved
                                    </p>
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
        dashboard_url: str
    ):
        subject = f"Organizational Burnout Report – {company_name}"

        body = f"""
        Dear Administrator,<br><br>

        The latest organizational burnout analysis for <strong>{company_name}</strong> has been completed.<br><br>

        <strong>Average Burnout Level:</strong> {average_burnout:.2f}%<br>
        <strong>Organizational Risk Level:</strong> {risk_level}<br><br>

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
        company_name: str,
        at_risk_employees: List[dict],
        recommendations: str,
        dashboard_url: str
    ):
        subject = f"HR Alert – Employees at Risk ({company_name})"

        employee_list_html = "<ul>"
        for emp in at_risk_employees:
            employee_list_html += f"""
            <li>
                <strong>{emp.get('name')}</strong> – 
                Burnout Score: {emp.get('burnout_score')}%
            </li>
            """
        employee_list_html += "</ul>"

        body = f"""
        Dear HR Team,<br><br>

        The burnout monitoring system has identified employees at elevated risk levels within <strong>{company_name}</strong>.<br><br>

        <strong>Employees flagged:</strong>
        {employee_list_html}

        <strong>Recommended Actions:</strong><br>
        {recommendations}<br><br>

        We advise initiating confidential follow-ups and reviewing workload distribution.
        """

        await EmailService.send_email(
            recipient_email=recipient_email,
            subject=subject,
            title="HR Burnout Risk Alert",
            body_text=body,
            button_text="Open HR Dashboard",
            button_url=dashboard_url
        )

    @staticmethod
    async def send_employee_support_email(
        recipient_email: str,
        employee_name: str,
        support_recommendations: str,
        meeting_url: str = None
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