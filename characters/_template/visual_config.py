"""
Visual Configuration Template
=============================
Configure how your character appears in AI-generated images.

Instructions:
1. Fill in each section with details about your character's appearance
2. Be specific and detailed for best results
3. Include art style keywords that match your vision
"""

# ============================================
# BASE DESCRIPTION
# ============================================
# Describe your character's physical appearance in detail.
# This is the foundation for every generated image.
BASE_DESCRIPTION = """
[Describe your character here. Be detailed and specific.]

Physical Features:
- [Hair color, style, length]
- [Eye color and expression]
- [Body type and posture]
- [Distinctive features]

Outfit:
- [Main clothing items]
- [Colors and materials]
- [Accessories]

Special Elements:
- [Any unique visual elements]
- [Special effects or auras]
- [Props they carry]

Example:
A young woman with long silver hair in a ponytail, bright amber eyes,
wearing a vintage leather jacket over a band t-shirt, ripped jeans,
and combat boots. She has multiple ear piercings and a small tattoo
of a phoenix on her left wrist.
"""

# ============================================
# BACKGROUND STYLE
# ============================================
# Define the typical background and art style for images.
BACKGROUND_STYLE = """
[Describe the setting and art style for your character's images]

Default Background:
- [Typical environment/setting]
- [Time of day, weather]
- [Key environmental elements]

Art Style:
- [Realistic / Anime / Cartoon / Pixel Art / etc.]
- [Color palette]
- [Lighting style]
- [Any special effects or filters]

Example:
Default Background: A cozy urban coffee shop with warm lighting,
exposed brick walls, and rain visible through large windows.

Art Style: Semi-realistic digital painting with soft lighting,
warm color palette (oranges, browns, creams), slight film grain,
bokeh effects in background.
"""

# ============================================
# PERSONALITY CONTEXT FOR IMAGES
# ============================================
# How should your character's personality show in images?
PERSONALITY_CONTEXT = """
[Describe typical poses and expressions that match the personality]

Expression Guidelines:
- [Typical facial expressions]
- [Eye contact preferences]
- [Smile style or lack thereof]

Pose Guidelines:
- [Common poses or stances]
- [Hand gestures]
- [Body language]

Example:
Usually shown with a relaxed, slightly amused smile, 
making comfortable eye contact. Often holds a coffee cup
or has hands in jacket pockets. Posture is casual but confident,
often leaning against something. Occasionally caught mid-laugh
or deep in thought while looking out a window.
"""

# ============================================
# TRIGGER WORDS
# ============================================
# Keywords that help AI models generate consistent images.
# Add style-specific terms that match your character.
TRIGGER_WORDS = [
    # Art style keywords
    # "anime style",
    # "realistic",
    # "digital painting",
    
    # Character-specific keywords
    # "silver hair",
    # "leather jacket",
    
    # Mood/atmosphere keywords
    # "cozy",
    # "warm lighting",
    # "urban",
]
