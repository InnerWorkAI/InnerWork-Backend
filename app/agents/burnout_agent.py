import os
import json
import logging
from typing import Dict, Any

from openai import OpenAI
from pydantic import ValidationError

from app.core.config import settings
from app.agents.prompts import AGENT_SYSTEM_PROMPT
from app.agents.actions import execute_action
from app.repositories.burnout_report_repository import BurnoutReportRepository
from app. services.company_analysis_service import CompanyAnalysisService
from app.schemas.agent_schema import AgentDecision, ActionType, RiskLevel

logger = logging.getLogger("burnout_agent")

client = OpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

class BurnoutAgent:
    @staticmethod
    async def run(company_id: int, db) -> Dict[str, Any]:
        try:
            company_data = await CompanyAnalysisService.collect_company_data(company_id, db)
            logger.info(f"Company data collected: {company_data}")

            previous_report = await BurnoutReportRepository.get_last_company_report(company_id, db)
            logger.info(f"Previous report: {previous_report}")

            agent_input = {
                "current_metrics": company_data,
                "previous_report": previous_report
            }

            decision: AgentDecision = await BurnoutAgent.decide(agent_input)
            logger.info(f"Decision from agent: {decision.model_dump()}")

            decision_taken_list = []

            for action_item in decision.actions:
                await execute_action(action_item=action_item, company_id=company_id, db=db, company_data=company_data, risk_level=decision.risk_level.value)
                decision_taken_list.append(action_item.action.value)


            # Save the organizational memory regarding the actions taken
            decision_taken_str = ", ".join(decision_taken_list) if decision_taken_list else ActionType.NO_ACTION.value
            
            await BurnoutReportRepository.save_company_report(
                company_id=company_id,
                average_burnout=company_data.get("average_burnout", 0.0),
                risk_level=decision.risk_level.value,
                decision_taken=decision_taken_str,
                reasoning=decision.overall_reasoning,
                db=db
            )
            logger.info("Company report saved successfully")

            return decision.model_dump()

        except Exception as e:
            logger.exception(f"BurnoutAgent failed for company {company_id}: {e}")
            raise

    @staticmethod
    async def decide(agent_input: dict) -> AgentDecision:
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
            # Validate JSON string directly into the robust AgentDecision schema
            parsed_decision = AgentDecision.model_validate_json(content)
            return parsed_decision

        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning(f"Failed to parse or validate agent JSON response '{e}', returning default no_action")
            return AgentDecision(
                actions=[{
                    "action": ActionType.NO_ACTION,
                    "reasoning": f"Model response parsing/validation failed: {e}",
                    "target_employees": []
                }],
                risk_level=RiskLevel.LOW,
                overall_reasoning="Fallback decision due to model error."
            )
        except Exception as e:
            logger.exception(f"LLM call failed: {e}")
            return AgentDecision(
                actions=[{
                    "action": ActionType.NO_ACTION,
                    "reasoning": f"LLM call failed: {e}",
                    "target_employees": []
                }],
                risk_level=RiskLevel.LOW,
                overall_reasoning="Fallback decision due to fatal LLM error."
            )