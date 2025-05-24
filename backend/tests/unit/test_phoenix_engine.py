"""
Unit tests for Phoenix engine
Tests business logic with mocked external dependencies
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.schemas import LeonardoPhoenixRequest, LeonardoEngineConfig
from core.engine.leonardo.phoenix import PhoenixEngine, PHOENIX_STYLES


@pytest.fixture
def mock_config():
    """Mock Leonardo engine configuration."""
    return LeonardoEngineConfig(
        name="phoenix",
        vendor="leonardo",
        api_key="test-api-key",
        base_url="https://api.test.com",
        timeout=60,
        poll_interval=1
    )


@pytest.fixture
def mock_leonardo_client():
    """Mock Leonardo client."""
    client = Mock()
    client.create_generation = Mock(return_value="test-generation-id")
    client.poll_generation = Mock(return_value={
        "generated_images": [
            {"url": "https://example.com/image1.jpg"},
            {"url": "https://example.com/image2.jpg"}
        ]
    })
    client.download_image = Mock(return_value=b"fake-image-data")
    return client


@pytest.fixture
def phoenix_engine(mock_config):
    """Create Phoenix engine with mocked client."""
    with patch('backend.core.engine.leonardo.phoenix.LeonardoClient') as mock_client_class:
        mock_client_class.return_value = Mock()
        engine = PhoenixEngine(mock_config)
        return engine


class TestPhoenixEngine:
    """Test Phoenix engine functionality."""
    
    def test_initialization(self, mock_config):
        """Test engine initialization."""
        with patch('backend.core.engine.leonardo.phoenix.LeonardoClient'):
            engine = PhoenixEngine(mock_config)
            assert engine.config.name == "phoenix"
            assert engine.config.vendor == "leonardo"
    
    def test_validate_request_success(self, phoenix_engine):
        """Test successful request validation."""
        request = LeonardoPhoenixRequest(
            prompt="test prompt",
            style="Cinematic",
            width=1024,
            height=1024
        )
        
        # Should not raise exception
        phoenix_engine.validate_request(request)
    
    def test_validate_request_invalid_style(self, phoenix_engine):
        """Test validation with invalid style."""
        request = LeonardoPhoenixRequest(
            prompt="test prompt",
            style="InvalidStyle",
            width=1024,
            height=1024
        )
        
        with pytest.raises(ValueError, match="Unknown style"):
            phoenix_engine.validate_request(request)
    
    def test_validate_request_invalid_dimensions(self, phoenix_engine):
        """Test validation with invalid dimensions."""
        request = LeonardoPhoenixRequest(
            prompt="test prompt",
            width=500,  # Invalid
            height=1024
        )
        
        with pytest.raises(ValueError, match="Invalid width"):
            phoenix_engine.validate_request(request)
    
    def test_build_payload_basic(self, phoenix_engine):
        """Test basic payload building."""
        request = LeonardoPhoenixRequest(
            prompt="test prompt",
            width=1024,
            height=1024,
            style="Cinematic"
        )
        
        payload = phoenix_engine._build_payload(request)
        
        assert payload["prompt"] == "test prompt"
        assert payload["width"] == 1024
        assert payload["height"] == 1024
        assert payload["styleUUID"] == PHOENIX_STYLES["Cinematic"]
        assert "negativePrompt" not in payload  # Should not be included when None
    
    def test_build_payload_with_negative_prompt(self, phoenix_engine):
        """Test payload building with negative prompt."""
        request = LeonardoPhoenixRequest(
            prompt="test prompt",
            negative_prompt="ugly, blurry",
            width=1024,
            height=1024
        )
        
        payload = phoenix_engine._build_payload(request)
        
        assert payload["negativePrompt"] == "ugly, blurry"
    
    def test_build_payload_with_upscale(self, phoenix_engine):
        """Test payload building with upscaling enabled."""
        request = LeonardoPhoenixRequest(
            prompt="test prompt",
            width=1024,
            height=1024,
            upscale=True,
            upscale_strength=0.7
        )
        
        payload = phoenix_engine._build_payload(request)
        
        assert payload["upscaleRatio"] == 2
        assert payload["upscaleStrength"] == 0.7
    
    def test_estimate_cost_basic(self, phoenix_engine):
        """Test cost estimation."""
        request = LeonardoPhoenixRequest(
            prompt="test prompt",
            num_outputs=2,
            width=1024,
            height=1024
        )
        
        cost = phoenix_engine.estimate_cost(request)
        
        assert isinstance(cost, float)
        assert cost > 0
    
    def test_estimate_cost_with_alchemy(self, phoenix_engine):
        """Test cost estimation with Alchemy enabled."""
        request_no_alchemy = LeonardoPhoenixRequest(
            prompt="test prompt",
            alchemy=False,
            width=1024,
            height=1024
        )
        
        request_with_alchemy = LeonardoPhoenixRequest(
            prompt="test prompt",
            alchemy=True,
            width=1024,
            height=1024
        )
        
        cost_no_alchemy = phoenix_engine.estimate_cost(request_no_alchemy)
        cost_with_alchemy = phoenix_engine.estimate_cost(request_with_alchemy)
        
        assert cost_with_alchemy > cost_no_alchemy
    
    @pytest.mark.asyncio
    async def test_generate_success(self, phoenix_engine, mock_leonardo_client):
        """Test successful image generation."""
        phoenix_engine.client = mock_leonardo_client
        
        request = LeonardoPhoenixRequest(
            prompt="test prompt",
            num_outputs=2,
            width=1024,
            height=1024
        )
        
        result = await phoenix_engine.generate(request)
        
        assert len(result.outputs) == 2
        assert result.metadata.generation_id == "test-generation-id"
        assert result.metadata.engine_name == "phoenix"
        assert result.metadata.vendor == "leonardo"
        
        # Verify client calls
        mock_leonardo_client.create_generation.assert_called_once()
        mock_leonardo_client.poll_generation.assert_called_once_with("test-generation-id")
        assert mock_leonardo_client.download_image.call_count == 2
    
    def test_get_available_styles(self):
        """Test getting available styles."""
        styles = PhoenixEngine.get_available_styles()
        
        assert isinstance(styles, list)
        assert "Cinematic" in styles
        assert "Portrait" in styles
        assert len(styles) > 0
    
    def test_get_style_uuid(self):
        """Test getting style UUID."""
        uuid = PhoenixEngine.get_style_uuid("Cinematic")
        assert uuid == PHOENIX_STYLES["Cinematic"]
        
        uuid = PhoenixEngine.get_style_uuid("NonexistentStyle")
        assert uuid is None


@pytest.mark.parametrize("style,expected_uuid", [
    ("Cinematic", "6090d980-5b1f-44c3-a3e9-a3a83b05b2a6"),
    ("Portrait", "23e98ab7-7b91-4a29-9ab4-f726e1a2f4a5"),
    ("None", None),
])
def test_style_uuids(style, expected_uuid):
    """Test style UUID mapping."""
    assert PhoenixEngine.get_style_uuid(style) == expected_uuid
