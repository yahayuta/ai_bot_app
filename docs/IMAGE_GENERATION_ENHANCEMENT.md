# Enhanced Image Generation System

## Overview

This enhancement provides a sophisticated prompt engineering framework for image generation, leveraging multiple AI providers (Stability AI and OpenAI DALL-E) with intelligent prompt enhancement and provider selection.

## Key Features

### 1. **Structured Prompt Building**
- Parse user input with components: `subject | style:value | location:value | art:value`
- Automatic quality boosters based on style
- Provider-specific optimizations

### 2. **Multiple AI Providers**
- **Stability AI**: Best for artistic styles, anime, complex compositions
- **OpenAI DALL-E**: Best for realistic images, simple subjects
- **Auto-selection**: Intelligent provider choice based on prompt content

### 3. **Specialized Commands**
- `genimg` - OpenAI DALL-E with enhanced prompts
- `genimgsd` - Stability AI with enhanced prompts  
- `genauto` - Auto-select best provider
- `genanime` - Anime-style character generation
- `genphoto` - Photorealistic image generation
- `genrandom` - Random artwork with random style

### 4. **Rich Prompt Categories**
- **Topics**: 40+ categories (musicians, movies, places, etc.)
- **Places**: 16+ geographical locations
- **Patterns**: 80+ artistic styles and techniques
- **Cartoons**: 100+ anime and cartoon references

## Usage Examples

### Basic Commands
```
genimg cat in garden
genimgsd dragon flying over mountains
genauto beautiful sunset
```

### Structured Prompts
```
cat | style:anime | location:Tokyo | art:Studio Ghibli style
dragon | style:realistic | location:medieval castle | art:oil painting
robot | style:cartoon | location:space station | art:pixel art
```

### Specialized Generation
```
genanime cute girl with blue hair wearing school uniform
genphoto professional portrait of a businessman
genrandom dragon
```

## Architecture

### Core Modules

1. **`module_prompt_builder.py`**
   - `PromptBuilder` class for structured prompt creation
   - Component parsing and enhancement
   - Style-specific prompt templates

2. **`module_enhanced_image.py`**
   - `EnhancedImageGenerator` class
   - Provider selection logic
   - Error handling and result metadata

3. **`prompt_templates.py`**
   - Example prompts and usage instructions
   - Quality boosters for different styles
   - Template functions

4. **`prompt_config.py`**
   - Configuration settings
   - Validation rules
   - Provider-specific parameters

### Integration Points

- **LINE Handler**: Enhanced with new commands and error handling
- **Facebook Handler**: Can be similarly enhanced
- **Existing Modules**: Leverages `module_common.py` categories

## Configuration

### Environment Variables
```bash
OPENAI_TOKEN=your_openai_key
STABILITY_KEY=your_stability_key
LINE_API_TOKEN=your_line_token
```

### Prompt Enhancement Rules
```python
ENHANCEMENT_RULES = {
    "add_quality_boosters": True,
    "add_style_prefix": True,
    "add_style_suffix": True,
    "auto_select_provider": True,
    "enhance_with_location": True,
    "enhance_with_art_style": True
}
```

## Quality Improvements

### Before Enhancement
```
Input: "cat"
Output: "cat" (basic prompt)
```

### After Enhancement
```
Input: "cat"
Output: "cat, high quality, detailed, professional, award winning"
```

### Structured Input
```
Input: "cat | style:anime | location:Tokyo | art:Studio Ghibli style"
Output: "cat, anime style, high quality, detailed, set in Tokyo, in the style of Studio Ghibli style, detailed character design, vibrant colors, clean lines"
```

## Provider Selection Logic

### Stability AI (Better for)
- Artistic styles (oil painting, watercolor, anime)
- Complex compositions
- Creative interpretations
- Anime and cartoon styles

### OpenAI DALL-E (Better for)
- Realistic images
- Simple subjects
- Professional photography
- Natural scenes

## Error Handling

- **Prompt Validation**: Length, forbidden words, required components
- **Provider Failures**: Automatic fallback and error reporting
- **API Errors**: Detailed error messages for debugging

## Future Enhancements

1. **Prompt Learning**: Analyze successful prompts for optimization
2. **Style Transfer**: Apply learned styles to new prompts
3. **Batch Generation**: Generate multiple variations
4. **Prompt Templates**: User-defined prompt templates
5. **A/B Testing**: Compare different prompt strategies

## Testing

### Test Cases
```python
# Basic enhancement
assert enhanced_prompt("cat") == "cat, high quality, detailed, professional, award winning"

# Structured input
assert enhanced_prompt("cat | style:anime") == "cat, anime style, high quality, detailed character design, vibrant colors, clean lines"

# Provider selection
assert select_provider("anime character") == "stability"
assert select_provider("photorealistic portrait") == "openai"
```

## Performance Considerations

- **Prompt Processing**: Minimal overhead (< 10ms)
- **Provider Selection**: Rule-based, no API calls
- **Error Recovery**: Graceful degradation
- **Memory Usage**: Lightweight, no heavy processing

## Security

- **Input Validation**: Sanitize user inputs
- **Forbidden Words**: Filter inappropriate content
- **API Key Management**: Secure environment variables
- **Error Messages**: No sensitive information exposure 