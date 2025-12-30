<!-- ash-bot/docs/clean_architecture_charter.md -->
<!--
Clean Architecture Charter for Ash-Bot Service
FILE VERSION: v5.0
LAST MODIFIED: 2025-12-30
-->
# Clean Architecture Charter - Ash-Bot

## Sacred Principles - NEVER TO BE VIOLATED

**Repository**: https://github.com/the-alphabet-cartel/ash-bot  
**Project**: Ash-Bot v5.0
**Community**: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org  
**FILE VERSION**: v5.0
**LAST UPDATED**: 2025-12-30

---

# 🎯 CORE SYSTEM VISION (Never to be violated):

## **Ash-Bot is a CRISIS DETECTION Natural Language Processor that**:
1. **FIRST**: Uses Zero-Shot AI models for primary semantic classification
2. **SECOND**: Enhances AI results with contextual pattern analysis
3. **PURPOSE**: Detect crisis messages in Discord community communications

## 🏛️ **IMMUTABLE ARCHITECTURE RULES**

### **Rule #1: Factory Function Pattern - MANDATORY**
- **ALL managers MUST use factory functions** - `create_[manager_name]()`
- **NEVER call constructors directly**
- **Factory functions enable**: dependency injection, testing, consistency
- **Examples**: `create_model_manager()`, `create_patterns_detection_manager()`, `create_settings_config_manager()`

### **Rule #2: Dependency Injection - REQUIRED**
- **All managers accept dependencies through constructor parameters**
- **UnifiedConfigManager is always the first parameter**
- **Additional managers passed as named parameters**
- **Clean separation of concerns maintained**

### **Rule #3: Phase-Additive Development - STANDARD**
- **New phases ADD functionality, never REMOVE**
- **Maintain backward compatibility within phase**
- **Each phase builds on previous phases' foundations**
- **Phase 3a + Phase 3b + Phase 3c + Phase 3d = cumulative enhancement**

### **Rule #4: JSON Configuration + Environment Overrides - SACRED**
- **All configuration externalized to JSON files**
- **JSON configuration files set DEFAULT values**
- **Environment Variables override JSON defaults**
- **No hardcoded configuration in source code**
- **UnifiedConfigManager handles all configuration loading**

### **Rule #5: Resilient Validation with Smart Fallbacks - PRODUCTION CRITICAL**
- **Invalid configurations trigger graceful fallbacks, not system crashes**
- **Data type validation provides safe defaults with logging**
- **Configuration path issues handled transparently**  
- **System prioritizes operational continuity for life-saving functionality**
- **Clear error logging for debugging while maintaining service availability**

### **Rule #6: File Versioning System - MANDATORY**
- **ALL code files MUST include version headers** in the format:
  - `v[Major].[Minor]-[Phase]-[Step]-[Increment]`
- **Version format**:
  - `v5.0-1a-1.1-1` (Clean Architecture v5.0, Phase 1a, Step 1.1, Increment 1)
- **Header placement**: At the top of each file in comments or docstrings
- **Version increments**: Required for each meaningful change within a step
- **Cross-conversation continuity**: Ensures accurate file tracking across sessions
- **Version Headers should include at the top of the header a file description of what the file code does**
  - `[fileDescription] for Ash-Bot Service`

#### **Required Version Header Format:**
```python
"""
Ash-Bot: Crisis Detection Backend for The Alphabet Cartel Discord Community
CORE PRINCIPLE: Zero-Shot AI Models → Pattern Enhancement → Crisis Classification
******************  CORE SYSTEM VISION (Never to be violated):  ****************
Ash-Bot is a CRISIS DETECTION BACKEND that:
1. FIRST: Uses Zero-Shot AI models for primary semantic classification
2. SECOND: Enhances AI results with contextual pattern analysis  
3. PURPOSE: Detect crisis messages in Discord community communications
********************************************************************************
{fileDescription} for Ash-Bot Service
---
FILE VERSION: v5.0-1a-1.1-1
LAST MODIFIED: 2025-12-30
PHASE: 1a Step 1.1-1 - {Phase / Step Description}
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""
```

#### **Version Increment Guidelines:**
- **Major changes**: New functionality, architectural modifications
- **Minor changes**: Bug fixes, small improvements, documentation updates
- **Step completion**: Always increment when completing a phase step
- **Cross-session**: Always increment when continuing work across conversations

