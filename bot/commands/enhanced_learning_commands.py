"""
Enhanced False Positive & Negative Learning System - Discord Slash Commands
Fixed version with proper error handling and data structure validation
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
import time

logger = logging.getLogger(__name__)

class EnhancedLearningCommands(commands.Cog):
    """Slash commands for reporting and learning from both false positives AND false negatives"""
    
    def __init__(self, bot):
        self.bot = bot
        self.crisis_response_role_id = int(os.getenv('BOT_CRISIS_RESPONSE_ROLE_ID', '0'))
        self.learning_data_file = './data/learning_data.json'
        self.nlp_client = getattr(bot, 'nlp_client', None)
        
        # Ensure learning data file exists with proper structure
        self._ensure_learning_data_file()
        
        logger.info("🧠 Enhanced learning commands loaded (false positives + false negatives)")
    
    def _ensure_learning_data_file(self):
        """Create enhanced learning data file if it doesn't exist or fix incomplete structure"""
        data_exists = os.path.exists(self.learning_data_file)
        
        # Define the complete expected structure
        expected_structure = {
            'false_positives': [],
            'false_negatives': [],
            'learning_patterns': {
                'common_false_positive_phrases': [],
                'missed_crisis_patterns': [],
                'context_indicators': [],
                'sentiment_overrides': []
            },
            'statistics': {
                'total_false_positives': 0,
                'total_false_negatives': 0,
                'false_positives_by_level': {'high': 0, 'medium': 0, 'low': 0},
                'false_negatives_by_level': {'high': 0, 'medium': 0, 'low': 0},
                'learning_effectiveness': {
                    'patterns_learned': 0,
                    'adjustments_applied': 0,
                    'last_update': None
                }
            }
        }
        
        if not data_exists:
            # Create new file
            os.makedirs('./data', exist_ok=True)
            with open(self.learning_data_file, 'w') as f:
                json.dump(expected_structure, f, indent=2)
            logger.info(f"Created enhanced learning data file: {self.learning_data_file}")
        else:
            # Check and fix existing file structure
            try:
                with open(self.learning_data_file, 'r') as f:
                    existing_data = json.load(f)
                
                # Check if structure needs updating
                needs_update = False
                
                # Ensure all main keys exist
                for key in expected_structure:
                    if key not in existing_data:
                        existing_data[key] = expected_structure[key]
                        needs_update = True
                
                # Ensure statistics structure is complete
                if 'statistics' in existing_data:
                    stats = existing_data['statistics']
                    expected_stats = expected_structure['statistics']
                    
                    for key in expected_stats:
                        if key not in stats:
                            stats[key] = expected_stats[key]
                            needs_update = True
                    
                    # Ensure learning_effectiveness is complete
                    if 'learning_effectiveness' in stats:
                        le = stats['learning_effectiveness']
                        expected_le = expected_stats['learning_effectiveness']
                        
                        for key in expected_le:
                            if key not in le:
                                le[key] = expected_le[key]
                                needs_update = True
                    else:
                        stats['learning_effectiveness'] = expected_stats['learning_effectiveness']
                        needs_update = True
                
                # Save updated structure if needed
                if needs_update:
                    with open(self.learning_data_file, 'w') as f:
                        json.dump(existing_data, f, indent=2)
                    logger.info("Updated learning data file structure to include missing fields")
                
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error reading existing learning data file: {e}")
                # Backup and recreate
                if os.path.exists(self.learning_data_file):
                    backup_name = f"{self.learning_data_file}.backup_{int(datetime.now().timestamp())}"
                    os.rename(self.learning_data_file, backup_name)
                    logger.info(f"Backed up corrupt file to: {backup_name}")
                
                with open(self.learning_data_file, 'w') as f:
                    json.dump(expected_structure, f, indent=2)
                logger.info("Recreated learning data file with proper structure")
    
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
    
    @app_commands.command(name="learning_stats", description="View comprehensive learning system statistics")
    async def learning_stats(self, interaction: discord.Interaction):
        """View comprehensive learning system statistics - NEW ENHANCED VERSION"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        try:
            with open(self.learning_data_file, 'r') as f:
                data = json.load(f)
            
            stats = data.get('statistics', {})
            recent_fps = data.get('false_positives', [])[-10:]  # Last 10 false positives
            recent_fns = data.get('false_negatives', [])[-10:]   # Last 10 false negatives
            
            embed = discord.Embed(
                title="📊 Enhanced Learning Statistics",
                description="Comprehensive learning system performance overview",
                color=discord.Color.purple()
            )
            
            # Overall statistics with safe access
            learning_eff = stats.get('learning_effectiveness', {})
            embed.add_field(
                name="📈 Overall Performance",
                value=f"**False Positives:** {stats.get('total_false_positives', 0)}\n"
                      f"**False Negatives:** {stats.get('total_false_negatives', 0)}\n"
                      f"**Learning Updates:** {learning_eff.get('adjustments_applied', 0)}\n"
                      f"**Patterns Learned:** {learning_eff.get('patterns_learned', 0)}",
                inline=True
            )
            
            # False positive breakdown with safe access
            fp_stats = stats.get('false_positives_by_level', {'high': 0, 'medium': 0, 'low': 0})
            embed.add_field(
                name="🔴 False Positives",
                value=f"**High→Other:** {fp_stats.get('high', 0)}\n"
                      f"**Medium→Other:** {fp_stats.get('medium', 0)}\n"
                      f"**Low→Other:** {fp_stats.get('low', 0)}",
                inline=True
            )
            
            # False negative breakdown with safe access
            fn_stats = stats.get('false_negatives_by_level', {'high': 0, 'medium': 0, 'low': 0})
            embed.add_field(
                name="🟡 False Negatives", 
                value=f"**Missed High:** {fn_stats.get('high', 0)}\n"
                      f"**Missed Medium:** {fn_stats.get('medium', 0)}\n"
                      f"**Missed Low:** {fn_stats.get('low', 0)}",
                inline=True
            )
            
            # Recent activity with safe access
            if recent_fps or recent_fns:
                recent_activity = []
                
                # Combine and sort recent reports by timestamp
                all_recent = []
                for fp in recent_fps[-5:]:
                    if 'timestamp' in fp and 'detection_error' in fp:
                        all_recent.append((fp['timestamp'], 'FP', fp['detection_error']))
                for fn in recent_fns[-5:]:
                    if 'timestamp' in fn and 'detection_error' in fn:
                        all_recent.append((fn['timestamp'], 'FN', fn['detection_error']))
                
                all_recent.sort(key=lambda x: x[0], reverse=True)
                
                for timestamp, report_type, error in all_recent[:5]:
                    try:
                        if report_type == 'FP':
                            detected = error.get('detected_level', 'unknown').title()
                            correct = error.get('correct_level', 'unknown').title()
                            desc = f"🔴 {detected} → {correct}"
                        else:  # FN
                            actually = error.get('actually_detected', 'unknown').title()
                            should = error.get('should_detect_level', 'unknown').title()
                            desc = f"🟡 {actually} → {should}"
                        recent_activity.append(desc)
                    except (KeyError, AttributeError):
                        continue  # Skip malformed entries
                
                if recent_activity:
                    embed.add_field(
                        name="🔄 Recent Reports",
                        value='\n'.join(recent_activity),
                        inline=False
                    )
            
            # Learning effectiveness with safe access
            last_update = learning_eff.get('last_update')
            if last_update:
                embed.add_field(
                    name="🧠 Learning Status",
                    value=f"**Last Update:** {last_update[:10] if len(last_update) >= 10 else last_update}\n"
                          f"**System Status:** {'Active' if learning_eff.get('adjustments_applied', 0) > 0 else 'Initializing'}",
                    inline=False
                )
            else:
                embed.add_field(
                    name="🧠 Learning Status",
                    value="**System Status:** Initializing\n**Last Update:** Never",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except FileNotFoundError:
            logger.error("Learning data file not found")
            await interaction.response.send_message(
                "❌ Learning data file not found. Please contact an administrator.",
                ephemeral=True
            )
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing learning data file: {e}")
            await interaction.response.send_message(
                "❌ Learning data file is corrupted. Please contact an administrator.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error generating learning stats: {e}")
            await interaction.response.send_message(
                "❌ Error retrieving statistics. Please try again or contact an administrator.",
                ephemeral=True
            )

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
        """Report a false positive detection for learning (EXISTING - Enhanced)"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        # Validate that this is actually a false positive
        if detected_level == correct_level:
            await interaction.response.send_message(
                "❌ This isn't a false positive - detected and correct levels are the same",
                ephemeral=True
            )
            return
        
        # Validate that detected level is higher than correct (true false positive)
        level_hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        if level_hierarchy[detected_level] <= level_hierarchy[correct_level]:
            await interaction.response.send_message(
                "❌ This appears to be a false negative (missed crisis). Use `/report_missed_crisis` instead.",
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
        self._save_learning_record(false_positive_record, 'false_positive')
        
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
    
    @app_commands.command(name="report_missed_crisis", description="Report a missed crisis detection for learning (False Negative)")
    @app_commands.describe(
        message_link="Discord message link that should have been flagged",
        should_detect_level="Crisis level that should have been detected",
        actually_detected="What was actually detected (if anything)",
        context="Additional context about why this should have been detected"
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
        actually_detected: str = "none",
        context: str = None
    ):
        """Report a missed crisis detection for learning (False Negative) - NEW FEATURE"""
        
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
        
        # Create false negative record
        false_negative_record = {
            'id': f"fn_{int(datetime.now(timezone.utc).timestamp())}",
            'type': 'false_negative',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'reported_by': {
                'user_id': interaction.user.id,
                'username': interaction.user.display_name
            },
            'message_details': message_details,
            'detection_error': {
                'should_detect_level': should_detect_level,
                'actually_detected': actually_detected,
                'severity_score': self._calculate_false_negative_severity(should_detect_level, actually_detected),
                'error_type': 'under_detection'
            },
            # FIXED: Store context as dictionary instead of string
            'context': {'description': context or "No additional context provided"},
            'learning_status': 'pending'
        }
        
        # Save false negative
        self._save_learning_record(false_negative_record, 'false_negative')
        
        # Trigger immediate learning analysis
        learning_result = await self._trigger_learning_analysis(false_negative_record)
        
        # Create response embed
        embed = discord.Embed(
            title="✅ Missed Crisis Reported",
            description="Thank you for reporting this under-detection. The system will learn to be more sensitive.",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="📊 Detection Error",
            value=f"**Should Detect:** {should_detect_level.title()}\n**Actually Got:** {actually_detected.title()}",
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
        
        embed.set_footer(text=f"Report ID: {false_negative_record['id']}")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Log the false negative report
        logger.warning(f"False negative reported by {interaction.user}: {actually_detected} → {should_detect_level}")
        
        # Send learning notification to NLP server if available
        if self.nlp_client:
            try:
                await self._send_learning_update_to_nlp(false_negative_record)
            except Exception as e:
                logger.error(f"Failed to send learning update to NLP server: {e}")
    
    async def _extract_message_from_link(self, message_link: str) -> Optional[Dict]:
        """Extract message content and details from Discord message link"""
        try:
            # Parse Discord message link format:
            # https://discord.com/channels/BOT_GUILD_ID/CHANNEL_ID/MESSAGE_ID
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
    
    def _calculate_false_negative_severity(self, should_detect: str, actually_detected: str) -> int:
        """Calculate severity score for false negative (1-10, higher = worse)"""
        level_hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        
        should_score = level_hierarchy.get(should_detect, 0)
        actual_score = level_hierarchy.get(actually_detected, 0)
        
        # Higher missed level = worse false negative
        difference = should_score - actual_score
        
        if difference == 3:  # None → High (completely missed high crisis)
            return 10
        elif difference == 2:  # Low → High or None → Medium
            return 7
        elif difference == 1:  # Any single level missed
            return 4
        else:
            return 1
    
    def _save_learning_record(self, record: Dict, record_type: str):
        """Save learning record to file"""
        try:
            with open(self.learning_data_file, 'r') as f:
                data = json.load(f)
            
            if record_type == 'false_positive':
                data['false_positives'].append(record)
                data['statistics']['total_false_positives'] += 1
                data['statistics']['false_positives_by_level'][record['detection_error']['detected_level']] += 1
            elif record_type == 'false_negative':
                data['false_negatives'].append(record)
                data['statistics']['total_false_negatives'] += 1
                data['statistics']['false_negatives_by_level'][record['detection_error']['should_detect_level']] += 1
            
            with open(self.learning_data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {record_type} record: {record['id']}")
            
        except Exception as e:
            logger.error(f"Error saving {record_type}: {e}")
    
    async def _trigger_learning_analysis(self, record: Dict) -> Dict:
        """Trigger immediate learning analysis on the NLP server"""
        try:
            if not self.nlp_client:
                return {'status': 'no_nlp_server', 'patterns_discovered': 0, 'confidence_adjustments': 0}
            
            # Send to NLP server for pattern analysis
            nlp_host = os.getenv('GLOBAL_NLP_API_HOST', '10.20.30.253')
            nlp_port = os.getenv('GLOBAL_NLP_API_PORT', '8881')
            
            # Choose endpoint based on record type
            if record['type'] == 'false_positive':
                endpoint = "/analyze_false_positive"
                # FIXED: Context is already a dictionary now
                payload = {
                    'message': record['message_details']['content'],
                    'detected_level': record['detection_error']['detected_level'],
                    'correct_level': record['detection_error']['correct_level'],
                    'context': record['context'],  # Already a dictionary
                    'severity_score': record['detection_error']['severity_score']
                }
            else:  # false_negative
                endpoint = "/analyze_false_negative"
                # FIXED: Context is already a dictionary now
                payload = {
                    'message': record['message_details']['content'],
                    'should_detect_level': record['detection_error']['should_detect_level'],
                    'actually_detected': record['detection_error']['actually_detected'],
                    'context': record['context'],  # Already a dictionary
                    'severity_score': record['detection_error']['severity_score']
                }
            
            nlp_url = f"http://{nlp_host}:{nlp_port}{endpoint}"
            
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
            nlp_host = os.getenv('GLOBAL_NLP_API_HOST', '10.20.30.253')
            nlp_port = os.getenv('GLOBAL_NLP_API_PORT', '8881')
            nlp_url = f"http://{nlp_host}:{nlp_port}/update_learning_model"
            
            # FIXED: Context is already a dictionary, and using proper field names
            payload = {
                'learning_record_id': record['id'],
                'record_type': record['type'],
                'message_data': record['message_details'],
                'correction_data': record['detection_error'],
                'context_data': record['context'],  # Already a dictionary
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
    
    @app_commands.command(name="learning_stats", description="View comprehensive learning system statistics")
    async def learning_stats(self, interaction: discord.Interaction):
        """View comprehensive learning system statistics - NEW ENHANCED VERSION"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        try:
            with open(self.learning_data_file, 'r') as f:
                data = json.load(f)
            
            stats = data['statistics']
            recent_fps = data['false_positives'][-10:]  # Last 10 false positives
            recent_fns = data['false_negatives'][-10:]   # Last 10 false negatives
            
            embed = discord.Embed(
                title="📊 Enhanced Learning Statistics",
                description="Comprehensive learning system performance overview",
                color=discord.Color.purple()
            )
            
            # Overall statistics
            embed.add_field(
                name="📈 Overall Performance",
                value=f"**False Positives:** {stats['total_false_positives']}\n"
                      f"**False Negatives:** {stats['total_false_negatives']}\n"
                      f"**Learning Updates:** {stats['learning_effectiveness']['adjustments_applied']}\n"
                      f"**Patterns Learned:** {stats['learning_effectiveness']['patterns_learned']}",
                inline=True
            )
            
            # False positive breakdown
            fp_stats = stats['false_positives_by_level']
            embed.add_field(
                name="🔴 False Positives",
                value=f"**High→Other:** {fp_stats['high']}\n"
                      f"**Medium→Other:** {fp_stats['medium']}\n"
                      f"**Low→Other:** {fp_stats['low']}",
                inline=True
            )
            
            # False negative breakdown  
            fn_stats = stats['false_negatives_by_level']
            embed.add_field(
                name="🟡 False Negatives", 
                value=f"**Missed High:** {fn_stats['high']}\n"
                      f"**Missed Medium:** {fn_stats['medium']}\n"
                      f"**Missed Low:** {fn_stats['low']}",
                inline=True
            )
            
            # Recent activity
            if recent_fps or recent_fns:
                recent_activity = []
                
                # Combine and sort recent reports by timestamp
                all_recent = []
                for fp in recent_fps[-5:]:
                    all_recent.append((fp['timestamp'], 'FP', fp['detection_error']))
                for fn in recent_fns[-5:]:
                    all_recent.append((fn['timestamp'], 'FN', fn['detection_error']))
                
                all_recent.sort(key=lambda x: x[0], reverse=True)
                
                for timestamp, report_type, error in all_recent[:5]:
                    if report_type == 'FP':
                        desc = f"🔴 {error['detected_level'].title()} → {error['correct_level'].title()}"
                    else:  # FN
                        desc = f"🟡 {error['actually_detected'].title()} → {error['should_detect_level'].title()}"
                    recent_activity.append(desc)
                
                embed.add_field(
                    name="🔄 Recent Reports",
                    value='\n'.join(recent_activity),
                    inline=False
                )
            
            # Learning effectiveness
            if stats['learning_effectiveness']['last_update']:
                embed.add_field(
                    name="🧠 Learning Status",
                    value=f"**Last Update:** {stats['learning_effectiveness']['last_update'][:10]}\n"
                          f"**System Status:** {'Active' if stats['learning_effectiveness']['adjustments_applied'] > 0 else 'Initializing'}",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error generating learning stats: {e}")
            await interaction.response.send_message(
                "❌ Error retrieving statistics",
                ephemeral=True
            )

    @app_commands.command(name="fp_correction", description="Quick false positive correction (three-model ensemble)")
    @app_commands.describe(
        message="The message that was incorrectly flagged as crisis",
        correct_level="What the crisis level should have been (none, low, medium, high)",
        reason="Optional reason for the correction"
    )
    async def false_positive_correction(
        self, 
        interaction: discord.Interaction, 
        message: str, 
        correct_level: str,
        reason: Optional[str] = None
    ):
        """Quick false positive correction for three-model ensemble"""
        
        if not await self._check_crisis_role(interaction):
            return
            
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Validate correct_level
            valid_levels = ['none', 'low', 'medium', 'high']
            if correct_level.lower() not in valid_levels:
                await interaction.followup.send(
                    f"❌ Invalid crisis level. Must be one of: {', '.join(valid_levels)}",
                    ephemeral=True
                )
                return
            
            # Get current detection for comparison
            detected_level = await self._get_current_detection(message)
            
            if detected_level is None:
                await interaction.followup.send(
                    "❌ Could not analyze the provided message. Please check the NLP service.",
                    ephemeral=True
                )
                return
            
            # Send learning feedback to NLP service
            success = await self._send_false_positive_feedback(
                message, 
                detected_level, 
                correct_level.lower(),
                {
                    "staff_user": str(interaction.user.id),
                    "staff_name": interaction.user.display_name,
                    "reason": reason,
                    "timestamp": time.time(),
                    "source": "fp_correction_command"
                }
            )
            
            if success:
                # Create success embed
                embed = discord.Embed(
                    title="✅ False Positive Correction Submitted",
                    description="Thank you for improving the three-model ensemble system!",
                    color=discord.Color.green()
                )
                
                embed.add_field(
                    name="📝 Message",
                    value=f"```{message[:500]}{'...' if len(message) > 500 else ''}```",
                    inline=False
                )
                
                embed.add_field(
                    name="🔄 Correction Details",
                    value=f"**Previously Detected:** {detected_level}\n"
                          f"**Should Be:** {correct_level.lower()}\n"
                          f"**Correction Type:** False Positive (over-detection)",
                    inline=False
                )
                
                if reason:
                    embed.add_field(
                        name="💭 Reason",
                        value=reason,
                        inline=False
                    )
                
                embed.add_field(
                    name="🧠 Three-Model Learning Impact",
                    value="• Depression model sensitivity may be reduced\n"
                          "• Emotional distress patterns will be refined\n"
                          "• Sentiment context analysis improved\n"
                          "• Ensemble consensus logic enhanced",
                    inline=False
                )
                
                embed.set_footer(text=f"Correction by {interaction.user.display_name} • Three-Model Ensemble Learning")
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                
                logger.info(f"✅ FP correction submitted by {interaction.user.display_name}: "
                           f"'{message[:50]}...' {detected_level} → {correct_level}")
                
            else:
                await interaction.followup.send(
                    "❌ Failed to submit correction to learning system. Please try again later.",
                    ephemeral=True
                )
            
        except Exception as e:
            logger.error(f"❌ Error in false positive correction: {e}")
            await interaction.followup.send(
                f"❌ An error occurred while processing the correction: {str(e)}",
                ephemeral=True
            )

    @app_commands.command(name="fn_correction", description="Quick false negative correction (three-model ensemble)")
    @app_commands.describe(
        message="The message that should have been detected as crisis",
        should_be_level="What the crisis level should have been (low, medium, high)",
        reason="Optional reason for the correction"
    )
    async def false_negative_correction(
        self, 
        interaction: discord.Interaction, 
        message: str, 
        should_be_level: str,
        reason: Optional[str] = None
    ):
        """Quick false negative correction for three-model ensemble"""
        
        if not await self._check_crisis_role(interaction):
            return
            
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Validate should_be_level
            valid_levels = ['low', 'medium', 'high']
            if should_be_level.lower() not in valid_levels:
                await interaction.followup.send(
                    f"❌ Invalid crisis level. Must be one of: {', '.join(valid_levels)}",
                    ephemeral=True
                )
                return
            
            # Get current detection for comparison
            actually_detected = await self._get_current_detection(message)
            
            if actually_detected is None:
                await interaction.followup.send(
                    "❌ Could not analyze the provided message. Please check the NLP service.",
                    ephemeral=True
                )
                return
            
            # Send learning feedback to NLP service
            success = await self._send_false_negative_feedback(
                message, 
                should_be_level.lower(), 
                actually_detected,
                {
                    "staff_user": str(interaction.user.id),
                    "staff_name": interaction.user.display_name,
                    "reason": reason,
                    "timestamp": time.time(),
                    "source": "fn_correction_command"
                }
            )
            
            if success:
                # Create success embed
                embed = discord.Embed(
                    title="✅ False Negative Correction Submitted",
                    description="Thank you for improving the three-model ensemble system!",
                    color=discord.Color.blue()
                )
                
                embed.add_field(
                    name="📝 Message",
                    value=f"```{message[:500]}{'...' if len(message) > 500 else ''}```",
                    inline=False
                )
                
                embed.add_field(
                    name="🔄 Correction Details",
                    value=f"**Actually Detected:** {actually_detected}\n"
                          f"**Should Have Been:** {should_be_level.lower()}\n"
                          f"**Correction Type:** False Negative (under-detection)",
                    inline=False
                )
                
                if reason:
                    embed.add_field(
                        name="💭 Reason",
                        value=reason,
                        inline=False
                    )
                
                embed.add_field(
                    name="🧠 Three-Model Learning Impact",
                    value="• Depression model sensitivity may be increased\n"
                          "• Emotional distress detection enhanced\n"
                          "• Sentiment analysis context improved\n"
                          "• Ensemble gap detection refined",
                    inline=False
                )
                
                embed.set_footer(text=f"Correction by {interaction.user.display_name} • Three-Model Ensemble Learning")
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                
                logger.info(f"✅ FN correction submitted by {interaction.user.display_name}: "
                           f"'{message[:50]}...' {actually_detected} → {should_be_level}")
                
            else:
                await interaction.followup.send(
                    "❌ Failed to submit correction to learning system. Please try again later.",
                    ephemeral=True
                )
            
        except Exception as e:
            logger.error(f"❌ Error in false negative correction: {e}")
            await interaction.followup.send(
                f"❌ An error occurred while processing the correction: {str(e)}",
                ephemeral=True
            )

    @app_commands.command(name="ensemble_stats", description="View three-model ensemble performance statistics")
    async def ensemble_statistics(self, interaction: discord.Interaction):
        """Display comprehensive ensemble system statistics"""
        
        if not await self._check_crisis_role(interaction):
            return
            
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Get stats from NLP client
            nlp_stats = {}
            if hasattr(self.bot, 'nlp_client') and self.bot.nlp_client:
                if hasattr(self.bot.nlp_client, 'get_ensemble_stats'):
                    nlp_stats = await self.bot.nlp_client.get_ensemble_stats()
                else:
                    nlp_stats = {'client_stats': getattr(self.bot.nlp_client, 'stats', {})}
            
            # Get stats from message handler
            handler_stats = {}
            if hasattr(self.bot, 'message_handler') and self.bot.message_handler:
                if hasattr(self.bot.message_handler, 'get_enhanced_stats'):
                    handler_stats = self.bot.message_handler.get_enhanced_stats()
                else:
                    handler_stats = getattr(self.bot.message_handler, 'message_stats', {})
            
            # Create comprehensive stats embed
            embed = discord.Embed(
                title="📊 Three-Model Ensemble Statistics",
                description="Performance metrics for the crisis detection system",
                color=discord.Color.purple()
            )
            
            # Ensemble performance
            client_stats = nlp_stats.get('client_stats', {})
            if client_stats:
                total_requests = client_stats.get('total_requests', 0)
                successful_requests = client_stats.get('successful_requests', 0)
                success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
                
                embed.add_field(
                    name="🎯 Ensemble Performance",
                    value=f"**Total Requests:** {total_requests:,}\n"
                          f"**Success Rate:** {success_rate:.1f}%\n"
                          f"**Gap Detections:** {client_stats.get('gap_detections', 0):,}\n"
                          f"**Staff Reviews Flagged:** {client_stats.get('staff_reviews_flagged', 0):,}",
                    inline=True
                )
            
            # Ensemble methods breakdown
            ensemble_methods = client_stats.get('ensemble_methods_used', {})
            if ensemble_methods:
                methods_text = ""
                for method, count in ensemble_methods.items():
                    methods_text += f"**{method.replace('_', ' ').title()}:** {count:,}\n"
                
                embed.add_field(
                    name="🔄 Ensemble Methods Used",
                    value=methods_text,
                    inline=True
                )
            
            # Detection method breakdown from handler
            detection_breakdown = handler_stats.get('detection_method_breakdown', {})
            if detection_breakdown:
                breakdown_text = ""
                total_detections = sum(detection_breakdown.values())
                for method, count in detection_breakdown.items():
                    if count > 0:
                        percentage = (count / total_detections * 100) if total_detections > 0 else 0
                        breakdown_text += f"**{method.replace('_', ' ').title()}:** {count:,} ({percentage:.1f}%)\n"
                
                if breakdown_text:
                    embed.add_field(
                        name="🔍 Detection Methods",
                        value=breakdown_text,
                        inline=False
                    )
            
            # Gap detection rates
            if handler_stats:
                gap_rate = handler_stats.get('gap_detection_rate', 0) * 100
                review_rate = handler_stats.get('staff_review_rate', 0) * 100
                consensus_rate = handler_stats.get('unanimous_consensus_rate', 0) * 100
                
                embed.add_field(
                    name="📈 Detection Quality Metrics",
                    value=f"**Gap Detection Rate:** {gap_rate:.1f}%\n"
                          f"**Staff Review Rate:** {review_rate:.1f}%\n"
                          f"**Unanimous Consensus Rate:** {consensus_rate:.1f}%",
                    inline=True
                )
            
            # Service health
            service_healthy = nlp_stats.get('service_healthy', False)
            ensemble_status = nlp_stats.get('ensemble_status', 'unknown')
            
            embed.add_field(
                name="🏥 Service Health",
                value=f"**NLP Service:** {'✅ Healthy' if service_healthy else '❌ Unhealthy'}\n"
                      f"**Ensemble Status:** {ensemble_status.title()}\n"
                      f"**Three Models:** {'✅ Active' if client_stats else '⚠️ Unknown'}",
                inline=True
            )
            
            embed.set_footer(text="Three-Model Ensemble • Real-time Statistics")
            embed.timestamp = discord.utils.utcnow()
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"❌ Error getting ensemble stats: {e}")
            await interaction.followup.send(
                f"❌ Error retrieving statistics: {str(e)}",
                ephemeral=True
            )

    @app_commands.command(name="test_ensemble", description="Test the three-model ensemble with a sample message")
    @app_commands.describe(
        message="Test message to analyze with the ensemble",
        show_details="Whether to show detailed model breakdown"
    )
    async def test_ensemble_analysis(
        self, 
        interaction: discord.Interaction, 
        message: str,
        show_details: bool = True
    ):
        """Test ensemble analysis on a sample message"""
        
        if not await self._check_crisis_role(interaction):
            return
            
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Get ensemble analysis
            if not hasattr(self.bot, 'nlp_client') or not self.bot.nlp_client:
                await interaction.followup.send(
                    "❌ NLP client not available",
                    ephemeral=True
                )
                return
            
            result = await self.bot.nlp_client.analyze_message(
                message,
                str(interaction.user.id),
                str(interaction.channel_id)
            )
            
            if not result:
                await interaction.followup.send(
                    "❌ No result from ensemble analysis",
                    ephemeral=True
                )
                return
            
            # Create analysis embed
            embed = discord.Embed(
                title="🧪 Three-Model Ensemble Test",
                description=f"Analysis of: `{message[:100]}{'...' if len(message) > 100 else ''}`",
                color=discord.Color.blue()
            )
            
            # Final result
            embed.add_field(
                name="⚡ Final Result",
                value=f"**Crisis Level:** {result.get('crisis_level', 'unknown')}\n"
                      f"**Confidence:** {result.get('confidence_score', 0):.2%}\n"
                      f"**Needs Response:** {'Yes' if result.get('needs_response') else 'No'}\n"
                      f"**Method:** {result.get('method', 'unknown')}",
                inline=False
            )
            
            # Gap detection
            if result.get('gap_detected'):
                gap_details = result.get('gap_details', [])
                embed.add_field(
                    name="🔍 Gap Detection",
                    value=f"**Gaps Detected:** {len(gap_details)}\n"
                          f"**Staff Review Required:** {'Yes' if result.get('requires_staff_review') else 'No'}",
                    inline=True
                )
            
            # Model breakdown if requested and available
            if show_details and result.get('model_breakdown'):
                model_breakdown = result.get('model_breakdown')
                breakdown_text = ""
                
                for model_name, model_data in model_breakdown.items():
                    prediction = model_data.get('prediction', 'unknown')
                    confidence = model_data.get('confidence', 0)
                    breakdown_text += f"**{model_name.title()}:** {prediction} ({confidence:.2%})\n"
                
                embed.add_field(
                    name="🎯 Individual Model Results",
                    value=breakdown_text,
                    inline=True
                )
            
            # Processing info
            processing_time = result.get('processing_time_ms', 0)
            embed.add_field(
                name="⏱️ Performance",
                value=f"**Processing Time:** {processing_time:.1f}ms",
                inline=True
            )
            
            embed.set_footer(text=f"Test by {interaction.user.display_name} • Three-Model Ensemble")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"❌ Error in ensemble test: {e}")
            await interaction.followup.send(
                f"❌ Error testing ensemble: {str(e)}",
                ephemeral=True
            )

    # ADD THESE HELPER METHODS:

    async def _get_current_detection(self, message: str) -> Optional[str]:
        """Get current detection level for a message"""
        try:
            if hasattr(self.bot, 'nlp_client') and self.bot.nlp_client:
                result = await self.bot.nlp_client.analyze_message(message)
                if result:
                    return result.get('crisis_level', 'none')
            return None
        except Exception as e:
            logger.error(f"Error getting current detection: {e}")
            return None

    async def _send_false_positive_feedback(self, message: str, detected_level: str, correct_level: str, context: Dict) -> bool:
        """Send false positive feedback to NLP learning system"""
        try:
            if hasattr(self.bot, 'nlp_client') and self.bot.nlp_client:
                if hasattr(self.bot.nlp_client, 'send_staff_feedback'):
                    success = await self.bot.nlp_client.send_staff_feedback(
                        message, correct_level, detected_level, "false_positive"
                    )
                    return success
            return False
        except Exception as e:
            logger.error(f"Error sending false positive feedback: {e}")
            return False

    async def _send_false_negative_feedback(self, message: str, should_be_level: str, actually_detected: str, context: Dict) -> bool:
        """Send false negative feedback to NLP learning system"""
        try:
            if hasattr(self.bot, 'nlp_client') and self.bot.nlp_client:
                if hasattr(self.bot.nlp_client, 'send_staff_feedback'):
                    success = await self.bot.nlp_client.send_staff_feedback(
                        message, should_be_level, actually_detected, "false_negative"
                    )
                    return success
            return False
        except Exception as e:
            logger.error(f"Error sending false negative feedback: {e}")
            return False

async def setup(bot):
    """Setup function for the enhanced learning commands cog"""
    await bot.add_cog(EnhancedLearningCommands(bot))
    logger.info("✅ Enhanced learning commands cog loaded")