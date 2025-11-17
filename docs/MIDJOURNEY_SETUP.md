# Midjourney Video Setup Guide

## Overview
Midjourney Video allows you to create video content using Midjourney's AI. Currently, Midjourney doesn't have an official public API, so there are a few options to integrate it.

## Integration Options

### Option 1: Unofficial API Services
There are third-party services that provide Midjourney API access:

#### Recommended Services:
1. **Midjourney API by GoAPI**
   - Website: https://www.goapi.ai/
   - Pricing: Pay-per-use
   - Setup:
     ```bash
     # Add to .env
     MIDJOURNEY_API_KEY=your_goapi_key
     MIDJOURNEY_API_URL=https://api.goapi.ai/mj/v2
     ```

2. **UseAPI**
   - Website: https://useapi.net/
   - Pricing: Subscription-based
   - Setup:
     ```bash
     # Add to .env
     MIDJOURNEY_API_KEY=your_useapi_key
     MIDJOURNEY_API_URL=https://api.useapi.net/v1
     ```

3. **Thenextleg**
   - Website: https://www.thenextleg.io/
   - API-first Midjourney service
   - Setup:
     ```bash
     # Add to .env
     MIDJOURNEY_API_KEY=your_thenextleg_key
     MIDJOURNEY_API_URL=https://api.thenextleg.io/v2
     ```

### Option 2: Self-Hosted Solution
You can run your own Midjourney bot interface:

1. **Requirements:**
   - Midjourney subscription ($10-60/month)
   - Discord account
   - Server to run the bot

2. **Setup:**
   - Create a Discord bot
   - Join Midjourney Discord server
   - Use Discord bot to send commands
   - Parse image/video results

### Option 3: Official API (When Available)
Midjourney is working on an official API. Check their website for updates:
- Website: https://www.midjourney.com/
- Discord: https://discord.gg/midjourney

## Current Implementation

### Service File Location
`app/services/image/midjourney_service.py` (to be created)

### Required Implementation
```python
class MidjourneyService(BaseImageProvider):
    """Midjourney API integration."""

    async def generate_image(self, prompt: str, **kwargs) -> ImageResponse:
        """Generate image using Midjourney."""
        # Implementation depends on chosen API provider
        pass

    async def generate_video(self, prompt: str, **kwargs) -> VideoResponse:
        """Generate video using Midjourney Video."""
        # Implementation depends on chosen API provider
        pass
```

## Setup Steps (Using Third-Party API)

### 1. Choose API Provider
Select one of the services listed above based on:
- Pricing model
- Features needed
- Reliability requirements

### 2. Get API Key
1. Sign up for the chosen service
2. Subscribe to a plan
3. Generate API key from dashboard

### 3. Configure Bot
Add to `.env` file:
```bash
MIDJOURNEY_API_KEY=your_api_key_here
MIDJOURNEY_API_URL=https://api.provider.com/v1
MIDJOURNEY_PROVIDER=goapi  # or useapi, thenextleg
```

### 4. Install Dependencies
```bash
pip install aiohttp  # Already installed
```

### 5. Test Connection
```bash
python scripts/test_midjourney.py
```

## Usage in Bot
Once configured:
1. Click "Создать фото" → "Midjourney"
2. Or "Создать видео" → "Midjourney Video"
3. Send text description
4. Wait for generation (1-3 minutes for images, 3-5 minutes for videos)
5. Receive result

## Token Costs
- **Image generation:** ~3,000 tokens
- **Video generation:** ~10,000 tokens

## API Rate Limits
Varies by provider:
- GoAPI: ~30 requests/minute
- UseAPI: Based on subscription tier
- Thenextleg: ~20 requests/minute

## Common Issues

### Issue: "API key invalid"
- Verify API key is correct
- Check if subscription is active
- Ensure API key has necessary permissions

### Issue: "Generation timeout"
- Midjourney can take time (2-5 minutes)
- Check provider status page
- Increase timeout in code if needed

### Issue: "Content filtered"
- Midjourney has content policies
- Modify prompt to avoid banned terms
- Check provider's content guidelines

## Pricing Comparison

### GoAPI
- Basic: $0.05 per image
- Video: $0.15 per video
- No monthly fee

### UseAPI
- Starter: $29/month (500 generations)
- Pro: $79/month (2000 generations)
- Enterprise: Custom pricing

### Thenextleg
- Pay-as-you-go: $0.04 per image
- Monthly plans available

## Alternative Solutions

If official Midjourney is not feasible, consider:
1. **Stable Diffusion** (already implemented)
2. **DALL-E 3** (OpenAI)
3. **Recraft AI**
4. **Leonardo AI**

## Support
For setup help: @gigavidacha

## Resources
- [Midjourney Documentation](https://docs.midjourney.com/)
- [GoAPI Docs](https://www.goapi.ai/midjourney-api)
- [UseAPI Docs](https://docs.useapi.net/)
- [Thenextleg Docs](https://docs.thenextleg.io/)

## Notes
- This is a workaround until official API is available
- Third-party APIs may have additional costs
- Terms of service vary by provider
- Always check current pricing and availability
