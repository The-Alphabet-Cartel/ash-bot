"""
Enhanced Crisis Handler - v3.0 CLEANED VERSION
Removed all legacy/backward compatibility methods
Only keeps the diagnostic conversation instruction methods
"""

import logging
import discord
from discord import Message

logger = logging.getLogger(__name__)

class CrisisHandler:
    """v3.0 Crisis escalation handler with conversation instructions"""
    
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        
        # Configuration with diagnostic logging
        logger.info("🔧 Initializing v3.0 Crisis Handler...")
        
        try:
            self.resources_channel_id = config.get_int('BOT_RESOURCES_CHANNEL_ID')
            logger.info(f"📁 Resources Channel ID: {self.resources_channel_id}")
        except Exception as e:
            logger.error(f"❌ Failed to get BOT_RESOURCES_CHANNEL_ID: {e}")
            self.resources_channel_id = None
        
        try:
            self.crisis_response_channel_id = config.get_int('BOT_CRISIS_RESPONSE_CHANNEL_ID')
            logger.info(f"🚨 Crisis Response Channel ID: {self.crisis_response_channel_id}")
        except Exception as e:
            logger.error(f"❌ Failed to get BOT_CRISIS_RESPONSE_CHANNEL_ID: {e}")
            self.crisis_response_channel_id = None
        
        try:
            self.crisis_response_role_id = config.get_int('BOT_CRISIS_RESPONSE_ROLE_ID')
            logger.info(f"👥 Crisis Response Role ID: {self.crisis_response_role_id}")
        except Exception as e:
            logger.error(f"❌ Failed to get BOT_CRISIS_RESPONSE_ROLE_ID: {e}")
            self.crisis_response_role_id = None
        
        try:
            self.staff_ping_user_id = config.get_int('BOT_STAFF_PING_USER')
            logger.info(f"📧 Staff Ping User ID: {self.staff_ping_user_id}")
        except Exception as e:
            logger.error(f"❌ Failed to get BOT_STAFF_PING_USER: {e}")
            self.staff_ping_user_id = None
        
        # v3.0 Enhanced statistics tracking
        self.crisis_stats = {
            'high_crisis_count': 0,
            'medium_crisis_count': 0,
            'low_crisis_count': 0,
            'staff_dms_sent': 0,
            'team_alerts_sent': 0,
            'escalation_errors': 0,
            'conversation_instructions_sent': 0
        }
        
        logger.info(f"🚨 v3.0 Crisis handler initialized")

    async def handle_crisis_response_with_instructions(self, message: Message, crisis_level: str, ash_response: str):
        """v3.0 Enhanced crisis response with conversation instructions"""
        
        logger.warning(f"🚨 v3.0: Starting crisis response with instructions")
        logger.warning(f"   👤 User: {message.author} ({message.author.id})")
        logger.warning(f"   📍 Channel: {message.channel} ({message.channel.id})")
        logger.warning(f"   🚨 Crisis Level: {crisis_level}")
        logger.warning(f"   📝 Response Length: {len(ash_response)} chars")
        
        # Check bot permissions first
        try:
            channel_perms = message.channel.permissions_for(message.guild.me)
            logger.warning(f"🔐 Bot permissions in channel:")
            logger.warning(f"   📝 Send Messages: {channel_perms.send_messages}")
            logger.warning(f"   📎 Add Reactions: {channel_perms.add_reactions}")
        except Exception as e:
            logger.error(f"❌ Failed to check bot permissions: {e}")
        
        # Get configuration for conversation instructions
        try:
            show_instructions = self.config.get_bool('BOT_CONVERSATION_SETUP_INSTRUCTIONS', True)
            logger.warning(f"💬 Show instructions: {show_instructions}")
        except Exception as e:
            logger.error(f"❌ Failed to get conversation instructions config: {e}")
            show_instructions = True
        
        if show_instructions:
            try:
                bot_mention = f"<@{self.bot.user.id}>"
                continuation_instruction = (
                    f"\n\n*I'll be here for the next 5 minutes if you want to continue talking. "
                    f"Just mention me ({bot_mention}) or say 'Ash' to get my attention.*"
                )
                
                full_response = ash_response + continuation_instruction
                logger.warning(f"💬 Added continuation instructions (total length: {len(full_response)})")
                self.crisis_stats['conversation_instructions_sent'] += 1
            except Exception as e:
                logger.error(f"❌ Failed to add continuation instructions: {e}")
                full_response = ash_response
        else:
            full_response = ash_response
        
        # Update statistics
        self.crisis_stats[f'{crisis_level}_crisis_count'] += 1
        logger.warning(f"📊 Updated crisis stats - {crisis_level} count now: {self.crisis_stats[f'{crisis_level}_crisis_count']}")
        
        # v3.0 Enhanced crisis handling
        try:
            if crisis_level == 'high':
                logger.warning(f"🔴 Routing to HIGH crisis handler")
                await self._handle_high_crisis_with_instructions(message, full_response)
            elif crisis_level == 'medium':
                logger.warning(f"🟡 Routing to MEDIUM crisis handler")
                await self._handle_medium_crisis_with_instructions(message, full_response)
            else:  # low
                logger.warning(f"🟢 Routing to LOW crisis handler")
                await self._handle_low_crisis_with_instructions(message, full_response)
                
            logger.warning(f"✅ v3.0 Crisis response completed successfully")
            
        except Exception as e:
            logger.error(f"❌ v3.0 Crisis response failed: {e}")
            logger.exception("Full traceback:")
            self.crisis_stats['escalation_errors'] += 1

    async def _handle_high_crisis_with_instructions(self, message: Message, enhanced_response: str):
        """v3.0 High crisis handling with comprehensive logging"""
        
        logger.warning(f"🔴 v3.0: Starting HIGH crisis handler")
        logger.warning(f"   👤 User: {message.author} in {message.channel}")
        
        try:
            # Send enhanced Ash response with instructions
            logger.warning(f"📤 Attempting to send reply to message...")
            response_message = await message.reply(enhanced_response)
            logger.warning(f"✅ Reply sent successfully (message ID: {response_message.id})")
            
            # Add reaction to indicate active conversation
            try:
                await response_message.add_reaction('💬')
                logger.warning(f"✅ Reaction added successfully")
            except Exception as e:
                logger.warning(f"⚠️ Failed to add reaction: {e}")
            
            # v3.0 Enhanced escalation
            dm_success = await self._send_staff_dm(message, "HIGH")
            alert_success = await self._send_crisis_team_alert(message, "HIGH")
            
            # Enhanced logging
            logger.warning(f"✅ v3.0 High crisis handling completed:")
            logger.warning(f"   📧 Staff DM: {'✅ Sent' if dm_success else '❌ Failed'}")
            logger.warning(f"   📢 Team Alert: {'✅ Sent' if alert_success else '❌ Failed'}")
            logger.warning(f"   💬 Conversation instructions: ✅ Included")
            logger.warning(f"   📊 Total high crises: {self.crisis_stats['high_crisis_count']}")
            
        except Exception as e:
            self.crisis_stats['escalation_errors'] += 1
            logger.error(f"❌ Error in v3.0 high crisis handling: {e}")
            logger.exception("Full traceback:")

    async def _send_staff_dm(self, message: Message, crisis_level: str) -> bool:
        """v3.0 Enhanced staff DM with comprehensive logging"""
        
        logger.warning(f"📧 v3.0: Starting staff DM process")
        logger.warning(f"   🎯 Staff User ID: {self.staff_ping_user_id}")
        logger.warning(f"   🚨 Crisis Level: {crisis_level}")
        
        if not self.staff_ping_user_id:
            logger.error(f"❌ No staff ping user ID configured!")
            return False
        
        try:
            staff_user = await self.bot.fetch_user(self.staff_ping_user_id)
            logger.warning(f"✅ Staff user fetched: {staff_user} ({staff_user.id})")
            
            dm_message = f"🚨 URGENT: {crisis_level} crisis detected from {message.author.display_name} in {message.channel.mention}. Please check the crisis channel for details."
            
            await staff_user.send(dm_message)
            
            self.crisis_stats['staff_dms_sent'] += 1
            logger.warning(f"✅ v3.0 Staff DM sent successfully to {staff_user.display_name}")
            
            return True
            
        except discord.Forbidden as e:
            logger.error(f"❌ Permission denied sending staff DM: {e}")
            return False
        except discord.NotFound as e:
            logger.error(f"❌ Staff user not found: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error sending staff DM: {e}")
            logger.exception("Full traceback:")
            return False
    
    async def _send_crisis_team_alert(self, message: Message, crisis_level: str) -> bool:
        """v3.0 Enhanced crisis team alert with comprehensive logging"""
        
        logger.warning(f"📢 v3.0: Starting crisis team alert process")
        logger.warning(f"   📍 Crisis Channel ID: {self.crisis_response_channel_id}")
        logger.warning(f"   👥 Crisis Role ID: {self.crisis_response_role_id}")
        logger.warning(f"   🚨 Crisis Level: {crisis_level}")
        
        if not self.crisis_response_channel_id:
            logger.error(f"❌ No crisis response channel ID configured!")
            return False
        
        try:
            crisis_channel = self.bot.get_channel(self.crisis_response_channel_id)
            
            if not crisis_channel:
                logger.error(f"❌ Crisis response channel not found: {self.crisis_response_channel_id}")
                return False
            
            logger.warning(f"✅ Crisis channel found: {crisis_channel} ({crisis_channel.id})")
            
            # Check bot permissions in crisis channel
            try:
                channel_perms = crisis_channel.permissions_for(crisis_channel.guild.me)
                if not channel_perms.send_messages:
                    logger.error(f"❌ Bot cannot send messages in crisis channel!")
                    return False
            except Exception as e:
                logger.error(f"❌ Failed to check crisis channel permissions: {e}")
            
            # Build role mention
            role_mention = ""
            if self.crisis_response_role_id:
                role_mention = f"<@&{self.crisis_response_role_id}> "
            
            # v3.0 Enhanced alert message
            alert_message = (
                f"{role_mention}🚨 **{crisis_level} CRISIS ALERT** (v3.0)\n\n"
                f"**User:** {message.author.mention} ({message.author.display_name})\n"
                f"**Channel:** {message.channel.mention}\n"
                f"**Message:** {message.content[:200]}{'...' if len(message.content) > 200 else ''}\n"
                f"**Jump:** {message.jump_url}\n\n"
                f"⚠️ Immediate attention required!"
            )
            
            sent_message = await crisis_channel.send(alert_message)
            logger.warning(f"✅ v3.0 Crisis alert sent successfully (message ID: {sent_message.id})")
            
            # Try to add reaction
            try:
                await sent_message.add_reaction("🚨")
                logger.warning(f"✅ Reaction added to crisis alert")
            except Exception as e:
                logger.warning(f"⚠️ Failed to add reaction to crisis alert: {e}")
            
            self.crisis_stats['team_alerts_sent'] += 1
            
            return True
            
        except discord.Forbidden as e:
            logger.error(f"❌ Permission denied sending crisis team alert: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error sending crisis team alert: {e}")
            logger.exception("Full traceback:")
            return False

    async def _handle_medium_crisis_with_instructions(self, message: Message, enhanced_response: str):
        """v3.0 Medium crisis handling"""
        
        logger.warning(f"🟡 v3.0: Starting MEDIUM crisis handler for {message.author}")
        
        try:
            response_message = await message.reply(enhanced_response)
            logger.warning(f"✅ v3.0 Medium crisis reply sent")
            
            await response_message.add_reaction('💬')
            alert_success = await self._send_crisis_team_alert(message, "MEDIUM")
            
            logger.warning(f"✅ v3.0 Medium crisis completed - Team Alert: {'Success' if alert_success else 'Failed'}")
            
        except Exception as e:
            self.crisis_stats['escalation_errors'] += 1
            logger.error(f"❌ Error in v3.0 medium crisis handling: {e}")

    async def _handle_low_crisis_with_instructions(self, message: Message, enhanced_response: str):
        """v3.0 Low crisis handling"""
        
        logger.warning(f"🟢 v3.0: Starting LOW crisis handler for {message.author}")
        
        try:
            response_message = await message.reply(enhanced_response)
            logger.warning(f"✅ v3.0 Low crisis reply sent")
            
            await response_message.add_reaction('💬')
            logger.warning(f"✅ v3.0 Low crisis completed successfully")
            
        except Exception as e:
            self.crisis_stats['escalation_errors'] += 1
            logger.error(f"❌ Error in v3.0 low crisis handling: {e}")

    def get_crisis_stats(self) -> dict:
        """Get v3.0 comprehensive crisis handling statistics"""
        total_crises = (
            self.crisis_stats['high_crisis_count'] + 
            self.crisis_stats['medium_crisis_count'] + 
            self.crisis_stats['low_crisis_count']
        )
        
        success_rate = 0
        if total_crises > 0:
            successful_responses = total_crises - self.crisis_stats['escalation_errors']
            success_rate = (successful_responses / total_crises) * 100
        
        return {
            'component': 'v3.0_CrisisHandler',
            **self.crisis_stats,
            'total_crises_today': total_crises,
            'success_rate_percent': round(success_rate, 2),
            'configuration': {
                'staff_dm_enabled': self.staff_ping_user_id is not None,
                'team_alerts_enabled': self.crisis_response_channel_id is not None,
                'crisis_role_configured': self.crisis_response_role_id is not None,
                'resources_channel_configured': self.resources_channel_id is not None,
                'conversation_instructions_enabled': True
            }
        }