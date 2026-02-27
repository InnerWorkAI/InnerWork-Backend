import os
import json
import logging
from openai import OpenAI
from app.core.config import settings
from app.agents.prompts import AGENT_SYSTEM_PROMPT
from app.agents.actions import execute_action
from app.services.company_analysis_service import collect_company_data
from app.repositories.burnout_report_repository import BurnoutReportRepository

logger = logging.getLogger("burnout_agent")

client = OpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

class BurnoutAgent:

    @staticmethod
    async def run(company_id: int, db):
        try:
            logger.info(f"BurnoutAgent starting for company {company_id}")

            # Recoger métricas actuales
            company_data = await collect_company_data(company_id, db)
            logger.info(f"Company data collected: {company_data}")

            # Obtener último reporte (memoria)
            previous_report = await BurnoutReportRepository.get_last_company_report(company_id, db)
            logger.info(f"Previous report: {previous_report}")

            agent_input = {
                "current_metrics": company_data,
                "previous_report": previous_report
            }

            # Decidir acción con LLM
            decision = await BurnoutAgent.decide(agent_input)
            logger.info(f"Decision from agent: {decision}")

            # Ejecutar acción
            await execute_action(decision, company_id, db, company_data=company_data)
            logger.info("Actions executed successfully")

            # Guardar memoria organizacional
            await BurnoutReportRepository.save_company_report(
                company_id=company_id,
                average_burnout=company_data["average_burnout"],
                risk_level=decision.get("risk_level"),
                decision_taken=decision.get("action"),
                reasoning=decision.get("reasoning"),
                db=db
            )
            logger.info("Company report saved successfully")

            return decision

        except Exception as e:
            logger.exception(f"BurnoutAgent failed for company {company_id}: {e}")
            raise

    @staticmethod
    async def decide(agent_input: dict):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                    {"role": "user", "content": json.dumps(agent_input)}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content.strip()
            return json.loads(content)

        except json.JSONDecodeError:
            logger.warning("Failed to parse agent JSON response, returning no_action")
            return {
                "action": "no_action",
                "risk_level": "LOW",
                "reasoning": "Model response parsing failed.",
                "target_employees": []
            }
        except Exception as e:
            logger.exception(f"LLM call failed: {e}")
            return {
                "action": "no_action",
                "risk_level": "LOW",
                "reasoning": f"LLM call failed: {e}",
                "target_employees": []
            }