# Ash-Bot Clean Architecture v3.1 Complete Recode Implementation Guide

**Repository**: https://github.com/the-alphabet-cartel/ash-bot  
**Branch**: v3.1  
**Community**: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org  
**FILE VERSION**: v3.1-1a-2-2  
**LAST UPDATED**: 2025-09-05  
**CLEAN ARCHITECTURE**: v3.1 Compliant  

---

## 🎯 **RECODE MISSION**

Complete transformation of Ash-Bot from current codebase to Clean Architecture v3.1, maintaining all existing functionality while implementing proper manager patterns, JSON configuration, and production-ready resilience for life-saving mental health crisis detection in The Alphabet Cartel LGBTQIA+ community.

---

## 🔧 **CONFIGURATION ACCESS STANDARDS**

### **UnifiedConfigManager get_config_section() Method**
**CRITICAL**: All configuration access must use `UnifiedConfigManager`'s `get_config_section()` method. This method:
- Replaces placeholders in JSON files with environment variables
- Validates and converts data types
- Provides fallback defaults
- Handles resilient error recovery

### **Configuration Access Patterns**
```python
# Load entire configuration file
config = self.config_manager.get_config_section('discord_config')

# Load entire section
settings = self.config_manager.get_config_section('discord_config', 'discord_settings', {})

# Load specific setting with default
guild_id = self.config_manager.get_config_section('discord_config', 'discord_settings.guild_id', 0)
command_prefix = self.config_manager.get_config_section('discord_config', 'discord_settings.command_prefix', '!ash ')

# Load nested settings
intent_guilds = self.config_manager.get_config_section('discord_config', 'intents.guilds', True)
status_name = self.config_manager.get_config_section('discord_config', 'status.activity.name', 'default status')
```

### **DO NOT USE**
- ❌ `config_manager.load_config_file()` - deprecated pattern
- ❌ Direct dictionary access like `config.get('section', {})`
- ❌ Direct environment variable access unless specifically needed

---

## 🏗️ **IMPLEMENTATION SEQUENCE**

### **Phase 1a: Foundation Managers (v3.1-1a-X-X)**
Starting file version: `v3.1-1a-1-1`

#### **✅ COMPLETED - Manager 1: discord_client.py (DiscordClientManager)**
- **File Version**: v3.1-1a-1-1
- **Status**: ✅ Complete with integration test
- **Purpose**: Core Discord bot connection and event handling
- **Dependencies**: UnifiedConfigManager (existing), LoggingConfigManager (existing)
- **Key Responsibilities**:
  - Discord bot initialization and connection
  - Guild management and validation
  - Event routing to appropriate managers
  - Health monitoring and reconnection logic