### **Rule #7: Environment Variable Reuse - MANDATORY**
- **Always check existing environment variables in `.env.template` before creating new ones**
- **Map new functionality to existing variables whenever possible**
- **Prevent environment variable bloat and configuration sprawl**
- **Maintain consistent naming conventions and patterns**
- **Document the mapping relationship when reusing variables**

#### **Rule #7 Implementation Process**:
1. **Audit Existing Variables**: Search `./.env.template` for related functionality
2. **Map Requirements**: Identify how new needs can use existing variables
3. **Calculate Conversions**: Create appropriate scaling/conversion logic if needed
4. **Document Reuse**: Clearly document which existing variables are being leveraged
5. **Test Thoroughly**: Ensure existing functionality isn't impacted by reuse

#### **Success Example**:
```bash
# ❌ WRONG: Creating new undefined variables
${NLP_CRISIS_AMPLIFIER_BASE_WEIGHT}     # New variable
${NLP_POSITIVE_REDUCER_BASE_WEIGHT}     # New variable

# ✅ RIGHT: Reusing existing variables with conversion
NLP_ANALYSIS_CONTEXT_BOOST_WEIGHT=1.5   # Existing variable
# Convert: crisis_base_weight = context_boost_weight * 0.1 = 0.15

NLP_CONFIG_CRISIS_CONTEXT_BOOST_MULTIPLIER=1.0  # Existing variable  
# Use directly for scaling calculations
```

#### **Benefits of Rule #7**:
- **Prevents Variable Bloat**: Keeps configuration manageable
- **Reuses Infrastructure**: Leverages existing patterns and validation
- **Maintains Consistency**: Uses established naming conventions
- **Reduces Complexity**: Fewer variables to manage, test, and document
- **Sustainable Development**: Encourages thoughtful design over quick additions

### **Rule #8: Always use real-world tests and logger for testing - MANDATORY**
- **Never use mock methods for testing**
- **Always use the actual methods we've designed**
- **Always use our LoggingConfigManager and logger methods as designed for testing.**
  - `managers/logging_config_manager.py`

#### **Benefits of Rule #8**:
- **Tests the actual implementation**: Not just the logic behind it
- **Ensures readability for human counterparts**: Key for testing so that we may assist in the testing and troubleshooting sequences

### **Rule #9: Always ask for the current version of a specific file before making any modifications, changes, or edits to that file - STANDARD**

#### **Benefits of Rule #9**:
- **Prevents wasted time on edits to old code**
- **Ensures that everyone is on the "same page"**
- **Reduces confusion between team members**
- **Reduces frustration between team members**

### **Rule #10: All files need to stay within ~1,000 lines of code (give or take 2%) - STANDARD**
- **Code going over ~1,000 lines needs to be split into helper files**
- **Helper files will be stored in the same directory as the file being worked on under a sub-directory named `helpers`**
  - **Helper files will be named `*_helper.py`**

#### **Benefits of Rule #10**:
- **Manageable file sizes**
- **Ease of artifact creation**
- **Less chance of artifacts corrupting**

### **Rule #11: All files will use the LoggingConfigManager for debug and informational log output - MANDATORY**
- **This colorizes and unifies the output so that it is human readable**
- **Logging is essential to debugging and ensuring the systems are working as intended**

#### **Benefits of Rule #11**:
- **Human readable, colorized logs based on priority**
- **Uses the built in python logger system, no need for other methods**

---

## 🔧 **MANAGER IMPLEMENTATION STANDARDS**

### **Required Manager Structure:**
```python
"""
Ash-Bot: Crisis Detection Backend for The Alphabet Cartel Discord Community
CORE PRINCIPLE: Zero-Shot AI Models → Pattern Enhancement → Crisis Classification
******************  CORE SYSTEM VISION (Never to be violated):  ****************
Ash-Bot is a CRISIS DETECTION BACKEND that:
1. FIRST: Uses Zero-Shot AI models for primary semantic classification
2. SECOND: Enhances AI results with contextual pattern analysis  
3. PURPOSE: Detect crisis messages in Discord community communications
********************************************************************************
{managerDescription} for Ash-Bot Service
---
FILE VERSION: v{major}.{minor}-{phase}-{step}-{increment}
LAST MODIFIED: {date}
PHASE: {phase}, {step}
CLEAN ARCHITECTURE: Compliant
"""

class [Manager]Manager:
    def __init__(self, config_manager, [additional_managers...]):
        """Constructor with dependency injection"""
        # Standard initialization pattern with resilient error handling
    
    def get_[functionality](self):
        """Standard getter methods with safe defaults"""
        # Implementation with graceful fallbacks
    
    def validate_[aspect](self):
        """Standard validation methods with resilient behavior"""
        # Validation that logs issues but maintains functionality

def create_[manager]_manager([parameters]) -> [Manager]Manager:
    """Factory function - MANDATORY"""
    return [Manager]Manager([parameters])

__all__ = ['[Manager]Manager', 'create_[manager]_manager']
```

