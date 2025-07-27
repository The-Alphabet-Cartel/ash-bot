"""
False Positive Learning System - Discord Slash Commands
Fixed version with proper context dictionary handling
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

class FalsePositiveLearningCommands(commands.Cog):
    """Slash commands for reporting and learning from false positives"""
    
    def __init__(self, bot):
        self.bot = bot
        self.crisis_response_role_id = int(os.getenv('CRISIS_RESPONSE_ROLE_ID', '0'))
        self.false_positives_file = './data/false_positives.json'
        self.nlp_client = getattr(bot, 'nlp_client', None)
        
        # Ensure false positives file exists
        self._ensure_false_positives_file()
        
        logger.info("🔍 False positive learning commands loaded")
    
    def _ensure_false_positives_file(self):
        """Create false positives file if it doesn't exist"""
        if not os.path.exists(self.false_positives_file):
            os.makedirs('./data', exist_ok=True)
            
            initial_data = {
                'false_positives': [],
                'learning_patterns': {
                    'common_phrases': [],
                    'context_indicators': [],
                    'sentiment_overrides': []
                },
                'statistics': {
                    'total_reported': 0,
                    'by_crisis_level': {'high': 0, 'medium': 0, 'low': 0},
                    'most_common_errors': []
                }
            }
            
            with open(self.false_positives_file, 'w') as f:
                json.dump(initial_data, f, indent=2)
            
            logger.info(f"Created false positives data file: {self.false_positives_file}")
    
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
        correct_level="What the correct crisis level should have been",
        context="Additional context about why this was a false positive"
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
        correct_level: str,
        context: str = None
    ):
        """Report a false positive detection for learning"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        # Validate that this is actually a false positive
        if detected_level == correct_level:
            await interaction.response.send_message(
                "❌ This isn't a false positive - detected and correct levels are the same",
                ephemeral=True
            )
            return
        
        # Extract message details from link
        try:
            message_details = await self._extract_message_from_link(message_link)
            if not message_details:
                await interaction.response.send_message(
                    "❌ Could not extract message from link. Please ensure it's a valid Discord message link",
                    ephemeral=True
                )
                return
        except Exception as e:
            logger.error(f"Error extracting message: {e}")
            await interaction.response.send_message(
                "❌ Error processing message link",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Create false positive record
        false_positive_record = {
            'id': f"fp_{int(datetime.now(timezone.utc).timestamp())}",
            'type': 'false_positive',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'reported_by': {
                'user_id': interaction.user.id,
                'username': interaction.user.display_name
            },
            'message_details': message_details,
            'detection_error': {
                'detected_level': detected_level,
                'correct_level': correct_level,
                'severity_score': self._calculate_false_positive_severity(detected_level, correct_level),
                'error_type': 'over_detection'
            },
            # FIXED: Store context as dictionary instead of string
            'context': {'description': context or "No additional context provided"},
            'learning_status': 'pending'
        }
        
        # Save false positive
        self._save_false_positive(false_positive_record)
        
        # Trigger immediate learning analysis
        learning_result = await self._trigger_learning_analysis(false_positive_record)
        
        # Create response embed
        embed = discord.Embed(
            title="✅ False Positive Reported",
            description="Thank you for reporting this over-detection. The system will learn to be less sensitive.",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📊 Detection Error",
            value=f"**Detected:** {detected_level.title()}\n**Should Be:** {correct_level.title()}",
            inline=True
        )
        
        embed.add_field(
            name="🧠 Learning Analysis",
            value=f"**Status:** {learning_result['status'].title()}\n"
                  f"**Patterns Found:** {learning_result['patterns_discovered']}\n"
                  f"**Adjustments:** {learning_result['confidence_adjustments']}",
            inline=True
        )
        
        if context:
            embed.add_field(
                name="💬 Context",
                value=f"```{context[:200]}{'...' if len(context) > 200 else ''}```",
                inline=False
            )
        
        embed.set_footer(text=f"Report ID: {false_positive_record['id']}")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Log the false positive report
        logger.warning(f"False positive reported by {interaction.user}: {detected_level} → {correct_level}")
        
        # Send learning notification to NLP server if available
        if self.nlp_client:
            try:
                await self._send_learning_update_to_nlp(false_positive_record)
            except Exception as e:
                logger.error(f"Failed to send learning update to NLP server: {e}")
    
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
            
            # Get the message
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return None
            
            channel = guild.get_channel(channel_id)
            if not channel:
                return None
            
            message = await channel.fetch_message(message_id)
            if not message:
                return None
            
            return {
                'content': message.content,
                'author_id': message.author.id,
                'author_name': message.author.display_name,
                'channel_id': channel_id,
                'guild_id': guild_id,
                'message_id': message_id,
                'timestamp': message.created_at.isoformat(),
                'link': message_link
            }
            
        except Exception as e:
            logger.error(f"Error extracting message from link: {e}")
            return None
    
    def _calculate_false_positive_severity(self, detected_level: str, correct_level: str) -> int:
        """Calculate severity score for false positive (1-10, higher = worse)"""
        level_hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        
        detected_score = level_hierarchy.get(detected_level, 0)
        correct_score = level_hierarchy.get(correct_level, 0)
        
        # Higher difference = worse false positive
        difference = detected_score - correct_score
        
        if difference == 3:  # High → None
            return 10
        elif difference == 2:  # High → Low or Medium → None
            return 7
        elif difference == 1:  # Any single level difference
            return 4
        else:
            return 1
    
    def _save_false_positive(self, record: Dict):
        """Save false positive record to file"""
        try:
            with open(self.false_positives_file, 'r') as f:
                data = json.load(f)
            
            data['false_positives'].append(record)
            data['statistics']['total_reported'] += 1
            data['statistics']['by_crisis_level'][record['detection_error']['detected_level']] += 1
            
            with open(self.false_positives_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved false positive record: {record['id']}")
            
        except Exception as e:
            logger.error(f"Error saving false positive: {e}")
    
    async def _trigger_learning_analysis(self, record: Dict) -> Dict:
        """Trigger immediate learning analysis on the NLP server"""
        try:
            if not self.nlp_client:
                return {'status': 'no_nlp_server', 'patterns_discovered': 0, 'confidence_adjustments': 0}
            
            # Send to NLP server for pattern analysis
            nlp_host = os.getenv('NLP_SERVICE_HOST', '10.20.30.16')
            nlp_port = os.getenv('NLP_SERVICE_PORT', '8881')
            nlp_url = f"http://{nlp_host}:{nlp_port}/analyze_false_positive"
            
            # FIXED: Ensure context is sent as dictionary
            payload = {
                'message': record['message_details']['content'],
                'detected_level': record['detection_error']['detected_level'],
                'correct_level': record['detection_error']['correct_level'],
                'context': record['context'],  # Already a dictionary now
                'severity_score': record['detection_error']['severity_score']
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(nlp_url, json=payload, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            'status': 'success',
                            'patterns_discovered': result.get('patterns_discovered', 0),
                            'confidence_adjustments': result.get('confidence_adjustments', 0),
                            'learning_applied': result.get('learning_applied', False)
                        }
                    else:
                        logger.warning(f"NLP learning analysis failed: {response.status}")
                        return {'status': 'nlp_error', 'patterns_discovered': 0, 'confidence_adjustments': 0}
        
        except Exception as e:
            logger.error(f"Error in learning analysis: {e}")
            return {'status': 'error', 'patterns_discovered': 0, 'confidence_adjustments': 0}
    
    async def _send_learning_update_to_nlp(self, record: Dict):
        """Send learning update to NLP server for model adjustment"""
        try:
            nlp_host = os.getenv('NLP_SERVICE_HOST', '10.20.30.16')
            nlp_port = os.getenv('NLP_SERVICE_PORT', '8881')
            nlp_url = f"http://{nlp_host}:{nlp_port}/update_learning_model"
            
            # FIXED: Send proper field names and ensure context_data is dictionary
            payload = {
                'learning_record_id': record['id'],
                'record_type': record['type'],
                'message_data': record['message_details'],
                'correction_data': record['detection_error'],
                'context_data': record['context'],  # Already a dictionary now
                'timestamp': record['timestamp']
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(nlp_url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        logger.info(f"Successfully sent learning update to NLP server")
                    else:
                        logger.warning(f"NLP learning update failed: {response.status}")
        
        except Exception as e:
            logger.error(f"Error sending learning update to NLP: {e}")

    # Additional commands for statistics and management...
    @app_commands.command(name="false_positive_stats", description="View false positive statistics")
    async def false_positive_stats(self, interaction: discord.Interaction):
        """View false positive statistics"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        try:
            with open(self.false_positives_file, 'r') as f:
                data = json.load(f)
            
            stats = data['statistics']
            recent_fps = data['false_positives'][-10:]  # Last 10 reports
            
            embed = discord.Embed(
                title="📊 False Positive Statistics",
                description="Learning system performance overview",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📈 Overall Stats",
                value=f"**Total Reported:** {stats['total_reported']}\n"
                      f"**High→Other:** {stats['by_crisis_level']['high']}\n"
                      f"**Medium→Other:** {stats['by_crisis_level']['medium']}\n"
                      f"**Low→Other:** {stats['by_crisis_level']['low']}",
                inline=True
            )
            
            if recent_fps:
                recent_desc = []
                for fp in recent_fps[-5:]:  # Show last 5
                    det = fp['detection_error']['detected_level']
                    cor = fp['detection_error']['correct_level']
                    recent_desc.append(f"• {det.title()} → {cor.title()}")
                
                embed.add_field(
                    name="🔄 Recent Reports",
                    value='\n'.join(recent_desc),
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error generating false positive stats: {e}")
            await interaction.response.send_message(
                "❌ Error retrieving statistics",
                ephemeral=True
            )

async def setup(bot):
    """Setup function for the false positive learning commands cog"""
    await bot.add_cog(FalsePositiveLearningCommands(bot))
    logger.info("✅ False positive learning commands cog loaded")