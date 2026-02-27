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
        You are an expert HR Analyst.

        Create a professional HR burnout risk notification for {company_name}.

        IMPORTANT RULES:
        - Output ONLY a clean HTML snippet.
        - DO NOT include <html>, <head>, or <body>.
        - DO NOT include tables.
        - DO NOT include styling wrappers.
        - Keep it concise and executive-level.
        - No emojis.

        Employees at risk:
        {employees_data}

        Structure required:

        <h3>Executive Overview</h3>
        Short professional summary.

        <h3>Employees Requiring Attention</h3>
        Use a <ul> list mentioning name + burnout score + trend.

        <h3>Recommended Next Steps</h3>
        Bullet points with actionable HR actions.
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