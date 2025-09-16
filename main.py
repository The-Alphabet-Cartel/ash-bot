#!/usr/bin/env python3
"""
Ash-Bot: Crisis Detection Discord Bot for The Alphabet Cartel Discord Community
********************************************************************************
Ash-Bot Main Application Entry Point - Complete System Orchestration
---
FILE VERSION: v3.1-final-1-1
LAST MODIFIED: 2025-09-16
PHASE: Final Integration
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import asyncio
import logging
import os
import sys
import signal
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# ============================================================================
# ALL MANAGER IMPORTS - USING FACTORY FUNCTIONS (Clean Architecture v3.1)
# ============================================================================
from managers.unified_config import create_unified_config_manager
from managers.logging_config import create_logging_config_manager
from managers.discord_client import create_discord_client_manager
from managers.nlp_integration import create_nlp_integration_manager
from managers.crisis_analysis import create_crisis_analysis_manager
from managers.conversation_handler import create_conversation_handler_manager
from managers.crisis_response import create_crisis_response_manager
from managers.learning_system import create_learning_system_manager
from managers.api_server import create_api_server_manager

# ============================================================================
# ASH-BOT APPLICATION CLASS
# ============================================================================
class AshBotApplication:
    """
    Main Ash-Bot Application Class
    
    Orchestrates all 7 managers in Clean Architecture v3.1 pattern:
    - Foundation Managers (Phase 1a): Discord, NLP, Crisis Analysis
    - Response Managers (Phase 1b): Conversation Handler, Crisis Response  
    - Learning & Analytics (Phase 1c): Learning System, API Server
    
    Provides production-ready startup, shutdown, and error handling
    for life-saving mental health crisis detection.
    """
    
    # ============================================================================
    # INITIALIZE
    # ============================================================================
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Foundation managers (existing)
        self.config_manager = None
        self.logging_manager = None
        
        # Phase 1a: Foundation managers
        self.discord_client_manager = None
        self.nlp_integration_manager = None
        self.crisis_analysis_manager = None
        
        # Phase 1b: Response managers
        self.conversation_handler_manager = None
        self.crisis_response_manager = None
        
        # Phase 1c: Learning & analytics managers  
        self.learning_system_manager = None
        self.api_server_manager = None
        
        # Application state
        self.is_running = False
        self.shutdown_event = asyncio.Event()
    # ============================================================================
        
    # ============================================================================
    # INITIALIZE MANAGERS
    # ============================================================================
    async def initialize_managers(self, unified_config) -> bool:
        """
        Initialize foundation managers (UnifiedConfigManager, LoggingConfigManager)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # ============================================================================
            # FOUNDATION MANAGERS
            # ============================================================================
            self.logger.info("🔧 Initializing foundation managers...")
            
            # Initialize UnifiedConfigManager (existing foundation)
            self.config_manager = unified_config
            self.logger.debug("✅ UnifiedConfig initialized")
            
            # Initialize LoggingConfigManager (existing foundation)
            self.logging_manager = create_logging_config_manager(self.config_manager)
            self.logger.debug("✅ LoggingConfig initialized")
            
            # Initialize Discord Client Manager
            self.discord_client_manager = create_discord_client_manager(
                config_manager=self.config_manager,
                logging_manager=self.logging_manager
            )
            self.logger.debug("✅ DiscordClient initialized")
            
            # Initialize NLP Integration Manager
            self.nlp_integration_manager = create_nlp_integration_manager(
                config_manager=self.config_manager,
                logging_manager=self.logging_manager
            )
            self.logger.debug("✅ NLPIntegration initialized")
            
            # Initialize Crisis Analysis Manager
            self.crisis_analysis_manager = create_crisis_analysis_manager(
                config_manager=self.config_manager,
                logging_manager=self.logging_manager,
                nlp_integration_manager=self.nlp_integration_manager
            )
            self.logger.debug("✅ CrisisAnalysis initialized")
            
            self.logger.info("✅ Foundation managers initialized successfully")
            # ============================================================================

            # ============================================================================
            # RESPONSE MANAGERS
            # ============================================================================
            self.logger.info("🔧 Initializing response managers...")
            
            # Initialize Conversation Handler Manager
            self.conversation_handler_manager = create_conversation_handler_manager(
                config_manager=self.config_manager,
                logging_manager=self.logging_manager,
                crisis_analysis_manager=self.crisis_analysis_manager
            )
            self.logger.debug("✅ ConversationHandler initialized")
            
            # Initialize Crisis Response Manager
            self.crisis_response_manager = create_crisis_response_manager(
                config_manager=self.config_manager,
                logging_manager=self.logging_manager
            )
            self.logger.debug("✅ CrisisResponse initialized")
            
            self.logger.info("✅ Response managers initialized successfully")
            # ============================================================================

            # ============================================================================
            # LEARNING AND ANALYTICS MANAGERS
            # ============================================================================
            self.logger.info("🔧 Initializing learning & analytics managers...")
            
            # Initialize Learning System Manager
            self.learning_system_manager = create_learning_system_manager(
                config_manager=self.config_manager,
                logging_manager=self.logging_manager,
                nlp_integration_manager=self.nlp_integration_manager
            )
            self.logger.debug("✅ LearningSystem initialized")
            
            # Initialize API Server Manager
            self.api_server_manager = create_api_server_manager(
                config_manager=self.config_manager,
                logging_manager=self.logging_manager,
                discord_client_manager=self.discord_client_manager,
                nlp_integration_manager=self.nlp_integration_manager,
                crisis_analysis_manager=self.crisis_analysis_manager,
                conversation_handler_manager=self.conversation_handler_manager,
                crisis_response_manager=self.crisis_response_manager,
                learning_system_manager=self.learning_system_manager
            )
            self.logger.debug("✅ APIServer initialized")
            
            self.logger.info("✅ learning & analytics managers initialized successfully")
            # ============================================================================
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize managers: {e}")
            return False
    # ============================================================================
    
    # ============================================================================
    # START / STOP SERVICES
    # ============================================================================
    async def start_services(self) -> bool:
        """
        Start all application services
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info("🚀 Starting application services...")
            
            # Start API Server (provides monitoring while other services start)
            if self.api_server_manager:
                await self.api_server_manager.start_server()
                self.logger.info("✅ API Server started")
            
            # Start Discord Client (main service)
            if self.discord_client_manager:
                await self.discord_client_manager.connect_to_discord()
                self.logger.info("✅ Discord Client connected")
            
            self.logger.info("✅ All services started successfully")
            self.is_running = True
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start services: {e}")
            return False
    
    async def stop_services(self) -> None:
        """
        Gracefully stop all application services
        """
        try:
            self.logger.info("🛑 Stopping application services...")
            self.is_running = False
            
            # Stop Discord Client first (main service)
            if self.discord_client_manager:
                await self.discord_client_manager.disconnect_from_discord()
                self.logger.info("✅ Discord Client disconnected")
            
            # Stop API Server last (monitoring until the end)
            if self.api_server_manager:
                await self.api_server_manager.stop_server()
                self.logger.info("✅ API Server stopped")
            
            self.logger.info("✅ All services stopped gracefully")
            
        except Exception as e:
            self.logger.error(f"❌ Error during service shutdown: {e}")
    # ============================================================================

    # ============================================================================
    # HEALTHCHECK
    # ============================================================================
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform application health check
        
        Returns:
            Dict containing health status of all managers
        """
        try:
            health_status = {
                'application': {
                    'status': 'healthy' if self.is_running else 'stopped',
                    'managers_initialized': 0
                },
                'managers': {}
            }
            
            # Count initialized managers
            managers = [
                ('config_manager', self.config_manager),
                ('logging_manager', self.logging_manager),
                ('discord_client_manager', self.discord_client_manager),
                ('nlp_integration_manager', self.nlp_integration_manager),
                ('crisis_analysis_manager', self.crisis_analysis_manager),
                ('conversation_handler_manager', self.conversation_handler_manager),
                ('crisis_response_manager', self.crisis_response_manager),
                ('learning_system_manager', self.learning_system_manager),
                ('api_server_manager', self.api_server_manager)
            ]
            
            for name, manager in managers:
                if manager:
                    health_status['managers'][name] = 'initialized'
                    health_status['application']['managers_initialized'] += 1
                else:
                    health_status['managers'][name] = 'not_initialized'
            
            # Get detailed health from API server if available
            if self.api_server_manager:
                try:
                    detailed_health = await self.api_server_manager._get_system_health_summary()
                    if detailed_health:
                        health_status['detailed'] = detailed_health
                except Exception as e:
                    self.logger.warning(f"Could not get detailed health: {e}")
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {'application': {'status': 'unhealthy', 'error': str(e)}}
    # ============================================================================
    
    # ============================================================================
    # MAIN LOOP
    # ============================================================================
    async def run(self) -> int:
        """
        Main application run loop
        
        Returns:
            int: Exit code (0 for success, 1 for error)
        """
        try:
            self.logger.info("🎯 Starting Ash-Bot Application...")
            self.logger.info("🏳️‍🌈 Serving The Alphabet Cartel community")
            self.logger.info("❤️  Providing life-saving mental health crisis detection")
            
            # Initialize all managers in phases
            if not await self.initialize_managers(unified_config):
                return 1
            
            self.logger.info("✅ All managers initialized successfully")
            self.logger.info("📊 Managers ready: 7/7 (100% complete)")
            
            # Start all services
            if not await self.start_services():
                return 1
            
            self.logger.info("🚀 Ash-Bot Application running successfully!")
            self.logger.info("💖 Crisis detection system operational")
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
            return 0
            
        except KeyboardInterrupt:
            self.logger.info("🛑 Received shutdown signal (Ctrl+C)")
            return 0
            
        except Exception as e:
            self.logger.error(f"❌ Application error: {e}")
            return 1
        
        finally:
            await self.stop_services()
            self.logger.info("👋 Ash-Bot Application shutdown complete")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"🛑 Received signal {signum}")
        self.shutdown_event.set()
    # ============================================================================

