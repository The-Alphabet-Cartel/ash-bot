"""
Low Crisis Keywords for Ash Bot
These keywords trigger supportive responses without team alerts

Crisis Level: LOW 🟢
Response: Ash reply only (no alerts)
"""

# Depression symptoms - manageable but needing support
DEPRESSION_SYMPTOMS = [
    'feel worthless', 'hate myself', 'feel empty', 'so tired',
    'can\'t sleep', 'no energy', 'feel numb', 'so lonely',
    'nobody cares', 'feel invisible', 'exhausted', 'hopeless',
    'feel down', 'really sad', 'depressed today', 'feeling low',
    'unmotivated', 'can\'t focus', 'brain fog', 'sluggish',
    'feel heavy', 'dragging myself', 'no appetite', 'oversleeping',
    'crying for no reason', 'emotional today', 'feel fragile',
    'dark thoughts', 'negative spiral', 'mood is off'
]

# Seasonal and situational struggles
SEASONAL_SITUATIONAL = [
    'seasonal depression', 'winter blues', 'holiday stress',
    'anniversary sadness', 'birthday depression', 'new year anxiety',
    'monday blues', 'sunday scaries', 'post vacation depression',
    'moving stress', 'change is hard', 'transition anxiety',
    'graduation sadness', 'empty nest', 'milestone anxiety'
]

# Anxiety symptoms - manageable worry and stress
ANXIETY_SYMPTOMS = [
    'so anxious', 'worried about everything', 'overthinking',
    'can\'t stop worrying', 'feel on edge', 'restless', 'nervous',
    'stressed out', 'tension headache', 'jaw clenched', 'shoulders tight',
    'mind racing', 'what if scenarios', 'catastrophizing',
    'social anxiety', 'afraid to go out', 'avoiding people',
    'imposter syndrome', 'second guessing', 'anticipatory anxiety',
    'worry spiral', 'anxious thoughts', 'feeling jittery'
]

# Identity struggles - questioning and self-doubt
IDENTITY_STRUGGLES = [
    'don\'t know who i am', 'feel fake', 'pretending', 'imposter',
    'not good enough', 'don\'t belong', 'questioning everything',
    'identity crisis', 'feel lost', 'confused about myself',
    'who am i really', 'lost sense of self', 'don\'t fit anywhere',
    'feeling different', 'outsider looking in', 'mask slipping',
    'authentic self', 'people pleasing', 'chameleon personality',
    'lost my way', 'direction unclear', 'purpose missing'
]

# Relationship struggles - interpersonal difficulties
RELATIONSHIP_TRAUMA = [
    'feel betrayed', 'used me', 'feel unlovable', 'trust issues',
    'abandoned again', 'nobody understands', 'rejected', 'alone',
    'friendship drama', 'feeling excluded', 'left out',
    'misunderstood', 'communication breakdown', 'conflict avoidance',
    'attachment issues', 'fear of abandonment', 'pushing people away',
    'vulnerability hangover', 'opened up too much', 'regret sharing',
    'social rejection', 'ghosted again', 'one sided friendship'
]

# LGBTQIA+ struggles - identity and acceptance challenges
LGBTQIA_STRUGGLES = [
    'coming out', 'family rejected me', 'not accepted', 'dysphoria',
    'internalized homophobia', 'feel different', 'closeted',
    'transition struggles', 'pronouns ignored', 'deadnamed',
    'questioning sexuality', 'am i really gay', 'bi confusion',
    'gender questioning', 'what are my pronouns', 'coming out fear',
    'family not supportive', 'friends don\'t understand', 'workplace discrimination',
    'religious guilt', 'internalized shame', 'heteronormative pressure',
    'passing anxiety', 'misgendered today', 'chosen name ignored',
    'pride month complicated', 'visibility exhausting', 'tokenism'
]

# Failure and self-worth issues - performance and achievement struggles
FAILURE_FEELINGS = [
    'such a failure', 'disappointed everyone', 'screwed up again',
    'can\'t do anything right', 'let everyone down', 'failed at life',
    'messed up bad', 'embarrassed myself', 'stupid mistake',
    'perfectionist paralysis', 'fear of failure', 'procrastinating',
    'comparing myself', 'everyone else succeeding', 'behind in life',
    'wasted potential', 'missed opportunities', 'regret choices',
    'academic pressure', 'career confusion', 'quarter life crisis'
]

# Daily functioning struggles - routine and self-care issues
DAILY_FUNCTIONING = [
    'can\'t get motivated', 'procrastinating everything', 'messy room',
    'haven\'t showered', 'eating poorly', 'skipping meals',
    'sleep schedule messed up', 'doom scrolling', 'avoiding responsibilities',
    'executive dysfunction', 'task paralysis', 'overwhelmed by chores',
    'self care failing', 'basic hygiene hard', 'dishes piling up',
    'laundry mountain', 'can\'t adult today', 'functioning poorly'
]

# Work and school stress - achievement and performance pressure
WORK_SCHOOL_STRESS = [
    'work is overwhelming', 'burned out', 'deadline pressure',
    'boss is terrible', 'toxic workplace', 'underpaid overworked',
    'school stress', 'exam anxiety', 'paper due', 'grades dropping',
    'struggling in class', 'teacher doesn\'t like me', 'group project hell',
    'job search depression', 'interview anxiety', 'rejection letters',
    'career uncertainty', 'major regret', 'graduation anxiety'
]

# Combine all low crisis categories
LOW_CRISIS_KEYWORDS = {
    'depression_symptoms': DEPRESSION_SYMPTOMS + SEASONAL_SITUATIONAL,
    'anxiety_symptoms': ANXIETY_SYMPTOMS,
    'identity_struggles': IDENTITY_STRUGGLES,
    'relationship_trauma': RELATIONSHIP_TRAUMA,
    'lgbtqia_struggles': LGBTQIA_STRUGGLES,
    'failure_feelings': FAILURE_FEELINGS,
    'daily_functioning': DAILY_FUNCTIONING,
    'work_school_stress': WORK_SCHOOL_STRESS
}

def get_low_crisis_keywords():
    """
    Returns the complete dictionary of low crisis keywords
    
    Returns:
        dict: Dictionary with category names as keys and keyword lists as values
    """
    return LOW_CRISIS_KEYWORDS

def get_category_keywords(category):
    """
    Get keywords for a specific low crisis category
    
    Args:
        category (str): Category name ('depression_symptoms', 'anxiety_symptoms', etc.)
        
    Returns:
        list: List of keywords for that category, or empty list if category not found
    """
    return LOW_CRISIS_KEYWORDS.get(category, [])

def get_all_keywords():
    """
    Get a flat list of all low crisis keywords across all categories
    
    Returns:
        list: All low crisis keywords in a single list
    """
    all_keywords = []
    for category_keywords in LOW_CRISIS_KEYWORDS.values():
        all_keywords.extend(category_keywords)
    return all_keywords

def add_keywords(category, new_keywords):
    """
    Add new keywords to a specific category
    
    Args:
        category (str): Category name
        new_keywords (list): List of new keywords to add
    """
    if category in LOW_CRISIS_KEYWORDS:
        LOW_CRISIS_KEYWORDS[category].extend(new_keywords)
    else:
        LOW_CRISIS_KEYWORDS[category] = new_keywords

def get_keyword_count():
    """
    Get count of keywords in each category and total
    
    Returns:
        dict: Category names with keyword counts plus total
    """
    counts = {}
    total = 0
    for category, keywords in LOW_CRISIS_KEYWORDS.items():
        count = len(keywords)
        counts[category] = count
        total += count
    counts['total'] = total
    return counts