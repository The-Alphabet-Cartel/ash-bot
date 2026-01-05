# Clean Architecture Charter - Ash-Bot

## Sacred Principles - NEVER TO BE VIOLATED

**Version**: v5.1  
**Last Modified**: 2026-01-03  
**Repository**: https://github.com/the-alphabet-cartel/ash-bot  
**Community**: [The Alphabet Cartel](https://discord.gg/alphabetcartel) | [alphabetcartel.org](https://alphabetcartel.org)

---

# 🎯 CORE SYSTEM VISION (Never to be violated):

## **Ash-Bot is a CRISIS DETECTION Discord Bot that**:
1. **FIRST**: Monitors all messages within our discord server and sends them to our NLP server for semantic classification.
2. **SECONDARY**: If the NLP server detects a crisis, the bot alerts the appropriate staff members within the Crisis Response Team (CRT) using "pings" (@crisis_response) to the CRT role within the crisis-response channel utilizing discord's embeds feature to show crisis details based on the NLP determined severity of the crisis.
3. **TERTIARY**: Tracks historical patterns and messages and sends them to our NLP server for semantic classification to determine if there is a pattern of escalation over time.
4. **PURPOSE**: To detect crisis messages in Discord community communications.

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

#### **Required Version Header Format - Ash Ecosystem Standard:**

```python
"""
============================================================================
{Project Name}: {Project Tagline}
The Alphabet Cartel - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

MISSION - NEVER TO BE VIOLATED:
    {Mission Line 1}
    {Mission Line 2}
    {Mission Line 3}
    {Mission Line 4}

============================================================================
{File Description}
----------------------------------------------------------------------------
FILE VERSION: {version}
LAST MODIFIED: {date}
PHASE: {phase}
CLEAN ARCHITECTURE: Compliant
Repository: {repository_url}
============================================================================
"""
```

#### **Ash-Bot Specific Header:**

```python
"""
============================================================================
Ash-Bot: Crisis Detection Discord Bot
The Alphabet Cartel - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

MISSION - NEVER TO BE VIOLATED:
    Monitor  → Send messages to Ash-NLP for crisis classification
    Alert    → Notify Crisis Response Team via embeds when crisis detected
    Track    → Maintain user history for escalation pattern detection
    Protect  → Safeguard our LGBTQIA+ community through early intervention

============================================================================
{File Description}
----------------------------------------------------------------------------
FILE VERSION: v5.0-1-1.0-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 1 - {Phase Description}
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
"""
```

#### **Ash-NLP Specific Header:**

```python
"""
============================================================================
Ash-NLP: Crisis Detection NLP Server
The Alphabet Cartel - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

MISSION - NEVER TO BE VIOLATED:
    Analyze  → Process messages through multi-model ensemble classification
    Detect   → Identify crisis signals with weighted consensus algorithms
    Explain  → Provide human-readable explanations for all decisions
    Protect  → Safeguard our LGBTQIA+ community through accurate detection

============================================================================
{File Description}
----------------------------------------------------------------------------
FILE VERSION: v5.0-1-1.0-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 1 - {Phase Description}
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-nlp
============================================================================
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
${BOT_CRISIS_AMPLIFIER_BASE_WEIGHT}     # New variable
${BOT_POSITIVE_REDUCER_BASE_WEIGHT}     # New variable

# ✅ RIGHT: Reusing existing variables with conversion
BOT_ANALYSIS_CONTEXT_BOOST_WEIGHT=1.5   # Existing variable
# Convert: crisis_base_weight = context_boost_weight * 0.1 = 0.15

BOT_CONFIG_CRISIS_CONTEXT_BOOST_MULTIPLIER=1.0  # Existing variable  
# Use directly for scaling calculations
```

#### **Benefits of Rule #7**:
- **Prevents Variable Bloat**: Keeps configuration manageable
- **Reuses Infrastructure**: Leverages existing patterns and validation
- **Maintains Consistency**: Uses established naming conventions
- **Reduces Complexity**: Fewer variables to manage, test, and document
- **Sustainable Development**: Encourages thoughtful design over quick additions

### **Rule #8: Real-World Testing Standards - MANDATORY**

#### **General Testing Principles**
- **Never use mock methods for testing**
- **Always use the actual methods we've designed**
- **Always use our LoggingConfigManager and logger methods as designed for testing**

#### **Benefits of Rule #8**:
- **Tests actual implementation** not just logic
- **Ensures human readability** for collaborative testing
- **Validates production performance** under real conditions
- **Reveals true model capabilities** and limitations
- **Informs deployment decisions** with real metrics

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

### **Rule #12: Environment Version Specificity - MANDATORY**

All version-dependent commands MUST use explicit version references.

#### **Python Package Installation**
```python
# ✅ CORRECT - Explicit Python version
python3.11 -m pip install package_name
python3.11 -m pip install -r requirements.txt

# ❌ INCORRECT - May use wrong Python version
pip install package_name  # Could install to 3.10 when running 3.11
pip install -r requirements.txt
```

#### **Version Verification**
Before installing packages, verify Python version:
```bash
# Check which Python pip uses
pip --version  # Output: pip X.X from /path/to/pythonX.X/

# Check which Python you're running
python --version  # Must match pip's Python version

# Explicitly use correct version
python3.11 -m pip install package
```

#### **Common Version Mismatch Scenarios**
1. **System has multiple Python versions** (3.10, 3.11, 3.12)
2. **pip symlink points to different version** than python symlink
3. **Virtual environments** not activated correctly
4. **Docker containers** with multiple Python installations

#### **Real-World Impact**
Phase 1 encountered:
```bash
# Installed packages successfully
pip install transformers torch
# Output: Successfully installed transformers-4.57.3 torch-2.9.1

# Runtime failed
python -c "import transformers"
# Error: ModuleNotFoundError: No module named 'transformers'

# Diagnosis:
pip --version  # pip from Python 3.10
python --version  # Python 3.11

# Packages installed to 3.10, code ran on 3.11!
```

#### **Fix Applied**
```dockerfile
# Dockerfile fix - explicit version
RUN python3.11 -m pip install --upgrade pip
RUN python3.11 -m pip install -r requirements.txt
```

#### **Requirements for All Scripts**
- Use `python3.11 -m pip` not `pip`
- Use `python3.11 script.py` not `python script.py` (if version matters)
- Document expected Python version in README
- Verify version match in CI/CD pipelines

#### **Benefits of Rule #12**:
- **Prevents "module not found" errors** despite successful installation
- **Explicit version control** across environments
- **Reproducible builds** across team members
- **Clear debugging** when version issues occur

### **Rule #13: AI Assistant File System Tool Usage - MANDATORY**

When Claude or other AI assistants are editing project files, they MUST use the correct tools for the file location.

#### **User's Computer (Network Shares, Local Files)**
For files on the user's computer (Windows network shares like `\\10.20.30.253\...` or local paths):

```
# ✅ CORRECT - Use Filesystem tools
Filesystem:read_file       - Read file contents
Filesystem:edit_file       - Make targeted edits (preferred for changes)
Filesystem:write_file      - Write entire file (use sparingly)
Filesystem:list_directory  - Browse directories
Filesystem:search_files    - Search for files

# ❌ INCORRECT - These only work on Claude's container
str_replace    - Only works on Claude's Linux container
view           - Only works on Claude's Linux container  
create_file    - Only works on Claude's Linux container
bash_tool      - Only works on Claude's Linux container
```

#### **Claude's Computer (Container Filesystem)**
For files in Claude's container (`/home/claude/`, `/mnt/user-data/uploads/`):

```
# ✅ CORRECT - Use computer use tools
str_replace    - Edit files in Claude's container
view           - Read files in Claude's container
create_file    - Create files in Claude's container
bash_tool      - Execute commands in Claude's container
```

#### **How to Identify File Location**
| Path Pattern | Location | Tools to Use |
|--------------|----------|-------------|
| `\\10.20.30.253\...` | User's network share | `Filesystem:*` |
| `C:\Users\...` | User's Windows PC | `Filesystem:*` |
| `/home/claude/...` | Claude's container | `str_replace`, `view`, etc. |
| `/mnt/user-data/...` | Claude's container | `str_replace`, `view`, etc. |

#### **Best Practices for File Editing**
1. **Prefer `Filesystem:edit_file`** over `Filesystem:write_file` for changes
   - `edit_file` shows a diff preview and is safer
   - `write_file` replaces entire file content
2. **Use `dryRun: true`** first to preview changes before applying
3. **Always verify file path** before editing to ensure correct tool selection

#### **Benefits of Rule #13**:
- **Prevents failed edits** due to wrong tool selection
- **Maintains cross-conversation consistency** by documenting tool usage
- **Reduces frustration** from "file not found" errors
- **Enables targeted edits** instead of full file rewrites
- **Preserves file history** with smaller, traceable changes

---

## 🔧 **MANAGER IMPLEMENTATION STANDARDS**

### **Required Manager Structure:**
```python
"""
============================================================================
Ash-Bot: Crisis Detection Discord Bot
The Alphabet Cartel - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

MISSION - NEVER TO BE VIOLATED:
    Monitor  → Send messages to Ash-NLP for crisis classification
    Alert    → Notify Crisis Response Team via embeds when crisis detected
    Track    → Maintain user history for escalation pattern detection
    Protect  → Safeguard our LGBTQIA+ community through early intervention

============================================================================
{Manager Description}
----------------------------------------------------------------------------
FILE VERSION: v{major}.{minor}-{phase}-{step}-{increment}
LAST MODIFIED: {date}
PHASE: {phase} - {step description}
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
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
    "high": "${BOT_ANALYSIS_CRISIS_THRESHOLD_HIGH}",
    "medium": "${BOT_ANALYSIS_CRISIS_THRESHOLD_MEDIUM}",
    "low": "${BOT_ANALYSIS_CRISIS_THRESHOLD_LOW}",
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

### **VALIDATION AND TESTING METHODS**
**Pattern**: `validate_*`, `test_*`, `verify_*`
- ✅ `validate_ai_classification()` - Verify AI models are working
- ✅ `test_zero_shot_availability()` - Test if AI models are available
- ✅ `verify_ensemble_functionality()` - Verify AI ensemble is operational

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
10. **Does this use version-specific commands (python3.11 -m pip)?** ✅ Required
11. **Am I using the correct file system tools for the file location?** ✅ Required

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
- ❌ Using generic `pip install` instead of version-specific commands
- ❌ Assuming Python version without verification

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
- ✅ Version-specific commands used throughout (python3.11 -m pip)

### **Integration Health:**
- ✅ Tests use same patterns as production code
- ✅ Factory functions handle all initialization
- ✅ Managers properly integrated across phases
- ✅ Configuration overrides working consistently
- ✅ System maintains availability under adverse conditions
- ✅ File versions track accurately across conversations
- ✅ Environment variable bloat is avoided
- ✅ Python package versions match runtime versions

### **Production Readiness:**
- ✅ **Operational continuity preserved** under configuration issues
- ✅ **Comprehensive logging** for debugging and monitoring
- ✅ **Safe fallback mechanisms** for all critical functionality
- ✅ **Crisis detection capability** maintained regardless of configuration state
- ✅ **Version tracking** enables precise change management
- ✅ **Environment version consistency** prevents runtime errors

---

## 💪 **COMMITMENT**

**This architecture serves The Alphabet Cartel community by providing:**
- **Reliable mental health crisis detection** that stays operational
- **Maintainable and extensible codebase** with production-ready resilience
- **Clear separation of concerns** with intelligent error recovery
- **Professional-grade system design** optimized for life-saving service delivery
- **Precise version tracking** for maintainable cross-conversation development
- **Industry-standard ML evaluation** that measures real-world effectiveness
- **Environment version consistency** that ensures reliable operation

**Every architectural decision supports the mission of providing continuous, reliable mental health support to LGBTQIA+ community members.**

---

**Status**: Living Document - Updated for Ash Ecosystem Header Standard
**Authority**: Project Lead + AI Assistant Collaboration
**Enforcement**: Mandatory for ALL code changes
**Version**: v5.1

---

## 🏆 **ARCHITECTURE PLEDGE**

*"I commit to maintaining Clean Architecture principles with production-ready resilience, realistic ML evaluation standards, environment version specificity, and consistent file versioning in every code change, recognizing that system availability, operational continuity, and precise change tracking directly impact the ability to provide life-saving mental health crisis detection for The Alphabet Cartel community."*

---

**Built with care for chosen family** 🏳️‍🌈
