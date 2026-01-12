# Billing System Reference

## Token Price
**1 token = 0.000588 RUB**

## Token Packages

| Duration | Tokens | Price (RUB) |
|----------|--------|-------------|
| 7 days   | 150,000 | 88 |
| 14 days  | 250,000 | 176 |
| 21 days  | 500,000 | 260 |
| 30 days  | 1,000,000 | 537 |
| 30 days  | 5,000,000 | 2,511 |

## Text Models (Dynamic Billing)

Formula: `tokens_spent = base_tokens + (prompt_tokens + completion_tokens) * per_gpt_token`

| Model | Display Name | Base Tokens | Per GPT Token |
|-------|--------------|-------------|---------------|
| gpt-4.1-mini | GPT-4.1 Mini | 140 | 1.6 |
| gpt-4o | GPT-4o | 520 | 6.8 |
| gpt-5-mini | GPT-5 Mini | 170 | 1.8 |
| o3-mini | O3 Mini | 260 | 3.1 |
| deepseek-chat | DeepSeek Chat | 180 | 2.0 |
| deepseek-r1 | DeepSeek R1 | 300 | 3.4 |
| gemini-flash-2.0 | Gemini Flash 2.0 | 130 | 1.3 |
| nano-banana-text | nano Banana (text) | 110 | 1.1 |
| sonar | Sonar (with search) | 220 | 2.6 |
| sonar-pro | Sonar Pro | 260 | 3.0 |
| claude-4 | Claude 4 | 320 | 3.6 |

### Example Calculation

For GPT-4o with 500 prompt tokens + 1000 completion tokens:
```
tokens_spent = 520 + (500 + 1000) * 6.8 = 520 + 10,200 = 10,720 tokens
cost_rub = 10,720 * 0.000588 = 6.3 RUB
```

## Image Models (Fixed Billing)

| Model | Display Name | Tokens per Generation |
|-------|--------------|----------------------|
| dalle3 | DALL·E 3 | 8,500 |
| midjourney | Midjourney | 13,000 |
| nano-banana-image | Nano Banana | 5,500 |
| banana-pro | Banana PRO | 22,000 |
| stable-diffusion | Stable Diffusion | 6,000 |
| recraft | Recraft | 6,500 |
| kling-image | Kling AI | 7,500 |
| face-swap | Face Swap | 10,000 |

## Video Models (Fixed Billing)

| Model | Display Name | Tokens per Generation |
|-------|--------------|----------------------|
| sora2 | Sora 2 (10 sec) | 43,000 |
| veo-3.1-fast | Veo 3.1 Fast | 98,000 |
| midjourney-video-sd | Midjourney Video SD | 75,000 |
| midjourney-video-hd | Midjourney Video HD | 225,000 |
| kling-video | Kling (10 sec) | 550,000 |
| kling-effects | Kling Effects | 90,000 |
| hailuo | Hailuo | 78,000 |
| luma | Luma | 85,000 |

## Implementation Notes

### Text Models
- Billing occurs AFTER API call when exact token counts are known
- If API doesn't return token counts, estimation is used based on text length (~4 chars = 1 token)
- Minimum balance check before API call ensures user has enough for base cost

### Image/Video Models
- Billing occurs BEFORE generation (fixed cost known upfront)
- No refunds if generation fails (user should contact support)

### User Interface
- Text models: Show dynamic billing info (base + multiplier)
- Image/Video models: Show exact cost in description
- All models: Show remaining balance and estimated generations available

## Files Modified

1. **Core Configuration:**
   - `app/core/billing_config.py` - New billing configuration for all models
   - `app/services/subscription/subscription_service.py` - Updated tariffs

2. **Billing Service:**
   - `app/services/billing/billing_service.py` - New service for cost calculation and charging
   - `app/database/repositories/ai_request.py` - New repository for AI requests

3. **AI Services:**
   - `app/services/ai/base.py` - Extended AIResponse with prompt_tokens and completion_tokens
   - `app/services/ai/openai_service.py` - Updated to return token usage details

4. **Bot Handlers:**
   - `app/bot/handlers/text_ai.py` - Completely rewritten with new billing system
   - `app/bot/handlers/media_handler.py` - Updated prices for video/image models

## Testing

To test the billing system:

1. **Create a test user with tokens:**
```python
from app.services.subscription.subscription_service import SubscriptionService
# Add tokens to test user
```

2. **Test text model billing:**
- Send request to GPT-4o
- Check that tokens are calculated correctly
- Verify tokens deducted from balance

3. **Test image model billing:**
- Generate with DALL-E 3
- Verify 8,500 tokens deducted

4. **Test video model billing:**
- Generate with Veo 3.1
- Verify 98,000 tokens deducted

## Migration Notes

### For Existing Users
- Existing subscriptions remain valid
- Existing token balances are preserved
- New billing applies to all NEW requests

### Backward Compatibility
- Legacy model IDs (gpt-4, claude, gemini) are mapped to new IDs
- Old TARIFFS remain available for existing subscriptions
- Database schema unchanged (no migration needed)

## Future Enhancements

1. **More Accurate Token Counting:**
   - Implement token counting for Anthropic, Google, DeepSeek models
   - Add pre-request token estimation using tiktoken

2. **Cost Optimization:**
   - Cache frequently used prompts
   - Implement token usage analytics
   - Add budget limits and alerts

3. **User Features:**
   - Show detailed billing history
   - Export usage reports
   - Set up auto-refill

4. **Admin Features:**
   - Adjust prices without code changes
   - Create promotional packages
   - Generate revenue reports
