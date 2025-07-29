import os
from typing import Dict
import module_stability
import module_openai
from module_prompt_builder import prompt_builder

class EnhancedImageGenerator:
    """Enhanced image generator with advanced prompt handling and multiple AI providers."""
    
    def __init__(self):
        self.stability_key = os.environ.get('STABILITY_KEY', '')
        self.openai_key = os.environ.get('OPENAI_TOKEN', '')
    
    def generate_with_enhanced_prompt(self, 
                                    user_input: str, 
                                    provider: str = 'auto',
                                    image_path: str = None) -> Dict:
        """
        Generate image with enhanced prompt processing.
        
        Args:
            user_input: User's prompt or structured input
            provider: 'stability', 'openai', or 'auto'
            image_path: Path to save the generated image
            
        Returns:
            Dict with generation results and metadata
        """
        # Parse user input for structured components
        if '|' in user_input:
            components = prompt_builder.parse_user_input(user_input)
            enhanced_prompt = prompt_builder.build_enhanced_prompt(
                base_prompt=components['base_prompt'],
                style=components['style'],
                location=components['location'],
                art_style=components['art_style']
            )
        else:
            # Simple prompt - apply basic enhancement
            enhanced_prompt = prompt_builder.build_enhanced_prompt(
                base_prompt=user_input
            )
        
        # Choose provider
        if provider == 'auto':
            provider = self._select_best_provider(enhanced_prompt)
        
        # Generate image
        try:
            if provider == 'stability':
                result = self._generate_stability(enhanced_prompt, image_path)
            else:  # openai
                result = self._generate_openai(enhanced_prompt, image_path)
            
            result['enhanced_prompt'] = enhanced_prompt
            result['provider'] = provider
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'enhanced_prompt': enhanced_prompt,
                'provider': provider
            }
    
    def _select_best_provider(self, prompt: str) -> str:
        """Select the best provider based on prompt characteristics."""
        # Stability AI is better for artistic styles and complex compositions
        artistic_keywords = ['oil painting', 'watercolor', 'anime', 'cartoon', 'artistic']
        if any(keyword in prompt.lower() for keyword in artistic_keywords):
            return 'stability'
        
        # OpenAI DALL-E is better for realistic and simple subjects
        return 'openai'
    
    def _generate_stability(self, prompt: str, image_path: str) -> Dict:
        """Generate image using Stability AI."""
        if not self.stability_key:
            raise Exception("Stability AI key not configured")
        
        module_stability.generate(prompt, image_path)
        
        return {
            'success': True,
            'provider': 'stability',
            'prompt': prompt
        }
    
    def _generate_openai(self, prompt: str, image_path: str) -> Dict:
        """Generate image using OpenAI DALL-E."""
        if not self.openai_key:
            raise Exception("OpenAI key not configured")
        
        module_openai.openai_create_image(prompt, image_path)
        
        return {
            'success': True,
            'provider': 'openai',
            'prompt': prompt
        }
    
    def generate_random_artwork(self, subject: str = None, image_path: str = None) -> Dict:
        """Generate artwork with random artistic style."""
        if not subject:
            subject = prompt_builder.get_random_topic()
        
        random_style = prompt_builder.get_random_style()
        random_location = prompt_builder.get_random_location()
        
        enhanced_prompt = prompt_builder.build_enhanced_prompt(
            base_prompt=subject,
            art_style=random_style,
            location=random_location
        )
        
        return self.generate_with_enhanced_prompt(enhanced_prompt, 'auto', image_path)
    
    def generate_anime_character(self, character_description: str, anime_style: str = None, image_path: str = None) -> Dict:
        """Generate anime-style character."""
        enhanced_prompt = prompt_builder.build_anime_prompt(character_description, anime_style)
        return self.generate_with_enhanced_prompt(enhanced_prompt, 'stability', image_path)
    
    def generate_photorealistic(self, subject: str, location: str = None, image_path: str = None) -> Dict:
        """Generate photorealistic image."""
        enhanced_prompt = prompt_builder.build_photorealistic_prompt(subject, location)
        return self.generate_with_enhanced_prompt(enhanced_prompt, 'openai', image_path)

# Global instance
enhanced_generator = EnhancedImageGenerator() 