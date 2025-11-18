# Veo 3.1 Setup Guide

## Overview
Veo 3.1 is Google's latest video generation model, now available via the Gemini API. This guide will help you set up Veo 3.1 for the AI bot.

**Updated:** November 2025 - Now uses Gemini API (google-generativeai library)

## Prerequisites
- Google Account
- Google AI Studio API access
- Admin access to the bot configuration

## Setup Steps

### 1. Get Google Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key (starts with `AIza...`)

**Important:** Keep your API key secure and never commit it to version control!

### 2. Configure Bot

Add the API key to your `.env` file:

```bash
# Google Gemini API Key for Veo 3.1
GOOGLE_GEMINI_API_KEY=AIzaSy...your-key-here
```

**Alternative:** You can also use `GOOGLE_AI_API_KEY` as the variable name.

### 3. Install Required Packages

The required package is already in `requirements.txt`:

```bash
pip install google-generativeai==0.3.2
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

### 4. Verify Installation

Run the bot and check logs for successful initialization:

```bash
python main.py
```

Look for:
```
INFO     veo_initialized    api_key_present=True
```

## Usage in Bot

Once configured, users can generate videos in multiple ways:

### Method 1: Direct Command
```
/veo
```
This opens the video creation menu where users can select Veo 3.1.

### Method 2: Main Menu Navigation
1. Start the bot: `/start`
2. Click "🎞 Создать видео"
3. Select "🌊 Veo 3.1"
4. Send a text description of the desired video

### Method 3: Video Menu
From the main menu, users can navigate to the video creation interface.

## Video Generation Process

1. **User sends prompt**: Describe the video in detail
   - Example: "a golden retriever playing in a field of sunflowers at sunset"

2. **Bot processes**:
   - Checks user has sufficient tokens (~15,000 required)
   - Initializes Veo 3.1 API
   - Submits generation request

3. **Generation time**: 1-3 minutes (users see progress updates)

4. **Video delivery**: Bot sends the generated video directly in Telegram

## Technical Details

### Model Information
- **Model ID:** `veo-3.1-generate-preview`
- **Provider:** Google Gemini API
- **Default duration:** 8 seconds
- **Default resolution:** 720p
- **Default aspect ratio:** 16:9

### Supported Parameters
- **Aspect ratios:** 1:1, 16:9, 9:16, 4:3, 3:4
- **Resolutions:** 720p, 1080p
- **Duration:** 8 seconds base (can be extended up to 141 seconds)
- **Negative prompts:** Optional - describe what to avoid

### API Architecture
The implementation uses:
- `google.genai.Client()` for API access
- Async/await pattern for non-blocking operations
- Polling mechanism for operation status
- Automatic file download and storage

## Pricing & Token Costs

### Token Cost
- **Veo 3.1:** ~15,000 tokens per 8-second video

### Tariff Examples
For a user to generate one Veo video:
- **7-day plan:** 150,000 tokens = ~10 videos
- **14-day plan:** 250,000 tokens = ~16 videos
- **30-day plan (1M):** 1,000,000 tokens = ~66 videos

### Google API Pricing
Check current pricing at [Google AI Pricing](https://ai.google.dev/pricing)

## Troubleshooting

### Error: "API key not configured"
**Solution:**
1. Verify `GOOGLE_GEMINI_API_KEY` is set in `.env`
2. Restart the bot after adding the key
3. Check for typos in the key

### Error: "google-generativeai library not available"
**Solution:**
```bash
pip install google-generativeai
```

### Error: "Permission denied" or "API key invalid"
**Solution:**
1. Verify your API key is active in [Google AI Studio](https://aistudio.google.com/apikey)
2. Check if you've enabled the Gemini API
3. Try generating a new API key

### Error: "Insufficient tokens"
**Solution:**
- User needs to purchase a subscription via `/shop`
- Required: at least 15,000 tokens
- Show available balance with `/profile`

### Error: "Video generation timed out"
**Possible causes:**
- Google API service temporary issue
- Network connectivity problems
- High load on Google servers

**Solution:**
- Retry after a few minutes
- Check [Google API Status](https://status.cloud.google.com/)

### Video quality issues
**Tips for better results:**
- Use detailed, descriptive prompts
- Specify camera angles, lighting, mood
- Use negative prompts to avoid unwanted elements
- Example: "close-up shot of...", "cinematic lighting", "4K quality"

## Migration from Vertex AI

If you previously used Vertex AI for Veo:

### What Changed
- ❌ **Old:** Vertex AI (`google-cloud-aiplatform`)
- ✅ **New:** Gemini API (`google-generativeai`)

### Configuration Changes
- ❌ **Old:** `GOOGLE_CLOUD_PROJECT`, `GOOGLE_APPLICATION_CREDENTIALS`
- ✅ **New:** `GOOGLE_GEMINI_API_KEY`

### Code Changes
- ❌ **Old:** `VideoGenerationModel.from_pretrained("veo-3.1")`
- ✅ **New:** `client.models.generate_videos(model="veo-3.1-generate-preview")`

### Migration Steps
1. Get Gemini API key from Google AI Studio
2. Add `GOOGLE_GEMINI_API_KEY` to `.env`
3. Update code (already done in this version)
4. Remove old Vertex AI credentials (optional)

## Example Prompts

### Good Prompts
```
"A serene beach at sunset with gentle waves and seagulls flying"

