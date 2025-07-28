"""
Testing Infrastructure for Ash Bot
"""

import pytest
import asyncio
import logging
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import sys

# Add bot directory to path for testing
bot_dir = Path(__file__).parent.parent / "bot"
sys.path.insert(0, str(bot_dir))

from utils.keyword_detector import KeywordDetector
from core.config_manager import ConfigManager
from handlers.message_handler import MessageHandler
from integrations.claude_api import ClaudeAPI

# Test fixtures
@pytest.fixture
def keyword_detector():
    """Create keyword detector instance for testing"""
    return KeywordDetector()

@pytest.fixture
def mock_config():
    """Create mock configuration"""
    config = Mock(spec=ConfigManager)
    config.get_int.return_value = 10
    config.get.return_value = "test"
    config.get_bool.return_value = True
    config.get_allowed_channels.return_value = []
    config.is_channel_allowed.return_value = True
    return config

@pytest.fixture
def mock_discord_message():
    """Create mock Discord message"""
    message = Mock()
    message.author = Mock()
    message.author.id = 123456789
    message.author.display_name = "TestUser"
    message.author.bot = False
    message.guild = Mock()
    message.guild.id = 987654321
    message.channel = Mock()
    message.channel.id = 555666777
    message.content = "I feel worthless"
    message.add_reaction = AsyncMock()
    message.reply = AsyncMock()
    return message

class TestKeywordDetector:
    """Test suite for KeywordDetector"""
    
    def test_high_crisis_detection(self, keyword_detector):
        """Test detection of high crisis keywords"""
        test_messages = [
            "I want to kill myself",
            "I'm going to end it all",
            "I can't take it anymore, I want to die",
            "Nobody would miss me if I was gone"
        ]
        
        for message in test_messages:
            result = keyword_detector.check_message(message)
            assert result['needs_response'] is True
            assert result['crisis_level'] == 'high'
            assert len(result['detected_categories']) > 0
    
    def test_medium_crisis_detection(self, keyword_detector):
        """Test detection of medium crisis keywords"""
        test_messages = [
            "I'm having a panic attack",
            "Everything hurts so much",
            "I can't breathe, I'm losing control",
            "I'm completely broken"
        ]
        
        for message in test_messages:
            result = keyword_detector.check_message(message)
            assert result['needs_response'] is True
            assert result['crisis_level'] == 'medium'
            assert len(result['detected_categories']) > 0
    
    def test_low_crisis_detection(self, keyword_detector):
        """Test detection of low crisis keywords"""
        test_messages = [
            "I feel worthless",
            "I hate myself",
            "I'm so anxious lately",
            "I feel empty inside"
        ]
        
        for message in test_messages:
            result = keyword_detector.check_message(message)
            assert result['needs_response'] is True
            assert result['crisis_level'] == 'low'
            assert len(result['detected_categories']) > 0
    
    def test_no_crisis_detection(self, keyword_detector):
        """Test messages that shouldn't trigger detection"""
        test_messages = [
            "I love pizza",
            "How's the weather today?",
            "Thanks for helping me",
            "I'm excited about vacation"
        ]
        
        for message in test_messages:
            result = keyword_detector.check_message(message)
            assert result['needs_response'] is False
            assert result['crisis_level'] == 'none'
            assert len(result['detected_categories']) == 0
    
    def test_custom_keyword_addition(self, keyword_detector):
        """Test adding custom keywords"""
        custom_keywords = ["community specific phrase", "unique struggle term"]
        
        # Add custom keywords
        keyword_detector.add_custom_keywords('high', 'test_category', custom_keywords)
        
        # Test detection
        result = keyword_detector.check_message("I'm dealing with community specific phrase")
        assert result['needs_response'] is True
        assert result['crisis_level'] == 'high'
    
    def test_empty_message_handling(self, keyword_detector):
        """Test handling of empty or None messages"""
        test_cases = [None, "", "   ", "\n\t"]
        
        for message in test_cases:
            result = keyword_detector.check_message(message)
            assert result['needs_response'] is False
            assert result['crisis_level'] == 'none'
    
    def test_keyword_stats(self, keyword_detector):
        """Test keyword statistics functionality"""
        stats = keyword_detector.get_keyword_stats()
        
        assert 'high_crisis' in stats
        assert 'medium_crisis' in stats
        assert 'low_crisis' in stats
        assert 'total' in stats
        assert isinstance(stats['total'], int)
        assert stats['total'] > 0