### **Required Integration Pattern:**
```python
# In main.py or integration code - ALWAYS use factory functions
from managers.[manager]_manager import create_[manager]_manager

try:
    manager = create_[manager]_manager(
        config_manager=config_manager,
        [additional_managers...]
    )
except Exception as e:
    logger.error(f"❌ Manager initialization failed: {e}")
    # Use fallback or safe defaults - DO NOT CRASH THE SYSTEM
    manager = create_fallback_manager()
```

---

## 🔧 **JSON CONFIGURATION FILE STANDARDS**

### **Required JSON Structure:**
**Filename**:
- `*descriptiveName*_*configurationType*.json`
- Examples:
  - analysis_config.json
  - learning_settings.json
  - patterns_crisis.json

**JSON Structure**
```json
{
  "_metadata": {
    "file_version": "v{major}.{minor}-{phase}-{step}-{increment}",
    "last_modified": "{year}-{month}-{day}",
    "clean_architecture": "Compliant",
  },

  "*setting_category*": {
    "description": "*settingDescription*",
    "*setting_name*": "${*ENV_VAR*}",
    [...moreSettings...],
    "defaults": {
      "*setting_name*": *default_value*,
      [...moreSettings...],
    },
    "validation": {
      "*setting_name": {
        "type": "integer | boolean | list | float | string",
        "range": [min, max],
        "allowed_values": ["*value1*", "*value2*", "*value3*", ...],
        "required": true | false
      }
    }
  },
  [...],
}
```
- **NOTES:**
  - *Only Integers and Floats use the `"range"` validation field.*
  - *Only Strings use the `"allowed_values"` validation field.*

**Example**
```json
{
  "_metadata": {
    "file_version": "v5.0",
    "last_modified": "2025-12-30",
    "clean_architecture": "Compliant",
  },

  "crisis_thresholds": {
    "description": "Core crisis level mapping thresholds for analysis algorithms",
    "high": "${NLP_ANALYSIS_CRISIS_THRESHOLD_HIGH}",
    "medium": "${NLP_ANALYSIS_CRISIS_THRESHOLD_MEDIUM}",
    "low": "${NLP_ANALYSIS_CRISIS_THRESHOLD_LOW}",
    "defaults": {
      "high": 0.55,
      "medium": 0.28,
      "low": 0.16
    },
    "validation": {
      "high": {
        "type": "float",
        "range": [0.001, 1.000]
      },
      "medium": {
        "type": "float",
        "range": [0.001, 1.000]
      },
      "low": {
        "type": "float",
        "range": [0.001, 1.000]
      }
    }
  }
}
```
**Note:**
- *All data types in the JSON validation fields need to be full words*
  - "integer", not "int"
  - "float", not "flt"
  - "string", not "str"
  - "boolean", not "bool"
  - "list" for dictionaries

---
## 🏷️ **METHOD NAMING CONVENTIONS - Crisis Detection Architecture**

### **CORE PRINCIPLE**: Method names must clearly indicate the AI-first, pattern-enhancement architecture

---

### **PRIMARY CLASSIFICATION METHODS** (Zero-Shot AI First)
**Pattern**: `analyze_*`, `classify_*`, `detect_*`
- ✅ `analyze_message_with_ai()` - Main analysis entry point using AI models
- ✅ `classify_crisis_with_ensemble()` - AI ensemble classification 
- ✅ `detect_crisis_semantically()` - Zero-shot semantic detection
- ❌ `analyze_message()` - Too generic, doesn't indicate AI-first
- ❌ `pattern_analyze()` - Suggests patterns are primary

### **ENHANCEMENT METHODS** (Pattern Boosting/Adjustment)
**Pattern**: `enhance_*`, `boost_*`, `adjust_*`, `refine_*`
- ✅ `enhance_ai_scores_with_patterns()` - Pattern enhancement of AI results
- ✅ `boost_confidence_with_context()` - Context-based score boosting
- ✅ `adjust_scores_for_community_vocab()` - Community-specific adjustments
- ✅ `refine_ai_classification()` - General AI result refinement
- ❌ `pattern_analysis()` - Suggests patterns are standalone, not enhancement
- ❌ `context_scoring()` - Doesn't indicate it's enhancing AI results

