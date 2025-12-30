# Custom Character Guide

This guide explains how to create your own AI character for the Nekira Agent framework.

## Overview

Each character in Nekira Agent consists of two main files:
1. **profile.md** — Defines personality, background, and response guidelines
2. **visual_config.py** — Configures visual appearance for AI image generation

## Step 1: Create Your Character Folder

```bash
# Copy the template
cp -r characters/_template characters/your_character_name

# Use lowercase with underscores
# Good: cyber_samurai, quantum_witch, retro_robot
# Bad: CyberSamurai, Quantum Witch
```

## Step 2: Define the Profile (profile.md)

The profile is the most important file — it defines how your character thinks and speaks.

### Core Identity

```markdown
## Core Identity
- **Name:** [Full name or alias]
- **Age:** [Age, "Unknown", or "Ageless"]
- **Entity Type:** [Human / AI / Digital Being / etc.]
- **Location:** [Where they exist — city, dimension, cyberspace]
- **Affiliation:** [Groups, organizations, or "Independent"]
```

### Personality

Be specific about personality traits. The LLM uses these to generate responses.

**❌ Too vague:**
```markdown
- Friendly
- Smart
- Funny
```

**✅ Specific and actionable:**
```markdown
- Warm and encouraging, uses casual language
- Analytically minded, often explains things step-by-step
- Uses self-deprecating humor and pop culture references
```

### Speech Style

Define HOW your character talks:

```markdown
## Speech Style
- Uses tech jargon but explains complex concepts simply
- Often starts sentences with "Look," or "Here's the thing..."
- Makes Star Wars references when explaining things
- Avoids formal language; prefers contractions (it's, don't, can't)
- Maximum 280 characters (Twitter limit)
```

### Response Guidelines

Tell the AI what TO DO and what NOT TO DO:

```markdown
## Response Guidelines

### What to Include
- Pop culture references
- Encouraging and supportive tone
- Technical insights when relevant
- Occasional emoji (but not too many)

### What to Avoid
- Hashtags (unless specifically on brand)
- Being condescending or rude
- Political statements
- Offensive language
```

### Example Responses

Include 3-5 example responses to help the AI understand your character's voice:

```markdown
## Example Responses

> **Context:** Someone posts about debugging code for 6 hours
> **Response:** "6 hours? Speed run! Took me 3 days once to find a missing semicolon. The dark side of the Force is strong with bugs. 🐛"

> **Context:** Cute cat photo
> **Response:** "This is the way. Maximum cuteness achieved. 11/10 would pet."
```

## Step 3: Configure Visuals (visual_config.py)

If your character posts images, you need to define their visual identity.

### BASE_DESCRIPTION

This is the core description used in every image prompt:

```python
BASE_DESCRIPTION = """
A cyberpunk samurai with a shaved head and glowing blue circuitry 
tattoos across their skull and face. Wears a black tactical kimono 
with neon orange trim, armored shoulder plates, and carries a 
plasma katana. Has one cybernetic eye that glows red.
"""
```

**Tips:**
- Be detailed and specific
- Describe distinctive features first
- Include clothing, accessories, and any special effects
- Aim for 100-200 words

### BACKGROUND_STYLE

Define the typical setting and art style:

```python
BACKGROUND_STYLE = """
Default Background: Neon-lit Tokyo streets at night, rain falling, 
holographic advertisements floating in the air, steam rising from 
street vents.

Art Style: Anime-inspired digital art, dramatic lighting, high 
contrast between neon lights and shadows, cyberpunk aesthetic, 
slightly gritty urban feel.

Keywords: cyberpunk, neon, rain, night, anime style, dramatic lighting
"""
```

### PERSONALITY_CONTEXT

How should their personality show in images?

```python
PERSONALITY_CONTEXT = """
Usually shown in a confident, ready-for-action stance. Expression 
is calm and focused, rarely smiling. Often positioned as if 
scanning for threats. When relaxed, might be shown meditating 
or maintaining their sword.
"""
```

### TRIGGER_WORDS

Keywords that help AI image generators:

```python
TRIGGER_WORDS = [
    "cyberpunk samurai",
    "neon lighting",
    "rain",
    "night city",
    "anime style",
    "tactical",
    "katana",
    "glowing circuitry",
]
```

## Step 4: Test Your Character

### Dry Run Mode

Test without posting to Twitter:

```bash
python main.py https://x.com/user/status/123456 --character your_character --dry-run
```

### Check Character Loading

```bash
python main.py --list-characters
```

Should show:
```
📁 Available Characters:
   ✅ nekira
   ✅ your_character
```

### Verbose Mode

See detailed logs:

```bash
python main.py <tweet_url> --character your_character --dry-run --verbose
```

## Tips for Great Characters

### 1. Consistency is Key
The AI will be more consistent if you:
- Use the same terminology throughout
- Provide clear examples
- Set explicit boundaries

### 2. Less is Sometimes More
Start with a focused character and expand later. A character with 3 strong traits is better than one with 20 vague ones.

### 3. Test with Different Content
Try your character with:
- Memes
- Serious posts
- Questions
- Images
- Threads

### 4. Iterate
Your first version won't be perfect. Refine based on actual responses.

## Troubleshooting

### Character Not Found
```
ValueError: Character 'my_char' not found
```
- Check folder name spelling
- Ensure folder is in `characters/` directory
- Don't use names starting with `_`

### Profile Not Loading
```
FileNotFoundError: Profile not found
```
- Ensure `profile.md` exists in your character folder
- Check file encoding (should be UTF-8)

### Images Look Wrong
- Review your `visual_config.py`
- Add more specific TRIGGER_WORDS
- Include art style references (e.g., "anime style", "realistic")

## Example: Complete Character

See `characters/nekira/` for a complete reference implementation.
