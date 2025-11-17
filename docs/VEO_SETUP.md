# Veo 3.1 Setup Guide

## Overview
Veo 3.1 is Google's latest video generation model. To use it in the bot, you need to set up Google Cloud Platform and enable the Vertex AI API.

## Prerequisites
- Google Cloud Platform account
- Billing enabled on your GCP project
- Admin access to the bot configuration

## Setup Steps

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your Project ID

### 2. Enable Vertex AI API
1. Go to [Vertex AI API page](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com)
2. Click "Enable"
3. Wait for activation (may take a few minutes)

### 3. Create Service Account
1. Go to IAM & Admin → Service Accounts
2. Click "Create Service Account"
3. Name: `veo-bot-service`
4. Grant roles:
   - `Vertex AI User`
   - `Service Account Token Creator`
5. Click "Done"

### 4. Create Service Account Key
1. Click on the created service account
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose JSON format
5. Save the downloaded file securely

### 5. Configure Bot
1. Upload the service account JSON file to your server
2. Set environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
   ```
3. Or add to `.env` file:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   GOOGLE_CLOUD_PROJECT=your-project-id
   ```

### 6. Install Required Packages
```bash
pip install google-cloud-aiplatform
```

### 7. Test Connection
Run the diagnostic script:
```bash
python scripts/test_veo_connection.py
```

## Usage in Bot
Once configured, users can:
1. Click "Создать видео" → "Veo 3.1"
2. Send text description of the video
3. Wait for generation (may take 2-5 minutes)
4. Receive the generated video

## Pricing
- Veo 3.1: ~$0.10-0.30 per video (varies by duration and resolution)
- Check current pricing: [Vertex AI Pricing](https://cloud.google.com/vertex-ai/pricing)

## Token Costs
- Approximate cost: **12,000 tokens** per video

## Troubleshooting

### Error: "Project not found"
- Verify GOOGLE_CLOUD_PROJECT is set correctly
- Ensure the project exists in your GCP account

### Error: "API not enabled"
- Go to GCP Console → APIs & Services
- Enable "Vertex AI API"
- Wait 5-10 minutes for propagation

### Error: "Permission denied"
- Check service account has `Vertex AI User` role
- Verify service account key is valid and not expired

## Support
For issues, contact: @gigavidacha

## Additional Resources
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Veo API Reference](https://cloud.google.com/vertex-ai/docs/generative-ai/video/generate-video)
