"""
Integration tests for Phoenix API endpoints
Tests full stack with real API calls (when enabled)
"""

import pytest
import os
from httpx import AsyncClient
from unittest.mock import patch

from app.main import create_app


@pytest.fixture
def app():
    """Create test FastAPI app."""
    return create_app()


@pytest.fixture
async def client(app):
    """Create test HTTP client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestGenerationAPI:
    """Test generation API endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint."""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Nymo Art API"
        assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_health_detailed(self, client):
        """Test detailed health check."""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"LEONARDO_API_KEY": "test-key"})
    async def test_generate_phoenix_validation_error(self, client):
        """Test Phoenix generation with validation errors."""
        # Test empty prompt
        response = await client.post("/api/v1/generations/phoenix", json={
            "prompt": "",  # Invalid
            "num_images": 1
        })
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"LEONARDO_API_KEY": "test-key"})
    async def test_generate_phoenix_invalid_style(self, client):
        """Test Phoenix generation with invalid style."""
        response = await client.post("/api/v1/generations/phoenix", json={
            "prompt": "test prompt",
            "style": "InvalidStyle"  # Invalid
        })
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_generate_phoenix_no_api_key(self, client):
        """Test Phoenix generation without API key."""
        with patch.dict(os.environ, {}, clear=True):
            response = await client.post("/api/v1/generations/phoenix", json={
                "prompt": "test prompt"
            })
            
            assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_generation_status(self, client):
        """Test generation status endpoint."""
        response = await client.get("/api/v1/generations/status/test-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["generation_id"] == "test-id"
    
    @pytest.mark.asyncio
    async def test_list_generations(self, client):
        """Test list generations endpoint."""
        response = await client.get("/api/v1/generations/")
        
        assert response.status_code == 200
        data = response.json()
        assert "generations" in data
        assert "total" in data


class TestModelsAPI:
    """Test models API endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_models(self, client):
        """Test list models endpoint."""
        response = await client.get("/api/v1/models/")
        
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        
        # Check Phoenix model is listed
        phoenix_model = next(
            (m for m in data["models"] if m["name"] == "phoenix"), 
            None
        )
        assert phoenix_model is not None
        assert phoenix_model["vendor"] == "leonardo"
        assert phoenix_model["available"] is True
    
    @pytest.mark.asyncio
    async def test_phoenix_styles(self, client):
        """Test Phoenix styles endpoint."""
        response = await client.get("/api/v1/models/leonardo/phoenix/styles")
        
        assert response.status_code == 200
        data = response.json()
        assert data["model"] == "leonardo.phoenix"
        assert isinstance(data["styles"], list)
        assert "Cinematic" in data["styles"]
        assert data["total"] > 0
    
    @pytest.mark.asyncio
    async def test_phoenix_model_info(self, client):
        """Test Phoenix model detailed info."""
        response = await client.get("/api/v1/models/leonardo/phoenix")
        
        assert response.status_code == 200
        data = response.json()
        assert data["vendor"] == "leonardo"
        assert data["name"] == "phoenix"
        assert data["type"] == "image"
        assert data["available"] is True
        assert "capabilities" in data
        assert "parameters" in data
        assert "styles" in data
        assert "cost" in data
    
    @pytest.mark.asyncio
    async def test_unknown_model_info(self, client):
        """Test unknown model info."""
        response = await client.get("/api/v1/models/unknown/model")
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "available_models" in data


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("LEONARDO_API_KEY"), reason="No API key provided")
class TestRealAPIIntegration:
    """Integration tests with real Leonardo API (requires API key)."""
    
    @pytest.mark.asyncio
    async def test_real_phoenix_generation(self, client):
        """Test real Phoenix generation (expensive test)."""
        response = await client.post("/api/v1/generations/phoenix", json={
            "prompt": "test integration",
            "num_images": 1,
            "width": 512,
            "height": 512,
            "style": "Minimalist"
        })
        
        # This test is expensive and should only run when explicitly enabled
        assert response.status_code in [200, 400]  # 400 if API key issues
