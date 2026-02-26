from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings

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