# ============================================================================
# SETUP LOGGING
# ============================================================================
def setup_logging(unified_config):
    """
    Setup colorlog logging with unified configuration management
    """
    try:
        # Get logging configuration through unified config
        log_level = unified_config.get_config_section('logging_settings', 'global_settings.log_level', 'INFO')
        log_detailed = unified_config.get_config_section('logging_settings', 'detailed_logging.enable_detailed', True)
        enable_file_logging = unified_config.get_config_section('logging_settings', 'global_settings.enable_file_output', False)
        log_dir = unified_config.get_config_section('logging_settings', 'global_settings.log_directory', './logs')
        log_file = unified_config.get_config_section('logging_settings', 'global_settings.log_file', 'ash_bot.log')
        
        # Configure colorlog formatter
        if log_detailed == False:
            log_format_string = '%(log_color)s%(levelname)s%(reset)s: %(message)s'
        else:  # detailed
            log_format_string = '%(log_color)s%(asctime)s - %(name)s - %(levelname)s%(reset)s: %(message)s'
        
        # Create colorlog formatter
        formatter = colorlog.ColoredFormatter(
            log_format_string,
            datefmt='%Y-%m-%d %H:%M:%S',
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler
        console_handler = colorlog.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # Optional file handler
        if enable_file_logging:
            try:
                file_handler = logging.FileHandler(f'{log_dir}/{log_file}')
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(file_formatter)
                root_logger.addHandler(file_handler)
                logging.info(f"📁 File logging enabled: {log_dir}/{log_file}")
            except Exception as e:
                logging.warning(f"⚠️ Could not setup file logging: {e}")
        
        logging.info("🎨 Unified colorlog logging configured successfully")
        logging.info(f"📊 Log level: {log_level}")
        
    except Exception as e:
        # Fallback to basic logging
        logging.basicConfig(level=logging.INFO)
        logging.error(f"❌ Failed to setup unified logging: {e}")
        logging.info("🔄 Using fallback basic logging configuration")
# ============================================================================

# ============================================================================
# PRODUCTION ENVIRONMENT SETUP
# ============================================================================
def setup_environment():
    """Setup production environment and load configuration"""
    try:
#        # Load environment variables from .env file
#        env_file = Path(".env")
#        if env_file.exists():
#            load_dotenv(env_file)
#            print(f"✅ Loaded environment from {env_file}")
#        else:
#            print("⚠️  No .env file found, using system environment")
#        
#        # Setup basic logging before managers are initialized
#        logging.basicConfig(
#            level=logging.INFO,
#            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#        )
        unified_config = create_unified_config_manager()
        setup_logging(unified_config)
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to setup environment: {e}")
        return False
# ============================================================================

# ============================================================================
# MAIN APPLICATION ENTRY POINT
# ============================================================================
async def main():
    """
    Main async entry point for Ash-Bot application
    
    Handles complete system orchestration using Clean Architecture v3.1
    """
    # Setup environment
    if not setup_environment():
        return 1
    
    # Create and run application
    app = AshBotApplication()
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, app.signal_handler)
    signal.signal(signal.SIGTERM, app.signal_handler)
    
    # Run the application
    exit_code = await app.run()
    return exit_code

def sync_main():
    """Synchronous main function for compatibility"""
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal application error: {e}")
        sys.exit(1)
# ============================================================================

# ============================================================================
# MODULE EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("=" * 80)
    print("🤖 Ash-Bot: Crisis Detection Bot for The Alphabet Cartel")
    print("❤️  Mental Health Crisis Detection & Response System")
    print("🏳️‍🌈 Serving LGBTQIA+ Community Members")
    print("🔧 Clean Architecture v3.1")
    print("=" * 80)
    print("")
    
    sync_main()
# ============================================================================