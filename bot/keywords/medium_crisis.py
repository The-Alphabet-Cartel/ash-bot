"""
Medium Crisis Keywords for Ash Bot
These keywords trigger crisis team alerts for monitoring and potential intervention

Crisis Level: MEDIUM 🟡
Response: Ash reply + Crisis team ping in dedicated channel (no staff DM)
"""

# Severe depression symptoms - beyond normal sadness
SEVERE_DEPRESSION = [
    'can\'t take it anymore', 'everything hurts', 'so much pain',
    'completely broken', 'lost all hope', 'nothing matters',
    'why bother', 'give up', 'can\'t handle this', 'too much pain',
    'drowning in sadness', 'can\'t stop crying', 'hollow inside',
    'numb to everything', 'dead inside', 'empty shell', 'barely functioning',
    'can\'t get out of bed', 'sleeping all day', 'stopped caring',
    'world is gray', 'no point anymore', 'exhausted by existing'
]

# Panic and severe anxiety - acute distress
PANIC_ANXIETY = [
    'panic attack', 'can\'t breathe', 'heart racing', 'losing control',
    'going crazy', 'feel like dying', 'can\'t calm down', 'hyperventilating',
    'chest is tight', 'dizzy and shaking', 'world spinning', 'can\'t think straight',
    'overwhelming fear', 'terror washing over', 'paralyzed with fear',
    'adrenaline surge', 'fight or flight', 'impending doom', 'losing my mind',
    'spiraling out', 'anxiety through roof', 'can\'t stop shaking'
]

# Dissociation and detachment - concerning disconnection
DISSOCIATION = [
    'not real', 'floating away', 'watching myself', 'not in my body',
    'everything feels fake', 'disconnected', 'out of body', 'depersonalization',
    'like a dream', 'not really here', 'autopilot mode', 'zoned out completely',
    'feeling detached', 'reality feels off', 'in a fog', 'mentally elsewhere',
    'can\'t connect', 'observing my life', 'like watching tv', 'derealization',
    'nothing feels real', 'floating above myself', 'mind somewhere else'
]

# Trauma responses and flashbacks - PTSD symptoms
TRAUMA_FLASHBACKS = [
    'happening again', 'back there', 'can\'t escape', 'reliving it',
    'flashback', 'triggered', 'ptsd episode', 'memory won\'t stop',
    'vivid nightmare', 'woke up screaming', 'can\'t shake it off',
    'transported back', 'feels so real', 'trapped in memory',
    'intrusive thoughts', 'can\'t turn it off', 'haunted by it',
    'body remembers', 'triggered by smell', 'sound brought me back',
    'anniversary reaction', 'trauma response', 'hypervigilant'
]

# Severe overwhelm - feeling completely unable to cope
SEVERE_OVERWHELM = [
    'drowning in responsibilities', 'everything piling up', 'can\'t keep up',
    'too much at once', 'breaking point', 'about to snap',
    'overwhelmed completely', 'can\'t handle anymore', 'at my limit',
    'crashing down', 'falling apart', 'coming undone',
    'pressure is crushing', 'weight of world', 'can\'t breathe under it',
    'avalanche of problems', 'buried alive', 'suffocating pressure'
]

# Crisis relationship situations - severe interpersonal distress
RELATIONSHIP_CRISIS = [
    'everyone abandoned me', 'completely alone', 'nobody understands',
    'betrayed by everyone', 'can\'t trust anyone', 'isolated completely',
    'pushed everyone away', 'burned all bridges', 'toxic relationship',
    'emotional abuse', 'being manipulated', 'gaslighting me',
    'threatened by partner', 'scared to go home', 'walking on eggshells',
    'relationship imploding', 'family disowned me', 'kicked out'
]

# LGBTQIA+ specific medium crisis situations
LGBTQIA_MEDIUM_CRISIS = [
    'family rejected me completely', 'disowned for being gay', 'thrown out for being trans',
    'conversion therapy threat', 'parents sending me away', 'religious trauma response',
    'severe dysphoria episode', 'body feels wrong', 'can\'t handle deadnaming',
    'misgendering destroying me', 'passing anxiety', 'transition regret fears',
    'internalized homophobia crushing', 'self hate spiraling', 'closet suffocating me'
]

# Combine all medium crisis categories
MEDIUM_CRISIS_KEYWORDS = {
    'severe_depression': SEVERE_DEPRESSION,
    'panic_anxiety': PANIC_ANXIETY,
    'dissociation': DISSOCIATION,
    'trauma_flashbacks': TRAUMA_FLASHBACKS,
    'severe_overwhelm': SEVERE_OVERWHELM,
    'relationship_crisis': RELATIONSHIP_CRISIS + LGBTQIA_MEDIUM_CRISIS
}

def get_medium_crisis_keywords():
    """
    Returns the complete dictionary of medium crisis keywords
    
    Returns:
        dict: Dictionary with category names as keys and keyword lists as values
    """
    return MEDIUM_CRISIS_KEYWORDS

def get_category_keywords(category):
    """
    Get keywords for a specific medium crisis category
    
    Args:
        category (str): Category name ('severe_depression', 'panic_anxiety', etc.)
        
    Returns:
        list: List of keywords for that category, or empty list if category not found
    """
    return MEDIUM_CRISIS_KEYWORDS.get(category, [])

def get_all_keywords():
    """
    Get a flat list of all medium crisis keywords across all categories
    
    Returns:
        list: All medium crisis keywords in a single list
    """
    all_keywords = []
    for category_keywords in MEDIUM_CRISIS_KEYWORDS.values():
        all_keywords.extend(category_keywords)
    return all_keywords

def add_keywords(category, new_keywords):
    """
    Add new keywords to a specific category
    
    Args:
        category (str): Category name
        new_keywords (list): List of new keywords to add
    """
    if category in MEDIUM_CRISIS_KEYWORDS:
        MEDIUM_CRISIS_KEYWORDS[category].extend(new_keywords)
    else:
        MEDIUM_CRISIS_KEYWORDS[category] = new_keywords

def get_keyword_count():
    """
    Get count of keywords in each category and total
    
    Returns:
        dict: Category names with keyword counts plus total
    """
    counts = {}
    total = 0
    for category, keywords in MEDIUM_CRISIS_KEYWORDS.items():
        count = len(keywords)
        counts[category] = count
        total += count
    counts['total'] = total
    return counts