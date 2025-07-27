"""
Enhanced Crisis Handler with Conversation Instructions
"""

import logging
import discord
from discord import Message

logger = logging.getLogger(__name__)

class CrisisHandler:
    """Enhanced crisis escalation handler with conversation instructions"""
    
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        
        # Configuration
        self.resources_channel_id = config.get_int('RESOURCES_CHANNEL_ID')
        self.crisis_response_channel_id = config.get_int('CRISIS_RESPONSE_CHANNEL_ID')
        self.crisis_response_role_id = config.get_int('CRISIS_RESPONSE_ROLE_ID')
        self.staff_ping_user_id = config.get_int('STAFF_PING_USER')
        
        # Enhanced statistics tracking
        self.crisis_stats = {
            'high_crisis_count': 0,
            'medium_crisis_count': 0,
            'low_crisis_count': 0,
            'staff_dms_sent': 0,
            'team_alerts_sent': 0,
            'escalation_errors': 0
        }
        
        logger.info(f"🚨 Enhanced crisis handler initialized")
        logger.info(f"   📧 Staff DM user: {self.staff_ping_user_id}")
        logger.info(f"   📢 Crisis channel: {self.crisis_response_channel_id}")
        logger.info(f"   👥 Crisis role: {self.crisis_response_role_id}")
    
    async def handle_crisis_response(self, message: Message, crisis_level: str, ash_response: str):
        """
        Standard crisis response dispatcher (for backward compatibility)
        Routes to appropriate handler based on crisis level
        """
        
        # Update statistics
        self.crisis_stats[f'{crisis_level}_crisis_count'] += 1
        
        # Route to appropriate handler
        if crisis_level == 'high':
            await self.handle_high_crisis(message, ash_response)
        elif crisis_level == 'medium':
            await self.handle_medium_crisis(message, ash_response)
        else:  # low
            await self.handle_low_crisis(message, ash_response)

    async def handle_crisis_response_with_instructions(self, message: Message, crisis_level: str, ash_response: str):
        """Enhanced crisis response that includes conversation continuation instructions"""
        
        # Get configuration for whether to show instructions
        show_instructions = self.config.get_bool('CONVERSATION_SETUP_INSTRUCTIONS', True)
        
        if show_instructions:
            # Add continuation instructions to the response
            bot_mention = f"<@{self.bot.user.id}>"  # This creates @Ash mention
            continuation_instruction = (
                f"\n\n*I'll be here for the next 5 minutes if you want to continue talking. "
                f"Just mention me ({bot_mention}) or say 'Ash' to get my attention.*"
            )
            
            full_response = ash_response + continuation_instruction
        else:
            full_response = ash_response
        
        # Update statistics
        self.crisis_stats[f'{crisis_level}_crisis_count'] += 1
        
        # Use enhanced crisis handling logic with instructions
        if crisis_level == 'high':
            await self._handle_high_crisis_with_instructions(message, full_response)
        elif crisis_level == 'medium':
            await self._handle_medium_crisis_with_instructions(message, full_response)
        else:  # low
            await self._handle_low_crisis_with_instructions(message, full_response)

    async def _handle_high_crisis_with_instructions(self, message: Message, enhanced_response: str):
        """High crisis handling with conversation instructions"""
        
        logger.warning(f"🚨 HIGH CRISIS detected for {message.author} in {message.channel}")
        
        try:
            # Send enhanced Ash response with instructions
            response_message = await message.reply(enhanced_response)
            
            # Add reaction to indicate active conversation
            await response_message.add_reaction('💬')
            
            # Continue with escalation logic
            dm_success = await self._send_staff_dm(message, "HIGH")
            alert_success = await self._send_crisis_team_alert(message, "HIGH")
            
            # Enhanced logging
            logger.warning(f"✅ High crisis with conversation setup completed for {message.author}:")
            logger.warning(f"   📧 Staff DM: {'✅ Sent' if dm_success else '❌ Failed'}")
            logger.warning(f"   📢 Team Alert: {'✅ Sent' if alert_success else '❌ Failed'}")
            logger.warning(f"   💬 Conversation instructions: ✅ Included")
            
        except Exception as e:
            self.crisis_stats['escalation_errors'] += 1
            logger.error(f"❌ Error in high crisis handling with instructions: {e}")

    async def _handle_medium_crisis_with_instructions(self, message: Message, enhanced_response: str):
        """Medium crisis handling with conversation instructions"""
        
        logger.info(f"⚠️ MEDIUM CRISIS detected for {message.author} in {message.channel}")
        
        try:
            # Send enhanced Ash response with instructions
            response_message = await message.reply(enhanced_response)
            
            # Add reaction to indicate active conversation
            await response_message.add_reaction('💬')
            
            # Continue with team alert logic
            alert_success = await self._send_crisis_team_alert(message, "MEDIUM")
            
            # Enhanced logging
            logger.info(f"✅ Medium crisis with conversation setup completed for {message.author}:")
            logger.info(f"   📢 Team Alert: {'✅ Sent' if alert_success else '❌ Failed'}")
            logger.info(f"   💬 Conversation instructions: ✅ Included")
            
        except Exception as e:
            self.crisis_stats['escalation_errors'] += 1
            logger.error(f"❌ Error in medium crisis handling with instructions: {e}")

    async def _handle_low_crisis_with_instructions(self, message: Message, enhanced_response: str):
        """Low crisis handling with conversation instructions"""
        
        logger.info(f"ℹ️ LOW CRISIS support for {message.author} in {message.channel}")
        
        try:
            # Send enhanced Ash response with instructions
            response_message = await message.reply(enhanced_response)
            
            # Add reaction to indicate active conversation
            await response_message.add_reaction('💬')
            
            # Enhanced logging for trend analysis
            logger.info(f"✅ Low crisis with conversation setup completed for {message.author}")
            logger.info(f"   💬 Conversation instructions: ✅ Included")
            
        except Exception as e:
            self.crisis_stats['escalation_errors'] += 1
            logger.error(f"❌ Error in low crisis handling with instructions: {e}")

    async def handle_high_crisis(self, message: Message, ash_response: str):
        """
        Standard high crisis handling (for backward compatibility)
        - Send Ash's response
        - DM staff member directly  
        - Alert crisis team with role ping
        - Log comprehensive details
        """
        
        logger.warning(f"🚨 HIGH CRISIS detected for {message.author} in {message.channel}")
        
        try:
            # Send Ash's response first
            await message.reply(ash_response)
            
            # Send staff DM
            dm_success = await self._send_staff_dm(message, "HIGH")
            
            # Alert crisis response team
            alert_success = await self._send_crisis_team_alert(message, "HIGH")
            
            # Enhanced logging
            logger.warning(f"✅ High crisis escalation completed for {message.author}:")
            logger.warning(f"   📧 Staff DM: {'✅ Sent' if dm_success else '❌ Failed'}")
            logger.warning(f"   📢 Team Alert: {'✅ Sent' if alert_success else '❌ Failed'}")
            logger.warning(f"   📊 Total high crises today: {self.crisis_stats['high_crisis_count']}")
            
        except Exception as e:
            self.crisis_stats['escalation_errors'] += 1
            logger.error(f"❌ Error in high crisis handling: {e}")
    
    async def handle_medium_crisis(self, message: Message, ash_response: str):
        """
        Standard medium crisis handling (for backward compatibility)
        - Send Ash's response
        - Alert crisis team (no staff DM)
        - Enhanced monitoring logs
        """
        
        logger.info(f"⚠️ MEDIUM CRISIS detected for {message.author} in {message.channel}")
        
        try:
            # Send Ash's response
            await message.reply(ash_response)
            
            # Alert crisis response team (no staff DM for medium)
            alert_success = await self._send_crisis_team_alert(message, "MEDIUM")
            
            # Enhanced logging
            logger.info(f"✅ Medium crisis handling completed for {message.author}:")
            logger.info(f"   📢 Team Alert: {'✅ Sent' if alert_success else '❌ Failed'}")
            logger.info(f"   📊 Total medium crises today: {self.crisis_stats['medium_crisis_count']}")
            
        except Exception as e:
            self.crisis_stats['escalation_errors'] += 1
            logger.error(f"❌ Error in medium crisis handling: {e}")
    
    async def handle_low_crisis(self, message: Message, ash_response: str):
        """
        Standard low crisis handling (for backward compatibility)
        - Send Ash's response
        - Log for monitoring trends
        """
        
        logger.info(f"ℹ️ LOW CRISIS support for {message.author} in {message.channel}")
        
        try:
            # Send Ash's response
            await message.reply(ash_response)
            
            # Enhanced logging for trend analysis
            logger.info(f"✅ Low crisis support provided to {message.author}")
            logger.info(f"   📊 Total low crisis responses today: {self.crisis_stats['low_crisis_count']}")
            
        except Exception as e:
            self.crisis_stats['escalation_errors'] += 1
            logger.error(f"❌ Error in low crisis handling: {e}")
    
    async def _send_staff_dm(self, message: Message, crisis_level: str) -> bool:
        """Enhanced staff DM with better error handling and formatting"""
        
        try:
            staff_user = await self.bot.fetch_user(self.staff_ping_user_id)
            
            # Enhanced embed with more details
            embed = discord.Embed(
                title="🚨 Crisis Support Needed - URGENT",
                description="High-crisis keywords detected requiring immediate attention",
                color=discord.Color.red(),
                timestamp=message.created_at
            )
            
            # User information
            embed.add_field(
                name="👤 User Details", 
                value=f"**Name:** {message.author.display_name}\n"
                     f"**Mention:** {message.author.mention}\n"
                     f"**ID:** {message.author.id}", 
                inline=True
            )
            
            # Location information
            embed.add_field(
                name="📍 Location", 
                value=f"**Channel:** {message.channel.mention}\n"
                     f"**Server:** {message.guild.name}\n"
                     f"**Channel ID:** {message.channel.id}", 
                inline=True
            )
            
            # Crisis information
            embed.add_field(
                name="🚨 Crisis Details",
                value=f"**Level:** {crisis_level}\n"
                     f"**Time:** {message.created_at.strftime('%H:%M:%S')}\n"
                     f"**High Crises Today:** {self.crisis_stats['high_crisis_count']}",
                inline=True
            )
            
            # Message preview
            message_preview = message.content[:200] + "..." if len(message.content) > 200 else message.content
            embed.add_field(
                name="💬 Message Preview",
                value=f"```{message_preview}```",
                inline=False
            )
            
            # Quick action links
            embed.add_field(
                name="🔗 Quick Actions",
                value=f"[Jump to Message]({message.jump_url})\n"
                     f"[Resources Channel](<https://discord.com/channels/{message.guild.id}/{self.resources_channel_id}>)",
                inline=False
            )
            
            embed.set_footer(text="Immediate response may be needed | Ash Crisis System")
            
            await staff_user.send(embed=embed)
            
            self.crisis_stats['staff_dms_sent'] += 1
            logger.info(f"📧 Staff DM sent successfully to {staff_user.display_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending staff DM: {e}")
            return False
    
    async def _send_crisis_team_alert(self, message: Message, crisis_level: str) -> bool:
        """Enhanced crisis team alert with better formatting and quick actions"""
        
        try:
            crisis_channel = self.bot.get_channel(self.crisis_response_channel_id)
            if not crisis_channel:
                logger.error(f"Crisis response channel not found: {self.crisis_response_channel_id}")
                return False
            
            # Create enhanced embed
            color_map = {
                'HIGH': discord.Color.red(),
                'MEDIUM': discord.Color.orange(), 
                'LOW': discord.Color.yellow()
            }
            
            embed = discord.Embed(
                title=f"🚨 {crisis_level} Crisis Alert",
                description=f"Crisis detected in {message.channel.mention}",
                color=color_map.get(crisis_level, discord.Color.red()),
                timestamp=message.created_at
            )
            
            # User and location info
            embed.add_field(
                name="👤 User",
                value=f"{message.author.mention}\n"
                     f"**ID:** {message.author.id}\n"
                     f"**Name:** {message.author.display_name}",
                inline=True
            )
            
            embed.add_field(
                name="📍 Location", 
                value=f"**Channel:** {message.channel.mention}\n"
                     f"**Time:** {message.created_at.strftime('%H:%M:%S')}\n"
                     f"**Jump:** [Message Link]({message.jump_url})",
                inline=True
            )
            
            # Action needed based on crisis level
            action_map = {
                'HIGH': "🔴 **IMMEDIATE RESPONSE NEEDED**\nSuicidal ideation or severe distress detected",
                'MEDIUM': "🟡 **MONITORING REQUIRED**\nConcerning situation requiring attention", 
                'LOW': "🟢 **AWARENESS**\nMild concern, support provided"
            }
            
            embed.add_field(
                name="🎯 Required Action",
                value=action_map.get(crisis_level, "Unknown crisis level"),
                inline=False
            )
            
            # Message preview
            message_preview = message.content[:150] + "..." if len(message.content) > 150 else message.content
            embed.add_field(
                name="💬 Message",
                value=f"```{message_preview}```",
                inline=False
            )
            
            # Statistics
            total_today = sum([
                self.crisis_stats['high_crisis_count'],
                self.crisis_stats['medium_crisis_count'],
                self.crisis_stats['low_crisis_count']
            ])
            
            embed.add_field(
                name="📊 Today's Statistics",
                value=f"**Total:** {total_today}\n"
                     f"**High:** {self.crisis_stats['high_crisis_count']}\n"
                     f"**Medium:** {self.crisis_stats['medium_crisis_count']}",
                inline=True
            )
            
            # Quick links
            embed.add_field(
                name="🔗 Resources",
                value=f"[Resources Channel](<https://discord.com/channels/{message.guild.id}/{self.resources_channel_id}>)",
                inline=True
            )
            
            embed.set_footer(text=f"Crisis #{total_today} today | Ash Crisis System v2.0")
            
            # Send with role mention
            role_mention = f"<@&{self.crisis_response_role_id}>"
            sent_message = await crisis_channel.send(role_mention, embed=embed)
            
            # Add quick reaction options for team coordination
            await sent_message.add_reaction("👀")  # Monitoring
            await sent_message.add_reaction("🏃")  # Responding
            await sent_message.add_reaction("✅")  # Handled
            
            self.crisis_stats['team_alerts_sent'] += 1
            logger.info(f"📢 Enhanced {crisis_level} crisis team alert sent for {message.author}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending crisis team alert: {e}")
            return False
    
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
            'component': 'EnhancedCrisisHandler',
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