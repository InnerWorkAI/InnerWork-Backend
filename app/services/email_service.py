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

async def send_reset_email(email: str, token: str):
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Reset Your Password</title>
    </head>
    <body style="margin:0; padding:0; font-family: Arial, sans-serif; background-color:#f4f4f4;">
        <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:10px; padding:30px; margin:50px 0; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
                        <tr>
                            <td align="center" style="padding-bottom:20px;">
                                <h1 style="color:#9333ea; margin:0;">Reset Your Password</h1>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <p style="color:#333333; font-size:16px; line-height:1.5;">
                                    Hello,<br><br>
                                    You requested a password reset for your account. Click the button below to set a new password:
                                </p>
                                <table width="100%" cellspacing="0" cellpadding="0">
                                    <tr>
                                        <td align="center" style="padding:20px 0;">
                                            <!-- BOTÓN REAL -->
                                            <a href="{reset_url}" target="_blank" 
                                                style="
                                                    background-color:#9333ea;
                                                    color:#ffffff;
                                                    padding:12px 24px;
                                                    text-decoration:none;
                                                    font-weight:bold;
                                                    border-radius:6px;
                                                    display:inline-block;
                                                ">
                                                Reset Password
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                                <p style="color:#333333; font-size:14px; line-height:1.4;">
                                    If you did not request this, please ignore this email. The link will expire in {settings.RESET_TOKEN_EXPIRE_MINUTES} minutes.
                                </p>
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
        subject="Reset Your Password",
        recipients=[email],
        body=html_content,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)