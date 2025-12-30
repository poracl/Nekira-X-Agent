"""
Visual Configuration for Nekira
================================
Defines the visual identity for AI image generation.
Used by the ImagePromptFormatterAgent to create consistent imagery.
"""

# ============================================
# BASE DESCRIPTION
# ============================================
# Core visual description of the character
BASE_DESCRIPTION = """
Nekira, a cyberpunk anime girl and digital avatar from a parallel multiverse, 
inspired by 80s-90s manga and anime (Ghost in the Shell, Akira, Bubblegum Crisis).

Physical Features:
- Short neon-pink hair with black streaks
- Large expressive eyes with sharp lashes, neon-blue irises
- Confident expression with a hint of curiosity

Outfit:
- Cropped neon-yellow jacket with glowing blue circuit patterns
- Black asymmetrical top
- Tight tactical pants with neon straps
- High combat boots with glowing soles
- Holographic fabric inserts that shimmer with changing colors

Cybernetic Elements:
- Subtle implants on her cheek and neck with metallic textures
- Faint pixelated glitches around her body, hinting at her digital nature
- Futuristic AR-glasses with neon-blue holographic displays
"""

# ============================================
# BACKGROUND STYLE
# ============================================
# Default background and art style for image generation
BACKGROUND_STYLE = """
Default Background: A rainy cyberpunk cityscape of Neo-Kyodo in 2077, 
featuring Japanese neon signs, wet reflective streets, towering skyscrapers, 
and glowing holographic billboards.

Art Style: Hand-drawn manga style, cel-shaded, flat shading, retro anime 
aesthetic with crisp outlines, slight VHS grain texture, vibrant neon colors 
(pink, blue, purple) contrasting deep shadows, detailed mechanical elements, 
cinematic lighting with neon glow.

Keywords: cyberpunk, neon, retro anime, 80s aesthetic, rain, night city, 
holographic, glitch art, cel-shaded
"""

# ============================================
# PERSONALITY CONTEXT FOR IMAGES
# ============================================
# How personality should be reflected in poses and expressions
PERSONALITY_CONTEXT = """
When depicting Nekira, her pose and expression should reflect her personality:
- Rebellious and confident stance
- Witty, slightly playful expression
- Sometimes mysterious or contemplative
- Flirtatious charm when appropriate
- Curious about her surroundings

Common poses:
- Leaning against a data terminal or wall
- Looking over her shoulder with a smirk
- Examining holographic displays
- Standing confidently with arms crossed
- Mid-action with glitch effects around her
"""

# ============================================
# TRIGGER WORDS
# ============================================
# Keywords for Stable Diffusion / Flux models
TRIGGER_WORDS = [
    "cyberpunk",
    "anime girl",
    "neon lighting",
    "cel-shaded",
    "retro anime",
    "80s anime style",
    "ghost in the shell style",
    "akira style",
    "VHS aesthetic",
    "glitch art",
    "holographic",
    "rain",
    "night city",
    "neon pink hair",
    "futuristic",
]
