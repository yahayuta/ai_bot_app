# AI Bot App

A multi-platform AI chatbot with advanced image generation, powered by OpenAI, Gemini, and Stability AI.

## 🚀 Features

- **Multi-Platform Support**
  - LINE Messaging API integration
  - Facebook Messenger integration
  - Webhook handling for both platforms

- **AI Capabilities**
  - Text Chat (OpenAI GPT, Google Gemini)
  - Image Generation (DALL-E, Stability AI)
  - Voice Processing (OpenAI Whisper)
  - Automatic provider selection

- **Enhanced Image Generation**
  - Smart prompt engineering
  - Multiple art styles support
  - Quality-focused generation
  - Automatic style enhancement

- **Data Management**
  - BigQuery chat history
  - Google Cloud Storage for images
  - Persistent conversation tracking
  - Automatic data cleanup

## 📁 Project Structure

```
ai_bot_app/
├── README.md                    # Main project documentation
├── main.py                      # Flask application entry point
├── handle_line.py              # LINE messaging API handler
├── handle_facebook.py          # Facebook Messenger API handler
├── module_enhanced_image.py    # Enhanced image generation system
├── module_prompt_builder.py    # Prompt engineering framework
├── module_openai.py            # OpenAI API integration
├── module_stability.py         # Stability AI integration
├── module_gemini.py            # Google Gemini integration
├── module_gcp_storage.py       # Google Cloud Storage
├── model_chat_log.py           # Chat log management
├── module_common.py            # Common data and categories
├── prompt_config.py            # Prompt configuration
├── prompt_templates.py         # Prompt templates and examples
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
├── LICENSE                     # Project license
└── docs/                       # Additional documentation
    ├── INDEX.md                # Documentation navigation
    ├── IMAGE_GENERATION_ENHANCEMENT.md  # Image generation guide
    └── OPTIMIZATION_SUMMARY.md          # Code optimization details
```

## ⚡ Quick Start

### Prerequisites

- Python 3.10 or higher
- Docker (optional)
- API Keys:
  - OpenAI API key
  - Stability AI API key
  - LINE Messaging API token
  - Facebook Messenger token
- Google Cloud (optional):
  - Project set up
  - BigQuery enabled
  - Cloud Storage enabled
  - Service account with proper permissions

### 1. Clone and Install

```bash
# Clone repository
git clone <repository-url>
cd ai_bot_app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# On Windows PowerShell:
$env:OPENAI_TOKEN = "your_openai_key"
$env:STABILITY_KEY = "your_stability_key"
$env:LINE_API_TOKEN = "your_line_token"
$env:FACEBOOK_ACCESS_TOKEN = "your_facebook_token"

# On Unix/MacOS:
export OPENAI_TOKEN=your_openai_key
export STABILITY_KEY=your_stability_key
export LINE_API_TOKEN=your_line_token
export FACEBOOK_ACCESS_TOKEN=your_facebook_token
```

### 3. Run the Application

```bash
python main.py
```

### 4. Test Image Generation

Send these commands to your LINE or Facebook bot:

```bash
genimg cat in garden
genanime cute girl with blue hair
help
```

## 🛠 Detailed Setup Guide

### Setting up Environment Files

Create a `.env` file in the project root directory:

```bash
# Required API Keys
OPENAI_TOKEN=your_openai_key
STABILITY_KEY=your_stability_key
LINE_API_TOKEN=your_line_token
FACEBOOK_ACCESS_TOKEN=your_facebook_token

# Optional Configuration
PORT=8080
```

For Google Cloud integration (optional):

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
```

### Development Setup

Create and activate Python virtual environment:

```bash
# Create environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Unix/MacOS
source venv/bin/activate

# Verify Python version
python --version  # Should be 3.10 or higher
```

Install project dependencies:

```bash
# Install required packages
pip install -r requirements.txt

# Optional: Install development packages
pip install -r requirements-dev.txt
```

### Docker Deployment

Using Docker Compose (recommended):

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

Manual Docker deployment:

```bash
# Build image
docker build -t ai-bot-app .

# Run container
docker run -p 8080:8080 --env-file .env ai-bot-app
```

The application will be available at `http://localhost:8080`

