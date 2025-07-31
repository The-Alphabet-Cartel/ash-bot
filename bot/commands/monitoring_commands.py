"""
Enhanced Monitoring Commands - FIXED with detection_breakdown removed
Updated for three-model ensemble support
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
import os
import time
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class MonitoringCommands(commands.Cog):
    """Enhanced monitoring commands for the three-model ensemble bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.crisis_response_role_id = int(os.getenv('BOT_CRISIS_RESPONSE_ROLE_ID', '0'))
        
        logger.info("📊 Enhanced monitoring commands loaded (detection_breakdown removed)")
    
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
                description="Three-model ensemble with gap detection",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)
            )
            
            # Bot basic info
            current_time = datetime.now(timezone.utc)
            
            embed.add_field(
                name="🤖 Bot Information",
                value=f"**Status:** {'🟢 Online' if self.bot.is_ready() else '🔴 Offline'}\n"
                     f"**Guilds:** {len(self.bot.guilds)}\n"
                     f"**Users:** {len(self.bot.users)}\n"
                     f"**Commands:** {len(self.bot.tree.get_commands())}\n"
                     f"**Sync Status:** Global",
                inline=True
            )
            
            # Get enhanced message handler stats if available
            if hasattr(self.bot, 'message_handler') and self.bot.message_handler:
                try:
                    # Use the correct method name for EnhancedMessageHandler
                    stats = self.bot.message_handler.get_enhanced_stats()
                    
                    embed.add_field(
                        name="📨 Three-Model Ensemble",
                        value=f"**Messages Processed:** {stats['total_messages_processed']}\n"
                             f"**Crisis Responses:** {stats['crisis_responses_given']}\n"
                             f"**Ensemble Analyses:** {stats['ensemble_analyses_performed']}\n"
                             f"**Gaps Detected:** {stats['gaps_detected']}\n"
                             f"**Staff Reviews:** {stats['staff_reviews_flagged']}",
                        inline=True
                    )
                    
                    # Ensemble-specific metrics
                    embed.add_field(
                        name="🎯 Ensemble Metrics",
                        value=f"**Unanimous Consensus:** {stats['unanimous_consensus_count']}\n"
                             f"**Model Disagreements:** {stats['model_disagreement_count']}\n"
                             f"**Gap Detection Rate:** {stats['gap_detection_rate']:.1%}\n"
                             f"**Staff Review Rate:** {stats['staff_review_rate']:.1%}",
                        inline=True
                    )
                    
                except Exception as e:
                    embed.add_field(
                        name="📨 Message Processing",
                        value=f"Statistics unavailable: {str(e)[:50]}...",
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
                             f"**Success Rate:** {crisis_stats['success_rate_percent']}%",
                        inline=True
                    )
                except Exception as e:
                    embed.add_field(
                        name="🚨 Crisis Management",
                        value="Statistics unavailable",
                        inline=True
                    )
            
            # Service status checks
            service_status = []
            
            # NLP Service
            if hasattr(self.bot, 'nlp_client') and self.bot.nlp_client:
                service_status.append("✅ NLP Service (Three-Model Ensemble)")
            else:
                service_status.append("❌ NLP Service")
            
            # Claude API
            if hasattr(self.bot, 'claude_api') and self.bot.claude_api:
                service_status.append("✅ Claude API")
            else:
                service_status.append("❌ Claude API")
            
            # Keyword Detector
            if hasattr(self.bot, 'keyword_detector') and self.bot.keyword_detector:
                service_status.append("✅ Keyword Detector")
            else:
                service_status.append("❌ Keyword Detector")
            
            embed.add_field(
                name="🔧 Services",
                value="\n".join(service_status),
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
            
            embed.set_footer(text="Three-Model Ensemble System | Ash v2.0")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in system_status command: {e}")
            logger.exception("Full traceback:")
            await interaction.response.send_message(
                f"❌ Error retrieving system status: {str(e)}", 
                ephemeral=True
            )
    
    @app_commands.command(name="ensemble_stats", description="View three-model ensemble statistics")
    async def ensemble_stats(self, interaction: discord.Interaction):
        """View detailed three-model ensemble statistics"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        try:
            if not hasattr(self.bot, 'message_handler') or not self.bot.message_handler:
                await interaction.response.send_message(
                    "❌ Message handler not available", 
                    ephemeral=True
                )
                return
            
            stats = self.bot.message_handler.get_enhanced_stats()
            
            embed = discord.Embed(
                title="🎯 Three-Model Ensemble Statistics",
                description="Detailed breakdown of ensemble performance",
                color=discord.Color.purple()
            )
            
            # Detection method breakdown
            detection_methods = stats['detection_method_breakdown']
            total_detections = sum(detection_methods.values())
            
            if total_detections > 0:
                method_text = ""
                for method, count in detection_methods.items():
                    percentage = (count / total_detections) * 100
                    method_text += f"**{method.replace('_', ' ').title()}:** {count} ({percentage:.1f}%)\n"
                
                embed.add_field(
                    name="🔍 Detection Methods",
                    value=method_text,
                    inline=False
                )
            else:
                embed.add_field(
                    name="🔍 Detection Methods",
                    value="No detections recorded yet",
                    inline=False
                )
            
            # Ensemble performance metrics
            embed.add_field(
                name="📊 Ensemble Performance",
                value=f"**Total Analyses:** {stats['ensemble_analyses_performed']}\n"
                     f"**Gaps Detected:** {stats['gaps_detected']}\n"
                     f"**Staff Reviews Flagged:** {stats['staff_reviews_flagged']}\n"
                     f"**Gap Detection Rate:** {stats['gap_detection_rate']:.1%}\n"
                     f"**Staff Review Rate:** {stats['staff_review_rate']:.1%}",
                inline=True
            )
            
            # Consensus analysis
            embed.add_field(
                name="🤝 Consensus Analysis",
                value=f"**Unanimous Consensus:** {stats['unanimous_consensus_count']}\n"
                     f"**Model Disagreements:** {stats['model_disagreement_count']}\n"
                     f"**Consensus Rate:** {stats['unanimous_consensus_rate']:.1%}",
                inline=True
            )
            
            # Rate limiting and performance
            embed.add_field(
                name="⚡ Performance",
                value=f"**Messages Processed:** {stats['total_messages_processed']}\n"
                     f"**Crisis Responses:** {stats['crisis_responses_given']}\n"
                     f"**Rate Limits Hit:** {stats['rate_limits_hit']}\n"
                     f"**Daily Limits Hit:** {stats['daily_limits_hit']}",
                inline=False
            )
            
            embed.set_footer(text="Three-Model Ensemble: Depression • Sentiment • Emotional Distress")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in ensemble_stats command: {e}")
            logger.exception("Full traceback:")
            await interaction.response.send_message(
                f"❌ Error retrieving ensemble statistics: {str(e)}", 
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
            stats = handler.get_enhanced_stats()
            
            embed = discord.Embed(
                title="💬 Conversation Isolation Statistics",
                description="Statistics for the mention/ping requirement system",
                color=discord.Color.green()
            )
            
            # Conversation metrics
            embed.add_field(
                name="💬 Conversation Metrics",
                value=f"**Conversations Started:** {stats['conversations_started']}\n"
                     f"**Follow-ups Handled:** {stats['follow_ups_handled']}\n"
                     f"**Ignored Follow-ups:** {stats['ignored_follow_ups']}\n"
                     f"**Intrusions Blocked:** {stats['intrusion_attempts_blocked']}\n"
                     f"**Crisis Overrides:** {stats['crisis_overrides_triggered']}",
                inline=True
            )
            
            # Configuration info
            mention_required = self.bot.config.get_bool('BOT_CONVERSATION_REQUIRES_MENTION', True)
            triggers = self.bot.config.get('BOT_CONVERSATION_TRIGGER_PHRASES', 'ash,hey ash,ash help,@ash')
            timeout = self.bot.config.get_int('BOT_CONVERSATION_TIMEOUT', 300)
            
            embed.add_field(
                name="⚙️ Configuration",
                value=f"**Mention Required:** {'✅ Yes' if mention_required else '❌ No'}\n"
                     f"**Timeout:** {timeout} seconds\n"
                     f"**Override Levels:** {self.bot.config.get('BOT_CRISIS_OVERRIDE_LEVELS', 'medium,high')}",
                inline=True
            )
            
            # Current active conversations
            active_count = len(handler.active_conversations) if hasattr(handler, 'active_conversations') else 0
            embed.add_field(
                name="🔄 Current Status",
                value=f"**Active Conversations:** {active_count}\n"
                     f"**System Status:** {'🟢 Operational' if active_count >= 0 else '🔴 Error'}",
                inline=False
            )
            
            # Trigger phrases
            trigger_list = triggers.split(',')[:5]  # Show first 5
            embed.add_field(
                name="🔤 Trigger Phrases",
                value=" • " + "\n • ".join(trigger_list) + 
                     (f"\n • ...and {len(triggers.split(',')) - 5} more" if len(triggers.split(',')) > 5 else ""),
                inline=False
            )
            
            embed.set_footer(text="Conversations expire after timeout • Crisis overrides bypass isolation")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in conversation_stats command: {e}")
            logger.exception("Full traceback:")
            await interaction.response.send_message(
                f"❌ Error retrieving conversation statistics: {str(e)}", 
                ephemeral=True
            )

    @app_commands.command(name="active_conversations", description="View currently active conversations")
    async def active_conversations(self, interaction: discord.Interaction):
        """View currently active conversations"""
        
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
            
            if not hasattr(handler, 'active_conversations') or not handler.active_conversations:
                embed = discord.Embed(
                    title="💬 Active Conversations",
                    description="No active conversations currently",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="💬 Active Conversations",
                    description=f"{len(handler.active_conversations)} conversations active",
                    color=discord.Color.orange()
                )
                
                # Show conversation details
                for user_id, conv_data in list(handler.active_conversations.items())[:10]:  # Limit to 10
                    try:
                        user = await self.bot.fetch_user(user_id)
                        duration = time.time() - conv_data.get('start_time', time.time())
                        time_left = max(0, handler.conversation_timeout - duration)
                        
                        embed.add_field(
                            name=f"👤 {user.display_name}",
                            value=f"**Crisis Level:** {conv_data.get('crisis_level', 'unknown')}\n"
                                 f"**Duration:** {duration:.0f}s\n"
                                 f"**Time Left:** {time_left:.0f}s\n"
                                 f"**Channel:** <#{conv_data.get('channel_id', 'unknown')}>",
                            inline=True
                        )
                    except Exception:
                        embed.add_field(
                            name=f"👤 User {user_id}",
                            value=f"**Crisis Level:** {conv_data.get('crisis_level', 'unknown')}\n"
                                 f"**Channel:** <#{conv_data.get('channel_id', 'unknown')}>",
                            inline=True
                        )
                
                if len(handler.active_conversations) > 10:
                    embed.add_field(
                        name="📋 Note",
                        value=f"Showing first 10 of {len(handler.active_conversations)} conversations",
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

    @app_commands.command(name="test_message_analysis", description="Test message analysis and crisis detection on sample text")
    @app_commands.describe(
        message="Message text to analyze for crisis detection",
        show_details="Show detailed analysis breakdown"
    )
    async def test_message_analysis(self, interaction: discord.Interaction, 
                                  message: str,
                                  show_details: bool = True):
        """Test message analysis and crisis detection capabilities - FINAL FIXED VERSION"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Validate input message
            if not message or not message.strip():
                await interaction.followup.send(
                    "❌ Error: Message cannot be empty. Please provide a message to analyze.", 
                    ephemeral=True
                )
                return
            
            test_message = message.strip()
            logger.info(f"🧪 Testing message analysis for: '{test_message}' (length: {len(test_message)})")
            
            # Initialize analysis results
            analysis_results = {
                'keyword_detection': None,
                'nlp_analysis': None,
                'final_decision': None
            }
            
            # Test keyword detection ONLY
            if hasattr(self.bot, 'keyword_detector') and self.bot.keyword_detector:
                try:
                    logger.debug(f"🔤 Testing keyword detection with: '{test_message}'")
                    keyword_result = self.bot.keyword_detector.check_message(test_message)
                    analysis_results['keyword_detection'] = keyword_result
                    logger.debug(f"🔤 Keyword result: {keyword_result}")
                except Exception as e:
                    logger.error(f"Keyword detection failed: {e}")
                    analysis_results['keyword_detection'] = {'error': str(e)}
            
            # REMOVED: Direct NLP call to prevent duplicates
            # The message handler will call NLP internally, and we'll get those results
            
            # Test full detection decision through message handler - SINGLE COMPREHENSIVE CALL
            if hasattr(self.bot, 'message_handler') and self.bot.message_handler:
                try:
                    logger.debug(f"⚡ Testing message handler with: '{test_message}'")
                    
                    # Create a mock message for testing - ENSURE CONTENT IS SET
                    class MockMessage:
                        def __init__(self, content):
                            if not content or not content.strip():
                                raise ValueError(f"MockMessage content cannot be empty: '{content}'")
                            self.content = content.strip()
                            self.author = type('author', (), {
                                'id': interaction.user.id, 
                                'mention': f'<@{interaction.user.id}>',
                                'display_name': interaction.user.display_name
                            })()
                            self.channel = interaction.channel
                            self.guild = interaction.guild
                            logger.debug(f"🤖 Created MockMessage with content: '{self.content}' (length: {len(self.content)})")
                    
                    mock_msg = MockMessage(test_message)
                    
                    # Use the message handler's hybrid detection - this will call NLP internally
                    if hasattr(self.bot.message_handler, '_perform_enhanced_hybrid_detection'):
                        final_result = await self.bot.message_handler._perform_enhanced_hybrid_detection(mock_msg)
                    elif hasattr(self.bot.message_handler, '_perform_hybrid_detection'):
                        final_result = await self.bot.message_handler._perform_hybrid_detection(mock_msg)
                    else:
                        raise AttributeError("No hybrid detection method found on message handler")
                    
                    analysis_results['final_decision'] = final_result
                    if final_result:
                        logger.debug(f"⚡ Final result: {final_result.get('crisis_level')} via {final_result.get('method')}")
                        
                        # Extract NLP results from the final decision for display
                        if final_result.get('ensemble_details'):
                            # Build NLP analysis results from the final decision
                            analysis_results['nlp_analysis'] = {
                                'crisis_level': final_result.get('nlp_result', 'none'),
                                'confidence_score': final_result.get('confidence', 0.0),
                                'method': final_result.get('method', 'unknown'),
                                'gaps_detected': final_result.get('gaps_detected', False),
                                'requires_staff_review': final_result.get('requires_staff_review', False),
                                'processing_time_ms': final_result.get('processing_time_ms', 0),
                                'ensemble_details': final_result.get('ensemble_details', {})
                            }
                        else:
                            # Fallback: Basic NLP result extraction
                            analysis_results['nlp_analysis'] = {
                                'crisis_level': final_result.get('nlp_result', 'none'),
                                'confidence_score': final_result.get('confidence', 0.0),
                                'method': final_result.get('method', 'unknown'),
                                'gaps_detected': final_result.get('gaps_detected', False),
                                'requires_staff_review': final_result.get('requires_staff_review', False),
                                'processing_time_ms': final_result.get('processing_time_ms', 0)
                            }
                    
                except Exception as e:
                    logger.error(f"Message handler analysis failed: {e}")
                    logger.exception("Full traceback:")
                    analysis_results['final_decision'] = {'error': str(e)}
            
            # Create response embed - SAME AS BEFORE
            embed = discord.Embed(
                title="🧪 Three-Model Ensemble Analysis Test",
                description=f"**Test Message:** `{test_message[:100]}{'...' if len(test_message) > 100 else ''}`",
                color=discord.Color.blue()
            )
            
            # Keyword Detection Results
            if analysis_results['keyword_detection']:
                kw_result = analysis_results['keyword_detection']
                if 'error' in kw_result:
                    embed.add_field(
                        name="🔤 Keyword Detection",
                        value=f"❌ Error: {kw_result['error'][:50]}...",
                        inline=True
                    )
                else:
                    kw_color = "🔴" if kw_result['crisis_level'] == 'high' else "🟡" if kw_result['crisis_level'] == 'medium' else "🟢" if kw_result['crisis_level'] == 'low' else "⚪"
                    
                    embed.add_field(
                        name="🔤 Keyword Detection",
                        value=f"{kw_color} **Level:** {kw_result['crisis_level'].title()}\n"
                              f"**Needs Response:** {'✅' if kw_result['needs_response'] else '❌'}\n"
                              f"**Categories:** {', '.join(kw_result.get('detected_categories', [])) if kw_result.get('detected_categories') else 'None'}",
                        inline=True
                    )
            else:
                embed.add_field(
                    name="🔤 Keyword Detection",
                    value="❌ Keyword detector not available",
                    inline=True
                )
            
            # Three-Model Ensemble Results (from final decision)
            if analysis_results['nlp_analysis']:
                nlp_result = analysis_results['nlp_analysis']
                if 'error' in nlp_result:
                    embed.add_field(
                        name="🎯 Three-Model Ensemble",
                        value=f"❌ Error: {nlp_result['error'][:50]}...",
                        inline=True
                    )
                else:
                    confidence = nlp_result.get('confidence_score', 0)
                    nlp_level = nlp_result.get('crisis_level', 'unknown')
                    nlp_color = "🔴" if nlp_level == 'high' else "🟡" if nlp_level == 'medium' else "🟢" if nlp_level == 'low' else "⚪"
                    
                    processing_time = nlp_result.get('processing_time_ms', 0)
                    method = nlp_result.get('method', 'unknown')
                    
                    ensemble_text = f"{nlp_color} **Level:** {nlp_level.title()}\n"
                    ensemble_text += f"**Confidence:** {confidence:.2%}\n"
                    ensemble_text += f"**Method:** {method.replace('_', ' ').title()}\n"
                    ensemble_text += f"**Processing:** {processing_time:.1f}ms"
                    
                    if nlp_result.get('gaps_detected'):
                        ensemble_text += f"\n🔍 **Gaps Detected:** Yes"
                    
                    embed.add_field(
                        name="🎯 Three-Model Ensemble",
                        value=ensemble_text,
                        inline=True
                    )
                    
                    # Show model breakdown if available and requested
                    if show_details and nlp_result.get('ensemble_details'):
                        ensemble_details = nlp_result['ensemble_details']
                        predictions = ensemble_details.get('model_predictions', {})
                        confidences = ensemble_details.get('individual_confidence_scores', {})
                        
                        if predictions:
                            breakdown_text = ""
                            for model, prediction in predictions.items():
                                conf = confidences.get(model, 0)
                                breakdown_text += f"**{model.title()}:** {prediction} ({conf:.2%})\n"
                            
                            if breakdown_text:
                                embed.add_field(
                                    name="🤖 Model Breakdown",
                                    value=breakdown_text,
                                    inline=False
                                )
            else:
                embed.add_field(
                    name="🎯 Three-Model Ensemble",
                    value="❌ NLP service not available",
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
                    crisis_level = final_result.get('crisis_level', 'unknown')
                    confidence = final_result.get('confidence', 0)
                    method = final_result.get('method', 'unknown')
                    
                    decision_color = "🔴" if crisis_level == 'high' else "🟡" if crisis_level == 'medium' else "🟢" if crisis_level == 'low' else "⚪"
                    
                    embed.add_field(
                        name="⚡ Final Decision",
                        value=f"{decision_color} **Level:** {crisis_level.title()}\n"
                              f"**Method:** {method.replace('_', ' ').title()}\n"
                              f"**Confidence:** {confidence:.2%}\n"
                              f"**Needs Response:** {'✅' if final_result.get('needs_response') else '❌'}\n"
                              f"**Gaps Detected:** {'🔍' if final_result.get('gaps_detected') else '❌'}",
                        inline=False
                    )
                    
                    # Show breakdown if both keyword and NLP results available
                    if (final_result.get('keyword_result') and final_result.get('nlp_result') and 
                        final_result['keyword_result'] != 'none' and final_result['nlp_result'] != 'none'):
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
            if analysis_results['keyword_detection'] and analysis_results['keyword_detection'].get('needs_response'):
                summary_lines.append("✅ Keywords detected crisis language")
            if analysis_results['nlp_analysis'] and not analysis_results['nlp_analysis'].get('error'):
                nlp_confidence = analysis_results['nlp_analysis'].get('confidence_score', 0)
                if nlp_confidence > 0.7:
                    summary_lines.append("✅ High NLP confidence in analysis")
                elif nlp_confidence > 0.4:
                    summary_lines.append("⚠️ Moderate NLP confidence")
                else:
                    summary_lines.append("⚪ Low NLP confidence")
            
            if analysis_results['nlp_analysis'] and analysis_results['nlp_analysis'].get('gaps_detected'):
                summary_lines.append("🔍 Model disagreement detected - staff review recommended")
            
            if summary_lines:
                embed.add_field(
                    name="📊 Analysis Summary",
                    value="\n".join(summary_lines),
                    inline=False
                )
            
            embed.set_footer(text=f"Analysis completed • Detection System v3.0")
            
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
    logger.info("✅ Enhanced monitoring commands cog loaded (detection_breakdown removed)")