"Close-up of a steaming cup of coffee on a wooden table, morning light"

"Time-lapse of city traffic at night with car light trails"

"A cat playing with a ball of yarn in slow motion"
```

### Advanced Prompts with Parameters
```
Prompt: "Cinematic shot of mountain landscape with morning fog"
Aspect ratio: 16:9
Resolution: 1080p
Negative prompt: "people, buildings, cars"
```

## Best Practices

1. **Prompt Engineering**
   - Be specific and descriptive
   - Include camera angles and movement
   - Specify lighting and mood
   - Use cinematic terminology

2. **Resource Management**
   - Monitor token usage
   - Set appropriate limits for free users
   - Consider video generation quotas

3. **Error Handling**
   - Implement retry logic for transient failures
   - Provide clear error messages to users
   - Log all API interactions for debugging

4. **User Experience**
   - Show progress updates during generation
   - Estimate wait times accurately
   - Provide example prompts to users

## API Rate Limits

Google Gemini API has rate limits:
- **Requests per minute:** Check your tier
- **Concurrent requests:** Limited
- **Daily quota:** Based on your API key tier

For production use, consider:
- Implementing request queuing
- Adding rate limit monitoring
- Upgrading to higher API tiers

## Support & Resources

### Documentation
- [Google Gemini API Docs](https://ai.google.dev/docs)
- [Veo Model Card](https://deepmind.google/technologies/veo/)
- [API Reference](https://ai.google.dev/api/rest)

### Getting Help
- Bot support: @gigavidacha
- Google AI Studio: https://aistudio.google.com/
- GitHub Issues: Report bugs in the project repository

### Community
- Share your generated videos
- Exchange prompt tips
- Report issues and improvements

## Security Notes

1. **API Key Security**
   - Never commit API keys to Git
   - Use environment variables
   - Rotate keys periodically
   - Use different keys for dev/prod

2. **User Content**
   - Implement content moderation
   - Follow Google's usage policies
   - Monitor for abuse

3. **Data Privacy**
   - Don't log user prompts unnecessarily
   - Follow GDPR/privacy regulations
   - Secure video storage

## Updates & Changelog

### November 2025
- ✅ Updated to Gemini API (google-generativeai)
- ✅ Simplified setup (API key vs service account)
- ✅ Improved error handling
- ✅ Better progress feedback

### Previous Versions
- Used Vertex AI with service account authentication
- Required Google Cloud Platform project setup
