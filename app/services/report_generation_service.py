from openai import OpenAI
from app.core.config import settings


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

        prompt = f"""
        You are an expert, compassionate HR Analyst.

        Create a professional and highly respectful HR burnout risk notification for {company_name}.
        The tone must be empathetic but urgent.

        IMPORTANT RULES:
        - Output ONLY a clean HTML snippet.
        - DO NOT include <html>, <head>, or <body>.
        - DO NOT include tables.
        - DO NOT include styling wrappers.
        - Keep it concise, executive-level, and action-oriented.
        - No emojis.

        Employees at risk:
        {employees_data}

        Structure required:

        <h3>Executive Overview</h3>
        Provide a short professional summary focusing on the importance of acting early to support wellbeing.

        <h3>Employees Requiring Attention</h3>
        Use a <ul> list mentioning the employee name, burnout score, and trend. Format it cleanly.

        <h3>Recommended Next Steps</h3>
        Provide bullet points with concrete, supportive actions HR can take (e.g., 1-on-1 check-ins, workload review).
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You output only clean HTML snippets."
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
        prompt = f"""
        You are an empathetic Wellbeing Coach.
        
        You need to write a short, supportive, and confidential message snippet to be included in an email for {employee_name}.
        
        The employee has an average burnout score of {metrics.get('average', 0)}% and a trend that is '{metrics.get('trend', 'stable')}'.
        
        IMPORTANT RULES:
        - Output ONLY a clean HTML snippet (e.g., a few <p> tags and maybe a <ul>).
        - DO NOT include <html>, <head>, or <body>.
        - Do not use a robotic or diagnostic tone. Do not explicitly state their "burnout score is X".
        - Focus on normalization, support, and practical but gentle recommendations (e.g., taking time off, prioritizing workload, scheduling a chat).
        - Keep it under 3 paragraphs.
        - No emojis.
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You output only clean HTML snippets focusing on employee wellbeing."
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