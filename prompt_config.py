"""
Prompt Configuration for Image Generation Tuning

This module contains configuration settings for prompt enhancement and generation parameters.
"""

# Default quality boosters for different image types
DEFAULT_QUALITY_BOOSTERS = {
    "general": [
        "high quality",
        "detailed",
        "professional",
        "award winning"
    ],
    
    "anime": [
        "anime style",
        "high quality",
        "detailed character design",
        "vibrant colors",
        "clean lines",
        "official art"
    ],
    
    "realistic": [
        "photorealistic",
        "highly detailed",
        "professional photography",
        "8K resolution",
        "sharp focus"
    ],
    
    "artistic": [
        "masterpiece",
        "award winning artwork",
        "professional composition",
        "beautiful lighting",
        "detailed brushwork"
    ]
}

# Provider-specific prompt enhancements
PROVIDER_ENHANCEMENTS = {
    "stability": {
        "artistic_keywords": [
            "oil painting", "watercolor", "anime", "cartoon", "artistic",
            "digital art", "illustration", "concept art"
        ],
        "quality_boosters": [
            "masterpiece", "award winning", "professional artwork"
        ]
    },
    
    "openai": {
        "realistic_keywords": [
            "photorealistic", "photography", "realistic", "natural"
        ],
        "quality_boosters": [
            "highly detailed", "professional", "sharp focus"
        ]
    }
}

# Prompt validation rules
VALIDATION_RULES = {
    "min_length": 3,
    "max_length": 1000,
    "forbidden_words": [
        "nude", "naked", "explicit", "sexual", "violence", "blood"
    ]
}

def get_quality_boosters(style: str = "general") -> list:
    """Get quality boosters for a specific style."""
    return DEFAULT_QUALITY_BOOSTERS.get(style, DEFAULT_QUALITY_BOOSTERS["general"])

def get_provider_enhancements(provider: str) -> dict:
    """Get provider-specific enhancements."""
    return PROVIDER_ENHANCEMENTS.get(provider, {})

def validate_prompt(prompt: str) -> tuple[bool, str]:
    """Validate a prompt according to the rules."""
    if len(prompt) < VALIDATION_RULES["min_length"]:
        return False, f"Prompt too short (minimum {VALIDATION_RULES['min_length']} characters)"
    
    if len(prompt) > VALIDATION_RULES["max_length"]:
        return False, f"Prompt too long (maximum {VALIDATION_RULES['max_length']} characters)"
    
    for word in VALIDATION_RULES["forbidden_words"]:
        if word.lower() in prompt.lower():
            return False, f"Forbidden word detected: {word}"
    
    return True, "Valid prompt" 