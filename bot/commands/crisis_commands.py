"""
Crisis Response Slash Commands for Ash Bot
Allows CrisisResponse role members to manage custom keywords
"""

import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CrisisKeywordCommands(commands.Cog):
    """Slash commands for managing crisis keywords - restricted to CrisisResponse role"""
    
    def __init__(self, bot):
        self.bot = bot
        self.custom_keywords_file = './data/custom_keywords.json'
        self.crisis_response_role_id = int(os.getenv('BOT_CRISIS_RESPONSE_ROLE_ID', '0'))
        
        # Ensure custom keywords file exists
        self._ensure_custom_keywords_file()
        
        # Get security manager from bot
        self.security_manager = getattr(bot, 'security_manager', None)
        if not self.security_manager:
            logger.warning("Security manager not available in crisis commands")

        # Log that commands are being registered
        logger.info(f"🔧 Registering crisis keyword commands with role ID: {self.crisis_response_role_id}")

    def _ensure_custom_keywords_file(self):
        """Create custom keywords file if it doesn't exist"""
        if not os.path.exists(self.custom_keywords_file):
            # Ensure data directory exists
            os.makedirs('./data', exist_ok=True)
            
            initial_data = {
                'high_crisis': {
                    'custom_phrases': [],
                    'last_modified': None,
                    'modified_by': None
                },
                'medium_crisis': {
                    'custom_phrases': [],
                    'last_modified': None,
                    'modified_by': None
                },
                'low_crisis': {
                    'custom_phrases': [],
                    'last_modified': None,
                    'modified_by': None
                }
            }
            with open(self.custom_keywords_file, 'w') as f:
                json.dump(initial_data, f, indent=2)
            logger.info(f"Created custom keywords file: {self.custom_keywords_file}")
    
    def _load_custom_keywords(self):
        """Load custom keywords from file"""
        try:
            with open(self.custom_keywords_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading custom keywords: {e}")
            self._ensure_custom_keywords_file()
            return self._load_custom_keywords()
    
    def _save_custom_keywords(self, data, user):
        """Save custom keywords to file with metadata"""
        try:
            # Add metadata
            timestamp = datetime.utcnow().isoformat()
            user_info = f"{user.display_name} ({user.id})"
            
            for crisis_level in data.keys():
                if crisis_level in ['high_crisis', 'medium_crisis', 'low_crisis']:
                    data[crisis_level]['last_modified'] = timestamp
                    data[crisis_level]['modified_by'] = user_info
            
            with open(self.custom_keywords_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Reload bot's keyword detector with new custom keywords
            self._reload_keyword_detector()
            
            logger.info(f"Custom keywords updated by {user_info}")
            return True
        except Exception as e:
            logger.error(f"Error saving custom keywords: {e}")
            return False
    
    def _reload_keyword_detector(self):
        """Reload the bot's keyword detector with custom keywords"""
        try:
            custom_data = self._load_custom_keywords()
            
            # Clear existing custom keywords first
            if hasattr(self.bot.keyword_detector, 'clear_custom_keywords'):
                self.bot.keyword_detector.clear_custom_keywords()
            
            # Add custom keywords to the bot's keyword detector
            for crisis_level, data in custom_data.items():
                custom_phrases = data.get('custom_phrases', [])
                if custom_phrases:
                    self.bot.keyword_detector.add_custom_keywords(
                        crisis_level.replace('_crisis', ''),  # Convert 'high_crisis' to 'high'
                        'custom_phrases',
                        custom_phrases
                    )
            
            logger.info("Keyword detector reloaded with custom keywords")
        except Exception as e:
            logger.error(f"Error reloading keyword detector: {e}")
    
    def _has_crisis_response_role(self, interaction: discord.Interaction) -> bool:
        """Check if user has CrisisResponse role"""
        if not interaction.user.roles:
            return False
        
        return any(role.id == self.crisis_response_role_id for role in interaction.user.roles)

    async def _crisis_role_check(self, interaction: discord.Interaction) -> bool:
        """Enhanced crisis role check with security logging"""
        try:
            crisis_role_id = int(os.getenv('BOT_CRISIS_RESPONSE_ROLE_ID'))
            
            # Validate user has required role using security manager
            if self.security_manager:
                has_permission = self.security_manager.validate_discord_permissions(
                    interaction.user.roles, 
                    crisis_role_id
                )
            else:
                # Fallback to basic check
                user_role_ids = [role.id for role in interaction.user.roles]
                has_permission = crisis_role_id in user_role_ids
            
            if not has_permission:
                # Log unauthorized access attempt
                if self.security_manager:
                    self.security_manager.log_security_event(
                        "unauthorized_command_access",
                        interaction.user.id,
                        interaction.guild.id,
                        interaction.channel.id,
                        {
                            "command": interaction.command.name if interaction.command else "unknown",
                            "required_role": crisis_role_id,
                            "user_roles": [role.id for role in interaction.user.roles]
                        },
                        "warning"
                    )
                
                await interaction.response.send_message(
                    "❌ You need the Crisis Response role to use this command", 
                    ephemeral=True
                )
                return False
            
            # Log successful authorization
            if self.security_manager:
                self.security_manager.log_security_event(
                    "authorized_command_access",
                    interaction.user.id,
                    interaction.guild.id,
                    interaction.channel.id,
                    {"command": interaction.command.name if interaction.command else "unknown"},
                    "info"
                )
            
            return True
            
        except (ValueError, TypeError) as e:
            logger.error(f"Role check error: {e}")
            
            # Log configuration error
            if self.security_manager:
                self.security_manager.log_security_event(
                    "role_check_config_error",
                    interaction.user.id,
                    interaction.guild.id,
                    interaction.channel.id,
                    {"error": str(e)},
                    "error"
                )
            
            await interaction.response.send_message(
                "❌ Crisis Response role not properly configured", 
                ephemeral=True
            )
            return False

    # Crisis Level choices for commands
    CRISIS_LEVELS = [
        app_commands.Choice(name="Low Crisis", value="low_crisis"),
        app_commands.Choice(name="Medium Crisis", value="medium_crisis"), 
        app_commands.Choice(name="High Crisis", value="high_crisis")
    ]

    @app_commands.command(name="add_keyword", description="Add a custom keyword/phrase to crisis detection")
    @app_commands.describe(
        crisis_level="Which crisis level to add the keyword to",
        keyword="The keyword or phrase to add (can contain spaces)"
    )
    @app_commands.choices(crisis_level=CRISIS_LEVELS)
    async def add_keyword(self, interaction: discord.Interaction, crisis_level: str, keyword: str):
        """Add a custom keyword to specified crisis level"""
        
        if not await self._crisis_role_check(interaction):
            return

        # Security validation of keyword input
        if self.security_manager:
            is_valid, validation_message = self.security_manager.validate_keyword_input(keyword)
            if not is_valid:
                await interaction.response.send_message(
                    f"❌ Invalid keyword: {validation_message}", 
                    ephemeral=True
                )
                
                # Log invalid input attempt
                self.security_manager.log_security_event(
                    "invalid_keyword_input",
                    interaction.user.id,
                    interaction.guild.id,
                    interaction.channel.id,
                    {"keyword": keyword[:20] + "..." if len(keyword) > 20 else keyword, "reason": validation_message},
                    "warning"
                )
                return
            
            # Sanitize the keyword
            keyword = self.security_manager.sanitize_user_input(keyword, max_length=100)

        # Clean and validate keyword
        keyword = keyword.strip().lower()
        if not keyword:
            embed = discord.Embed(
                title="❌ Invalid Keyword",
                description="Keyword cannot be empty.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if len(keyword) > 100:
            embed = discord.Embed(
                title="❌ Keyword Too Long",
                description="Keywords must be 100 characters or less.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Load current data
        data = self._load_custom_keywords()
        
        # Check if keyword already exists
        existing_phrases = data[crisis_level]['custom_phrases']
        if keyword in existing_phrases:
            embed = discord.Embed(
                title="⚠️ Keyword Already Exists",
                description=f"The keyword `{keyword}` is already in the {crisis_level.replace('_', ' ')} list.",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Add keyword
        data[crisis_level]['custom_phrases'].append(keyword)
        
        # Save data
        if self._save_custom_keywords(data, interaction.user):
            embed = discord.Embed(
                title="✅ Keyword Added",
                description=f"Added `{keyword}` to {crisis_level.replace('_', ' ')} detection.",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Crisis Level", 
                value=crisis_level.replace('_', ' ').title(), 
                inline=True
            )
            embed.add_field(
                name="Total Custom Keywords", 
                value=len(data[crisis_level]['custom_phrases']), 
                inline=True
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Log to bot logs
            logger.info(f"Keyword added: '{keyword}' to {crisis_level} by {interaction.user}")
        else:
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to save keyword. Please try again.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        # Log successful keyword addition
        if self.security_manager:
            self.security_manager.log_security_event(
                "keyword_added",
                interaction.user.id,
                interaction.guild.id,
                interaction.channel.id,
                {"keyword": keyword, "crisis_level": crisis_level},
                "info"
            )

    @app_commands.command(name="remove_keyword", description="Remove a custom keyword from crisis detection")
    @app_commands.describe(
        crisis_level="Which crisis level to remove the keyword from",
        keyword="The keyword or phrase to remove"
    )
    @app_commands.choices(crisis_level=CRISIS_LEVELS)
    async def remove_keyword(self, interaction: discord.Interaction, crisis_level: str, keyword: str):
        """Remove a custom keyword from specified crisis level"""
        
        if not await self._crisis_role_check(interaction):
            return
        
        keyword = keyword.strip().lower()
        
        # Load current data
        data = self._load_custom_keywords()
        existing_phrases = data[crisis_level]['custom_phrases']
        
        if keyword not in existing_phrases:
            embed = discord.Embed(
                title="❌ Keyword Not Found",
                description=f"The keyword `{keyword}` is not in the {crisis_level.replace('_', ' ')} list.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Remove keyword
        data[crisis_level]['custom_phrases'].remove(keyword)
        
        # Save data
        if self._save_custom_keywords(data, interaction.user):
            embed = discord.Embed(
                title="✅ Keyword Removed",
                description=f"Removed `{keyword}` from {crisis_level.replace('_', ' ')} detection.",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Crisis Level", 
                value=crisis_level.replace('_', ' ').title(), 
                inline=True
            )
            embed.add_field(
                name="Remaining Custom Keywords", 
                value=len(data[crisis_level]['custom_phrases']), 
                inline=True
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            logger.info(f"Keyword removed: '{keyword}' from {crisis_level} by {interaction.user}")
        else:
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to remove keyword. Please try again.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="list_keywords", description="List all custom keywords for a crisis level")
    @app_commands.describe(crisis_level="Which crisis level to list keywords for")
    @app_commands.choices(crisis_level=CRISIS_LEVELS)
    async def list_keywords(self, interaction: discord.Interaction, crisis_level: str):
        """List all custom keywords for specified crisis level"""
        
        if not await self._crisis_role_check(interaction):
            return
        
        data = self._load_custom_keywords()
        custom_phrases = data[crisis_level]['custom_phrases']
        last_modified = data[crisis_level].get('last_modified')
        modified_by = data[crisis_level].get('modified_by')
        
        embed = discord.Embed(
            title=f"🔍 Custom Keywords - {crisis_level.replace('_', ' ').title()}",
            color=discord.Color.blue()
        )
        
        if custom_phrases:
            # Split into chunks if too many keywords
            keyword_text = ", ".join(f"`{phrase}`" for phrase in sorted(custom_phrases))
            
            if len(keyword_text) > 1000:
                # Split into multiple fields if too long
                chunks = []
                current_chunk = ""
                for phrase in sorted(custom_phrases):
                    formatted_phrase = f"`{phrase}`, "
                    if len(current_chunk + formatted_phrase) > 1000:
                        chunks.append(current_chunk.rstrip(", "))
                        current_chunk = formatted_phrase
                    else:
                        current_chunk += formatted_phrase
                if current_chunk:
                    chunks.append(current_chunk.rstrip(", "))
                
                for i, chunk in enumerate(chunks):
                    field_name = "Keywords" if i == 0 else f"Keywords (cont. {i+1})"
                    embed.add_field(name=field_name, value=chunk, inline=False)
            else:
                embed.add_field(name="Keywords", value=keyword_text, inline=False)
        else:
            embed.add_field(name="Keywords", value="*No custom keywords added yet*", inline=False)
        
        embed.add_field(name="Total Count", value=len(custom_phrases), inline=True)
        
        if last_modified and modified_by:
            embed.add_field(name="Last Modified", value=f"{modified_by}\n{last_modified[:10]}", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="keyword_stats", description="Show statistics for all custom keywords")
    async def keyword_stats(self, interaction: discord.Interaction):
        """Show statistics for all custom keywords"""
        
        if not await self._crisis_role_check(interaction):
            return
        
        data = self._load_custom_keywords()
        
        embed = discord.Embed(
            title="📊 Custom Keywords Statistics",
            description="Overview of all custom crisis detection keywords",
            color=discord.Color.purple()
        )
        
        total_custom = 0
        for crisis_level, info in data.items():
            if crisis_level.endswith('_crisis'):
                count = len(info['custom_phrases'])
                total_custom += count
                
                level_name = crisis_level.replace('_', ' ').title()
                embed.add_field(
                    name=f"{level_name}",
                    value=f"{count} custom keywords",
                    inline=True
                )
        
        embed.add_field(name="Total Custom Keywords", value=total_custom, inline=False)
        
        # Get stats from bot's keyword detector if available
        if hasattr(self.bot, 'keyword_detector'):
            try:
                detector_stats = self.bot.keyword_detector.get_keyword_stats()
                embed.add_field(
                    name="Built-in Keywords",
                    value=f"High: {detector_stats.get('high_crisis', 0)}\n"
                          f"Medium: {detector_stats.get('medium_crisis', 0)}\n" 
                          f"Low: {detector_stats.get('low_crisis', 0)}",
                    inline=True
                )
                embed.add_field(
                    name="Grand Total",
                    value=f"{detector_stats.get('total', 0) + total_custom} keywords",
                    inline=True
                )
            except Exception as e:
                logger.error(f"Error getting detector stats: {e}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="security_status", description="View security manager status (Crisis Response only)")
    async def security_status(self, interaction: discord.Interaction):
        """View security status - Crisis Response role only"""
        
        if not await self._crisis_role_check(interaction):
            return
        
        if not self.security_manager:
            await interaction.response.send_message(
                "❌ Security manager not available", 
                ephemeral=True
            )
            return
        
        try:
            # Get security summary
            summary = self.security_manager.get_security_summary()
            
            embed = discord.Embed(
                title="🔐 Security Manager Status",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📊 24-Hour Activity",
                value=f"**Recent Events:** {summary['recent_events_24h']}\n"
                      f"**Total Log Entries:** {summary['audit_log_entries']}",
                inline=True
            )
            
            embed.add_field(
                name="🚨 Security Alerts",
                value=f"**Critical:** {summary['events_by_severity'].get('critical', 0)}\n"
                      f"**Error:** {summary['events_by_severity'].get('error', 0)}\n"
                      f"**Warning:** {summary['events_by_severity'].get('warning', 0)}",
                inline=True
            )
            
            embed.add_field(
                name="🔒 Access Control",
                value=f"**Locked Out Users:** {summary['locked_out_users']}\n"
                      f"**Suspicious Users:** {summary['suspicious_users']}\n"
                      f"**Failed Attempts:** {summary['total_failed_attempts']}",
                inline=True
            )
            
            # Show most common event types
            if summary['events_by_type']:
                top_events = sorted(summary['events_by_type'].items(), key=lambda x: x[1], reverse=True)[:5]
                event_list = '\n'.join([f"• {event}: {count}" for event, count in top_events])
                embed.add_field(
                    name="🎯 Top Event Types",
                    value=event_list,
                    inline=False
                )
            
            embed.set_footer(text="Security events are automatically logged and monitored")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Log security status check
            self.security_manager.log_security_event(
                "security_status_checked",
                interaction.user.id,
                interaction.guild.id,
                interaction.channel.id,
                {},
                "info"
            )
            
        except Exception as e:
            logger.error(f"Error in security_status command: {e}")
            await interaction.response.send_message(
                f"❌ Error retrieving security status: {str(e)}", 
                ephemeral=True
            )

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(CrisisKeywordCommands(bot))