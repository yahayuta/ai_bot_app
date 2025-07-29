"""
Prompt Templates and Examples for Enhanced Image Generation

This module provides example prompts and templates for different types of image generation.
"""

# Example prompts for different styles and subjects
EXAMPLE_PROMPTS = {
    "anime_character": [
        "genanime cute girl with blue hair wearing school uniform",
        "genanime muscular hero with spiky hair and cape",
        "genanime magical girl with pink dress and wand"
    ],
    
    "photorealistic": [
        "genphoto beautiful sunset over mountains",
        "genphoto professional portrait of a businessman",
        "genphoto modern city skyline at night"
    ],
    
    "artistic": [
        "genauto oil painting of a flower garden",
        "genauto watercolor landscape of mountains",
        "genauto digital art of a futuristic city"
    ],
    
    "structured": [
        "cat | style:anime | location:Tokyo | art:Studio Ghibli style",
        "dragon | style:realistic | location:medieval castle | art:oil painting",
        "robot | style:cartoon | location:space station | art:pixel art"
    ],
    
    "random": [
        "genrandom",  # Random topic and style
        "genrandom dragon",  # Specific subject with random style
        "genrandom musician"  # Specific topic with random style
    ]
}

# Usage instructions
USAGE_INSTRUCTIONS = """
Enhanced Image Generation Commands:

1. Basic Commands:
   - genimg <prompt> - OpenAI DALL-E with enhanced prompts
   - genimgsd <prompt> - Stability AI with enhanced prompts
   - genauto <prompt> - Auto-select best provider

2. Specialized Commands:
   - genanime <description> - Anime-style character generation
   - genphoto <subject> - Photorealistic image generation
   - genrandom [subject] - Random artwork with random style

3. Structured Prompts (use | to separate components):
   - subject | style:anime | location:Tokyo | art:Studio Ghibli style
   - subject | style:realistic | location:forest | art:oil painting

4. Examples:
   - genanime cute girl with blue hair
   - genphoto beautiful sunset over mountains
   - genauto dragon | style:anime | art:watercolor
   - genrandom cat
   - cat | style:realistic | location:garden | art:photography

5. Available Styles:
   - anime, realistic, cartoon, artistic
   - Any art style from the patterns list

6. Available Locations:
   - Any place from the places list
   - Custom locations

7. Available Art Styles:
   - All patterns from the patterns list
   - Custom art styles
"""

def get_example_prompts(category: str = None) -> dict:
    """Get example prompts for a specific category or all categories."""
    if category:
        return EXAMPLE_PROMPTS.get(category, [])
    return EXAMPLE_PROMPTS 