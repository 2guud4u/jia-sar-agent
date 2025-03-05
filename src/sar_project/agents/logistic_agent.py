import json
import datetime
from typing import Dict, List, Any
from base_agent import SARBaseAgent
from google import genai
import os

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
        from dotenv import load_dotenv
        load_dotenv()
        
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Enhanced data tracking
        self.current_conditions = {}
        self.resources = {}
        self.regulations = {}
        self.historical_incidents = []  # Changed to a list to store multiple incidents
        self.resource_usage_log = []  # New log to track resource usage across missions

    def process_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced process_request method with incident and resource tracking
        """
        try:
            # Log the entire incoming message for comprehensive tracking
            request_log = {
                "timestamp": str(datetime.datetime.now()),
                "full_message": message
            }
            
            # Extract request type and parameters from the message
            request_type = message.get("request_type")
            params = message.get("parameters", {})

            # Process the request based on type
            if request_type == "get_supplies":
                response = self.get_supplies(
                    location=params.get("location"),
                    team=params.get("team"),
                    duration=params.get("duration"),
                    required_resources=params.get("resources", [])
                )
            elif request_type == "get_supply_count":
                response = self.get_supply_count()
            
            elif request_type == "assess_supply_needs":
                response = self.assess_supply_needs(
                    location=params.get("location"),
                    conditions=params.get("conditions", {})
                )
            else:
                response = {
                    "status": "error",
                    "message": f"Unknown request type: {request_type}"
                }

            # Enhance response with request details and track the incident
            full_response = {
                "original_request": request_log,
                **response,
                "request_details": {
                    "type": request_type,
                    "parameters": params
                }
            }

            # Log the incident for historical analysis
            self.log_incident(full_response)

            return full_response

        except Exception as e:
            error_response = {
                "status": "error",
                "message": str(e),
                "timestamp": str(datetime.datetime.now()),
                "original_message": message
            }
            self.log_incident(error_response)
            return error_response

    def log_incident(self, incident_data: Dict[str, Any]):
        """
        Log incidents for future reference and analysis
        """
        try:
            # Add timestamp if not present
            if "timestamp" not in incident_data:
                incident_data["timestamp"] = str(datetime.datetime.now())
            
            # Store the incident
            self.historical_incidents.append(incident_data)
            
            # Optional: Limit the number of stored incidents to prevent excessive memory usage
            if len(self.historical_incidents) > 100:
                self.historical_incidents = self.historical_incidents[-100:]
            
            return True
        except Exception as e:
            print(f"Error logging incident: {e}")
            return False

    def track_resource_usage(self, mission_id: str, resources_used: Dict[str, Any]):
        """
        Track resources used in a specific mission
        """
        usage_log_entry = {
            "mission_id": mission_id,
            "timestamp": str(datetime.datetime.now()),
            "resources_used": resources_used
        }
        
        self.resource_usage_log.append(usage_log_entry)
        
        # Update overall resource inventory
        for resource, quantity in resources_used.items():
            if resource in self.resources:
                self.resources[resource] -= quantity
            else:
                print(f"Warning: Resource {resource} not found in inventory")
        
        return usage_log_entry

    def get_historical_incidents(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve recent historical incidents
        """
        return self.historical_incidents[-limit:]

    def get_supplies(self, location: str, team: str, duration: int, 
                    required_resources: List[str]) -> Dict[str, Any]:
        """Generate supply recommendations using the configured LLM"""
        try:
            # Use historical incident analysis to inform supply recommendations
            historical_context = self.analyze_historical_incidents(location)

            prompt = f"""Based on the following mission parameters and historical context, provide detailed supply recommendations:
            Location: {location}
            Team Size: {team}
            Duration: {duration} days
            Required Resources: {', '.join(required_resources)}
            Historical Context: {historical_context}

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

    def analyze_historical_incidents(self, location: str) -> str:
        """
        Analyze historical incidents for a specific location
        """
        relevant_incidents = [
            incident for incident in self.historical_incidents 
            if incident.get('location') == location
        ]
        
        if not relevant_incidents:
            return "No previous incidents found for this location."
        
        # Summarize key insights from relevant incidents
        summary = "Previous Incident Insights:\n"
        for incident in relevant_incidents[-3:]:  # Take last 3 incidents
            summary += f"- {incident.get('timestamp')}: {incident.get('message', 'No details')}\n"
        
        return summary

    def generate(self, prompt: str) -> str:
        """Generate content using Gemini"""
        config = self.get_config_list()
        response = self.client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        return response.text