- **Environment Variables Reused** (Rule #7):
  - `BOT_GUILD_ID=895173212424519710` (existing)
  - `BOT_RATE_LIMIT_PER_USER=10` (existing)
- **Configuration**: `config/discord_config.json`
- **Integration Test**: `test_phase_1a_step_1.py` (v3.1-1a-1-3)

#### **✅ COMPLETED - Manager 2: nlp_integration.py (NLPIntegrationManager)**
- **File Version**: v3.1-1a-2-1
- **Status**: ✅ Complete, needs integration test
- **Purpose**: Communication with NLP server at 172.20.0.11:8881
- **Dependencies**: UnifiedConfigManager, LoggingConfigManager
- **Key Responsibilities**:
  - NLP server connection and health monitoring
  - Message analysis requests (`/analyze` endpoint)
  - Feedback submission (`/analyze_false_positive`, `/analyze_false_negative`)
  - Statistics retrieval (`/stats` endpoint)
  - Response processing from sample_response.json format
- **Environment Variables Reused** (Rule #7):
  - `GLOBAL_NLP_API_HOST=172.20.0.11` (Docker network)
  - `GLOBAL_NLP_API_PORT=8881` (existing)
  - `GLOBAL_REQUEST_TIMEOUT=30` (existing)
  - `GLOBAL_LEARNING_SYSTEM_ENABLED=true` (existing)
  - `BOT_MAX_LEARNING_ADJUSTMENTS_PER_DAY=50` (existing)
- **Configuration**: `config/nlp_config.json` (v3.1-1a-2-1)
- **Integration Test**: **NEXT TO CREATE** - `test_phase_1a_step_2.py` (v3.1-1a-2-2)

#### **🔄 NEXT - Manager 3: crisis_analysis.py (CrisisAnalysisManager)**
- **File Version**: v3.1-1a-3-1 (to be created)
- **Purpose**: Crisis level determination and response coordination
- **Dependencies**: UnifiedConfigManager, LoggingConfigManager, NLPIntegrationManager
- **Key Responsibilities**:
  - Process NLP analysis results
  - Determine crisis levels (none, low, medium, high)
  - Coordinate appropriate responses
  - Staff notification triggers
- **Environment Variables** (Rule #7 - Reuse existing):
  - `BOT_CRISIS_OVERRIDE_LEVELS=medium,high` (existing)
  - `BOT_CRISIS_RESPONSE_CHANNEL_ID` (existing)
  - `BOT_CRISIS_RESPONSE_ROLE_ID` (existing)

### **Phase 1b: Response Managers (v3.1-1b-X-X)**

#### **Manager 4: conversation_handler.py (ConversationHandlerManager)**
- **Purpose**: Discord conversation management and Claude integration
- **Dependencies**: UnifiedConfigManager, LoggingConfigManager, DiscordClientManager
- **Environment Variables** (Rule #7 - Reuse existing):
  - `GLOBAL_CLAUDE_API_KEY` (existing)
  - `GLOBAL_CLAUDE_MODEL=claude-sonnet-4-20250514` (existing)
  - `BOT_CONVERSATION_REQUIRES_MENTION=true` (existing)
  - `BOT_CONVERSATION_TRIGGER_PHRASES` (existing)
  - `BOT_CONVERSATION_TIMEOUT=300` (existing)

#### **Manager 5: crisis_response.py (CrisisResponseManager)**
- **Purpose**: Execute crisis responses based on analysis
- **Dependencies**: UnifiedConfigManager, LoggingConfigManager, DiscordClientManager, CrisisAnalysisManager
- **Environment Variables** (Rule #7 - Reuse existing):
  - `BOT_STAFF_PING_USER` (existing)
  - `BOT_RESOURCES_CHANNEL_ID` (existing)
  - `BOT_ENABLE_GAP_NOTIFICATIONS=true` (existing)
  - `BOT_GAP_NOTIFICATION_CHANNEL_ID` (existing)

### **Phase 1c: Learning & Analytics (v3.1-1c-X-X)**

#### **Manager 6: learning_system.py (LearningSystemManager)**
- **Purpose**: Staff feedback collection and NLP server learning
- **Dependencies**: UnifiedConfigManager, LoggingConfigManager, NLPIntegrationManager

#### **Manager 7: api_server.py (APIServerManager)**
- **Purpose**: HTTP API server for monitoring and analytics
- **Dependencies**: UnifiedConfigManager, LoggingConfigManager, DiscordClientManager, CrisisAnalysisManager, LearningSystemManager

---

## 📁 **FILE STRUCTURE ORGANIZATION**

```
ash-bot/
├── managers/
│   ├── discord_client.py          # ✅ DiscordClientManager (v3.1-1a-1-1)
│   ├── nlp_integration.py         # ✅ NLPIntegrationManager (v3.1-1a-2-1)
│   ├── crisis_analysis.py         # 🔄 CrisisAnalysisManager (next)
│   ├── conversation_handler.py    # ConversationHandlerManager
│   ├── crisis_response.py         # CrisisResponseManager
│   ├── learning_system.py         # LearningSystemManager
│   ├── api_server.py              # APIServerManager
│   ├── unified_config.py          # UnifiedConfigManager (existing - do not touch)
│   ├── logging_config.py          # LoggingConfigManager (existing - do not touch)
│   └── helpers/                   # Helper files for managers >1000 lines
├── config/
│   ├── discord_config.json        # ✅ Discord client configuration (v3.1-1a-1-1)
│   ├── nlp_config.json            # ✅ NLP integration settings (v3.1-1a-2-1)
│   ├── crisis_config.json         # 🔄 Crisis analysis thresholds (next)
│   ├── conversation_config.json   # Conversation handler settings
│   ├── response_config.json       # Crisis response templates
│   ├── learning_config.json       # Learning system parameters
│   └── api_config.json            # API server configuration
├── test_phase_1a_step_1.py        # ✅ Discord manager test (v3.1-1a-1-3)
├── test_phase_1a_step_2.py        # 🔄 NLP manager test (next - v3.1-1a-2-2)
├── main.py                        # Application entry point (new)
├── docs/
│   ├── clean_architecture_charter.md (existing - reference only)
│   ├── sample_response.json       (existing - reference only)
│   └── project_instructions.md    (existing - reference only)
├── .env.template                  (existing - reference for Rule #7)
├── Dockerfile                     (existing - maintain)
├── docker-compose.yml             (existing - maintain)
└── requirements.txt               (existing - maintain)
```

---

## 🏗️ **MANAGER CREATION PATTERN**

### **Standard Manager Template**
```python
"""
Ash-Bot: Crisis Detection Bot for The Alphabet Cartel Discord Community
********************************************************************************
{Manager Description} for Ash-Bot
---
FILE VERSION: v3.1-1a-X-X
LAST MODIFIED: 2025-09-05
PHASE: 1a Step X
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import logging
from typing import Dict, Any, Optional
from managers.unified_config import UnifiedConfigManager
from managers.logging_config import LoggingConfigManager

logger = logging.getLogger(__name__)

class {ManagerName}Manager:
    """
    {Manager Description}
    
    Responsibilities:
    - {Responsibility 1}
    - {Responsibility 2}
    - {Responsibility 3}
    """
    
    def __init__(self, config_manager: UnifiedConfigManager, logging_manager: LoggingConfigManager, **kwargs):
        """
        Initialize {ManagerName}Manager
        
        Args:
            config_manager: UnifiedConfigManager instance (ALWAYS FIRST PARAMETER)
            logging_manager: LoggingConfigManager instance
            **kwargs: Additional manager dependencies
        """
        self.config_manager = config_manager
        self.logging_manager = logging_manager
        
        # Load configuration using proper get_config_section method
        self.config = self.config_manager.get_config_section('{config_file_name}')
        
        # Access specific settings using get_config_section
        self.setting_value = self.config_manager.get_config_section(
            '{config_file_name}', 
            'section.subsection.setting', 
            'default_value'
        )
        
        # Initialize manager state
        self._initialize_manager()
        
        logger.info(f"✅ {ManagerName}Manager initialized successfully")
    
    def _initialize_manager(self):
        """Initialize manager-specific state"""
        # Implementation specific to manager
        pass

def create_{manager_name}_manager(config_manager: UnifiedConfigManager, **kwargs) -> {ManagerName}Manager:
    """
    Factory function for {ManagerName}Manager (MANDATORY per Rule #1)
    
    Args:
        config_manager: UnifiedConfigManager instance
        **kwargs: Additional dependencies
        
    Returns:
        Initialized {ManagerName}Manager instance
    """
    try:
        # Get or create logging manager
        logging_manager = kwargs.get('logging_manager')
        if not logging_manager:
            from managers.logging_config import create_logging_config_manager
            logging_manager = create_logging_config_manager(config_manager)
        
        return {ManagerName}Manager(
            config_manager=config_manager,
            logging_manager=logging_manager,
            **kwargs
        )
    except Exception as e:
        logger.error(f"❌ Failed to create {ManagerName}Manager: {e}")
        # Implement resilient fallback per Rule #5
        raise
```

---

## 🔄 **CROSS-CONVERSATION CONTINUITY**

### **File Version Tracking**
- **Current Phase**: 1a  
- **Current Step**: 2 (nlp_integration.py - COMPLETED, needs integration test)
- **Completed Steps**: 
  - Step 1: v3.1-1a-1-1 (DiscordClientManager) ✅
  - Step 2: v3.1-1a-2-1 (NLPIntegrationManager) ✅ 
- **Next Step**: Create test_phase_1a_step_2.py (v3.1-1a-2-2)
- **Next Phase**: Step 3 - crisis_analysis.py (v3.1-1a-3-1)
- **Phase Completion**: Move to v3.1-1b-1-1 when Phase 1a complete

### **Phase Completion Checklist**
- [x] **Phase 1a Step 1 Complete**: discord_client.py + discord_config.json ✅
  - [x] DiscordClientManager created with Clean Architecture v3.1
  - [x] Factory function pattern implemented
  - [x] JSON configuration with environment variable mapping
  - [x] **UPDATED**: Proper get_config_section() method usage implemented
  - [x] Rule #7 compliance: Reused existing BOT_GUILD_ID and BOT_RATE_LIMIT_PER_USER
  - [x] Resilient error handling and fallback mechanisms
  - [x] Integration test updated to validate get_config_section functionality
  - [x] File versioning: v3.1-1a-1-1 (manager) and v3.1-1a-1-3 (updated test)
- [x] **Phase 1a Step 2 Complete**: nlp_integration.py + nlp_config.json ✅
  - [x] NLPIntegrationManager created with Clean Architecture v3.1
  - [x] Factory function pattern implemented  
  - [x] JSON configuration with get_config_section() method usage
  - [x] Rule #7 compliance: Reused GLOBAL_NLP_API_HOST, GLOBAL_NLP_API_PORT, GLOBAL_REQUEST_TIMEOUT, GLOBAL_LEARNING_SYSTEM_ENABLED, BOT_MAX_LEARNING_ADJUSTMENTS_PER_DAY
  - [x] Maintains existing NLP endpoints: /analyze, /analyze_false_positive, /analyze_false_negative, /stats
  - [x] Processes sample_response.json format correctly
  - [x] Docker network configuration: 172.20.0.11:8881
  - [x] Resilient error handling and connection retry logic
  - [x] File versioning: v3.1-1a-2-1 (manager and config)
  - [ ] **NEXT**: Create integration test (v3.1-1a-2-2)
- [ ] **Phase 1a Step 3**: crisis_analysis.py + crisis_config.json
- [ ] **Phase 1b Complete**: All response managers created and tested
  - [ ] conversation_handler.py + conversation_config.json
  - [ ] crisis_response.py + response_config.json
- [ ] **Phase 1c Complete**: All learning & analytics managers created and tested
  - [ ] learning_system.py + learning_config.json
  - [ ] api_server.py + api_config.json
- [ ] **Integration Testing**: All managers working together
- [ ] **main.py**: Application entry point with proper factory function usage

### **Integration Test Scripts**
- [x] `test_phase_1a_step_1.py` - ✅ Discord manager integration test (v3.1-1a-1-3)
- [ ] `test_phase_1a_step_2.py` - 🔄 **NEXT TO CREATE** - NLP manager integration test (v3.1-1a-2-2)
- [ ] `test_phase_1a_step_3.py` - Crisis analysis integration test
- [ ] `test_phase_1a.py` - Foundation managers integration test  
- [ ] `test_phase_1b.py` - Response managers integration test  
- [ ] `test_phase_1c.py` - Learning & analytics integration test
- [ ] `test_complete_system.py` - Full system integration test

---

## 🚨 **CRITICAL REMINDERS**

### **Clean Architecture Charter Compliance**
- ✅ **Rule #1**: ALL managers use factory functions
- ✅ **Rule #2**: UnifiedConfigManager always first parameter
- ✅ **Rule #3**: Phase-additive development (never remove functionality)
- ✅ **Rule #4**: JSON configuration + environment overrides
- ✅ **Rule #5**: Resilient validation with smart fallbacks
- ✅ **Rule #6**: File versioning in every code file
- ✅ **Rule #7**: ALWAYS check .env.template before creating new variables
- ✅ **Rule #8**: Real-world testing with actual methods

### **Environment Variable Reuse Strategy (Rule #7)**
1. **Before creating any new environment variable**:
   - Search .env.template for existing similar functionality
   - Calculate conversions/mappings to reuse existing variables
   - Document the mapping relationship clearly
   - Only create new variables if absolutely no existing option works

### **Existing Infrastructure to Preserve**
- Docker network: `172.20.0.11:8881` for NLP server
- API endpoints: `/analyze`, `/analyze_false_positive`, `/analyze_false_negative`, `/stats`
- Response format: As defined in docs/sample_response.json
- Docker secrets: `/run/secrets/` pattern for sensitive data
- Health checks: Existing Docker health check configuration

---

## 🎯 **NEXT STEPS FOR CONTINUATION**

1. **Create Integration Test**: `test_phase_1a_step_2.py` (v3.1-1a-2-2)
   - Test NLPIntegrationManager factory function
   - Test NLP server connection and health checks
   - Test message analysis with sample_response.json format
   - Test staff feedback submission
   - Test environment variable mapping (Rule #7)

2. **Start Phase 1a Step 3**: `crisis_analysis.py` (v3.1-1a-3-1)
   - CrisisAnalysisManager with crisis level determination
   - Integration with NLPIntegrationManager
   - Crisis response coordination logic

3. **Continue Phase 1a**: Complete all foundation managers

4. **Integration Testing**: Ensure all managers work together

**🚀 Ready for seamless cross-conversation continuation!**