class TestConfigManager:
    """Test suite for ConfigManager"""
    
    def test_required_config_validation(self):
        """Test that missing required config raises error"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                ConfigManager()
            assert "Missing required configuration" in str(exc_info.value)
    
    def test_valid_config_loading(self):
        """Test loading valid configuration"""
        valid_env = {
            'BOT_DISCORD_TOKEN': 'MTAyNzM4OTQyNzUxNjQzMjQ2Ng.GXxKzQ.' + 'a' * 50,
            'BOT_GUILD_ID': '123456789012345678',
            'GLOBAL_CLAUDE_API_KEY': 'sk-ant-' + 'a' * 50,
            'BOT_RESOURCES_CHANNEL_ID': '987654321098765432',
            'BOT_CRISIS_RESPONSE_CHANNEL_ID': '876543210987654321',
            'BOT_CRISIS_RESPONSE_ROLE_ID': '765432109876543210',
            'BOT_STAFF_PING_USER': '654321098765432109'
        }
        
        with patch.dict('os.environ', valid_env, clear=True):
            config = ConfigManager()
            assert config.is_valid()
            assert config.get_int('BOT_GUILD_ID') == 123456789012345678
            assert config.get('GLOBAL_CLAUDE_MODEL') == 'claude-sonnet-4-20250514'
    
    def test_channel_restrictions(self):
        """Test channel restriction functionality"""
        config = Mock(spec=ConfigManager)
        config.get_allowed_channels.return_value = [123, 456, 789]
        
        assert config.is_channel_allowed(123) is True
        assert config.is_channel_allowed(999) is False
        
        # Test no restrictions (empty list)
        config.get_allowed_channels.return_value = []
        assert config.is_channel_allowed(999) is True

@pytest.mark.asyncio
class TestMessageHandler:
    """Test suite for MessageHandler"""
    
    async def test_message_filtering(self, mock_config):
        """Test message filtering logic"""
        # Create mock dependencies
        claude_api = Mock(spec=ClaudeAPI)
        nlp_client = Mock()
        keyword_detector = Mock(spec=KeywordDetector)
        crisis_handler = Mock()
        
        handler = MessageHandler(
            bot=Mock(),
            claude_api=claude_api,
            nlp_client=nlp_client,
            keyword_detector=keyword_detector,
            crisis_handler=crisis_handler,
            config=mock_config
        )
        
        # Test bot message filtering
        bot_message = Mock()
        bot_message.author.bot = True
        
        assert handler._should_process_message(bot_message) is False
        
        # Test valid message
        valid_message = Mock()
        valid_message.author.bot = False
        valid_message.guild.id = 987654321
        valid_message.channel.id = 555666777
        
        with patch.object(handler.config, 'get_int', return_value=987654321), \
             patch.object(handler.config, 'is_channel_allowed', return_value=True):
            assert handler._should_process_message(valid_message) is True
    
    async def test_rate_limiting(self, mock_config):
        """Test rate limiting functionality"""
        handler = MessageHandler(
            bot=Mock(),
            claude_api=Mock(),
            nlp_client=Mock(),
            keyword_detector=Mock(),
            crisis_handler=Mock(),
            config=mock_config
        )
        
        user_id = 123456789
        
        # Should pass initially
        assert await handler.check_rate_limits(user_id) is True
        
        # Simulate multiple rapid calls
        for _ in range(15):  # Exceed rate limit
            await handler.record_api_call(user_id)
        
        # Should be rate limited now
        assert await handler.check_rate_limits(user_id) is False

@pytest.mark.asyncio
class TestClaudeAPI:
    """Test suite for ClaudeAPI"""
    
    def test_claude_api_initialization(self):
        """Test Claude API initialization"""
        with patch.dict('os.environ', {'GLOBAL_CLAUDE_API_KEY': 'sk-ant-test123'}):
            api = ClaudeAPI()
            assert api.api_key == 'sk-ant-test123'
            assert api.model == 'claude-sonnet-4-20250514'
    
    async def test_connection_test(self):
        """Test Claude API connection testing"""
        with patch.dict('os.environ', {'GLOBAL_CLAUDE_API_KEY': 'sk-ant-test123'}):
            api = ClaudeAPI()
            
            # Mock successful response
            with patch.object(api, 'get_ash_response', return_value="Test response"):
                result = await api.test_connection()
                assert result is True
            
            # Mock failed response
            with patch.object(api, 'get_ash_response', side_effect=Exception("Connection failed")):
                result = await api.test_connection()
                assert result is False

class TestSecurityManager:
    """Test suite for SecurityManager"""
    
    def test_input_validation(self):
        """Test input validation and sanitization"""
        from utils.security import InputValidator
        
        # Test Discord ID validation
        assert InputValidator.validate_discord_id("123456789012345678") is True
        assert InputValidator.validate_discord_id("invalid") is False
        assert InputValidator.validate_discord_id("0") is False
        
        # Test crisis level validation
        assert InputValidator.validate_crisis_level("high") is True
        assert InputValidator.validate_crisis_level("invalid") is False
        
        # Test message content sanitization
        dangerous_content = "Test message with \x00 control chars"
        sanitized = InputValidator.sanitize_message_content(dangerous_content)
        assert "\x00" not in sanitized

# Performance tests
class TestPerformance:
    """Performance test suite"""
    
    def test_keyword_detection_performance(self, keyword_detector):
        """Test keyword detection performance"""
        import time
        
        test_message = "I feel worthless and hate myself, everything hurts"
        
        start_time = time.time()
        for _ in range(1000):
            result = keyword_detector.check_message(test_message)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 1000
        assert avg_time < 0.01  # Should be under 10ms per detection

# Integration tests
@pytest.mark.integration
class TestIntegration:
    """Integration test suite"""
    
    @pytest.mark.asyncio
    async def test_full_crisis_flow(self, mock_discord_message, mock_config):
        """Test complete crisis detection and response flow"""
        # This would test the full pipeline from message to response
        # Requires more setup but provides end-to-end validation
        pass

# Test configuration
pytest_plugins = ['pytest_asyncio']

def pytest_configure():
    """Configure pytest"""
    logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])