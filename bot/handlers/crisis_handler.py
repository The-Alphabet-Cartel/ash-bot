"""
Enhanced Crisis Handler with Conversation Instructions - FIXED IMPORTS
"""

import logging
import discord
from discord import Message

logger = logging.getLogger(__name__)

class CrisisHandler:
    """Enhanced crisis escalation handler with conversation instructions - FIXED IMPORTS"""
    
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        
        # Configuration with EXTENSIVE DIAGNOSTIC LOGGING
        logger.info("🔧 DIAGNOSTIC: Initializing Crisis Handler with proper imports...")
        
        try:
            self.resources_channel_id = config.get_int('BOT_RESOURCES_CHANNEL_ID')
            logger.info(f"📁 DIAGNOSTIC: Resources Channel ID: {self.resources_channel_id}")
        except Exception as e:
            logger.error(f"❌ DIAGNOSTIC: Failed to get BOT_RESOURCES_CHANNEL_ID: {e}")
            self.resources_channel_id = None
        
        try:
            self.crisis_response_channel_id = config.get_int('BOT_CRISIS_RESPONSE_CHANNEL_ID')
            logger.info(f"🚨 DIAGNOSTIC: Crisis Response Channel ID: {self.crisis_response_channel_id}")
        except Exception as e:
            logger.error(f"❌ DIAGNOSTIC: Failed to get BOT_CRISIS_RESPONSE_CHANNEL_ID: {e}")
            self.crisis_response_channel_id = None
        
        try:
            self.crisis_response_role_id = config.get_int('BOT_CRISIS_RESPONSE_ROLE_ID')
            logger.info(f"👥 DIAGNOSTIC: Crisis Response Role ID: {self.crisis_response_role_id}")
        except Exception as e:
            logger.error(f"❌ DIAGNOSTIC: Failed to get BOT_CRISIS_RESPONSE_ROLE_ID: {e}")
            self.crisis_response_role_id = None
        
        try:
            self.staff_ping_user_id = config.get_int('BOT_STAFF_PING_USER')
            logger.info(f"📧 DIAGNOSTIC: Staff Ping User ID: {self.staff_ping_user_id}")
        except Exception as e:
            logger.error(f"❌ DIAGNOSTIC: Failed to get BOT_STAFF_PING_USER: {e}")
            self.staff_ping_user_id = None
        
        # Enhanced statistics tracking
        self.crisis_stats = {
            'high_crisis_count': 0,
            'medium_crisis_count': 0,
            'low_crisis_count': 0,
            'staff_dms_sent': 0,
            'team_alerts_sent': 0,
            'escalation_errors': 0
        }
        
        logger.info(f"🚨 DIAGNOSTIC: Crisis handler initialized with config:")
        logger.info(f"   📧 Staff DM user: {self.staff_ping_user_id}")
        logger.info(f"   📢 Crisis channel: {self.crisis_response_channel_id}")
        logger.info(f"   👥 Crisis role: {self.crisis_response_role_id}")
        logger.info(f"   📁 Resources channel: {self.resources_channel_id}")
        logger.info(f"   🤖 Bot user: {self.bot.user if self.bot.user else 'Not logged in yet'}")

    async def handle_crisis_response_with_instructions(self, message: Message, crisis_level: str, ash_response: str):
        """Enhanced crisis response with EXTENSIVE DIAGNOSTIC LOGGING"""
        
        logger.warning(f"🚨 DIAGNOSTIC: Starting crisis response with instructions")
        logger.warning(f"   👤 User: {message.author} ({message.author.id})")
        logger.warning(f"   📍 Channel: {message.channel} ({message.channel.id})")
        logger.warning(f"   🚨 Crisis Level: {crisis_level}")
        logger.warning(f"   📝 Response Length: {len(ash_response)} chars")
        
        # Check bot permissions first
        try:
            channel_perms = message.channel.permissions_for(message.guild.me)
            logger.warning(f"🔐 DIAGNOSTIC: Bot permissions in channel:")
            logger.warning(f"   📝 Send Messages: {channel_perms.send_messages}")
            logger.warning(f"   📎 Add Reactions: {channel_perms.add_reactions}")
            logger.warning(f"   📱 Use External Emojis: {channel_perms.use_external_emojis}")
            logger.warning(f"   📋 Embed Links: {channel_perms.embed_links}")
        except Exception as e:
            logger.error(f"❌ DIAGNOSTIC: Failed to check bot permissions: {e}")
        
        # Get configuration for whether to show instructions
        try:
            show_instructions = self.config.get_bool('BOT_CONVERSATION_SETUP_INSTRUCTIONS', True)
            logger.warning(f"💬 DIAGNOSTIC: Show instructions: {show_instructions}")
        except Exception as e:
            logger.error(f"❌ DIAGNOSTIC: Failed to get conversation instructions config: {e}")
            show_instructions = True
        
        if show_instructions:
            # Add continuation instructions to the response
            try:
                bot_mention = f"<@{self.bot.user.id}>"  # This creates @Ash mention
                continuation_instruction = (
                    f"\n\n*I'll be here for the next 5 minutes if you want to continue talking. "
                    f"Just mention me ({bot_mention}) or say 'Ash' to get my attention.*"
                )
                
                full_response = ash_response + continuation_instruction
                logger.warning(f"💬 DIAGNOSTIC: Added continuation instructions (total length: {len(full_response)})")
            except Exception as e:
                logger.error(f"❌ DIAGNOSTIC: Failed to add continuation instructions: {e}")
                full_response = ash_response
        else:
            full_response = ash_response
        
        # Update statistics
        self.crisis_stats[f'{crisis_level}_crisis_count'] += 1
        logger.warning(f"📊 DIAGNOSTIC: Updated crisis stats - {crisis_level} count now: {self.crisis_stats[f'{crisis_level}_crisis_count']}")
        
        # Use enhanced crisis handling logic with instructions
        try:
            if crisis_level == 'high':
                logger.warning(f"🔴 DIAGNOSTIC: Routing to HIGH crisis handler")
                await self._handle_high_crisis_with_instructions(message, full_response)
            elif crisis_level == 'medium':
                logger.warning(f"🟡 DIAGNOSTIC: Routing to MEDIUM crisis handler")
                await self._handle_medium_crisis_with_instructions(message, full_response)
            else:  # low
                logger.warning(f"🟢 DIAGNOSTIC: Routing to LOW crisis handler")
                await self._handle_low_crisis_with_instructions(message, full_response)
                
            logger.warning(f"✅ DIAGNOSTIC: Crisis response routing completed successfully")
            
        except Exception as e:
            logger.error(f"❌ DIAGNOSTIC: Crisis response routing failed: {e}")
            logger.exception("Full traceback:")
            self.crisis_stats['escalation_errors'] += 1

    async def _handle_high_crisis_with_instructions(self, message: Message, enhanced_response: str):
        """High crisis handling with EXTENSIVE DIAGNOSTIC LOGGING"""
        
        logger.warning(f"🔴 DIAGNOSTIC: Starting HIGH crisis handler")
        logger.warning(f"   👤 User: {message.author} in {message.channel}")
        logger.warning(f"   📝 Response preview: '{enhanced_response[:100]}...'")
        
        try:
            # Send enhanced Ash response with instructions
            logger.warning(f"📤 DIAGNOSTIC: Attempting to send reply to message...")
            response_message = await message.reply(enhanced_response)
            logger.warning(f"✅ DIAGNOSTIC: Reply sent successfully (message ID: {response_message.id})")
            
            # Add reaction to indicate active conversation
            logger.warning(f"😊 DIAGNOSTIC: Attempting to add reaction...")
            try:
                await response_message.add_reaction('💬')
                logger.warning(f"✅ DIAGNOSTIC: Reaction added successfully")
            except Exception as e:
                logger.warning(f"⚠️ DIAGNOSTIC: Failed to add reaction: {e}")
            
            # Continue with escalation logic
            logger.warning(f"📧 DIAGNOSTIC: Attempting to send staff DM...")
            try:
                dm_success = await self._send_staff_dm(message, "HIGH")
                logger.warning(f"📧 DIAGNOSTIC: Staff DM result: {'✅ Success' if dm_success else '❌ Failed'}")
            except Exception as e:
                logger.error(f"❌ DIAGNOSTIC: Staff DM exception: {e}")
                dm_success = False
            
            logger.warning(f"📢 DIAGNOSTIC: Attempting to send crisis team alert...")
            try:
                alert_success = await self._send_crisis_team_alert(message, "HIGH")
                logger.warning(f"📢 DIAGNOSTIC: Crisis team alert result: {'✅ Success' if alert_success else '❌ Failed'}")
            except Exception as e:
                logger.error(f"❌ DIAGNOSTIC: Crisis team alert exception: {e}")
                alert_success = False
            
            # Enhanced logging
            logger.warning(f"✅ DIAGNOSTIC: High crisis handling completed:")
            logger.warning(f"   📧 Staff DM: {'✅ Sent' if dm_success else '❌ Failed'}")
            logger.warning(f"   📢 Team Alert: {'✅ Sent' if alert_success else '❌ Failed'}")
            logger.warning(f"   💬 Conversation instructions: ✅ Included")
            logger.warning(f"   📊 Total high crises today: {self.crisis_stats['high_crisis_count']}")
            
        except Exception as e:
            self.crisis_stats['escalation_errors'] += 1
            logger.error(f"❌ DIAGNOSTIC: Error in high crisis handling: {e}")
            logger.exception("Full traceback:")

    async def _send_staff_dm(self, message: Message, crisis_level: str) -> bool:
        """Enhanced staff DM with EXTENSIVE DIAGNOSTIC LOGGING"""
        
        logger.warning(f"📧 DIAGNOSTIC: Starting staff DM process")
        logger.warning(f"   🎯 Staff User ID: {self.staff_ping_user_id}")
        logger.warning(f"   🚨 Crisis Level: {crisis_level}")
        
        if not self.staff_ping_user_id:
            logger.error(f"❌ DIAGNOSTIC: No staff ping user ID configured!")
            return False
        
        try:
            logger.warning(f"👤 DIAGNOSTIC: Fetching staff user...")
            staff_user = await self.bot.fetch_user(self.staff_ping_user_id)
            logger.warning(f"✅ DIAGNOSTIC: Staff user fetched: {staff_user} ({staff_user.id})")
            
            # Check if we can DM this user
            logger.warning(f"💬 DIAGNOSTIC: Attempting to send DM...")
            test_message = f"🚨 URGENT: Crisis detected from {message.author.display_name} in {message.channel.mention}. Please check the crisis channel for details."
            
            await staff_user.send(test_message)
            
            self.crisis_stats['staff_dms_sent'] += 1
            logger.warning(f"✅ DIAGNOSTIC: Staff DM sent successfully to {staff_user.display_name}")
            
            return True
            
        except discord.Forbidden as e:
            logger.error(f"❌ DIAGNOSTIC: Permission denied sending staff DM: {e}")
            logger.error(f"   🔐 Staff user may have DMs disabled")
            return False
        except discord.NotFound as e:
            logger.error(f"❌ DIAGNOSTIC: Staff user not found: {e}")
            logger.error(f"   👤 User ID {self.staff_ping_user_id} may be invalid")
            return False
        except Exception as e:
            logger.error(f"❌ DIAGNOSTIC: Unexpected error sending staff DM: {e}")
            logger.exception("Full traceback:")
            return False
    
    async def _send_crisis_team_alert(self, message: Message, crisis_level: str) -> bool:
        """Enhanced crisis team alert with EXTENSIVE DIAGNOSTIC LOGGING"""
        
        logger.warning(f"📢 DIAGNOSTIC: Starting crisis team alert process")
        logger.warning(f"   📍 Crisis Channel ID: {self.crisis_response_channel_id}")
        logger.warning(f"   👥 Crisis Role ID: {self.crisis_response_role_id}")
        logger.warning(f"   🚨 Crisis Level: {crisis_level}")
        
        if not self.crisis_response_channel_id:
            logger.error(f"❌ DIAGNOSTIC: No crisis response channel ID configured!")
            return False
        
        try:
            logger.warning(f"📍 DIAGNOSTIC: Getting crisis channel...")
            crisis_channel = self.bot.get_channel(self.crisis_response_channel_id)
            
            if not crisis_channel:
                logger.error(f"❌ DIAGNOSTIC: Crisis response channel not found: {self.crisis_response_channel_id}")
                logger.error(f"   🔍 Available channels: {[c.id for c in self.bot.get_all_channels()]}")
                return False
            
            logger.warning(f"✅ DIAGNOSTIC: Crisis channel found: {crisis_channel} ({crisis_channel.id})")
            
            # Check bot permissions in crisis channel
            try:
                channel_perms = crisis_channel.permissions_for(crisis_channel.guild.me)
                logger.warning(f"🔐 DIAGNOSTIC: Bot permissions in crisis channel:")
                logger.warning(f"   📝 Send Messages: {channel_perms.send_messages}")
                logger.warning(f"   📎 Add Reactions: {channel_perms.add_reactions}")
                logger.warning(f"   📋 Embed Links: {channel_perms.embed_links}")
                logger.warning(f"   🔔 Mention Everyone: {channel_perms.mention_everyone}")
                
                if not channel_perms.send_messages:
                    logger.error(f"❌ DIAGNOSTIC: Bot cannot send messages in crisis channel!")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ DIAGNOSTIC: Failed to check crisis channel permissions: {e}")
            
            # Create simple message first (not embed to avoid complications)
            logger.warning(f"📝 DIAGNOSTIC: Creating crisis alert message...")
            
            # Build role mention
            role_mention = ""
            if self.crisis_response_role_id:
                role_mention = f"<@&{self.crisis_response_role_id}> "
                logger.warning(f"👥 DIAGNOSTIC: Role mention: {role_mention}")
            
            # Simple text message for testing
            alert_message = (
                f"{role_mention}🚨 **{crisis_level} CRISIS ALERT**\n\n"
                f"**User:** {message.author.mention} ({message.author.display_name})\n"
                f"**Channel:** {message.channel.mention}\n"
                f"**Message:** {message.content[:200]}{'...' if len(message.content) > 200 else ''}\n"
                f"**Jump:** {message.jump_url}\n\n"
                f"⚠️ Immediate attention required!"
            )
            
            logger.warning(f"📤 DIAGNOSTIC: Sending crisis alert to channel...")
            sent_message = await crisis_channel.send(alert_message)
            logger.warning(f"✅ DIAGNOSTIC: Crisis alert sent successfully (message ID: {sent_message.id})")
            
            # Try to add reaction
            try:
                await sent_message.add_reaction("🚨")
                logger.warning(f"✅ DIAGNOSTIC: Reaction added to crisis alert")
            except Exception as e:
                logger.warning(f"⚠️ DIAGNOSTIC: Failed to add reaction to crisis alert: {e}")
            
            self.crisis_stats['team_alerts_sent'] += 1
            logger.warning(f"📊 DIAGNOSTIC: Crisis team alert statistics updated")
            
            return True
            
        except discord.Forbidden as e:
            logger.error(f"❌ DIAGNOSTIC: Permission denied sending crisis team alert: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ DIAGNOSTIC: Unexpected error sending crisis team alert: {e}")
            logger.exception("Full traceback:")
            return False

    # Include medium and low crisis handlers with basic diagnostic logging
    async def _handle_medium_crisis_with_instructions(self, message: Message, enhanced_response: str):
        """Medium crisis handling with diagnostic logging"""
        
        logger.warning(f"🟡 DIAGNOSTIC: Starting MEDIUM crisis handler for {message.author}")
        
        try:
            response_message = await message.reply(enhanced_response)
            logger.warning(f"✅ DIAGNOSTIC: Medium crisis reply sent")
            
            await response_message.add_reaction('💬')
            alert_success = await self._send_crisis_team_alert(message, "MEDIUM")
            
            logger.warning(f"✅ DIAGNOSTIC: Medium crisis completed - Team Alert: {'Success' if alert_success else 'Failed'}")
            
        except Exception as e:
            self.crisis_stats['escalation_errors'] += 1
            logger.error(f"❌ DIAGNOSTIC: Error in medium crisis handling: {e}")

    async def _handle_low_crisis_with_instructions(self, message: Message, enhanced_response: str):
        """Low crisis handling with diagnostic logging"""
        
        logger.warning(f"🟢 DIAGNOSTIC: Starting LOW crisis handler for {message.author}")
        
        try:
            response_message = await message.reply(enhanced_response)
            logger.warning(f"✅ DIAGNOSTIC: Low crisis reply sent")
            
            await response_message.add_reaction('💬')
            logger.warning(f"✅ DIAGNOSTIC: Low crisis completed successfully")
            
        except Exception as e:
            self.crisis_stats['escalation_errors'] += 1
            logger.error(f"❌ DIAGNOSTIC: Error in low crisis handling: {e}")

    # Keep all your existing methods for backward compatibility
    async def handle_crisis_response(self, message: Message, crisis_level: str, ash_response: str):
        """Standard crisis response dispatcher - routes to diagnostic version"""
        logger.warning(f"🔄 DIAGNOSTIC: Routing standard crisis response to diagnostic version")
        await self.handle_crisis_response_with_instructions(message, crisis_level, ash_response)

    async def handle_high_crisis(self, message: Message, ash_response: str):
        """Standard high crisis handling - routes to diagnostic version"""
        logger.warning(f"🔄 DIAGNOSTIC: Routing standard high crisis to diagnostic version")
        await self.handle_crisis_response_with_instructions(message, 'high', ash_response)

    async def handle_medium_crisis(self, message: Message, ash_response: str):
        """Standard medium crisis handling - routes to diagnostic version"""
        logger.warning(f"🔄 DIAGNOSTIC: Routing standard medium crisis to diagnostic version")  
        await self.handle_crisis_response_with_instructions(message, 'medium', ash_response)

    async def handle_low_crisis(self, message: Message, ash_response: str):
        """Standard low crisis handling - routes to diagnostic version"""
        logger.warning(f"🔄 DIAGNOSTIC: Routing standard low crisis to diagnostic version")
        await self.handle_crisis_response_with_instructions(message, 'low', ash_response)

    def get_crisis_stats(self) -> dict:
        """Get comprehensive crisis handling statistics"""
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
            'component': 'DiagnosticCrisisHandler',
            **self.crisis_stats,
            'total_crises_today': total_crises,
            'success_rate_percent': round(success_rate, 2),
            'configuration': {
                'staff_dm_enabled': self.staff_ping_user_id is not None,
                'team_alerts_enabled': self.crisis_response_channel_id is not None,
                'crisis_role_configured': self.crisis_response_role_id is not None,
                'resources_channel_configured': self.resources_channel_id is not None
            }
        }