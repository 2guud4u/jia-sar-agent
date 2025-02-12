import pytest
from logistic_agent import LogisticAgent

class TestLogisticAgent:
    @pytest.fixture
    def agent(self):
        return LogisticAgent()
    
    def test_initialization(self, agent):
        """Test agent initialization and default values"""
        assert agent.name == "logistics_specialist"
        assert agent.role == "Logistic Supply Specialist"
        assert agent.mission_status == "standby"
        assert isinstance(agent.current_conditions, dict)
        assert isinstance(agent.resources, dict)
        assert isinstance(agent.regulations, dict)
        assert isinstance(agent.historical_incidents, dict)

    def test_process_request_get_supplies(self, agent):
        """Test processing a get_supplies request"""
        message = {
            "request_type": "get_supplies",
            "parameters": {
                "location": "Mountain Base Camp",
                "team": "5 members",
                "duration": 3,
                "resources": ["medical", "shelter", "food"]
            }
        }
        response = agent.process_request(message)
        
        assert "status" in response
        assert "recommendations" in response
        assert "metadata" in response
        assert response["metadata"]["location"] == "Mountain Base Camp"
        assert response["metadata"]["team_size"] == "5 members"
        assert response["metadata"]["duration"] == 3
        assert isinstance(response["metadata"]["timestamp"], str)

    def test_process_request_assess_supply_needs(self, agent):
        """Test processing a supply needs assessment request"""
        message = {
            "request_type": "assess_supply_needs",
            "parameters": {
                "location": "Alpine Region",
                "conditions": {
                    "temperature": -5,
                    "weather": "snowing",
                    "terrain": "mountainous"
                }
            }
        }
        response = agent.process_request(message)
        
        assert "status" in response
        assert "assessment" in response
        assert "metadata" in response
        assert response["metadata"]["location"] == "Alpine Region"
        assert isinstance(response["metadata"]["conditions"], dict)
        assert isinstance(response["metadata"]["timestamp"], str)

    def test_process_request_invalid_type(self, agent):
        """Test processing an invalid request type"""
        message = {
            "request_type": "invalid_type",
            "parameters": {}
        }
        response = agent.process_request(message)
        
        assert response["status"] == "error"
        assert "Unknown request type" in response["message"]
        assert isinstance(response["timestamp"], str)

    def test_get_supply_count(self, agent):
        """Test getting supply inventory"""
        response = agent.get_supply_count()
        
        assert "status" in response
        assert "inventory" in response
        assert isinstance(response["inventory"], dict)
        assert isinstance(response["timestamp"], str)

    def test_update_mission_status(self, agent):
        """Test updating mission status"""
        response = agent.update_mission_status("active")
        
        assert response["status"] == "success"
        assert response["new_status"] == "active"
        assert isinstance(response["timestamp"], str)
        assert agent.get_status() == "active"

    def test_error_handling(self, agent):
        """Test error handling in process_request"""
        message = {
            "request_type": "get_supplies",
            "parameters": {
                # Missing required parameters
            }
        }
        response = agent.process_request(message)
        
        assert response["status"] == "error"
        assert isinstance(response["message"], str)
        assert isinstance(response["timestamp"], str)

    def test_get_supplies_detailed(self, agent):
        """Test detailed supply recommendations"""
        location = "Desert Region"
        team = "10 members"
        duration = 5
        required_resources = ["water", "shelter", "communications"]
        
        response = agent.get_supplies(location, team, duration, required_resources)
        
        assert response["status"] == "success"
        assert isinstance(response["recommendations"], str)
        assert response["metadata"]["location"] == location
        assert response["metadata"]["team_size"] == team
        assert response["metadata"]["duration"] == duration
        assert isinstance(response["metadata"]["timestamp"], str)

    def test_assess_supply_needs_detailed(self, agent):
        """Test detailed supply needs assessment"""
        location = "Coastal Area"
        conditions = {
            "weather": "stormy",
            "temperature": 25,
            "humidity": "high",
            "wind_speed": 30
        }
        
        response = agent.assess_supply_needs(location, conditions)
        
        assert response["status"] == "success"
        assert isinstance(response["assessment"], str)
        assert response["metadata"]["location"] == location
        assert response["metadata"]["conditions"] == conditions
        assert isinstance(response["metadata"]["timestamp"], str)

    @pytest.mark.parametrize("status", ["active", "standby", "deployed", "returning"])
    def test_multiple_status_updates(self, agent, status):
        """Test multiple status updates"""
        response = agent.update_mission_status(status)
        assert response["status"] == "success"
        assert response["new_status"] == status
        assert agent.get_status() == status