### **FALLBACK METHODS** (When AI Fails)
**Pattern**: `fallback_*`, `emergency_*`, `backup_*`
- ✅ `fallback_to_pattern_only()` - Clear fallback when AI unavailable
- ✅ `emergency_pattern_classification()` - Emergency classification mode
- ✅ `backup_keyword_analysis()` - Backup analysis when models fail
- ❌ `pattern_classification()` - Doesn't indicate it's a fallback
- ❌ `alternative_analysis()` - Too vague about when to use

### **MODEL MANAGEMENT METHODS**
**Pattern**: `load_*`, `initialize_*`, `manage_*`, `cache_*`
- ✅ `load_zero_shot_pipeline()` - Load AI model pipeline
- ✅ `initialize_ensemble_models()` - Initialize AI model ensemble
- ✅ `cache_model_results()` - Cache AI model outputs
- ✅ `manage_model_lifecycle()` - Manage AI model loading/unloading

### **VALIDATION AND TESTING METHODS**
**Pattern**: `validate_*`, `test_*`, `verify_*`
- ✅ `validate_ai_classification()` - Verify AI models are working
- ✅ `test_zero_shot_availability()` - Test if AI models are available
- ✅ `verify_ensemble_functionality()` - Verify AI ensemble is operational

---

### **NAMING HIERARCHY RULES**

1. **Primary Flow**: Always start with AI-focused verbs
   - `analyze_` → `enhance_` → `finalize_`
   - `classify_` → `boost_` → `output_`

2. **Secondary Qualifiers**: Add specific technology/approach
   - `_with_ai`, `_with_ensemble`, `_with_zero_shot` (for primary)
   - `_with_patterns`, `_with_context`, `_with_vocab` (for enhancement)
   - `_pattern_only`, `_emergency`, `_fallback` (for backups)

3. **Tertiary Descriptors**: Add specific domain/function
   - `_crisis_`, `_mental_health_`, `_community_`
   - `_detection`, `_classification`, `_analysis`

### **EXAMPLES OF COMPLETE METHOD NAMES**
```python
# PRIMARY AI CLASSIFICATION
def analyze_crisis_with_zero_shot_ensemble(message, labels):
def classify_mental_health_with_ai_models(text, confidence_threshold):
def detect_patterns_crisis_semantically(message, model_weights):

# ENHANCEMENT OF AI RESULTS  
def enhance_ai_scores_with_patterns_crisis(ai_results, pattern_matches):
def boost_ensemble_confidence_with_context(scores, message_context):
def adjust_ai_classification_for_community(results, vocab_patterns):

# FALLBACK WHEN AI FAILS
def fallback_to_pattern_detection_only(message, emergency_patterns):
def emergency_keyword_classification(text, critical_word_list):
def backup_pattern_analysis_no_ai(message, fallback_config):

# MODEL MANAGEMENT
def load_zero_shot_crisis_pipeline(model_name, device):
def initialize_mental_health_ensemble(model_configs):
def cache_ai_classification_results(message_hash, results):
```

### **VIOLATION DETECTION**

#### **Red Flag Method Names** (*require immediate review*):
- Any method starting with pattern_* that isn't clearly fallback
- Methods with analyze_* that don't specify AI involvement
- Methods suggesting patterns are primary: `pattern_classify()`, `keyword_detect()`
- Generic names that hide the AI-first architecture: `process_message()`, `score_text()`

#### ENFORCEMENT STRATEGY
- **Documentation Updates**: When adding new methods, update this convention guide
- **Refactoring Protocol**: When renaming methods, update all callers and tests simultaneously

---

## 🏥 **PRODUCTION RESILIENCE PHILOSOPHY**

### **Mission-Critical System Requirements**
This system serves **The Alphabet Cartel LGBTQIA+ community** by providing **life-saving mental health crisis detection**. Therefore:

#### **🛡️ Operational Continuity Over Perfection**
- **System availability is paramount** - better to run with safe defaults than crash
- **Graceful degradation** when facing configuration issues
- **Comprehensive logging** of all issues for post-incident analysis
- **Self-healing mechanisms** where possible

#### **⚡ Smart Fail-Fast vs. Resilient Behavior**
- **Fail-Fast**: Only for **unrecoverable errors** that would produce dangerous results
- **Resilient**: For **configuration issues**, **missing files**, **invalid data types**
- **Logging**: All issues logged clearly for debugging and monitoring

