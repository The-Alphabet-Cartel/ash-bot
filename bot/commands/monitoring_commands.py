"""
Enhanced Monitoring Commands - FIXED datetime issue
Copy this to: ash/bot/commands/monitoring_commands.py
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class MonitoringCommands(commands.Cog):
    """Enhanced monitoring commands for the modular bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.crisis_response_role_id = int(os.getenv('BOT_CRISIS_RESPONSE_ROLE_ID', '0'))
        
        logger.info("📊 Enhanced monitoring commands loaded")
    
    async def _check_crisis_role(self, interaction: discord.Interaction) -> bool:
        """Check if user has crisis response role"""
        try:
            user_role_ids = [role.id for role in interaction.user.roles]
            
            if self.crisis_response_role_id not in user_role_ids:
                await interaction.response.send_message(
                    "❌ You need the Crisis Response role to use monitoring commands", 
                    ephemeral=True
                )
                return False
            return True
            
        except (ValueError, TypeError):
            await interaction.response.send_message(
                "❌ Crisis Response role not properly configured", 
                ephemeral=True
            )
            return False
    
    @app_commands.command(name="system_status", description="View comprehensive system status")
    async def system_status(self, interaction: discord.Interaction):
        """Get comprehensive system status"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        try:
            embed = discord.Embed(
                title="🖥️ Ash Bot v2.0 - Enhanced System Status",
                description="Comprehensive modular architecture status",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)  # FIXED: Use timezone-aware datetime
            )
            
            # Bot basic info - FIXED: Calculate uptime properly
            bot_created = self.bot.user.created_at
            current_time = datetime.now(timezone.utc)
            
            # Calculate actual bot uptime since startup (not since account creation)
            # Use a simple approach - just show current status
            embed.add_field(
                name="🤖 Bot Information",
                value=f"**Status:** ✅ Online\n"
                     f"**Architecture:** v2.0 Modular\n"
                     f"**User:** {self.bot.user}\n"
                     f"**Guild:** {interaction.guild.name}",
                inline=True
            )
            
            # Component status
            components_status = []
            if hasattr(self.bot, 'claude_api') and self.bot.claude_api:
                components_status.append("✅ Claude API")
            else:
                components_status.append("❌ Claude API")
                
            if hasattr(self.bot, 'nlp_client') and self.bot.nlp_client:
                components_status.append("✅ NLP Service")
            else:
                components_status.append("❌ NLP Service")
                
            if hasattr(self.bot, 'keyword_detector') and self.bot.keyword_detector:
                components_status.append("✅ Keyword Detector")
            else:
                components_status.append("❌ Keyword Detector")
                
            if hasattr(self.bot, 'crisis_handler') and self.bot.crisis_handler:
                components_status.append("✅ Crisis Handler")
            else:
                components_status.append("❌ Crisis Handler")
                
            if hasattr(self.bot, 'message_handler') and self.bot.message_handler:
                components_status.append("✅ Message Handler")
            else:
                components_status.append("❌ Message Handler")
            
            embed.add_field(
                name="🔧 Component Status",
                value="\n".join(components_status),
                inline=True
            )
            
            # Command status
            commands_count = len([cmd for cmd in self.bot.tree.walk_commands()])
            embed.add_field(
                name="⚡ Commands",
                value=f"**Slash Commands:** {commands_count}\n"
                     f"**Status:** ✅ Active\n"
                     f"**Sync Status:** Global",
                inline=True
            )
            
            # Get message handler stats if available
            if hasattr(self.bot, 'message_handler') and self.bot.message_handler:
                try:
                    stats = self.bot.message_handler.get_message_handler_stats()
                    embed.add_field(
                        name="📨 Message Processing",
                        value=f"**Processed Today:** {stats['message_processing']['total_messages_processed']}\n"
                             f"**Crisis Responses:** {stats['message_processing']['crisis_responses_given']}\n"
                             f"**Active Conversations:** {stats['conversation_tracking']['active_conversations']}\n"
                             f"**Rate Limit Success:** {stats['rate_limiting']['success_rate_percent']}%",
                        inline=True
                    )
                except Exception as e:
                    embed.add_field(
                        name="📨 Message Processing",
                        value="Statistics unavailable",
                        inline=True
                    )
            
            # Get crisis handler stats if available
            if hasattr(self.bot, 'crisis_handler') and self.bot.crisis_handler:
                try:
                    crisis_stats = self.bot.crisis_handler.get_crisis_stats()
                    embed.add_field(
                        name="🚨 Crisis Management",
                        value=f"**High Crises:** {crisis_stats['high_crisis_count']}\n"
                             f"**Medium Crises:** {crisis_stats['medium_crisis_count']}\n"
                             f"**Low Crises:** {crisis_stats['low_crisis_count']}\n"
                             f"**Success Rate:** {crisis_stats['success_rate']}%",
                        inline=True
                    )
                except Exception as e:
                    embed.add_field(
                        name="🚨 Crisis Management",
                        value="Statistics unavailable",
                        inline=True
                    )
            
            # Configuration status
            config_status = []
            if self.bot.config.get('BOT_DISCORD_TOKEN'):
                config_status.append("✅ Discord Token")
            if self.bot.config.get('GLOBAL_CLAUDE_API_KEY'):
                config_status.append("✅ Claude API Key")
            if self.bot.config.get_int('BOT_GUILD_ID'):
                config_status.append("✅ Guild Configuration")
            if self.bot.config.get_int('BOT_CRISIS_RESPONSE_CHANNEL_ID'):
                config_status.append("✅ Crisis Channel")
            
            embed.add_field(
                name="⚙️ Configuration",
                value="\n".join(config_status) if config_status else "❌ No configuration",
                inline=False
            )
            
            embed.set_footer(text="Enhanced Monitoring System | Ash v2.0 Modular")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in system_status command: {e}")
            logger.exception("Full traceback:")  # Added full traceback for debugging
            await interaction.response.send_message(
                f"❌ Error retrieving system status: {str(e)}", 
                ephemeral=True
            )
    
    @app_commands.command(name="conversation_stats", description="View conversation isolation statistics")
    async def conversation_stats(self, interaction: discord.Interaction):
        """View statistics about conversation isolation and mention requirements"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        try:
            if not hasattr(self.bot, 'message_handler') or not self.bot.message_handler:
                await interaction.response.send_message(
                    "❌ Message handler not available", 
                    ephemeral=True
                )
                return
            
            handler = self.bot.message_handler
            stats = handler.message_stats
            
            embed = discord.Embed(
                title="💬 Conversation Isolation Statistics",
                description="Statistics for the mention/ping requirement system",
                color=discord.Color.blue()
            )
            
            # Basic conversation stats
            embed.add_field(
                name="📊 Conversation Activity",
                value=f"**Started:** {stats.get('conversations_started', 0)}\n"
                     f"**Follow-ups handled:** {stats.get('follow_ups_handled', 0)}\n"
                     f"**Currently active:** {len(handler.active_conversations)}\n"
                     f"**Ignored attempts:** {stats.get('ignored_follow_ups', 0)}\n"
                     f"**🚫 Intrusions blocked:** {stats.get('intrusion_attempts_blocked', 0)}\n"
                     f"**🚨 Crisis overrides:** {stats.get('crisis_overrides_triggered', 0)}",
                inline=True
            )
            
            # Configuration status
            config_status = []
            if handler.config.get_bool('BOT_CONVERSATION_REQUIRES_MENTION', True):
                config_status.append("✅ Mention requirement: Enabled")
            else:
                config_status.append("❌ Mention requirement: Disabled")
                
            if handler.config.get_bool('BOT_CONVERSATION_SETUP_INSTRUCTIONS', True):
                config_status.append("✅ Setup instructions: Enabled")
            else:
                config_status.append("❌ Setup instructions: Disabled")
                
            if handler.config.get_bool('BOT_CONVERSATION_ALLOW_STARTERS', True):
                config_status.append("✅ Natural starters: Enabled")
            else:
                config_status.append("❌ Natural starters: Disabled")
                
            # Crisis override levels
            override_levels = handler.config.get('BOT_CRISIS_OVERRIDE_LEVELS', 'medium,high')
            config_status.append(f"🚨 Crisis overrides: {override_levels}")
            
            embed.add_field(
                name="⚙️ Configuration",
                value="\n".join(config_status),
                inline=True
            )
            
            # Trigger phrases
            triggers = handler.config.get('BOT_CONVERSATION_TRIGGER_PHRASES', 'ash,hey ash')
            trigger_list = [f"`{trigger.strip()}`" for trigger in triggers.split(',')[:5]]  # Show first 5
            
            embed.add_field(
                name="🔤 Trigger Phrases",
                value=" • " + "\n • ".join(trigger_list) + 
                     (f"\n • ...and {len(triggers.split(',')) - 5} more" if len(triggers.split(',')) > 5 else ""),
                inline=False
            )
            
            # Active conversations details
            if handler.active_conversations:
                active_details = []
                for user_id, conv_data in list(handler.active_conversations.items())[:5]:  # Show first 5
                    try:
                        user = await self.bot.fetch_user(user_id)
                        duration = time.time() - conv_data['start_time']
                        time_left = max(0, handler.conversation_timeout - duration)
                        
                        active_details.append(
                            f"**{user.display_name}** ({conv_data['crisis_level']}) - {time_left:.0f}s left"
                        )
                    except:
                        active_details.append(f"**User {user_id}** ({conv_data['crisis_level']})")
                
                embed.add_field(
                    name="👥 Active Conversations",
                    value="\n".join(active_details) + 
                         (f"\n...and {len(handler.active_conversations) - 5} more" if len(handler.active_conversations) > 5 else ""),
                    inline=False
                )
            
            # Effectiveness metrics
            total_attempts = stats.get('follow_ups_handled', 0) + stats.get('ignored_follow_ups', 0)
            intrusion_attempts = stats.get('intrusion_attempts_blocked', 0)
            
            if total_attempts > 0:
                success_rate = (stats.get('follow_ups_handled', 0) / total_attempts) * 100
                embed.add_field(
                    name="📈 Effectiveness",
                    value=f"**Follow-up success rate:** {success_rate:.1f}%\n"
                         f"**Isolation working:** {'✅ Yes' if stats.get('ignored_follow_ups', 0) > 0 else '⚠️ Untested'}\n"
                         f"**Intrusions blocked:** {'🛡️ ' + str(intrusion_attempts) if intrusion_attempts > 0 else '✅ None'}",
                    inline=True
                )
            
            embed.set_footer(text="Conversation Isolation System | Ash v2.0")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in conversation_stats command: {e}")
            await interaction.response.send_message(
                f"❌ Error retrieving conversation statistics: {str(e)}", 
                ephemeral=True
            )

    @app_commands.command(name="test_mention", description="Test the mention requirement system")
    async def test_mention(self, interaction: discord.Interaction, 
                          test_message: str = "ash help me"):
        """Test whether a message would trigger the mention system"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        try:
            if not hasattr(self.bot, 'message_handler') or not self.bot.message_handler:
                await interaction.response.send_message(
                    "❌ Message handler not available", 
                    ephemeral=True
                )
                return
            
            handler = self.bot.message_handler
            
            # Create a mock message object for testing
            class MockMessage:
                def __init__(self, content, author_id):
                    self.content = content
                    self.author = type('author', (), {'id': author_id})()
                    self.mentions = []  # Would contain bot mentions in real message
            
            mock_msg = MockMessage(test_message, interaction.user.id)
            
            # Test the trigger detection
            would_respond = handler._should_respond_in_conversation(mock_msg, interaction.user.id)
            
            embed = discord.Embed(
                title="🧪 Mention System Test",
                description=f"Testing message: `{test_message}`",
                color=discord.Color.green() if would_respond else discord.Color.red()
            )
            
            embed.add_field(
                name="🤖 Would Ash Respond?",
                value="✅ Yes" if would_respond else "❌ No",
                inline=True
            )
            
            # Check what triggered (or didn't trigger)
            triggers = handler.config.get('BOT_CONVERSATION_TRIGGER_PHRASES', 'ash,hey ash').split(',')
            message_lower = test_message.lower()
            
            matched_triggers = [trigger.strip() for trigger in triggers if trigger.strip().lower() in message_lower]
            
            if matched_triggers:
                embed.add_field(
                    name="🔤 Matched Triggers",
                    value=" • " + "\n • ".join([f"`{trigger}`" for trigger in matched_triggers]),
                    inline=True
                )
            
            # Check conversation starters
            if handler.config.get_bool('BOT_CONVERSATION_ALLOW_STARTERS', True):
                starters = ["i'm still", "i still", "but i", "what if", "can you", "help me", "i need"]
                matched_starters = [starter for starter in starters if message_lower.startswith(starter)]
                
                if matched_starters:
                    embed.add_field(
                        name="🗣️ Matched Starters",
                        value=" • " + "\n • ".join([f"`{starter}`" for starter in matched_starters]),
                        inline=True
                    )
            
            embed.add_field(
                name="💡 Tips",
                value="• Use `@Ash` or mention the bot directly\n"
                     "• Say 'ash', 'hey ash', or 'ash help'\n"
                     "• Start with natural phrases like 'I need' or 'Can you'",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in test_mention command: {e}")
            await interaction.response.send_message(
                f"❌ Error testing mention system: {str(e)}", 
                ephemeral=True
            )

    @app_commands.command(name="active_conversations", description="View active crisis conversations")
    async def active_conversations(self, interaction: discord.Interaction):
        """View all active crisis conversations"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        try:
            if not hasattr(self.bot, 'message_handler') or not self.bot.message_handler:
                await interaction.response.send_message(
                    "❌ Message handler not available", 
                    ephemeral=True
                )
                return
            
            active_convs = self.bot.message_handler.active_conversations
            
            if not active_convs:
                embed = discord.Embed(
                    title="💬 Active Conversations",
                    description="No active crisis conversations at this time",
                    color=discord.Color.green()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            embed = discord.Embed(
                title="💬 Active Crisis Conversations",
                description=f"Currently tracking {len(active_convs)} active conversations",
                color=discord.Color.orange()
            )
            
            for user_id, conv_data in list(active_convs.items())[:10]:  # Show max 10
                try:
                    user = await self.bot.fetch_user(user_id)
                    channel = self.bot.get_channel(conv_data['channel_id'])
                    
                    import time
                    current_time = time.time()
                    duration = current_time - conv_data['start_time']
                    time_remaining = max(0, 300 - duration)  # 5 minutes timeout
                    
                    embed.add_field(
                        name=f"👤 {user.display_name}",
                        value=f"**Crisis Level:** {conv_data['crisis_level'].title()}\n"
                             f"**Channel:** {channel.mention if channel else 'Unknown'}\n"
                             f"**Duration:** {duration:.0f}s\n"
                             f"**Time Left:** {time_remaining:.0f}s\n"
                             f"**Follow-ups:** {conv_data.get('follow_up_count', 0)}\n"
                             f"**Escalations:** {conv_data.get('escalations', 0)}",
                        inline=True
                    )
                except Exception as e:
                    embed.add_field(
                        name=f"👤 User {user_id}",
                        value=f"**Crisis Level:** {conv_data['crisis_level'].title()}\n"
                             f"**Error loading details:** {str(e)[:50]}",
                        inline=True
                    )
            
            if len(active_convs) > 10:
                embed.add_field(
                    name="Additional Conversations",
                    value=f"...and {len(active_convs) - 10} more active conversations",
                    inline=False
                )
            
            embed.set_footer(text="Conversations expire after 5 minutes of inactivity")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in active_conversations command: {e}")
            logger.exception("Full traceback:")
            await interaction.response.send_message(
                f"❌ Error retrieving conversations: {str(e)}", 
                ephemeral=True
            )
    
    @app_commands.command(name="detection_breakdown", description="View crisis detection method breakdown")
    async def detection_breakdown(self, interaction: discord.Interaction):
        """View detailed breakdown of detection methods"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        try:
            embed = discord.Embed(
                title="🔍 Crisis Detection Method Breakdown",
                description="Analysis of how crises are being detected",
                color=discord.Color.purple()
            )
            
            # Get message handler stats
            if hasattr(self.bot, 'message_handler') and self.bot.message_handler:
                stats = self.bot.message_handler.get_message_handler_stats()
                
                detection_methods = stats['detection_breakdown']
                total_detections = sum(detection_methods.values())
                
                if total_detections > 0:
                    for method, count in detection_methods.items():
                        percentage = (count / total_detections) * 100
                        embed.add_field(
                            name=f"🔍 {method.replace('_', ' ').title()}",
                            value=f"**Count:** {count}\n**Percentage:** {percentage:.1f}%",
                            inline=True
                        )
                    
                    embed.add_field(
                        name="📊 Total Detections",
                        value=f"{total_detections} crisis detections processed",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="📊 Detection Status",
                        value="No crisis detections recorded yet",
                        inline=False
                    )
                
                # Rate limiting info
                rate_info = stats['rate_limiting']
                embed.add_field(
                    name="⏱️ Rate Limiting",
                    value=f"**Success Rate:** {rate_info['success_rate_percent']}%\n"
                         f"**Daily Calls:** {rate_info['current_daily_calls']}/{rate_info['max_daily_calls']}\n"
                         f"**Per User Limit:** {rate_info['rate_limit_per_user']}/hour",
                    inline=True
                )
            else:
                embed.add_field(
                    name="❌ Detection Analysis",
                    value="Message handler not available for detailed breakdown",
                    inline=False
                )
            
            # Keyword detector stats
            if hasattr(self.bot, 'keyword_detector') and self.bot.keyword_detector:
                keyword_stats = self.bot.keyword_detector.get_keyword_stats()
                embed.add_field(
                    name="🔤 Keyword Statistics",
                    value=f"**High Crisis:** {keyword_stats['high_crisis']} keywords\n"
                         f"**Medium Crisis:** {keyword_stats['medium_crisis']} keywords\n"
                         f"**Low Crisis:** {keyword_stats['low_crisis']} keywords\n"
                         f"**Total:** {keyword_stats['total']} keywords",
                    inline=True
                )
            
            embed.set_footer(text="Detection methods: Keyword Only | NLP Primary | Hybrid Detection")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in detection_breakdown command: {e}")
            logger.exception("Full traceback:")
            await interaction.response.send_message(
                f"❌ Error retrieving detection breakdown: {str(e)}", 
                ephemeral=True
            )

    @app_commands.command(name="test_message_analysis", description="Test message analysis and crisis detection on sample text")
    @app_commands.describe(
        test_message="Message text to analyze for crisis detection",
        show_details="Show detailed analysis breakdown"
    )
    async def test_message_analysis(self, interaction: discord.Interaction, 
                                  test_message: str,
                                  show_details: bool = True):
        """Test message analysis and crisis detection capabilities"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Initialize analysis results
            analysis_results = {
                'keyword_detection': None,
                'nlp_analysis': None,
                'final_decision': None
            }
            
            # Test keyword detection
            if hasattr(self.bot, 'keyword_detector') and self.bot.keyword_detector:
                keyword_result = self.bot.keyword_detector.check_message(test_message)
                analysis_results['keyword_detection'] = keyword_result
            
            # Test NLP analysis if available
            if hasattr(self.bot, 'nlp_client') and self.bot.nlp_client:
                try:
                    nlp_result = await self.bot.nlp_client.analyze_message(test_message)
                    analysis_results['nlp_analysis'] = nlp_result
                except Exception as e:
                    logger.warning(f"NLP analysis failed: {e}")
                    analysis_results['nlp_analysis'] = {'error': str(e)}
            
            # Test full detection decision through message handler
            if hasattr(self.bot, 'message_handler') and self.bot.message_handler:
                try:
                    # Create a mock message for testing
                    class MockMessage:
                        def __init__(self, content):
                            self.content = content
                            self.author = type('author', (), {
                                'id': interaction.user.id, 
                                'mention': f'<@{interaction.user.id}>',
                                'display_name': interaction.user.display_name
                            })()
                            self.channel = interaction.channel
                            self.guild = interaction.guild
                    
                    mock_msg = MockMessage(test_message)
                    # Use the message handler's hybrid detection method
                    final_result = await self.bot.message_handler._perform_hybrid_detection(mock_msg)
                    analysis_results['final_decision'] = final_result
                except Exception as e:
                    logger.warning(f"Message handler analysis failed: {e}")
                    analysis_results['final_decision'] = {'error': str(e)}
            
            # Create response embed
            embed = discord.Embed(
                title="🧪 Message Analysis Test",
                description=f"**Test Message:** `{test_message[:100]}{'...' if len(test_message) > 100 else ''}`",
                color=discord.Color.blue()
            )
            
            # Keyword Detection Results
            if analysis_results['keyword_detection']:
                kw_result = analysis_results['keyword_detection']
                kw_color = "🔴" if kw_result['crisis_level'] == 'high' else "🟡" if kw_result['crisis_level'] == 'medium' else "🟢" if kw_result['crisis_level'] == 'low' else "⚪"
                
                embed.add_field(
                    name="🔤 Keyword Detection",
                    value=f"{kw_color} **Level:** {kw_result['crisis_level'].title()}\n"
                          f"**Needs Response:** {'✅' if kw_result['needs_response'] else '❌'}\n"
                          f"**Categories:** {', '.join(kw_result.get('detected_categories', [])) if kw_result.get('detected_categories') else 'None'}",
                    inline=True
                )
                
                if show_details and kw_result.get('detected_keywords'):
                    embed.add_field(
                        name="🎯 Detected Keywords",
                        value=f"```{', '.join(kw_result['detected_keywords'][:5])}{'...' if len(kw_result['detected_keywords']) > 5 else ''}```",
                        inline=True
                    )
            else:
                embed.add_field(
                    name="🔤 Keyword Detection",
                    value="❌ Keyword detector not available",
                    inline=True
                )
            
            # NLP Analysis Results
            if analysis_results['nlp_analysis']:
                nlp_result = analysis_results['nlp_analysis']
                if 'error' in nlp_result:
                    embed.add_field(
                        name="🧠 NLP Analysis",
                        value=f"❌ Error: {nlp_result['error'][:50]}...",
                        inline=True
                    )
                else:
                    # Use the correct field names from NLP response
                    confidence = nlp_result.get('confidence_score', 0)
                    nlp_level = nlp_result.get('crisis_level', 'unknown')
                    nlp_color = "🔴" if nlp_level == 'high' else "🟡" if nlp_level == 'medium' else "🟢" if nlp_level == 'low' else "⚪"
                    
                    processing_time = nlp_result.get('processing_time_ms', 0)
                    method = nlp_result.get('method', 'unknown')
                    
                    embed.add_field(
                        name="🧠 NLP Analysis",
                        value=f"{nlp_color} **Level:** {nlp_level.title()}\n"
                              f"**Confidence:** {confidence:.2%}\n"
                              f"**Method:** {method}\n"
                              f"**Time:** {processing_time:.1f}ms",
                        inline=True
                    )
                    
                    if show_details and nlp_result.get('reasoning'):
                        embed.add_field(
                            name="🔍 AI Reasoning",
                            value=f"```{nlp_result['reasoning'][:100]}{'...' if len(nlp_result['reasoning']) > 100 else ''}```",
                            inline=False
                        )
                    
                    # Show detected categories if available
                    if nlp_result.get('detected_categories'):
                        categories = nlp_result['detected_categories']
                        embed.add_field(
                            name="🏷️ Categories",
                            value=f"```{', '.join(categories[:3])}{'...' if len(categories) > 3 else ''}```",
                            inline=True
                        )
            else:
                embed.add_field(
                    name="🧠 NLP Analysis",
                    value="⚪ NLP service not available",
                    inline=True
                )
            
            # Final Decision
            if analysis_results['final_decision']:
                final_result = analysis_results['final_decision']
                if 'error' in final_result:
                    embed.add_field(
                        name="⚡ Final Decision",
                        value=f"❌ Error: {final_result['error'][:50]}...",
                        inline=False
                    )
                else:
                    final_level = final_result.get('crisis_level', 'unknown')
                    final_color = "🔴" if final_level == 'high' else "🟡" if final_level == 'medium' else "🟢" if final_level == 'low' else "⚪"
                    would_respond = final_result.get('needs_response', False)
                    method = final_result.get('method', 'Unknown')  # Fixed field name
                    confidence = final_result.get('confidence', 0)
                    
                    embed.add_field(
                        name="⚡ Final Decision",
                        value=f"{final_color} **Crisis Level:** {final_level.title()}\n"
                              f"**Would Respond:** {'✅ Yes' if would_respond else '❌ No'}\n"
                              f"**Method:** {method}\n"
                              f"**Confidence:** {confidence:.2%}",
                        inline=False
                    )
                    
                    # Show breakdown if available
                    if final_result.get('keyword_result') and final_result.get('nlp_result'):
                        embed.add_field(
                            name="🔍 Detection Breakdown",
                            value=f"**Keywords:** {final_result['keyword_result'].title()}\n"
                                  f"**NLP:** {final_result['nlp_result'].title()}\n"
                                  f"**Winner:** {method.replace('_', ' ').title()}",
                            inline=True
                        )
            else:
                embed.add_field(
                    name="⚡ Final Decision",
                    value="❌ Message handler not available",
                    inline=False
                )
            
            # Summary and recommendations
            summary_lines = []
            if analysis_results['keyword_detection'] and analysis_results['keyword_detection']['needs_response']:
                summary_lines.append("✅ Keywords detected crisis language")
            if analysis_results['nlp_analysis'] and not analysis_results['nlp_analysis'].get('error'):
                nlp_confidence = analysis_results['nlp_analysis'].get('confidence', 0)
                if nlp_confidence > 0.7:
                    summary_lines.append("✅ High NLP confidence in analysis")
                elif nlp_confidence > 0.4:
                    summary_lines.append("⚠️ Moderate NLP confidence")
                else:
                    summary_lines.append("⚪ Low NLP confidence")
            
            if summary_lines:
                embed.add_field(
                    name="📊 Analysis Summary",
                    value="\n".join(summary_lines),
                    inline=False
                )
            
            embed.set_footer(text=f"Analysis completed • Detection System v2.0")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in test_message_analysis command: {e}")
            logger.exception("Full traceback:")
            await interaction.followup.send(
                f"❌ Error during message analysis: {str(e)}", 
                ephemeral=True
            )

async def setup(bot):
    """Setup function for the monitoring commands cog"""
    await bot.add_cog(MonitoringCommands(bot))
    logger.info("✅ Enhanced monitoring commands cog loaded")