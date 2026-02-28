from openai import OpenAI
from app.core.config import settings
from app.agents.prompts import (
    HR_REPORT_SYSTEM_PROMPT,
    HR_REPORT_USER_PROMPT_TEMPLATE,
    EMPLOYEE_SUPPORT_SYSTEM_PROMPT,
    EMPLOYEE_SUPPORT_USER_PROMPT_TEMPLATE
)

client = OpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


class ReportGenerationService:

    @staticmethod
    async def generate_hr_report(
        company_name: str,
        employees_data: list,
        dashboard_url: str
    ) -> dict:
        """
        Generates clean HTML snippet focused only on employees and actions.
        No layout wrappers.
        """

        prompt = HR_REPORT_USER_PROMPT_TEMPLATE.format(
            company_name=company_name,
            employees_data=employees_data
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": HR_REPORT_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        analysis_text = response.choices[0].message.content.strip()

        # Remove markdown fences if present
        if analysis_text.startswith("```html"):
            analysis_text = analysis_text[7:]
        if analysis_text.endswith("```"):
            analysis_text = analysis_text[:-3]

        return {
            "company_name": company_name,
            "analysis_text": analysis_text,
            "employees": employees_data,
            "dashboard_url": dashboard_url
        }

    @staticmethod
    async def generate_employee_support_content(
        employee_name: str,
        metrics: dict
    ) -> str:
        """
        Generates highly personalized, compassionate recommendations for an employee.
        """
        prompt = EMPLOYEE_SUPPORT_USER_PROMPT_TEMPLATE.format(
            employee_name=employee_name,
            metrics_average=metrics.get('average', 0),
            metrics_trend=metrics.get('trend', 'stable')
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": EMPLOYEE_SUPPORT_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4
        )

        content = response.choices[0].message.content.strip()

        # Remove markdown fences if present
        if content.startswith("```html"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]

        return content