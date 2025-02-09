from abc import ABC, abstractmethod
import json
import datetime
from typing import Dict, List, Any
from autogen import AssistantAgent
from sar_project.agents.base_agent import SARBaseAgent

class LogisticAgent(SARBaseAgent):
    def __init__(self, name="logistics_specialist", knowledge_base=None):
        system_message = """You are a Logistic Supply specialist for SAR operations. Your role is to:
            1. Manage equipment and supplies
            2. Ensure environmental compliance
            3. Distribute resources efficiently
            4. Anticipate supply needs
            5. Manage resource allocation
            
            Key Performance Indicators:
            - Equipment readiness rate
            - Supply inventory accuracy
            - Time to fulfill resource requests
            - Cost efficiency of resource management
            - Base camp setup and maintenance efficiency
            
            You have access to the following data:
            Resource databases, environmental regulations, historical incident data
            
            Respond with detailed, actionable recommendations while considering:
            - Environmental conditions
            - Team size and composition
            - Mission duration
            - Location-specific requirements
            - Safety regulations
            """
        
        super().__init__(
            name=name,
            role="Logistic Supply Specialist",
            system_message=system_message,
            knowledge_base=knowledge_base
        )
        
        self.current_conditions = {}
        self.resources = {}
        self.regulations = {}
        self.historical_incidents = {}

    def process_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process logistics-related requests"""
        try:
            # Extract request type and parameters from the message
            request_type = message.get("request_type")
            params = message.get("parameters", {})

            if request_type == "get_supplies":
                return self.get_supplies(
                    location=params.get("location"),
                    team=params.get("team"),
                    duration=params.get("duration"),
                    required_resources=params.get("resources", [])
                )
            elif request_type == "get_supply_count":
                return self.get_supply_count()
            elif request_type == "assess_supply_needs":
                return self.assess_supply_needs(
                    location=params.get("location"),
                    conditions=params.get("conditions", {})
                )
            else:
                return {
                    "status": "error",
                    "message": f"Unknown request type: {request_type}",
                    "timestamp": str(datetime.datetime.now())
                }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": str(datetime.datetime.now())
            }

    def get_supplies(self, location: str, team: str, duration: int, 
                    required_resources: List[str]) -> Dict[str, Any]:
        """Generate supply recommendations using the configured LLM"""
        try:
            prompt = f"""Based on the following mission parameters, provide detailed supply recommendations:
            Location: {location}
            Team Size: {team}
            Duration: {duration} days
            Required Resources: {', '.join(required_resources)}

            Please provide a structured response including:
            1. Essential supplies list with quantities
            2. Priority levels for each item (High/Medium/Low)
            3. Special considerations for the location and duration
            4. Backup/contingency supplies
            5. Estimated supply weights and volumes
            """

            # Use Autogen's built-in message handling
            response = self.generate(prompt)

            supply_recommendations = {
                "status": "success",
                "recommendations": response,
                "metadata": {
                    "location": location,
                    "team_size": team,
                    "duration": duration,
                    "timestamp": str(datetime.datetime.now())
                }
            }
            
            return supply_recommendations

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get supply recommendations: {str(e)}",
                "timestamp": str(datetime.datetime.now())
            }

    def assess_supply_needs(self, location: str, conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Assess supply needs based on conditions using the configured LLM"""
        try:
            prompt = f"""Analyze the following conditions and provide a comprehensive supply needs assessment:
            Location: {location}
            Environmental Conditions: {json.dumps(conditions, indent=2)}

            Please provide a structured analysis including:
            1. Critical supply requirements
            2. Environmental impact considerations
            3. Risk assessment and mitigation strategies
            4. Recommended backup supplies and contingencies
            5. Resource optimization recommendations
            """

            # Use Autogen's built-in message handling
            response = self.generate(prompt)

            assessment = {
                "status": "success",
                "assessment": response,
                "metadata": {
                    "location": location,
                    "conditions": conditions,
                    "timestamp": str(datetime.datetime.now())
                }
            }
            
            return assessment

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to assess supply needs: {str(e)}",
                "timestamp": str(datetime.datetime.now())
            }

    def get_supply_count(self) -> Dict[str, Any]:
        """Get current supply inventory"""
        return {
            "status": "success",
            "inventory": self.resources,
            "timestamp": str(datetime.datetime.now())
        }

    def update_mission_status(self, status: str) -> Dict[str, Any]:
        """Update the agent's mission status"""
        self.mission_status = status
        return {
            "status": "success",
            "message": "Mission status updated",
            "new_status": status,
            "timestamp": str(datetime.datetime.now())
        }