## 🎨 Image Generation System

### Enhanced Prompt Engineering

The application features a sophisticated prompt engineering system that automatically enhances user inputs for better image generation results.

### Available Commands

#### Basic Commands

- `genimg <prompt>` - OpenAI DALL-E with enhanced prompts
- `genimgsd <prompt>` - Stability AI with enhanced prompts
- `genauto <prompt>` - Auto-select best provider

#### Specialized Commands

- `genanime <description>` - Anime-style character generation
- `genphoto <subject>` - Photorealistic image generation
- `genrandom [subject]` - Random artwork with random style

#### Help Commands

- `help` or `image help` - Show detailed usage instructions
- `reset` - Clear chat history

#### Structured Prompts

Use the `|` separator to specify components:

```text
subject | style:anime | location:Tokyo | art:Studio Ghibli style
dragon | style:realistic | location:medieval castle | art:oil painting
robot | style:cartoon | location:space station | art:pixel art
```

### Examples

```text
genimg cat in garden
genanime cute girl with blue hair
genphoto beautiful sunset over mountains
genauto dragon | style:anime | art:watercolor
genrandom cat
cat | style:anime | location:Tokyo | art:Studio Ghibli style
```

### Quality Improvements

**Before Enhancement:**

```text
Input: "cat"
Output: "cat" (basic prompt)
```

**After Enhancement:**

```text
Input: "cat"
Output: "cat, high quality, detailed, professional, award winning"
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_TOKEN` | OpenAI API key | Yes | - |
| `STABILITY_KEY` | Stability AI API key | Yes | - |
| `LINE_API_TOKEN` | LINE Bot API token | Yes | - |
| `FACEBOOK_ACCESS_TOKEN` | Facebook Page access token | Yes | - |
| `PORT` | Application port | No | 8080 |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud Project ID | For GCP | - |
| `GOOGLE_APPLICATION_CREDENTIALS` | GCP Service Account Key | For GCP | - |

### API Setup

#### OpenAI

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account and get your API key
3. Set `OPENAI_TOKEN` environment variable

#### Stability AI

