import random
from typing import List, Dict, Optional
import module_common

class PromptBuilder:
    """Enhanced prompt builder for image generation with structured components."""
    
    def __init__(self):
        self.topics = module_common.topic
        self.places = module_common.place
        self.patterns = module_common.pattern
        self.cartoons = module_common.cartoons
    
    def build_enhanced_prompt(self, 
                             base_prompt: str,
                             style: Optional[str] = None,
                             location: Optional[str] = None,
                             art_style: Optional[str] = None,
                             quality_boosters: List[str] = None) -> str:
        """
        Build an enhanced prompt with structured components.
        
        Args:
            base_prompt: The main subject/object to generate
            style: Specific style (e.g., 'anime', 'realistic', 'cartoon')
            location: Setting/background location
            art_style: Artistic style from patterns list
            quality_boosters: List of quality enhancement terms
        """
        components = []
        
        # Base prompt
        components.append(base_prompt.strip())
        
        # Style specification
        if style:
            if style.lower() == 'anime':
                components.append("anime style, high quality, detailed")
            elif style.lower() == 'realistic':
                components.append("photorealistic, highly detailed, professional photography")
            elif style.lower() == 'cartoon':
                components.append("cartoon style, vibrant colors, clean lines")
            elif style.lower() == 'artistic':
                components.append("artistic interpretation, creative composition")
        
        # Location/background
        if location:
            components.append(f"set in {location}")
        
        # Art style
        if art_style:
            if art_style in self.patterns:
                components.append(f"in the style of {art_style}")
            else:
                components.append(art_style)
        
        # Quality boosters
        if quality_boosters:
            components.extend(quality_boosters)
        
        # Default quality boosters if none specified
        else:
            components.extend([
                "high quality",
                "detailed",
                "professional",
                "award winning"
            ])
        
        return ", ".join(components)
    
    def get_random_style(self) -> str:
        """Get a random art style from the patterns list."""
        return random.choice(self.patterns)
    
    def get_random_location(self) -> str:
        """Get a random location from the places list."""
        return random.choice(self.places)
    
    def get_random_topic(self) -> str:
        """Get a random topic from the topics list."""
        return random.choice(self.topics)
    
    def build_anime_prompt(self, subject: str, anime_style: str = None) -> str:
        """Build an anime-style prompt with specific anime references."""
        components = [subject]
        
        if anime_style and anime_style in self.cartoons:
            components.append(f"in the style of {anime_style}")
        else:
            components.append("anime style, official art")
        
        components.extend([
            "high quality",
            "detailed character design",
            "vibrant colors",
            "clean lines"
        ])
        
        return ", ".join(components)
    
    def build_photorealistic_prompt(self, subject: str, location: str = None) -> str:
        """Build a photorealistic prompt."""
        components = [subject]
        
        if location:
            components.append(f"in {location}")
        
        components.extend([
            "photorealistic",
            "highly detailed",
            "professional photography",
            "8K resolution",
            "sharp focus"
        ])
        
        return ", ".join(components)
    
    def parse_user_input(self, user_text: str) -> Dict[str, str]:
        """
        Parse user input to extract prompt components.
        Expected format: "subject | style:value | location:value | art:value"
        """
        parts = user_text.split('|')
        result = {
            'base_prompt': parts[0].strip(),
            'style': None,
            'location': None,
            'art_style': None
        }
        
        for part in parts[1:]:
            part = part.strip()
            if ':' in part:
                key, value = part.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key in ['style', 'location', 'art']:
                    result[f"{key}_style" if key == 'art' else key] = value
        
        return result

# Global instance
prompt_builder = PromptBuilder() 