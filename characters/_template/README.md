# Creating a Custom Character

This guide explains how to create your own AI character for the Nekira Agent framework.

## Quick Start

1. **Copy the template folder:**
   ```bash
   cp -r characters/_template characters/your_character_name
   ```

2. **Edit the profile:**
   Open `characters/your_character_name/profile.md` and fill in your character's details.

3. **Configure visuals:**
   Edit `characters/your_character_name/visual_config.py` to define how your character looks in generated images.

4. **Test your character:**
   ```bash
   python main.py <tweet_url> --character your_character_name --dry-run
   ```

## File Structure

```
characters/
└── your_character_name/
    ├── profile.md        # Character personality and background
    └── visual_config.py  # Visual appearance for image generation
```

## Profile Tips

### Be Specific
Instead of "friendly personality," write "warm and encouraging, uses casual language, often makes jokes to lighten the mood."

### Include Examples
Add example responses in your profile so the AI understands your character's voice.

### Set Boundaries
Clearly state what your character would NOT say or do. This helps maintain consistency.

## Visual Config Tips

### Detailed Descriptions
The more detail you provide, the more consistent your generated images will be.

### Use Trigger Words
Add style-specific keywords that help AI image generators understand your aesthetic.

### Test and Iterate
Generate a few images and refine your descriptions based on results.

## Testing Your Character

1. **Dry run mode** (no actual posting):
   ```bash
   python main.py https://x.com/user/status/123 --character your_character --dry-run
   ```

2. **List available characters:**
   ```bash
   python main.py --list-characters
   ```

## Need Help?

Check the main documentation or look at the `nekira` character as a reference implementation.