#### **🔧 Error Handling Hierarchy**
1. **Critical Safety Issues**: Fail-fast (e.g., model corruption, security breaches)
2. **Configuration Problems**: Resilient fallback with logging
3. **Data Type Issues**: Convert to safe defaults with warnings
4. **Path/File Issues**: Use fallbacks or defaults with clear logging
5. **Environment Variable Issues**: Schema-based type conversion with defaults

---

## **Future Work Requirements**
- **MUST follow established patterns**
- **MUST use factory functions**
- **MUST maintain cumulative integration**
- **MUST preserve all previous phase functionality**
- **MUST implement production-ready resilience**
- **MUST include file versioning headers**

---

## 🚨 **VIOLATION PREVENTION**

### **Before Making ANY Architectural Change:**
1. **Does this maintain factory function pattern?** ✅ Required
2. **Does this preserve all previous phase functionality?** ✅ Required  
3. **Does this follow dependency injection principles?** ✅ Required
4. **Does this maintain JSON + environment configuration?** ✅ Required
5. **Does this implement resilient error handling?** ✅ **PRODUCTION CRITICAL** - Required
6. **Does this maintain operational continuity for crisis detection?** ✅ **LIFE-SAVING** - Required
7. **Does this include proper file versioning?** ✅ Required
8. **Does this check existing environment variables first?** ✅ Required
9. **Have I verified we are working on the same file version?** ✅ Required

---

### **Red Flags - IMMEDIATE STOP:**
- ❌ Direct constructor calls in production code
- ❌ Removing functionality from previous phases
- ❌ Hardcoding configuration values
- ❌ Breaking manager integration patterns
- ❌ Bypassing factory functions
- ❌ Implementing fail-fast for non-critical configuration issues
- ❌ Allowing system crashes for recoverable problems
- ❌ Missing file version headers in code files
- ❌ Inconsistent version numbering across files
- ❌ Creating new environment variables without first checking current `.env.template` file
- ❌ Duplicating functionality with different variable names
- ❌ Ignoring existing infrastructure in favor of "clean slate" approaches
- ❌ Adding variables without considering conversion/mapping possibilities
- ❌ Not asking for current file version before making changes, edits, or modifications

---

## 🎯 **ARCHITECTURAL SUCCESS METRICS**

### **Code Quality Indicators:**
- ✅ All managers use factory functions
- ✅ All configuration externalized
- ✅ All phases cumulative and functional
- ✅ Clean dependency injection throughout
- ✅ Production-ready resilient error handling
- ✅ Consistent file versioning across all code files
- ✅ Consistent environment variables across all code files

### **Integration Health:**
- ✅ Tests use same patterns as production code
- ✅ Factory functions handle all initialization
- ✅ Managers properly integrated across phases
- ✅ Configuration overrides working consistently
- ✅ System maintains availability under adverse conditions
- ✅ File versions track accurately across conversations
- ✅ Environment variable bloat is avoided

### **Production Readiness:**
- ✅ **Operational continuity preserved** under configuration issues
- ✅ **Comprehensive logging** for debugging and monitoring
- ✅ **Safe fallback mechanisms** for all critical functionality
- ✅ **Crisis detection capability** maintained regardless of configuration state
- ✅ **Version tracking** enables precise change management

---

## 💪 **COMMITMENT**

**This architecture serves The Alphabet Cartel community by providing:**
- **Reliable mental health crisis detection** that stays operational
- **Maintainable and extensible codebase** with production-ready resilience
- **Clear separation of concerns** with intelligent error recovery
- **Professional-grade system design** optimized for life-saving service delivery
- **Precise version tracking** for maintainable cross-conversation development

**Every architectural decision supports the mission of providing continuous, reliable mental health support to LGBTQIA+ community members.**

---

**Status**: Living Document - Updated for Production Resilience
**Authority**: Project Lead + AI Assistant Collaboration
**Enforcement**: Mandatory for ALL code changes
**Version**: v5.0

---

## 🏆 **ARCHITECTURE PLEDGE**

*"I commit to maintaining Clean v3.1 architecture principles with production-ready resilience and consistent file versioning in every code change, recognizing that system availability, operational continuity, and precise change tracking directly impact the ability to provide life-saving mental health crisis detection for The Alphabet Cartel community."*

---

**Built with care for chosen family** 🏳️‍🌈
