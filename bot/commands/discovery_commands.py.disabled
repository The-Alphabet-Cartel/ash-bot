"""
Slash Commands for Keyword Discovery Management
Extends the existing crisis_commands.py with discovery features
"""

import discord
from discord.ext import commands
import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class DiscoveryCommands(commands.Cog):
    """Slash commands for managing keyword discovery"""
    
    def __init__(self, bot):
        self.bot = bot
        
    @discord.app_commands.command(name="discovery_status", description="Check keyword discovery system status")
    @discord.app_commands.describe()
    async def discovery_status(self, interaction: discord.Interaction):
        """Check the status of the keyword discovery system"""
        
        # Check if user has the crisis response role
        if not await self._check_crisis_role(interaction):
            return
        
        try:
            if not hasattr(self.bot, 'keyword_discovery'):
                await interaction.response.send_message(
                    "❌ Keyword discovery system not initialized", 
                    ephemeral=True
                )
                return
            
            # Get discovery stats
            stats = await self.bot.keyword_discovery.discovery_service.get_discovery_stats()
            
            # Get NLP server status
            nlp_status = "Unknown"
            try:
                if hasattr(self.bot, 'nlp_client'):
                    nlp_healthy = await self.bot.nlp_client.test_connection()
                    nlp_status = "✅ Connected" if nlp_healthy else "❌ Disconnected"
                else:
                    nlp_status = "❌ No NLP client configured"
            except Exception:
                nlp_status = "❌ Connection failed"
            
            embed = discord.Embed(
                title="🔍 Keyword Discovery System Status",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="Discovery System", 
                value="✅ Enabled" if stats['discovery_enabled'] else "❌ Disabled",
                inline=True
            )
            
            embed.add_field(
                name="NLP Server",
                value=nlp_status,
                inline=True
            )
            
            embed.add_field(
                name="Today's Discoveries",
                value=f"{stats['daily_discoveries']}/{stats['max_daily']}",
                inline=True
            )
            
            embed.add_field(
                name="Min Confidence",
                value=f"{stats['min_confidence']:.2f}",
                inline=True
            )
            
            embed.add_field(
                name="NLP Server",
                value=stats['nlp_server'],
                inline=True
            )
            
            embed.add_field(
                name="Last Discovery",
                value=stats['last_discovery_date'] or "Never",
                inline=True
            )
            
            # Add pending suggestions count
            pending_count = len(getattr(self.bot.keyword_discovery, 'pending_suggestions', []))
            embed.add_field(
                name="Pending Suggestions",
                value=f"{pending_count} keywords awaiting review",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in discovery_status command: {e}")
            await interaction.response.send_message(
                f"❌ Error checking discovery status: {str(e)}", 
                ephemeral=True
            )
    
    @discord.app_commands.command(name="discovery_suggestions", description="View pending keyword suggestions from NLP analysis")
    @discord.app_commands.describe(
        crisis_level="Filter by crisis level (default: all)"
    )
    async def discovery_suggestions(
        self, 
        interaction: discord.Interaction,
        crisis_level: str = "all"
    ):
        """View and manage pending keyword suggestions"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        try:
            if not hasattr(self.bot, 'keyword_discovery'):
                await interaction.response.send_message(
                    "❌ Keyword discovery system not available", 
                    ephemeral=True
                )
                return
            
            pending = getattr(self.bot.keyword_discovery, 'pending_suggestions', [])
            
            if not pending:
                await interaction.response.send_message(
                    "📭 No pending keyword suggestions", 
                    ephemeral=True
                )
                return
            
            # Filter by crisis level if specified
            if crisis_level != "all":
                pending = [kw for kw in pending if kw.get('crisis_level') == crisis_level]
            
            # Sort by confidence (highest first)
            pending.sort(key=lambda x: x.get('confidence', 0), reverse=True)
            
            embed = discord.Embed(
                title="🔍 Pending Keyword Suggestions",
                description=f"Found {len(pending)} suggested keywords from NLP analysis",
                color=discord.Color.orange()
            )
            
            # Show top 10 suggestions
            for i, suggestion in enumerate(pending[:10]):
                urgency = "🚨 " if suggestion.get('urgent') else ""
                embed.add_field(
                    name=f"{urgency}Suggestion {i+1}: '{suggestion['keyword']}'",
                    value=f"Level: {suggestion['crisis_level'].title()}\n"
                         f"Confidence: {suggestion['confidence']:.2f}\n"
                         f"Source: {suggestion.get('source', 'unknown')}\n"
                         f"Discovered: {suggestion.get('discovered_at', 'unknown')[:10]}",
                    inline=True
                )
            
            if len(pending) > 10:
                embed.add_field(
                    name="Additional Suggestions",
                    value=f"...and {len(pending) - 10} more suggestions available",
                    inline=False
                )
            
            embed.add_field(
                name="Actions",
                value="• Use `/add_keyword` to add promising suggestions\n"
                     "• Use `/clear_suggestions` to clear reviewed suggestions\n"
                     "• Use `/discovery_details` for more info on specific keywords",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in discovery_suggestions command: {e}")
            await interaction.response.send_message(
                f"❌ Error retrieving suggestions: {str(e)}", 
                ephemeral=True
            )
    
    @discord.app_commands.command(name="discovery_details", description="Get detailed analysis for a suggested keyword")
    @discord.app_commands.describe(keyword="The keyword to get details for")
    async def discovery_details(self, interaction: discord.Interaction, keyword: str):
        """Get detailed analysis for a specific suggested keyword"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        try:
            if not hasattr(self.bot, 'keyword_discovery'):
                await interaction.response.send_message(
                    "❌ Keyword discovery system not available", 
                    ephemeral=True
                )
                return
            
            pending = getattr(self.bot.keyword_discovery, 'pending_suggestions', [])
            
            # Find the keyword
            suggestion = None
            for s in pending:
                if s['keyword'].lower() == keyword.lower():
                    suggestion = s
                    break
            
            if not suggestion:
                await interaction.response.send_message(
                    f"❌ Keyword '{keyword}' not found in pending suggestions", 
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title=f"🔍 Keyword Analysis: '{suggestion['keyword']}'",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="Crisis Level",
                value=suggestion['crisis_level'].title(),
                inline=True
            )
            
            embed.add_field(
                name="Confidence Score",
                value=f"{suggestion['confidence']:.3f}",
                inline=True
            )
            
            embed.add_field(
                name="Discovery Source",
                value=suggestion.get('source', 'unknown'),
                inline=True
            )
            
            embed.add_field(
                name="Reasoning",
                value=suggestion.get('reasoning', 'No reasoning provided')[:200] + 
                     ("..." if len(suggestion.get('reasoning', '')) > 200 else ""),
                inline=False
            )
            
            if suggestion.get('original_message'):
                embed.add_field(
                    name="Original Context",
                    value=f"```{suggestion['original_message'][:300]}```",
                    inline=False
                )
            
            embed.add_field(
                name="Discovered At",
                value=suggestion.get('discovered_at', 'unknown'),
                inline=True
            )
            
            if suggestion.get('urgent'):
                embed.add_field(
                    name="Priority",
                    value="🚨 High Priority (Manual Intervention)",
                    inline=True
                )
            
            embed.add_field(
                name="Quick Actions",
                value=f"```/add_keyword crisis_level:{suggestion['crisis_level'].title()} Crisis keyword:{suggestion['keyword']}```",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in discovery_details command: {e}")
            await interaction.response.send_message(
                f"❌ Error getting keyword details: {str(e)}", 
                ephemeral=True
            )
    
    @discord.app_commands.command(name="clear_suggestions", description="Clear reviewed keyword suggestions")
    @discord.app_commands.describe(
        clear_all="Clear all suggestions (true/false)",
        crisis_level="Clear suggestions for specific crisis level only"
    )
    async def clear_suggestions(
        self, 
        interaction: discord.Interaction,
        clear_all: bool = True,
        crisis_level: str = None
    ):
        """Clear reviewed keyword suggestions"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        try:
            if not hasattr(self.bot, 'keyword_discovery'):
                await interaction.response.send_message(
                    "❌ Keyword discovery system not available", 
                    ephemeral=True
                )
                return
            
            pending = getattr(self.bot.keyword_discovery, 'pending_suggestions', [])
            initial_count = len(pending)
            
            if crisis_level:
                # Clear only specific level
                self.bot.keyword_discovery.pending_suggestions = [
                    s for s in pending if s.get('crisis_level') != crisis_level
                ]
                cleared = initial_count - len(self.bot.keyword_discovery.pending_suggestions)
                message = f"✅ Cleared {cleared} {crisis_level} crisis suggestions"
            elif clear_all:
                # Clear all
                self.bot.keyword_discovery.pending_suggestions = []
                cleared = initial_count
                message = f"✅ Cleared all {cleared} pending suggestions"
            else:
                message = "❌ Must specify either clear_all=True or a specific crisis_level"
            
            await interaction.response.send_message(message, ephemeral=True)
            logger.info(f"Cleared {cleared if 'cleared' in locals() else 0} keyword suggestions by {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error in clear_suggestions command: {e}")
            await interaction.response.send_message(
                f"❌ Error clearing suggestions: {str(e)}", 
                ephemeral=True
            )
    
    @discord.app_commands.command(name="trigger_discovery", description="Manually trigger keyword discovery analysis")
    @discord.app_commands.describe(
        message="Message text to analyze for crisis keywords",
        crisis_level="What crisis level this message should have triggered"
    )
    async def trigger_discovery(
        self, 
        interaction: discord.Interaction, 
        message: str,
        crisis_level: str
    ):
        """Manually trigger keyword discovery on a specific message"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            if not hasattr(self.bot, 'keyword_discovery'):
                await interaction.followup.send(
                    "❌ Keyword discovery system not available", 
                    ephemeral=True
                )
                return
            
            # Trigger discovery analysis
            discovery_result = await self.bot.keyword_discovery.discovery_service.analyze_missed_crisis(
                message,
                str(interaction.user.id),
                str(interaction.channel.id)
            )
            
            if not discovery_result or not discovery_result.get('discovered_keywords'):
                await interaction.followup.send(
                    "📭 No new keywords discovered from this message", 
                    ephemeral=True
                )
                return
            
            keywords = discovery_result['discovered_keywords']
            
            embed = discord.Embed(
                title="🔍 Manual Discovery Results",
                description=f"Discovered {len(keywords)} potential keywords",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="Analyzed Message",
                value=f"```{message[:200]}{'...' if len(message) > 200 else ''}```",
                inline=False
            )
            
            for i, keyword in enumerate(keywords[:5]):
                embed.add_field(
                    name=f"Keyword {i+1}: '{keyword['keyword']}'",
                    value=f"Level: {keyword['crisis_level'].title()}\n"
                         f"Confidence: {keyword['confidence']:.2f}",
                    inline=True
                )
            
            if len(keywords) > 5:
                embed.add_field(
                    name="Additional Keywords",
                    value=f"...and {len(keywords) - 5} more discovered",
                    inline=False
                )
            
            # Add to pending suggestions
            await self.bot.keyword_discovery._handle_urgent_discoveries(keywords, interaction.channel)
            
            embed.add_field(
                name="Next Steps",
                value="Keywords added to pending suggestions. Use `/discovery_suggestions` to review.",
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in trigger_discovery command: {e}")
            await interaction.followup.send(
                f"❌ Error triggering discovery: {str(e)}", 
                ephemeral=True
            )
    
    @discord.app_commands.command(name="discovery_config", description="Configure keyword discovery settings")
    @discord.app_commands.describe(
        setting="Setting to modify",
        value="New value for the setting"
    )
    async def discovery_config(
        self, 
        interaction: discord.Interaction,
        setting: str,
        value: str
    ):
        """Configure keyword discovery system settings"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        try:
            if not hasattr(self.bot, 'keyword_discovery'):
                await interaction.response.send_message(
                    "❌ Keyword discovery system not available", 
                    ephemeral=True
                )
                return
            
            service = self.bot.keyword_discovery.discovery_service
            
            if setting == "min_confidence":
                try:
                    new_confidence = float(value)
                    if 0.0 <= new_confidence <= 1.0:
                        service.min_confidence = new_confidence
                        message = f"✅ Minimum confidence set to {new_confidence:.2f}"
                    else:
                        message = "❌ Confidence must be between 0.0 and 1.0"
                except ValueError:
                    message = "❌ Invalid confidence value. Must be a number."
                    
            elif setting == "max_daily":
                try:
                    new_max = int(value)
                    if new_max > 0:
                        service.max_daily_discoveries = new_max
                        message = f"✅ Maximum daily discoveries set to {new_max}"
                    else:
                        message = "❌ Maximum must be greater than 0"
                except ValueError:
                    message = "❌ Invalid number. Must be an integer."
                    
            elif setting == "enabled":
                if value.lower() in ['true', '1', 'yes', 'on']:
                    service.discovery_enabled = True
                    message = "✅ Keyword discovery enabled"
                elif value.lower() in ['false', '0', 'no', 'off']:
                    service.discovery_enabled = False
                    message = "✅ Keyword discovery disabled"
                else:
                    message = "❌ Value must be true/false, yes/no, or 1/0"
            else:
                message = f"❌ Unknown setting: {setting}. Valid options: min_confidence, max_daily, enabled"
            
            await interaction.response.send_message(message, ephemeral=True)
            logger.info(f"Discovery config changed by {interaction.user}: {setting} = {value}")
            
        except Exception as e:
            logger.error(f"Error in discovery_config command: {e}")
            await interaction.response.send_message(
                f"❌ Error updating config: {str(e)}", 
                ephemeral=True
            )
    
    async def _check_crisis_role(self, interaction: discord.Interaction) -> bool:
        """Check if user has crisis response role"""
        try:
            crisis_role_id = int(os.getenv('CRISIS_RESPONSE_ROLE_ID'))
            user_role_ids = [role.id for role in interaction.user.roles]
            
            if crisis_role_id not in user_role_ids:
                await interaction.response.send_message(
                    "❌ You need the Crisis Response role to use discovery commands", 
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

# Remove the autocomplete functions and choices - simplified approach
async def setup(bot):
    """Setup function for the discovery commands cog"""
    await bot.add_cog(DiscoveryCommands(bot))
    logger.info("✅ Discovery commands cog loaded")