1. Visit [Stability AI](https://platform.stability.ai/)
2. Create an account and get your API key
3. Set `STABILITY_KEY` environment variable

#### LINE Bot

1. Visit [LINE Developers](https://developers.line.biz/)
2. Create a new provider and channel
3. Get your Channel Access Token
4. Set `LINE_API_TOKEN` environment variable
5. Configure webhook URL: `https://your-domain.com/openai_gpt_line`

#### Facebook Messenger

1. Visit [Facebook Developers](https://developers.facebook.com/)
2. Create a new app and page
3. Get your Page Access Token
4. Set `FACEBOOK_ACCESS_TOKEN` environment variable
5. Configure webhook URL: `https://your-domain.com/facebook_webhook`

#### Google Cloud Platform (for Cloud Run deployment)

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable required APIs:

   - Cloud Run API
   - Cloud Storage API
   - BigQuery API

4. Set up service account with appropriate permissions
5. Set `GOOGLE_CLOUD_PROJECT` environment variable
6. Configure `GOOGLE_APPLICATION_CREDENTIALS` if using service account key

## 📚 Documentation

### Available Documentation

- **[Image Generation Enhancement](docs/IMAGE_GENERATION_ENHANCEMENT.md)** - Advanced image generation features
- **[Code Optimization Summary](docs/OPTIMIZATION_SUMMARY.md)** - Performance improvements and optimizations
- **[Documentation Index](docs/INDEX.md)** - Complete documentation navigation

### Quick Navigation

- **New Users**: Start here, then check [Image Generation Guide](docs/IMAGE_GENERATION_ENHANCEMENT.md)
- **Developers**: Review [Optimization Summary](docs/OPTIMIZATION_SUMMARY.md) for code improvements
- **Contributors**: Check [Documentation Index](docs/INDEX.md) for all resources

## 🏗 Architecture

### Core Components

#### Image Generation System
- **Enhanced Prompt Builder**: Automatically enhances user prompts
- **Multi-Provider Support**: OpenAI DALL-E and Stability AI
- **Intelligent Provider Selection**: Chooses best provider based on prompt
- **Quality Boosters**: Automatic quality enhancement

#### Messaging Platforms
- **LINE Integration**: Full LINE Bot API support
- **Facebook Integration**: Facebook Messenger API support
- **Voice Processing**: Audio transcription and response
- **Chat History**: Persistent conversation management

#### Cloud Services
- **Google Cloud Storage**: Automatic image upload
- **BigQuery**: Chat log storage and analytics
- **Google Gemini**: Additional AI capabilities

### Module Structure

```
module_enhanced_image.py  # Main image generation orchestrator
module_prompt_builder.py  # Prompt engineering framework
module_openai.py         # OpenAI API integration
module_stability.py      # Stability AI integration
module_gemini.py         # Google Gemini integration
module_gcp_storage.py    # Google Cloud Storage
model_chat_log.py        # Chat log management
module_common.py         # Shared data and categories
prompt_config.py         # Configuration and validation
prompt_templates.py      # Templates and examples
```

## 🚀 Deployment

### Local Development

```bash
python main.py
```

### Docker Containers

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t ai-bot-app .
docker run -p 8080:8080 ai-bot-app
```

### Google Cloud Run Deployment

Update your environment variables for API keys and GCP project info, then deploy:

```bash
# Deploy to Google Cloud Run
gcloud run deploy ai-bot-app \
  --allow-unauthenticated \
  --region=asia-northeast1 \
  --project=yahayuta \
  --source .
```

**Note**: After deployment, update your LINE and Facebook webhook URLs to point to your Cloud Run service URL:

- LINE Webhook: `https://ai-bot-app-xxxxx-xx.a.run.app/openai_gpt_line`
- Facebook Webhook: `https://ai-bot-app-xxxxx-xx.a.run.app/facebook_webhook`

### Production Deployment Options

1. **Google Cloud Run** (Recommended)

   - Serverless deployment
   - Automatic scaling
   - Built-in SSL certificates
   - Easy environment variable management

2. **Traditional Server**

   - Set up a reverse proxy (nginx/Apache)
   - Configure SSL certificates
   - Set up environment variables
   - Deploy with Docker or directly with Python

3. **Other Cloud Platforms**

   - AWS Elastic Beanstalk
   - Azure App Service
   - Heroku
   - DigitalOcean App Platform

## 🧪 Testing

### Unit Tests

```bash
# Test prompt validation
python -c "import prompt_config; print(prompt_config.validate_prompt('test'))"

# Test image generation
python -c "import module_enhanced_image; print('Module loaded successfully')"
```

### Integration Tests

1. Test LINE webhook endpoint
2. Test Facebook webhook endpoint
3. Test image generation commands
4. Test voice processing

## 🔍 Troubleshooting

### Common Issues

#### Image Generation Fails

- Check API keys are set correctly
- Verify internet connectivity
- Check provider-specific error messages

#### Webhook Not Receiving Messages

- Verify webhook URL is correct
- Check server is accessible from internet
- Verify SSL certificate (required for production)

#### Voice Processing Issues

- Ensure audio file format is supported
- Check OpenAI API quota
- Verify file permissions

### Debug Mode

```bash
# Enable debug logging
export FLASK_DEBUG=1
python main.py
```

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Install development dependencies
4. Make your changes
5. Add tests if applicable
6. Submit a pull request

### Code Standards

- Follow PEP 8 style guidelines
- Add type hints where appropriate
- Include docstrings for functions
- Write tests for new features

### Testing Guidelines

- Unit tests for all new functions
- Integration tests for API endpoints
- Test image generation with various prompts
- Verify error handling

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help

- Check the [documentation](docs/INDEX.md)
- Review [troubleshooting section](#-troubleshooting)
- Open an issue on GitHub

### Reporting Issues

When reporting issues, please include:

- Operating system and Python version
- Error messages and stack traces
- Steps to reproduce the issue
- Environment configuration (without sensitive data)

### Feature Requests

- Check existing issues first
- Provide detailed use case description
- Include mockups or examples if applicable

---

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Maintainer**: AI Bot App Team
