#!/usr/bin/env python3
"""
Three Zero-Shot Model Ensemble Learning Commands for Ash Bot v3.0
Replaces the old individual learning system with modern ensemble approach
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional
import aiohttp

logger = logging.getLogger(__name__)

class EnsembleCommands(commands.Cog):
    """Discord commands for the Three Zero-Shot Model Ensemble learning system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.crisis_response_role_id = int(os.getenv('BOT_CRISIS_RESPONSE_ROLE_ID', '0'))
        self.nlp_client = getattr(bot, 'nlp_client', None)
        
        logger.info("🎯 Three Zero-Shot Model Ensemble commands loaded for Ash Bot v3.0")
    
    async def _check_crisis_role(self, interaction: discord.Interaction) -> bool:
        """Check if user has crisis response role"""
        if self.crisis_response_role_id == 0:
            return True  # No role restriction configured
        
        user_roles = [role.id for role in interaction.user.roles]
        if self.crisis_response_role_id not in user_roles:
            await interaction.response.send_message(
                "❌ You need the Crisis Response role to use this command",
                ephemeral=True
            )
            return False
        return True
    
    @app_commands.command(name="report_false_positive", description="Report a false positive detection for learning")
    @app_commands.describe(
        message_link="Discord message link that was incorrectly flagged",
        detected_level="Crisis level that was incorrectly detected",
        correct_level="What the correct crisis level should have been"
    )
    @app_commands.choices(
        detected_level=[
            app_commands.Choice(name="High Crisis", value="high"),
            app_commands.Choice(name="Medium Crisis", value="medium"),
            app_commands.Choice(name="Low Crisis", value="low")
        ],
        correct_level=[
            app_commands.Choice(name="None (No Crisis)", value="none"),
            app_commands.Choice(name="Low Crisis", value="low"),
            app_commands.Choice(name="Medium Crisis", value="medium")
        ]
    )
    async def report_false_positive(
        self, 
        interaction: discord.Interaction,
        message_link: str,
        detected_level: str,
        correct_level: str
    ):
        """Report a false positive detection for learning using Three Zero-Shot Model Ensemble"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        # Validate that this is actually a false positive
        level_hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        if level_hierarchy[detected_level] <= level_hierarchy[correct_level]:
            await interaction.response.send_message(
                "❌ This appears to be a false negative (missed crisis). Use `/report_missed_crisis` instead.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Extract message details from link
        try:
            message_details = await self._extract_message_from_link(message_link)
            if not message_details:
                await interaction.followup.send(
                    "❌ Could not extract message from link. Please ensure it's a valid Discord message link",
                    ephemeral=True
                )
                return
        except Exception as e:
            logger.error(f"Error extracting message: {e}")
            await interaction.followup.send("❌ Error processing message link", ephemeral=True)
            return
        
        # Send correction to ensemble NLP service
        success = await self._send_ensemble_correction(
            message_details['content'], 
            detected_level, 
            correct_level, 
            'false_positive'
        )
        
        if success:
            embed = discord.Embed(
                title="✅ False Positive Reported",
                description="Three Zero-Shot Model Ensemble system updated with your report",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="📊 Report Details",
                value=f"**Detected:** {detected_level.title()}\n**Correct:** {correct_level.title()}",
                inline=True
            )
            
            embed.add_field(
                name="🎯 Ensemble Learning",
                value="All three models will learn from this report to reduce similar false positives",
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"✅ False positive reported: {detected_level} → {correct_level}")
        else:
            await interaction.followup.send(
                "❌ Failed to send report to ensemble system. Please try again or contact an administrator.",
                ephemeral=True
            )
    
    @app_commands.command(name="report_missed_crisis", description="Report a missed crisis detection for learning")
    @app_commands.describe(
        message_link="Discord message link that should have been flagged",
        should_detect_level="Crisis level that should have been detected",
        actually_detected="What was actually detected (if anything)"
    )
    @app_commands.choices(
        should_detect_level=[
            app_commands.Choice(name="High Crisis", value="high"),
            app_commands.Choice(name="Medium Crisis", value="medium"),
            app_commands.Choice(name="Low Crisis", value="low")
        ],
        actually_detected=[
            app_commands.Choice(name="None (Not Detected)", value="none"),
            app_commands.Choice(name="Low Crisis", value="low"),
            app_commands.Choice(name="Medium Crisis", value="medium")
        ]
    )
    async def report_missed_crisis(
        self,
        interaction: discord.Interaction,
        message_link: str,
        should_detect_level: str,
        actually_detected: str = "none"
    ):
        """Report a missed crisis detection for learning using Three Zero-Shot Model Ensemble"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        # Validate that this is actually a false negative
        level_hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        if level_hierarchy[should_detect_level] <= level_hierarchy[actually_detected]:
            await interaction.response.send_message(
                "❌ This appears to be a false positive (over-detection). Use `/report_false_positive` instead.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Extract message details from link
        try:
            message_details = await self._extract_message_from_link(message_link)
            if not message_details:
                await interaction.followup.send(
                    "❌ Could not extract message from link. Please ensure it's a valid Discord message link",
                    ephemeral=True
                )
                return
        except Exception as e:
            logger.error(f"Error extracting message: {e}")
            await interaction.followup.send("❌ Error processing message link", ephemeral=True)
            return
        
        # Send correction to ensemble NLP service
        success = await self._send_ensemble_correction(
            message_details['content'], 
            actually_detected, 
            should_detect_level, 
            'false_negative'
        )
        
        if success:
            embed = discord.Embed(
                title="✅ Missed Crisis Reported",
                description="Three Zero-Shot Model Ensemble system updated with your report",
                color=discord.Color.orange()
            )
            
            embed.add_field(
                name="📊 Report Details",
                value=f"**Actually Detected:** {actually_detected.title()}\n**Should Detect:** {should_detect_level.title()}",
                inline=True
            )
            
            embed.add_field(
                name="🎯 Ensemble Learning",
                value="All three models will learn from this report to catch similar crises in the future",
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"✅ Missed crisis reported: {actually_detected} → {should_detect_level}")
        else:
            await interaction.followup.send(
                "❌ Failed to send report to ensemble system. Please try again or contact an administrator.",
                ephemeral=True
            )
    
    @app_commands.command(name="learning_ensemble_stats", description="View Three Zero-Shot Model Ensemble performance statistics")
    async def learning_ensemble_stats(self, interaction: discord.Interaction):
        """View comprehensive Three Zero-Shot Model Ensemble learning statistics"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Get ensemble statistics from NLP service
            ensemble_stats = await self._get_ensemble_stats()
            
            if not ensemble_stats:
                embed = discord.Embed(
                    title="❌ Ensemble Statistics Unavailable",
                    description="Could not retrieve ensemble statistics. This could be because:\n\n"
                               "• The NLP service is not running\n"
                               "• The NLP service doesn't support ensemble stats yet\n"
                               "• Network connectivity issues",
                    color=discord.Color.red()
                )
                
                # Add basic bot info if available
                if hasattr(self.bot, 'nlp_client'):
                    if self.bot.nlp_client:
                        embed.add_field(
                            name="🔧 Troubleshooting Info",
                            value="✅ NLP client is configured\n"
                                  "❓ Check NLP service logs for errors",
                            inline=False
                        )
                    else:
                        embed.add_field(
                            name="🔧 Troubleshooting Info", 
                            value="❌ NLP client is not initialized\n"
                                  "Check bot configuration",
                            inline=False
                        )
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            embed = discord.Embed(
                title="🎯 Three Zero-Shot Model Ensemble Statistics",
                description="Performance overview of the ensemble learning system",
                color=discord.Color.blue()
            )
            
            server_stats = ensemble_stats.get('server_stats', {})
            client_stats = ensemble_stats.get('client_stats', {})
            
            # Ensemble status
            ensemble_status = ensemble_stats.get('ensemble_status', 'unknown')
            embed.add_field(
                name="🔄 Ensemble Status",
                value=f"**Status:** {ensemble_status.title()}\n**Service:** {'Healthy' if ensemble_stats.get('service_healthy') else 'Unhealthy'}",
                inline=True
            )
            
            # Individual model status
            individual_models = server_stats.get('individual_models', {})
            if individual_models:
                model_status = []
                for model_name, model_info in individual_models.items():
                    status = "✅" if model_info.get('loaded') else "❌"
                    model_status.append(f"{status} {model_name.title()}")
                
                embed.add_field(
                    name="🤖 Individual Models",
                    value='\n'.join(model_status),
                    inline=True
                )
            
            # Ensemble method usage
            ensemble_methods = client_stats.get('ensemble_methods_used', {})
            if ensemble_methods:
                method_stats = []
                for method, count in ensemble_methods.items():
                    if count > 0:
                        method_name = method.replace('_', ' ').title()
                        method_stats.append(f"**{method_name}:** {count}")
                
                if method_stats:
                    embed.add_field(
                        name="🎯 Consensus Methods",
                        value='\n'.join(method_stats),
                        inline=True
                    )
            
            # Performance metrics
            total_requests = client_stats.get('total_requests', 0)
            successful_requests = client_stats.get('successful_requests', 0)
            gap_detections = client_stats.get('gap_detections', 0)
            
            if total_requests > 0:
                success_rate = (successful_requests / total_requests) * 100
                gap_rate = (gap_detections / total_requests) * 100
                
                embed.add_field(
                    name="📊 Performance Metrics",
                    value=f"**Total Requests:** {total_requests}\n"
                          f"**Success Rate:** {success_rate:.1f}%\n"
                          f"**Gap Detection Rate:** {gap_rate:.1f}%",
                    inline=True
                )
            
            # Gap detection info
            if gap_detections > 0:
                embed.add_field(
                    name="🔍 Gap Detection",
                    value=f"**Gaps Detected:** {gap_detections}\n"
                          f"**Staff Reviews:** {client_stats.get('staff_reviews_flagged', 0)}",
                    inline=True
                )
            
            embed.set_footer(text="Ash Bot v3.0 - Three Zero-Shot Model Ensemble System")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error getting ensemble stats: {e}")
            logger.exception("Full traceback:")
            await interaction.followup.send(
                "❌ Error retrieving ensemble statistics. Please try again or contact an administrator.",
                ephemeral=True
            )
    
    async def _extract_message_from_link(self, message_link: str) -> Optional[Dict]:
        """Extract message content and details from Discord message link"""
        try:
            # Parse Discord message link format:
            # https://discord.com/channels/GUILD_ID/CHANNEL_ID/MESSAGE_ID
            parts = message_link.split('/')
            if len(parts) < 7 or 'discord.com' not in message_link:
                return None
            
            guild_id = int(parts[-3])
            channel_id = int(parts[-2])
            message_id = int(parts[-1])
            
            # Get the guild and channel
            guild = discord.utils.get(self.bot.guilds, id=guild_id)
            if not guild:
                return None
            
            channel = guild.get_channel(channel_id)
            if not channel:
                return None
            
            # Fetch the message
            message = await channel.fetch_message(message_id)
            if not message:
                return None
            
            return {
                'content': message.content,
                'author_id': message.author.id,
                'author_name': message.author.display_name,
                'channel_id': channel_id,
                'message_id': message_id,
                'timestamp': message.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting message from link: {e}")
            return None
    
    async def _send_ensemble_correction(self, message_content: str, detected_level: str, correct_level: str, correction_type: str) -> bool:
        """Send correction to the ensemble NLP service"""
        try:
            if not self.nlp_client:
                logger.warning("No NLP client available for ensemble correction")
                return False
            
            # Use the updated nlp_integration.py method
            success = await self.nlp_client.send_staff_feedback(
                message_content, 
                correct_level, 
                detected_level, 
                correction_type
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending ensemble correction: {e}")
            return False
    
    async def _get_ensemble_stats(self) -> Optional[Dict]:
        """Get comprehensive ensemble statistics"""
        try:
            if not self.nlp_client:
                logger.warning("No NLP client available for ensemble stats")
                return None
            
            # Use the ensemble stats method from nlp_integration.py
            stats = await self.nlp_client.get_ensemble_stats()
            return stats
            
        except Exception as e:
            logger.error(f"Error getting ensemble stats: {e}")
            return None

async def setup(bot):
    """Setup function for the ensemble commands cog"""
    await bot.add_cog(EnsembleCommands(bot))
    logger.info("✅ Three Zero-Shot Model Ensemble commands cog loaded")