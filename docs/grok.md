Grok 4.3
The most truth-seeking large language model in the world.

Context
1 million tokens
Input
$1.25 / 1M tokens
Output
$2.50 / 1M tokens

import os
from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
)

chat = client.chat.create(model="grok-4.3")
chat.append(system("You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."))
chat.append(user("What is the meaning of life, the universe, and everything?"))
response = chat.sample()

print(response)


#### Introduction

# What is Grok?

Grok is a family of Large Language Models (LLMs) developed by [xAI](https://x.ai).

Inspired by the Hitchhiker's Guide to the Galaxy, Grok is a maximally truth-seeking AI that provides insightful, unfiltered truths about the universe.

xAI offers an API for developers to programmatically interact with our Grok [models](/developers/models). The same models power our consumer facing services such as [Grok.com](https://grok.com), the [iOS](https://apps.apple.com/us/app/grok/id6670324846) and [Android](https://play.google.com/store/apps/details?id=ai.x.grok) apps, as well as [Grok in X experience](https://grok.x.com).

## What is the xAI API? How is it different from Grok in other services?

The xAI API is a toolkit for developers to integrate xAI's Grok models into their own applications, the xAI API provides the building blocks to create new AI experiences.

To get started building with the xAI API, please head to [The Hitchhiker's Guide to Grok](/developers/quickstart).

## xAI API vs Grok in other services

| Category                      | xAI API                          | Grok.com                          | Mobile Apps                  | Grok in 𝕏                          |
|-------------------------------|----------------------------------|-----------------------------------|----------------------------|------------------------------------|
| **Accessible**                | API (api.x.ai)                   | grok.com + PWA (Android)          | App Store / Play Store     | X.com + 𝕏 apps                     |
| **Billing**                   | xAI                              | xAI / 𝕏                           | xAI / 𝕏                    | 𝕏                                  |
| **Programming Required**      | Yes                              | No                                | No                         | No                                 |
| **Description**               | Programmatic access for developers | Full-featured web AI assistant   | Mobile AI assistant        | X-integrated AI (fewer features)   |

Because these are separate offerings, your purchase on X (e.g. X Premium) won't affect your service status on xAI API, and vice versa.

This documentation is intended for users using xAI API.


#### Getting Started

# Getting Started

Welcome! In this guide, we'll walk you through the basics of using the xAI API, from creating an account to making your first request.

## Step 1: Create an xAI account

Sign up for an account at [accounts.x.ai](https://accounts.x.ai/sign-up?redirect=cloud-console), then load it with credits to start using the API.

## Step 2: Generate an API key

Create an API key via the [API Keys page](https://console.x.ai/team/default/api-keys) in the xAI Console. Then make it available to your code. Either export it in your terminal:

```bash
export XAI_API_KEY="your_api_key"
```

Or add it to a `.env` file in your project directory:

```bash
XAI_API_KEY=your_api_key
```

The xAI SDKs are configured to automatically read your API key from the `XAI_API_KEY` environment variable.

## Step 3: Install an SDK

Pick your language and install the SDK:

```bash customLanguage="pythonXAI"
pip install xai-sdk
```

```bash customLanguage="pythonOpenAISDK"
pip install openai
```

```bash customLanguage="javascriptAISDK"
npm install ai @ai-sdk/xai zod
```

```bash customLanguage="javascriptOpenAISDK"
npm install openai
```

## Step 4: Make your first request

Send a prompt to Grok and get a response:

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(api_key=os.getenv("XAI_API_KEY"))

chat = client.chat.create(model="grok-4.3")
chat.append(system("You are Grok, a highly intelligent, helpful AI assistant."))
chat.append(user("What is the meaning of life, the universe, and everything?"))

response = chat.sample()
print(response.content)
```

```python customLanguage="pythonOpenAISDK"
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

completion = client.responses.create(
    model="grok-4.3",
    input=[
        {"role": "system", "content": "You are Grok, a highly intelligent, helpful AI assistant."},
        {"role": "user", "content": "What is the meaning of life, the universe, and everything?"},
    ],
)

print(completion.output_text)
```

```javascript customLanguage="javascriptAISDK"
import { createXai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const xai = createXai({ apiKey: process.env.XAI_API_KEY });

const { text } = await generateText({
    model: xai.responses('grok-4.3'),
    system: 'You are Grok, a highly intelligent, helpful AI assistant.',
    prompt: 'What is the meaning of life, the universe, and everything?',
});

console.log(text);
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from 'openai';

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: 'https://api.x.ai/v1',
});

const response = await client.responses.create({
    model: 'grok-4.3',
    input: [
        { role: 'system', content: 'You are Grok, a highly intelligent, helpful AI assistant.' },
        { role: 'user', content: 'What is the meaning of life, the universe, and everything?' },
    ],
});

console.log(response.output_text);
```

```bash
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-4.3",
    "input": [
        {"role": "system", "content": "You are Grok, a highly intelligent, helpful AI assistant."},
        {"role": "user", "content": "What is the meaning of life, the universe, and everything?"}
    ]
  }'
```

Certain models also support [Structured Outputs](/developers/model-capabilities/text/structured-outputs), which allows you to enforce a schema for the LLM output. For an in-depth guide about using Grok for text responses, check out the [Text Generation Guide](/developers/model-capabilities/text/generate-text).

## Step 5: Analyze an image

Grok can accept both text and images as input. Pass an image URL alongside your prompt:

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
from xai_sdk.chat import user, image

client = Client(api_key=os.getenv("XAI_API_KEY"))

chat = client.chat.create(model="grok-4")
chat.append(
    user(
        "What's in this image?",
        image("https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png"),
    )
)

response = chat.sample()
print(response.content)
```

```python customLanguage="pythonOpenAISDK"
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

completion = client.responses.create(
    model="grok-4",
    input=[{
        "role": "user",
        "content": [
            {"type": "input_image", "image_url": "https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png"},
            {"type": "input_text", "text": "What's in this image?"},
        ],
    }],
)

print(completion.output_text)
```

```javascript customLanguage="javascriptAISDK"
import { createXai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const xai = createXai({ apiKey: process.env.XAI_API_KEY });

const { text } = await generateText({
    model: xai.responses('grok-4'),
    messages: [{
        role: 'user',
        content: [
            { type: 'image', image: 'https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png' },
            { type: 'text', text: "What's in this image?" },
        ],
    }],
});

console.log(text);
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from 'openai';

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: 'https://api.x.ai/v1',
});

const completion = await client.responses.create({
    model: 'grok-4',
    input: [{
        role: 'user',
        content: [
            { type: 'input_image', image_url: 'https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png' },
            { type: 'input_text', text: "What's in this image?" },
        ],
    }],
});

console.log(completion.output_text);
```

```bash
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-4",
    "input": [{
        "role": "user",
        "content": [
            {"type": "input_image", "image_url": "https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png"},
            {"type": "input_text", "text": "What'\''s in this image?"}
        ]
    }]
  }'
```

To learn how to use Grok vision for more advanced use cases, check out [Image Understanding](/developers/model-capabilities/images/understanding).

## What's next

Now that you've made your first request, explore what Grok can do:

### Resources

* [Streaming](/developers/model-capabilities/text/streaming) - Stream responses in real time
* [Files & Collections](/developers/files) - Upload documents and build RAG pipelines
* [Tools](/developers/tools/overview) - Web search, X search, code execution, and function calling
* [Models & Pricing](/developers/models) - Compare available models and their capabilities


#### Key Information

# Models and Pricing

We offer a range of models supporting multiple use cases and modalities.

## Which model should I choose?

Your choice depends on your use case. We have dedicated models and API’s for audio, image, and video capabilities. For everything else, use Grok 4.3. It is the most intelligent and fastest model we’ve built.

## Tools Pricing

Requests which make use of xAI provided [server-side tools](/developers/tools/overview) are priced based on two components: **token usage** and **server-side tool invocations**. Since the agent autonomously decides how many tools to call, costs scale with query complexity.

### Token Costs

All standard token types are billed at the [rate](#model-pricing) for the model used in the request:

* **Input tokens**: Your query and conversation history
* **Reasoning tokens**: Agent's internal thinking and planning
* **Completion tokens**: The final response
* **Image tokens**: Visual content analysis (when applicable)
* **Cached prompt tokens**: Prompt tokens that were served from cache rather than recomputed

### Tool Invocation Costs

| Tool | Description | Cost / 1k Calls | Tool Name |
| --- | --- | --- | --- |
| Web Search | Search the internet and browse web pages | $5 | `web_search` |
| X Search | Search X posts, user profiles, and threads | $5 | `x_search` |
| Code Execution | Run Python code in a sandboxed environment | $5 | `code_execution`, `code_interpreter[object Object]` |
| File Attachments | Search through files attached to messages | $10 | `attachment_search` |
| Collections Search | Query your uploaded document collections (RAG) | $2.50 | `collections_search`, `file_search[object Object]` |
| Image Understanding | Analyze images found during Web Search and X Search\* | Token-based | `view_image` |
| X Video Understanding | Analyze videos found during X Search\* | Token-based | `view_x_video` |
| Remote MCP Tools | Connect and use custom MCP tool servers | Token-based | *(set by MCP server)* |
\[object Object] All tool names work in the Responses API. In the gRPC API (Python xAI SDK), `code_interpreter` and `file_search` are not supported.
\* Only applies to images and videos found by search tools — not to images passed directly in messages.

For the view image and view x video tools, you will not be charged for the tool invocation itself but will be charged for the image tokens used to process the image or video.

For Remote MCP tools, you will not be charged for the tool invocation but will be charged for any tokens used.

For more information on using Tools, please visit [our guide on Tools](/developers/tools/overview).

## Batch API Pricing

The [Batch API](/developers/advanced-api-usage/batch-api) lets you process large volumes of requests asynchronously at a fraction of the cost of standard pricing — effectively cutting your token costs in half. Batch requests are queued and processed in the background, with most completing within 24 hours.

| | Real-time API | Batch API |
|---|---|---|
| Token pricing | Standard rates | **20%-50% off** standard rates |
| Response time | Immediate (seconds) | Typically within 24 hours |
| Rate limits | Per-minute limits apply | Requests don't count towards rate limits |

The batch discount applies to all token types — input tokens, output tokens, cached tokens, and reasoning tokens. To see batch pricing for a specific model, visit the model's detail page and toggle **"Show batch API pricing"**.

The batch discount applies to text and language models only. Image and video generation are supported in the Batch API but are billed at standard rates. See [Batch API documentation](/developers/advanced-api-usage/batch-api) for full details.

## Files and Collections Pricing

Files and collections stored on the xAI platform are billed based on the amount of storage used. These charges will take effect starting on April 20th, 2026.

| Resource | Rate |
|---|---|
| File storage | $0.025 / GiB / day |
| Collection storage | $0.10 / GiB / day |

### Download Costs

Downloading data from files and collections is charged at a flat rate based on the amount of data transferred:

| Resource | Rate |
|---|---|
| File downloads | $0.20 / GiB downloaded |
| Collection downloads | $0.20 / GiB downloaded |

You can view and manage your [files](https://console.x.ai/team/default/files) and [collections](https://console.x.ai/team/default/collections) through the xAI console or the [xAI API](/developers/files/managing-files).

## Usage Guidelines Violation Fee

When your request is deemed to be in violation of our usage guideline by our system, we will still charge for the generation of the request.

For violations that are caught before generation in the Responses API, we will charge a $0.05 usage guideline violation fee per request.

## Additional Information Regarding Models

* **No access to realtime events without search tools enabled**
  * Grok has no knowledge of current events or data beyond what was present in its training data.
  * To incorporate realtime data with your request, enable server-side search tools (Web Search / X Search). See [Web Search](/developers/tools/web-search) and [X Search](/developers/tools/x-search).
* **Chat models**
  * No role order limitation: You can mix `system`, `user`, or `assistant` roles in any sequence for your conversation context.
* **Image input models**
  * Maximum image size: `20MiB`
  * Maximum number of images: No limit
  * Supported image file types: `jpg/jpeg` or `png`.
  * Any image/text input order is accepted (e.g. text prompt can precede image prompt)

The knowledge cut-off date of Grok 3 and Grok 4 is November, 2024.

## Model Aliases

Some models have aliases to help users automatically migrate to the next version of the same model. In general:

* `<modelname>` is aliased to the latest stable version.
* `<modelname>-latest` is aliased to the latest version. This is suitable for users who want to access the latest features.
* `<modelname>-<date>` refers directly to a specific model release. This will not be updated and is for workflows that demand consistency.

For most users, the aliased `<modelname>` or `<modelname>-latest` are recommended, as you would receive the latest features automatically.

## Billing and Availability

Your model access might vary depending on various factors such as geographical location, account limitations, etc.

For how the **bills are charged**, visit [Manage Billing](/console/billing) for more information.

For the most up-to-date information on **your team's model availability**, visit [Models Page](https://console.x.ai/team/default/models) on xAI Console.

## Model Input and Output

Each model can have one or multiple input and output capabilities.
The input capabilities refer to which type(s) of prompt can the model accept in the request message body.
The output capabilities refer to which type(s) of completion will the model generate in the response message body.

This is a prompt example for models with `text` input capability:

```json
[
  {
    "role": "system",
    "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."
  },
  {
    "role": "user",
    "content": "What is the meaning of life, the universe, and everything?"
  }
]
```

This is a prompt example for models with `text` and `image` input capabilities:

```json
[
  {
    "role": "user",
    "content": [
      {
        "type": "image_url",
        "image_url": {
          "url": "data:image/jpeg;base64,<base64_image_string>",
          "detail": "high"
        }
      },
      {
        "type": "text",
        "text": "Describe what's in this image."
      }
    ]
  }
]
```

This is a prompt example for models with `text` input and `image` output capabilities:

```json
// The entire request body
{
  "model": "grok-4",
  "prompt": "A cat in a tree",
  "n": 4
}
```

## Context Window

The context window determines the maximum amount of tokens accepted by the model in the prompt.

For more information on how token is counted, visit [Consumption and Rate Limits](/developers/rate-limits).

If you are sending the entire conversation history in the prompt for use cases like chat assistant, the sum of all the prompts in your conversation history must be no greater than the context window.

## Cached prompt tokens

Trying to run the same prompt multiple times? You can now use cached prompt tokens to incur less cost on repeated prompts. By reusing stored prompt data, you save on processing expenses for identical requests. Enable caching in your settings and start saving today!

The caching is automatically enabled for all requests without user input. You can view the cached prompt token consumption in [the `"usage"` object](/developers/rate-limits#checking-token-consumption).

For details on the pricing, please refer to the pricing table above, or on [xAI Console](https://console.x.ai).



#### Key Information

# Consumption and Rate Limits

The cost of using our API is based on token consumption. We charge different prices based on token category:

* **Prompt text, audio and image tokens** - Charged at prompt token price
* **Cached prompt tokens** - Charged at cached prompt token price
* **Completion tokens** - Charged at completion token price
* **Reasoning tokens** - Charged at completion token price

Visit [Models and Pricing](../models) for general pricing, or [xAI Console](https://console.x.ai) for pricing applicable to your team.

Each `grok` model has different rate limits. To check your team's rate limits, you can visit [xAI Console Models Page](https://console.x.ai/team/default/models).

## Basic unit to calculate consumption — Tokens

A token is the basic unit of prompt size for model inference and pricing purposes. It consists of one or more character(s)/symbol(s).

When a Grok model handles your request, an input prompt will be decomposed into a list of tokens through a tokenizer.
The model will then make inference based on the prompt tokens, and generate completion tokens.
After the inference is completed, the completion tokens will be aggregated into a completion response sent back to you.

Our system will add additional formatting tokens to the input/output token, and if you selected a reasoning model, additional reasoning tokens will be added into the total token consumption as well.
Your actual consumption will be reflected either in the `usage` object returned in the API response, or in Usage Explorer on the [xAI Console](https://console.x.ai).

You can use [Tokenizer](https://console.x.ai/team/default/tokenizer) on xAI Console to visualize tokens a given text prompt, or use [Tokenize text](/developers/rest-api-reference/inference/other#tokenize-text) endpoint on the API.

### Text tokens

Tokens can be either of a whole word, or smaller chunks of character combinations. The more common a word is, the more likely it would be a whole token.

For example, Flint is broken down into two tokens, while Michigan is a whole token.

In another example, most words are tokens by themselves, but "drafter" is broken down into "dra" and "fter", and "postmaster" is broken down into "post" and "master".

For a given text/image/etc. prompt or completion sequence, different tokenizers may break it down into different lengths of lists.

Different Grok models may also share or use different tokenizers. Therefore, **the same prompt/completion sequence may not have the same amount of tokens across different models.**

The token count in a prompt/completion sequence should be approximately linear to the sequence length.

### Image prompt tokens

Each image prompt will take between 256 to 1792 tokens, depending on the size of the image. The image + text token count must be less than the overall context window of the model.

### Estimating consumption with tokenizer on xAI Console or through API

The tokenizer page or API might display less token count than the actual token consumption. The
inference endpoints would automatically add pre-defined tokens to help our system process the
request.

On xAI Console, you can use the [tokenizer page](https://console.x.ai/team/default/tokenizer) to estimate how many tokens your text prompt will consume. For example, the following message would consume 5 tokens (the actual consumption may vary because of additional special tokens added by the system).

Message body:

```json
[
  {
    "role": "user",
    "content": "How is the weather today?"
  }
]
```

Tokenize result on Tokenizer page:

You can also utilize the [Tokenize Text](/developers/rest-api-reference/inference/other#tokenize-text) API endpoint to tokenize the text, and count the output token array length.

### Cached prompt tokens

When you send the same prompt multiple times, we may cache your prompt tokens. This would result in reduced cost for these tokens at the cached token rate, and a quicker response.

The prompt is cached using prefix matching, using cache for the exact prefix matches in the subsequent requests. However, the cache size might be limited and distributed across different clusters.

You can also specify `x-grok-conv-id: <A constant uuid4 ID>` in the HTTP request header, to increase the likelihood of cache hit in the subsequent requests using the same header.

### Reasoning tokens

The model may use reasoning to process your request. The reasoning content is returned in the response's `reasoning_content` field. The reasoning token consumption will be counted separately from `completion_tokens`, but will be counted in the `total_tokens`.

The reasoning tokens will be charged at the same price as `completion_tokens`.

`grok-4` does not return `reasoning_content`

## Rate limit tiers

Your team's rate limits are determined by your **tier**, which is based on your cumulative spend on the xAI API since January 1, 2026. Tiers unlock automatically as you spend more—no manual upgrade required.

Rate limit tiers only apply to our text models. To request a rate limit increase for our Voice or Imagine APIs, please email [sales@x.ai](mailto:sales@x.ai).

| Tier | Spend threshold |
| ---- | --------------- |
| Tier 0 | $0 (default) |
| Tier 1 | $50 |
| Tier 2 | $250 |
| Tier 3 | $1,000 |
| Tier 4 | $5,000 |
| Enterprise | Available on request |

### How tier qualification works

* **Spend-based upgrades**: Qualification is based on total revenue received through prepaid credit purchases or successfully fulfilled invoices.
* **Permanent tiers**: Once you qualify for a higher tier, you remain there permanently. Tiers never downgrade, even if your future spend decreases.
* **Custom overrides**: If your team has per-model or team-level tier overrides from a previous arrangement, those take precedence over the automatic tier.

### What each tier provides

Each tier sets hard **rpm** (requests per minute) and **tpm** (tokens per minute) limits per model. These are strict upper limits—exceeding them returns a `429` error. Note that full availability is not guaranteed during peak system load.

Rate limits vary by model. You can view your team's current limits for each model on the [Rate Limits page](https://console.x.ai/team/default/rate-limits) in the xAI Console.

## Hitting rate limits

Once your request frequency has reached the rate limit, you will receive error code `429` in response.

To increase your limits, you can:

* **Spend more to unlock higher tiers** — Tiers upgrade automatically based on cumulative spend
* **Request a tier increase** — Submit a request through the Cloud Console if you need to increase limits without spend, or need limits beyond Tier 4
* **Optimize your consumption pattern** — Batch requests, implement exponential backoff, or spread requests over time

## Checking token consumption

In each completion response, there is a `usage` object detailing your prompt and completion token count. You might find it helpful to keep track of it, in order to avoid hitting rate limits or having cost surprises. You can view more details of the object on our [API Reference](/developers/rest-api-reference).

```json
"usage": {
    "prompt_tokens": 199,
    "completion_tokens": 1,
    "total_tokens": 200,
    "prompt_tokens_details": {
        "text_tokens": 199,
        "audio_tokens": 0,
        "image_tokens": 0,
        "cached_tokens": 163
    },
    "completion_tokens_details": {
        "reasoning_tokens": 0,
        "audio_tokens": 0,
        "accepted_prediction_tokens": 0,
        "rejected_prediction_tokens": 0
    },
    "num_sources_used": 0,
    "cost_in_usd_ticks": 158500
}
```

The `cost_in_usd_ticks` field expresses the total cost to perform the inference, in 1/10,000,000,000 US dollar. For a full guide on reading and using cost data across all APIs, see [Cost Tracking](/developers/cost-tracking).

**Note:** The `usage.prompt_tokens_details.text_tokens` is the total text input token, which includes `cached_tokens` and non-cached text tokens.

You can also check with the xAI or OpenAI SDKs (Anthropic SDK is deprecated).

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import system, user

client = Client(api_key=os.getenv("XAI_API_KEY"))

chat = client.chat.create(
model="grok-4.3",
messages=[system("You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy.")]
)
chat.append(user("What is the meaning of life, the universe, and everything?"))

response = chat.sample()
print(response.usage)
```

```pythonOpenAISDK
import os
from openai import OpenAI

XAI_API_KEY = os.getenv("XAI_API_KEY")
client = OpenAI(base_url="https://api.x.ai/v1", api_key=XAI_API_KEY)

completion = client.chat.completions.create(
model="grok-4.3",
messages=[
{
"role": "system",
"content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy.",
},
{
"role": "user",
"content": "What is the meaning of life, the universe, and everything?",
},
],
)

if completion.usage:
print(completion.usage.to_json())
```

```javascriptOpenAISDK
import OpenAI from "openai";
const openai = new OpenAI({
apiKey: "<api key>",
baseURL: "https://api.x.ai/v1",
});

const completion = await openai.chat.completions.create({
model: "grok-4.3",
messages: [
{
role: "system",
content:
"You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy.",
},
{
role: "user",
content:
"What is the meaning of life, the universe, and everything?",
},
],
});

console.log(completion.usage);
```



#### Key Information

# Cost Tracking

Every inference response from the xAI API includes the exact cost you were charged for that request, returned via a `cost_in_usd_ticks` field in the `usage` object of chat completions, Responses API, image generation, and video generation responses.

The cost is per-request: each call returns what that individual request cost, whether it's a simple completion, a streaming response, or an agentic loop with server-side tools. This is the actual amount billed, after all applicable discounts (including [prompt caching](/developers/advanced-api-usage/prompt-caching) reductions) have been applied, and inclusive of all token costs and server-side tool invocation costs. No estimation or after-the-fact billing lookup required.

## How it works

The cost is expressed in **ticks**, where 1 USD = 10,000,000,000 ticks (10^10). To convert to dollars:

```text
cost_usd = cost_in_usd_ticks / 10,000,000,000
```

For example, a response with `"cost_in_usd_ticks": 37756000` cost $0.0038. An image generation with `"cost_in_usd_ticks": 200000000` cost $0.02.

Ticks exist for precision: they represent costs down to fractions of a cent without floating-point rounding, which matters when you're processing thousands of requests and need the totals to add up.

## Reading cost from a response

### xAI SDK

The xAI SDK provides a `cost_usd` convenience property that converts ticks to dollars automatically. The raw ticks are also accessible via `response.usage.cost_in_usd_ticks` if you need integer precision:

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
from xai_sdk.chat import user

client = Client(api_key=os.getenv("XAI_API_KEY"))

chat = client.chat.create(
    model="grok-4.3",
    messages=[user("Say hello")],
)
response = chat.sample()

# Convenience property — ticks converted to dollars.
print(f"Cost: ${response.cost_usd:.6f}")

# Raw ticks for integer-precision accounting.
print(f"Cost (ticks): {response.usage.cost_in_usd_ticks}")
```

### Chat Completions and Responses API

The `usage` object in every REST completion and response includes `cost_in_usd_ticks`:

```json
"usage": {
    "input_tokens": 199,
    "output_tokens": 1,
    "total_tokens": 200,
    "cost_in_usd_ticks": 158500
}
```

```bash customLanguage="bash"
curl https://api.x.ai/v1/responses \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-4.3",
    "input": "Say hello"
  }' | jq '.usage.cost_in_usd_ticks'
```

```python customLanguage="pythonOpenAISDK"
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

completion = client.chat.completions.create(
    model="grok-4.3",
    messages=[{"role": "user", "content": "Say hello"}],
)

# cost_in_usd_ticks is available directly on the usage object.
cost_ticks = completion.usage.cost_in_usd_ticks
cost_usd = cost_ticks / 1e10
print(f"Cost: ${cost_usd:.6f}")
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.XAI_API_KEY,
  baseURL: "https://api.x.ai/v1",
});

const completion = await client.chat.completions.create({
  model: "grok-4.3",
  messages: [{ role: "user", content: "Say hello" }],
});

const costTicks = completion.usage.cost_in_usd_ticks;
const costUsd = costTicks / 1e10;
console.log(`Cost: $${costUsd.toFixed(6)}`);
```

The Vercel AI SDK (`@ai-sdk/xai`) does not currently surface `cost_in_usd_ticks` in its response metadata. To access it, use the OpenAI SDK or the raw REST API directly.

### Streaming

During streaming, each chunk carries a running `cost_in_usd_ticks` total; the last chunk reflects the final cost for the request. If you're using the xAI SDK, the assembled `Response` object carries this automatically:

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
from xai_sdk.chat import user

client = Client(api_key=os.getenv("XAI_API_KEY"))

chat = client.chat.create(
    model="grok-4.3",
    messages=[user("Tell me a joke")],
)

for response, chunk in chat.stream():
    print(chunk.content, end="", flush=True)
print()

# After the stream completes, cost is on the final response.
print(f"Cost: ${response.cost_usd:.6f}")
```

```python customLanguage="pythonOpenAISDK"
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

stream = client.chat.completions.create(
    model="grok-4.3",
    messages=[{"role": "user", "content": "Tell me a joke"}],
    stream=True,
    stream_options={"include_usage": True},
)

for chunk in stream:
    if chunk.usage:
        cost_ticks = chunk.usage.cost_in_usd_ticks
        print(f"\nCost: ${cost_ticks / 1e10:.6f}")
    elif chunk.choices:
        print(chunk.choices[0].delta.content or "", end="", flush=True)
```

## Tracking cost across a conversation

`cost_in_usd_ticks` is per-request; it does not accumulate across turns. In a multi-turn conversation, sum the costs yourself:

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
from xai_sdk.chat import system, user

client = Client(api_key=os.getenv("XAI_API_KEY"))

chat = client.chat.create(
    model="grok-4.3",
    messages=[system("You are a helpful assistant.")],
)

total_cost_usd = 0.0
while True:
    prompt = input("You: ")
    if prompt.lower() == "exit":
        break

    chat.append(user(prompt))
    response = chat.sample()
    print(f"Grok: {response.content}")
    chat.append(response)

    total_cost_usd += response.cost_usd or 0.0
    print(f"  (this turn: ${response.cost_usd or 0:.6f})")

print(f"Total session cost: ${total_cost_usd:.4f}")
```

```python customLanguage="pythonOpenAISDK"
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

messages = [{"role": "system", "content": "You are a helpful assistant."}]
total_cost_usd = 0.0

while True:
    prompt = input("You: ")
    if prompt.lower() == "exit":
        break

    messages.append({"role": "user", "content": prompt})
    completion = client.chat.completions.create(
        model="grok-4.3",
        messages=messages,
    )

    reply = completion.choices[0].message.content
    print(f"Grok: {reply}")
    messages.append({"role": "assistant", "content": reply})

    cost_ticks = completion.usage.cost_in_usd_ticks
    cost_usd = cost_ticks / 1e10
    total_cost_usd += cost_usd
    print(f"  (this turn: ${cost_usd:.6f})")

print(f"Total session cost: ${total_cost_usd:.4f}")
```

## Server-side tools

When a request uses server-side tools (web search, X search, code execution), the model may make multiple internal calls before returning a final answer. The returned `cost_in_usd_ticks` covers all token costs and all tool invocations from that request in a single value. No separate accumulation needed.

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search, x_search

client = Client(api_key=os.getenv("XAI_API_KEY"))

chat = client.chat.create(
    model="grok-4.3",
    tools=[web_search(), x_search()],
)
chat.append(user("What are people saying about xAI's latest announcement?"))

response = chat.sample()
print(response.content)

# Shows which server-side tools were invoked and how many times.
print(f"Tools used: {response.server_side_tool_usage}")
# Cost covers all model decodes + every tool call in the agentic loop.
print(f"Cost: ${response.cost_usd:.4f}")
```

```python customLanguage="pythonOpenAISDK"
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4.3",
    input="What are people saying about xAI's latest announcement?",
    tools=[
        {"type": "web_search"},
        {"type": "x_search"},
    ],
)

print(response.output_text)

# Cost covers all model decodes + every tool call in the agentic loop.
cost_ticks = response.usage.cost_in_usd_ticks
print(f"Cost: ${cost_ticks / 1e10:.4f}")
```

```bash customLanguage="bash"
curl https://api.x.ai/v1/responses \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-4.3",
    "tools": [{"type": "web_search"}, {"type": "x_search"}],
    "input": "What are people saying about xAI'\''s latest announcement?"
  }' | jq '{tools_used: .usage.num_server_side_tools_used, cost_in_usd_ticks: .usage.cost_in_usd_ticks}'
```

## Image and video generation

Image and video responses include the same `cost_in_usd_ticks` field in their `usage` object:

```bash customLanguage="bash"
# Image generation
curl https://api.x.ai/v1/images/generations \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-imagine-image",
    "prompt": "A cat on a rocket"
  }' | jq '.usage.cost_in_usd_ticks'
# => 200000000 ($0.02)
```

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Image generation
image = client.image.sample(
    model="grok-imagine-image",
    prompt="A cat on a rocket",
)
print(f"Image cost: ${image.cost_usd:.4f}")

# Video generation
video = client.video.generate(
    model="grok-imagine-video",
    prompt="A cat floating in space",
)
print(f"Video cost: ${video.cost_usd:.4f}")
```

```python customLanguage="pythonOpenAISDK"
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.images.generate(
    model="grok-imagine-image",
    prompt="A cat on a rocket",
)

cost_ticks = response.usage.cost_in_usd_ticks
print(f"Image cost: ${cost_ticks / 1e10:.4f}")
```

## Batch API

Batch results include per-request costs. You can sum them to get the total batch cost, or read the `cost_breakdown` on the batch object itself. See [Batch API](/developers/advanced-api-usage/batch-api) for details.



#### Key Information

# Regional Endpoints

By default, you can access our API at `https://api.x.ai`. This is the most suitable endpoint for most customers,
as the request will be automatically routed by us to be processed in the region with lowest latency for your request.

For example, if you are based in US East Coast and send your request to `https://api.x.ai`, your request will be forwarded
to our `us-east-1` region and we will try to process it there first. If there is not enough computing resource in `us-east-1`,
we will send your request to other regions that are geographically closest to you and can handle the request.

## Using a regional endpoint

If you have specific data privacy requirements that would require the request to be processed within a specified region,
you can leverage our regional endpoint.

You can send your request to `https://<region-name>.api.x.ai`. For the same example, to send request from Europe to `eu-west-1`,
you will now send the request to `https://eu-west-1.api.x.ai`. If for some reason, we cannot handle your request in `eu-west-1`, the request will fail.

If you have more specific requirements (such as requiring data to stay within a specific region at rest), please contact our sales team at [sales@x.ai](mailto:sales@x.ai?subject=Regional%20Data%20Processing). Additional costs may apply.

## Example of using regional endpoints

If you want to use a regional endpoint, you need to specify the endpoint url when making request with SDK. In xAI SDK, this is specified through the `api_host` parameter.

For example, to send request to `eu-west-1`:

```pythonWithoutSDK
import os

from xai_sdk import Client
from xai_sdk.chat import user

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    api_host="eu-west-1.api.x.ai" # Without the https://
)

chat = client.chat.create(model="grok-4.3")
chat.append(user("What is the meaning of life?"))

completion = chat.sample()
```

```pythonOpenAISDK
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://eu-west-1.api.x.ai/v1",
)

completion = client.chat.completions.create(
    model="grok-4.3",
    messages=[
        {"role": "user", "content": "What is the meaning of life?"}
    ]
)
```

```javascriptOpenAISDK
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: "https://eu-west-1.api.x.ai/v1",
});

const completion = await client.chat.completions.create({
    model: "grok-4.3",
    messages: [
        { role: "user", content: "What is the meaning of life?" }
    ]
});
```

```bash
curl https://eu-west-1.api.x.ai/v1/chat/completions \\
-H "Content-Type: application/json" \\
-H "Authorization: Bearer $XAI_API_KEY" \\
-d '{
    "messages": [
        {
            "role": "user",
            "content": "What is the meaning of life, the universe, and everything?"
        }
    ],
    "model": "grok-4.3",
    "stream": false
}'
```

## Model availability across regions

While we strive to make every model available across all regions, there could be occasions where some models are not
available in some regions.

By using the global `https://api.x.ai` endpoint, you would have access to all models available to your team, since we
route your request automatically. If you're using a regional endpoint, please refer to [xAI Console](https://console.x.ai)
for the available models to your team in each region, or [Models and Pricing](../models) for the publicly available models.



#### Getting Started

# Debugging Errors

When you send a request, you would normally get a `200 OK` response from the server with the expected response body.
If there has been an error with your request, or error with our service, the API endpoint will typically return an error code with error message.

If there is an ongoing service disruption, you can visit
[https://status.x.ai](https://status.x.ai) for the latest updates. The status is also available
via RSS at [https://status.x.ai/feed.xml](https://status.x.ai/feed.xml).

The service status is also indicated in the navigation bar of this site.

Most of the errors will be accompanied by an error message that is self-explanatory. For typical status codes of each endpoint, visit [API Reference](/developers/rest-api-reference).

## Status Codes

Here is a list of potential errors and statuses arranged by status codes.

### 4XX Status Codes

| Status Code                    | Endpoints                              | Cause                                                                                                                                                                       | Solution                                                                                                                                         |
| ------------------------------ | -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| 400Bad Request            | All Endpoints                          | - A `POST` method request body specified an invalid argument, or a `GET` method with dynamic route has an invalid param in the URL.- An incorrect API key is supplied. | - Please check your request body or request URL.                                                                                                 |
| 401Unauthorized           | All Endpoints                          | - No authorization header or an invalid authorization token is provided.                                                                                                    | - Supply an `Authorization: Bearer <XAI_API_KEY>` in the request header. You can get a new API key on [xAI Console](https://console.x.ai). |
| 403Forbidden              | All Endpoints                          | - Your API key/team doesn't have permission to perform the action.- Your API key/team is blocked.                                                                     | - Ask your team admin for permission.                                                                                                            |
| 404Not Found              | All Endpoints                          | - A model specified in a `POST` method request body is not found.- Trying to reach an invalid endpoint URL. (Misspelled URL)                                           | - Check your request body and endpoint URL with our [API Reference](/developers/rest-api-reference).                                                              |
| 405Method Not Allowed     | All Endpoints                          | - The request method is not allowed. For example, sending a `POST` request to an endpoint supporting only `GET`.                                                            | - Check your request method with our [API Reference](/developers/rest-api-reference).                                                                             |
| 415Unsupported Media Type | All Endpoints Supporting `POST` Method | - An empty request body in `POST` requests.- Not specifying `Content-Type: application/json` header.                                                                  | - Add a valid request body. - Ensure `Content-Type: application/json` header is present in the request header.                             |
| 422Unprocessable Entity   | All Endpoints Supporting `POST` Method | - An invalid format for a field in the `POST` request body.                                                                                                                 | - Check your request body is valid. You can find more information from [API Reference](/developers/rest-api-reference).                                           |
| 429Too Many Requests      | All Inference Endpoints                | - You are sending requests too frequently and reaching rate limit                                                                                                           | - Reduce your request rate or increase your rate limit. You can find your current rate limit on [xAI Console](https://console.x.ai).             |

### 2XX Error Codes

| Status Code      | Endpoints                                   | Cause                                                                                                    | Solution                       |
| ---------------- | ------------------------------------------- | -------------------------------------------------------------------------------------------------------- | ------------------------------ |
| 202Accepted | `/v1/chat/deferred-completion/{request_id}` | - Your deferred chat completion request is queued for processing, but the response is not available yet. | - Wait for request processing. |

## Bug Report

If you believe you have encountered a bug and would like to contribute to our development process, [email API Bug Report](mailto:support@x.ai?subject=API%20Bug%20Report) to support@x.ai with your API request and response and relevant logs.

You can also chat in the `#help` channel of our [xAI API Developer Discord](https://discord.gg/x-ai).






#### Model Capabilities

# Generate Text

The Responses API is the preferred way of interacting with our models via API. It allows optional **stateful interactions** with our models,
where **previous input prompts, reasoning content and model responses are saved and stored on xAI's servers**. You can continue the interaction by appending new
prompt messages instead of resending the full conversation. This behavior is on by default. If you would like to store your request/response locally, please see [Disable storing previous request/response on server](#disable-storing-previous-requestresponse-on-server).

Although you don't need to enter the conversation history in the request body, you will still be
billed for the entire conversation history when using Responses API. The cost might be reduced as
part of the conversation history is .

**The responses will be stored for 30 days, after which they will be removed. This means you can use the response ID to retrieve or continue a conversation within 30 days of sending the request.**
If you want to continue a conversation after 30 days, please store your responses history and the encrypted thinking content locally, and pass them in a new request body.

For Python, we also offer our [xAI SDK](https://github.com/xai-org/xai-sdk-python) which covers all of our features and uses gRPC for optimal performance. It's fine to mix both. The xAI SDK allows you to interact with all our products such as Collections, Voice API, API key management, and more, while the Responses API is more suited for chatbots and usage in RESTful APIs.

## Prerequisites

* xAI Account: You need an xAI account to access the API.
* API Key: Ensure that your API key has access to the Responses API endpoint and the model you want to use is enabled.

If you don't have these and are unsure of how to create one, follow [the Hitchhiker's Guide to Grok](/developers/quickstart).

You can create an API key on the [xAI Console API Keys Page](https://console.x.ai/team/default/api-keys).

Set your API key in your environment:

```bash
export XAI_API_KEY="your_api_key"
```

## Creating a new model response

The first step in using Responses API is analogous to using the legacy Chat Completions API. You will create a new response with prompts. By default, your request/response history is stored on our server.

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    management_api_key=os.getenv("XAI_MANAGEMENT_API_KEY"),
    timeout=3600,
)

chat = client.chat.create(model="grok-4.3")
chat.append(system("You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."))
chat.append(user("What is the meaning of life, the universe, and everything?"))
response = chat.sample()

print(response)

# The response ID that can be used to continue the conversation later

print(response.id)
```

```python customLanguage="pythonOpenAISDK"
import os
import httpx
from openai import OpenAI

client = OpenAI(
    api_key="<YOUR_XAI_API_KEY_HERE>",
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0), # Override default timeout with longer timeout for reasoning models
)

response = client.responses.create(
    model="grok-4.3",
    input=[
        {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."},
        {"role": "user", "content": "What is the meaning of life, the universe, and everything?"},
    ],
)

print(response)

# The response ID that can be used to continue the conversation later

print(response.id)
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000, // Override default timeout with longer timeout for reasoning models
});

const response = await client.responses.create({
    model: "grok-4.3",
    input: [
        {
            role: "system",
            content: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."
        },
        {
            role: "user",
            content: "What is the meaning of life, the universe, and everything?"
        },
    ],
});

console.log(response);

// The response ID that can be used to recall the conversation later
console.log(response.id);
```

```javascript customLanguage="javascriptAISDK"
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const { text, response } = await generateText({
  model: xai.responses('grok-4.3'),
  system: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy.",
  prompt: "What is the meaning of life, the universe, and everything?",
});

console.log(text);

// The response ID can be used to continue the conversation
console.log(response.id);
```

```bash
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -m 3600 \
  -d '{
    "model": "grok-4.3",
    "input": [
        {
            "role": "system",
            "content": "You are Grok, a chatbot inspired by the Hitchhiker'\''s Guide to the Galaxy."
        },
        {
            "role": "user",
            "content": "What is the meaning of life, the universe, and everything?"
        }
    ]
}'
```

### Disable storing previous request/response on server

If you do not want to store your previous request/response on the server, you can set `store: false` on the request.

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    management_api_key=os.getenv("XAI_MANAGEMENT_API_KEY"),
    timeout=3600,
)

chat = client.chat.create(model="grok-4.3", store_messages=False)
chat.append(system("You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."))
chat.append(user("What is the meaning of life, the universe, and everything?"))
response = chat.sample()

print(response)
```

```python customLanguage="pythonOpenAISDK"
import os
import httpx
from openai import OpenAI

client = OpenAI(
    api_key="<YOUR_XAI_API_KEY_HERE>",
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0), # Override default timeout with longer timeout for reasoning models
)

response = client.responses.create(
    model="grok-4.3",
    input=[
        {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."},
        {"role": "user", "content": "What is the meaning of life, the universe, and everything?"},
    ],
    store=False
)

print(response)
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000, // Override default timeout with longer timeout for reasoning models
});

const response = await client.responses.create({
    model: "grok-4.3",
    input: [
        {
            role: "system",
            content: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."
        },
        {
            role: "user",
            content: "What is the meaning of life, the universe, and everything?"
        },
    ],
    store: false
});

console.log(response);
```

```bash
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -m 3600 \
  -d '{
    "model": "grok-4.3",
    "input": [
        {
            "role": "system",
            "content": "You are Grok, a chatbot inspired by the Hitchhiker'\''s Guide to the Galaxy."
        },
        {
            "role": "user",
            "content": "What is the meaning of life, the universe, and everything?"
        }
    ],
    "store": false
}'
```

### Returning encrypted thinking content

If you want to return the encrypted thinking traces, you need to specify `use_encrypted_content=True` in xAI SDK or gRPC request message, or `include: ["reasoning.encrypted_content"]` in the request body.

Make sure to use a reasoning model when working with encrypted thinking content.

Modify the steps to create a chat client (xAI SDK) or change the request body as following:

```python customLanguage="pythonXAI"
chat = client.chat.create(model="grok-4.3",
        use_encrypted_content=True)
```

```python customLanguage="pythonOpenAISDK"
response = client.responses.create(
    model="grok-4.3",
    input=[
        {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."},
        {"role": "user", "content": "What is the meaning of life, the universe, and everything?"},
    ],
    include=["reasoning.encrypted_content"]
)
```

```javascript customLanguage="javascriptWithoutSDK"
const response = await client.responses.create({
    model: "grok-4.3",
    input: [
        {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."},
        {"role": "user", "content": "What is the meaning of life, the universe, and everything?"},
    ],
    include: ["reasoning.encrypted_content"],
});

```

```javascript customLanguage="javascriptAISDK"
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const { text, reasoning } = await generateText({
  model: xai.responses('grok-4.3'),
  system: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy.",
  prompt: "What is the meaning of life, the universe, and everything?",
  providerOptions: {
    xai: {
      include: ['reasoning.encrypted_content'],
    },
  },
});

console.log(text);
console.log(reasoning); // Contains encrypted reasoning content
```

```bash
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -m 3600 \
  -d '{
    "model": "grok-4.3",
    "input": [
        {
            "role": "system",
            "content": "You are Grok, a chatbot inspired by the Hitchhiker'\''s Guide to the Galaxy."
        },
        {
            "role": "user",
            "content": "What is the meaning of life, the universe, and everything?"
        }
    ],
    "include": ["reasoning.encrypted_content"]
}'
```

See [Adding encrypted thinking content](#adding-encrypted-thinking-content) on how to use the returned encrypted thinking content when making a new request.

## Chaining the conversation

We now have the `id` of the first response. With Chat Completions API, we typically send a stateless new request with all the previous messages.

With Responses API, we can send the `id` of the previous response, and the new messages to append to it.

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    management_api_key=os.getenv("XAI_MANAGEMENT_API_KEY"),
    timeout=3600,
)

chat = client.chat.create(model="grok-4.3", store_messages=True)
chat.append(system("You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."))
chat.append(user("What is the meaning of life, the universe, and everything?"))
response = chat.sample()

print(response)

# The response ID that can be used to continue the conversation later

print(response.id)

# New steps

chat = client.chat.create(
    model="grok-4.3",
    previous_response_id=response.id,
    store_messages=True,
)
chat.append(user("What is the meaning of 42?"))
second_response = chat.sample()

print(second_response)

# The response ID that can be used to continue the conversation later

print(second_response.id)
```

```python customLanguage="pythonOpenAISDK"
# Previous steps
import os
import httpx
from openai import OpenAI

client = OpenAI(
    api_key="<YOUR_XAI_API_KEY_HERE>",
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0), # Override default timeout with longer timeout for reasoning models
)

response = client.responses.create(
    model="grok-4.3",
    input=[
        {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."},
        {"role": "user", "content": "What is the meaning of life, the universe, and everything?"},
    ],
)

print(response)

# The response ID that can be used to continue the conversation later

print(response.id)

# New steps

second_response = client.responses.create(
    model="grok-4.3",
    previous_response_id=response.id,
    input=[
        {"role": "user", "content": "What is the meaning of 42?"},
    ],
)

print(second_response)

# The response ID that can be used to continue the conversation later

print(second_response.id)
```

```javascript customLanguage="javascriptWithoutSDK"
// Previous steps
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000, // Override default timeout with longer timeout for reasoning models
});

const response = await client.responses.create({
    model: "grok-4.3",
    input: [
        {
            role: "system",
            content: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."
        },
        {
            role: "user",
            content: "What is the meaning of life, the universe, and everything?"
        },
    ],
});

console.log(response);

// The response ID that can be used to recall the conversation later
console.log(response.id);

const secondResponse = await client.responses.create({
    model: "grok-4.3",
    previous_response_id: response.id,
    input: [
        {"role": "user", "content": "What is the meaning of 42?"},
    ],
});

console.log(secondResponse);

// The response ID that can be used to recall the conversation later
console.log(secondResponse.id);
```

```javascript customLanguage="javascriptAISDK"
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

// First request
const result = await generateText({
  model: xai.responses('grok-4.3'),
  system: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy.",
  prompt: "What is the meaning of life, the universe, and everything?",
});

console.log(result.text);

// Get the response ID from the response object
const responseId = result.response.id;

// Continue the conversation using previousResponseId
const { text: secondResponse } = await generateText({
  model: xai.responses('grok-4.3'),
  prompt: "What is the meaning of 42?",
  providerOptions: {
    xai: {
      previousResponseId: responseId,
    },
  },
});

console.log(secondResponse);
```

```bash
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -m 3600 \
  -d '{
    "model": "grok-4.3",
    "previous_response_id": "The previous response ID",
    "input": [
        {
            "role": "user",
            "content": "What is the meaning of 42?"
        }
    ]
}'
```

### Adding encrypted thinking content

After returning the encrypted thinking content, you can also add it to a new response's input.

Make sure to use a reasoning model when working with encrypted thinking content.

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    management_api_key=os.getenv("XAI_MANAGEMENT_API_KEY"),
    timeout=3600,
)

chat = client.chat.create(model="grok-4.3", store_messages=True, use_encrypted_content=True)
chat.append(system("You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."))
chat.append(user("What is the meaning of life, the universe, and everything?"))
response = chat.sample()

print(response)

# The response ID that can be used to continue the conversation later

print(response.id)

# New steps

chat.append(response)  ## Append the response and the SDK will automatically add the outputs from response to message history

chat.append(user("What is the meaning of 42?"))
second_response = chat.sample()

print(second_response)

# The response ID that can be used to continue the conversation later

print(second_response.id)
```

```python customLanguage="pythonOpenAISDK"
# Previous steps
import os
import httpx
from openai import OpenAI

client = OpenAI(
    api_key="<YOUR_XAI_API_KEY_HERE>",
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0), # Override default timeout with longer timeout for reasoning models
)

response = client.responses.create(
    model="grok-4.3",
    input=[
        {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."},
        {"role": "user", "content": "What is the meaning of life, the universe, and everything?"},
    ],
    include=["reasoning.encrypted_content"]
)

print(response)

# The response ID that can be used to continue the conversation later

print(response.id)

# New steps

second_response = client.responses.create(
    model="grok-4.3",
    input=[
        *response.output,  # Use response.output instead of the stored response
        {"role": "user", "content": "What is the meaning of 42?"},
    ],
)

print(second_response)

# The response ID that can be used to continue the conversation later

print(second_response.id)
```

```javascript customLanguage="javascriptWithoutSDK"
// Previous steps
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000, // Override default timeout with longer timeout for reasoning models
});

const response = await client.responses.create({
    model: "grok-4.3",
    input: [
        {
            role: "system",
            content: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."
        },
        {
            role: "user",
            content: "What is the meaning of life, the universe, and everything?"
        },
    ],
    include: ["reasoning.encrypted_content"],
});

console.log(response);

// The response ID that can be used to recall the conversation later
console.log(response.id);

const secondResponse = await client.responses.create({
    model: "grok-4.3",
    input: [
        ...response.output,  // Use response.output instead of the stored response
        {"role": "user", "content": "What is the meaning of 42?"},
    ],
});

console.log(secondResponse);

// The response ID that can be used to recall the conversation later
console.log(secondResponse.id);
```

```javascript customLanguage="javascriptAISDK"
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

// First request with encrypted reasoning content
const result = await generateText({
  model: xai.responses('grok-4.3'),
  system: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy.",
  prompt: "What is the meaning of life, the universe, and everything?",
  providerOptions: {
    xai: {
      include: ['reasoning.encrypted_content'],
    },
  },
});

console.log(result.text);

// Continue the conversation using previousResponseId
// The encrypted content is automatically included when using previousResponseId
const { text: secondResponse } = await generateText({
  model: xai.responses('grok-4.3'),
  prompt: "What is the meaning of 42?",
  providerOptions: {
    xai: {
      previousResponseId: result.response.id,
      include: ['reasoning.encrypted_content'],
    },
  },
});

console.log(secondResponse);
```

```bash
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -m 3600 \
  -d '{
    "model": "grok-4.3",
    "input": [
        {
            "role": "system",
            "content": "You are Grok, a chatbot inspired by the Hitchhiker'\''s Guide to the Galaxy."
        },
        {
            "role": "user",
            "content": "What is the meaning of life, the universe, and everything?"
        },
        {
            "id": "rs_51abe1aa-599b-80b6-57c8-dddc6263362f_us-east-1",
            "summary": [],
            "type": "reasoning",
            "status": "completed",
            "encrypted_content": "bvV88j99ILvgfHRTHCUSJtw+ISji6txJzPdZNbcSVuDk4OMG2Z9r5wOBBwjd3u3Hhm9XtpCWJO1YgTOlpgbn+g7DZX+pOagYYrCFUpQ19XkWz6Je8bHG9JcSDoGDqNgRbDbAUO8at6RCyqgPupJj5ArBDCt73fGQLTC4G3S0JMK9LsPiWz6GPj6qyzYoRzkj4R6bntRm74E4h8Y+z6u6B7+ixPSv8s1EFs8c+NUAB8TNKZZpXZquj2LXfx1xAie85Syl7qLqxLNtDG1dNBhBnHpYoE4gQzwyXqywf5pF2Q2imzPNzGQhurK+6gaNWgZbxRmjhdsW6TnzO5Kk6pzb5qpfgfcEScQeYHSj5GpD+yDUCNlhdbzhhWnEErH+wuBPpTG6UQhiC7m7yrJ7IY2E8K/BeUPlUvkhMaMwb4dA279pWMJdchNJ+TAxca+JVc80pXMG/PmrQUNJU9qdXRLbNmQbRadBNwV2qkPfgggL3q0yNd7Un9P+atmP3B9keBILif3ufsBDtVUobEniiyGV7YVDvQ/fQRVs7XDxJiOKkogjjQySyHgpjseO8iG5xtb9mrz6B3mDvv2aAuyDL6MHZRM7QDVPjUbgNMzDm5Sm3J7IhtzfR+3eMDws3qeTsxOt1KOslu983Btv1Wx37b5HJqX1pQU1dae/kOSJ7MifFd6wMkQtQBDgVoG3ka9wq5Vxq9Ki8bDOOMcwA2kUXhCcY3TZCXJfDWSKPTcCoNCYIv5LT2NFVdamiSfLIyeOjBNz459BfMvAoOZShFViQyc5YwjnReUQPQ8a18jcz8GoAK1O99e0h91oYxIgDV52EfS+IYrzqvJOEQbKQinB+LJwkPbBEp7ZtgAtiNBzm985hNgLfiBaVFWcRYwI3tNBCT1vkw2YI0NEEG0yOF29x+u64XzqyP1CX1pU6sGXEFn3RPdfYibf6bt/Y1BRqBL5l0CrXWsgDw02SqIFta8OvJ7Iwmq40/4acE/Ew6eWO/z2MHkWgqSpwGNjn7MfeKkTi44foZjfNqN9QOFQt6VG2tY+biKZDo0h9DAftae8Q2Xs2UDvsBYOm7YEahVkput6/uKzxljpXlz269qHk6ckvdN9hKLbaTO3/IZPCCPQ5a/a/sWn/1VOJj72sDk+23RNjBf0FL6bJMXZI5aQdtxbF1zij9mWcP9nJ9FHhj53ytuf1NiKl5xU8ZsaoKmCAJcXUz1n2FZvyWlqvgPYiszc7R8Y5dF6QbW2mlKnXzVy6qRMHNeQqGhCEncyT5nPNSdK5QlUwLokAIg"
        },
        {
            "content": [
                {
                    "type": "output_text",
                    "text": "42\n\nThis is, of course, the iconic answer from Douglas Adams'\'' *The Hitchhiker'\''s Guide to the Galaxy*, where a supercomputer named Deep Thought spends 7.5 million years computing the \"Answer to the Ultimate Question of Life, the Universe, and Everything\"—only to reveal it'\''s 42. (The real challenge, it turns out, is figuring out what the actual *question* was.)\n\nIf you'\''re asking in a more literal or philosophical sense, the universe doesn'\''t have a single tidy answer—it'\''s full of mysteries like quantum mechanics, dark matter, and why cats knock things off tables. But 42? That'\''s as good a starting point as any. What'\''s your take on it?",
                    "logprobs": null,
                    "annotations": []
                }
            ],
            "id": "msg_c2f68a9b-87cd-4f85-a9e9-b6047213a3ce_us-east-1",
            "role": "assistant",
            "type": "message",
            "status": "completed"
        },
        {
            "role": "user",
            "content": "What is the meaning of 42?"
        }
    ],
    "include": [
        "reasoning.encrypted_content"
    ]
}'
```

## Retrieving a previous model response

If you have a previous response's ID, you can retrieve the content of the response.

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    management_api_key=os.getenv("XAI_MANAGEMENT_API_KEY"),
    timeout=3600,
)

response = client.chat.get_stored_completion("<The previous response's id>")

print(response)
```

```python customLanguage="pythonOpenAISDK"
import os
import httpx
from openai import OpenAI

client = OpenAI(
    api_key="<YOUR_XAI_API_KEY_HERE>",
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0), # Override default timeout with longer timeout for reasoning models
)

response = client.responses.retrieve("<The previous response's id>")

print(response)
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000, // Override default timeout with longer timeout for reasoning models
});

const response = await client.responses.retrieve("<The previous response's id>");

console.log(response);
```

```javascript customLanguage="javascriptAISDK"
// Note: The Vercel AI SDK does not provide a method to retrieve previous responses.
// Use the OpenAI SDK as shown above for this functionality.

import OpenAI from "openai";

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000,
});

const response = await client.responses.retrieve("<The previous response's id>");

console.log(response);
```

```bash
curl https://api.x.ai/v1/responses/{response_id} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -m 3600
```

## Delete a model response

If you no longer want to store the previous model response, you can delete it.

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    management_api_key=os.getenv("XAI_MANAGEMENT_API_KEY"),
    timeout=3600,
)

response = client.chat.delete_stored_completion("<The previous response's id>")
print(response)
```

```python customLanguage="pythonOpenAISDK"
import os
import httpx
from openai import OpenAI

client = OpenAI(
    api_key="<YOUR_XAI_API_KEY_HERE>",
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0), # Override default timeout with longer timeout for reasoning models
)

response = client.responses.delete("<The previous response's id>")

print(response)
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000, // Override default timeout with longer timeout for reasoning models
});

const response = await client.responses.delete("<The previous response's id>");

console.log(response);
```

```javascript customLanguage="javascriptAISDK"
// Note: The Vercel AI SDK does not provide a method to delete previous responses.
// Use the OpenAI SDK as shown above for this functionality.

import OpenAI from "openai";

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000,
});

const response = await client.responses.delete("<The previous response's id>");

console.log(response);
```

```bash
curl -X DELETE https://api.x.ai/v1/responses/{response_id} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -m 3600
```


#### Model Capabilities

# Reasoning

`presencePenalty`, `frequencyPenalty` and `stop` parameters are not supported by reasoning models.
Adding them in the request would result in an error.

## Key Features

* **Think Before Responding**: Reasoning models think through problems step-by-step before delivering an answer.
* **Math & Quantitative Strength**: Excels at numerical challenges, logic puzzles, and complex analytical tasks.
* **Reasoning Trace**: Usage metrics expose `reasoning_tokens`. Some models can also return encrypted reasoning via `include: ["reasoning.encrypted_content"]` (see below).

### Encrypted Reasoning Content

The reasoning content is encrypted by us and can be returned if you pass `include: ["reasoning.encrypted_content"]` to the Responses API. You can send the encrypted content back to provide more context to a previous conversation. See [Adding encrypted thinking content](/developers/model-capabilities/text/generate-text#adding-encrypted-thinking-content) for more details on how to use the content.

When using the Vercel AI SDK, encrypted reasoning content is automatically included under the hood as long as `store: false` is not specified. No additional configuration is needed.

## The reasoning parameter

`reasoning_effort` is **not** supported by `grok-4.3` or `grok-4-1-fast`. Specifying `reasoning_effort` on these models will return an error. These models reason automatically without any configuration.

The only model that accepts the `reasoning` parameter is `grok-4.20-multi-agent`, where it controls **how many agents** collaborate on a request — not how hard the model thinks.

### Multi-agent model: agent count (not thinking effort)

For `grok-4.20-multi-agent`, the `reasoning` parameter does **not** control how hard the model thinks. Instead, it controls **how many agents** collaborate on the request.

When using `grok-4.20-multi-agent`, the `reasoning.effort` parameter selects between two agent configurations:

| Setting | Agent Count | Best For |
|---|---|---|
| `"low"` or `"medium"` | **4 agents** | Quick research, focused queries |
| `"high"` or `"xhigh"` | **16 agents** | Deep research, complex multi-faceted topics |

More agents means deeper, more thorough research at the cost of higher token usage and latency. For full details and code examples, see the [Multi Agent](/developers/model-capabilities/text/multi-agent) documentation.

### Summary table

| Model | `reasoning` parameter | Behavior |
|---|---|---|
| `grok-4.20-multi-agent` | `reasoning.effort`: `"low"` / `"medium"` / `"high"` / `"xhigh"` | Controls agent count (4 or 16) |
| `grok-4.3`, `grok-4-1-fast` | Not supported | Reasons automatically; returns an error if specified |

## Usage Example

Here is a simple example using `grok-4.3` to multiply 101 by 3. No `reasoning_effort` parameter is needed — the model reasons automatically.

```python customLanguage="pythonXAI"
import os

from xai_sdk import Client
from xai_sdk.chat import system, user

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    timeout=3600, # Override default timeout with longer timeout for reasoning models
)

chat = client.chat.create(
    model="grok-4.3",
    messages=[system("You are a highly intelligent AI assistant.")],
)
chat.append(user("What is 101*3?"))

response = chat.sample()

print("Final Response:")
print(response.content)

print("Number of completion tokens:")
print(response.usage.completion_tokens)

print("Number of reasoning tokens:")
print(response.usage.reasoning_tokens)
```

```python customLanguage="pythonOpenAISDK"
import os
import httpx
from openai import OpenAI

client = OpenAI(
    base_url="https://api.x.ai/v1",
    api_key=os.getenv("XAI_API_KEY"),
    timeout=httpx.Timeout(3600.0), # Override default timeout with longer timeout for reasoning models
)

response = client.responses.create(
    model="grok-4.3",
    input=[
        {"role": "system", "content": "You are a highly intelligent AI assistant."},
        {"role": "user", "content": "What is 101*3?"},
    ],
)

message = next(item for item in response.output if item.type == "message")
text = next(c.text for c in message.content if c.type == "output_text")

print("Final Response:")
print(text)

print("Number of output tokens:")
print(response.usage.output_tokens)

print("Number of reasoning tokens:")
print(response.usage.output_tokens_details.reasoning_tokens)
```

```typescript customLanguage="javascriptAISDK"
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const result = await generateText({
  model: xai.responses('grok-4.3'),
  system: 'You are a highly intelligent AI assistant.',
  prompt: 'What is 101*3?',
});

console.log('Final Response:', result.text);
console.log('Number of completion tokens:', result.totalUsage.completionTokens);
console.log('Number of reasoning tokens:', result.totalUsage.reasoningTokens);
```

```bash customLanguage="bash"
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -m 3600 \
  -d '{
    "input": [
        {
            "role": "system",
            "content": "You are a highly intelligent AI assistant."
        },
        {
            "role": "user",
            "content": "What is 101*3?"
        }
    ],
    "model": "grok-4.3",
    "stream": false
}'
```

### Sample Output

```output
Final Response:
The result of 101 multiplied by 3 is 303.

Number of completion tokens:
14

Number of reasoning tokens:
310
```

## Summarized Reasoning Content

For `grok-4.3`, we expose summarizations of the model's internal reasoning. Here's an example of how to stream the reasoning summary deltas alongside the final response:

```python customLanguage="pythonXAI"
import os

from xai_sdk import Client
from xai_sdk.chat import system, user

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    timeout=3600, # Override default timeout with longer timeout for reasoning models
)

chat = client.chat.create(
    model="grok-4.3",
    messages=[system("You are a highly intelligent AI assistant.")],
)
chat.append(user("A projectile is launched at 30 m/s at 37° above horizontal from a 45 m cliff. Find its speed on impact. (g=10 m/s²)"))

content_started = False

print("\n\n--------- Reasoning ---------", flush=True)

latest_response = None
for response, chunk in chat.stream():
    if chunk.reasoning_content:
        print(chunk.reasoning_content, end="", flush=True)
```

```python customLanguage="pythonOpenAISDK"
import os
import httpx
from openai import OpenAI

client = OpenAI(
    base_url="https://api.x.ai/v1",
    api_key=os.getenv("XAI_API_KEY"),
    timeout=httpx.Timeout(3600.0),
)

stream = client.responses.create(
    model="grok-4.3",
    input=[
        {"role": "system", "content": "You are a highly intelligent AI assistant."},
        {"role": "user", "content": "A projectile is launched at 30 m/s at 37° above horizontal from a 45 m cliff. Find its speed on impact. (g=10 m/s²)"},
    ],
    stream=True,
)

print("\n\n--------- Reasoning ---------", flush=True)
for event in stream:
    if event.type == "response.reasoning_summary_text.delta":
        print(event.delta, end="", flush=True)
```

```typescript customLanguage="javascriptAISDK"
import { xai } from '@ai-sdk/xai';
import { streamText } from 'ai';

const result = streamText({
  model: xai.responses('grok-4.3'),
  system: 'You are a highly intelligent AI assistant.',
  prompt: 'A projectile is launched at 30 m/s at 37° above horizontal from a 45 m cliff. Find its speed on impact. (g=10 m/s²)'
});

console.log("\n\n--------- Reasoning ---------")

for await (const part of result.fullStream) {
  if (part.type === 'reasoning-delta') {
    process.stdout.write(part.text);
  } 
}
```

```bash customLanguage="bash"
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -m 3600 \
  -d '{
    "input": [
        {
            "role": "system",
            "content": "You are a highly intelligent AI assistant."
        },
        {
            "role": "user",
            "content": "A ball is thrown upward at 25 m/s from the top of a 60 m building. Find the maximum height above the ground. (g=10 m/s²)"
        }
    ],
    "model": "grok-4.3",
    "stream": true
}'
```

### Sample Output

```output
--------- Reasoning ---------
The problem is: A projectile is launched at 30 m/s at 37° above horizontal from a 45 m cliff. Find its speed on impact. (g=10 m/s²)
I need to find the speed when the projectile hits the ground. It's launched at 30 m/s at 37° from a 45 m cliff, with g=10 m/s².

Conservation of energy is a good approach. The initial kinetic energy is (1/Assistant: 2)mv² with v=30 m/s, and initial potential energy is mgh with h=45 m, taking ground as zero.

At impact, potential energy is zero, so initial KE + initial PE = final KE.

Thus, (1/2)m(30)² + mg(45) = (1/2)m v_f²

v_f² = 900 + 2*10*45 = 900 + 900 = 1800

v_f = sqrt(1800) = 30√2 m/s ≈ 42.4 m/s

The angle doesn't affect the final speed because the initial kinetic energy and potentialenergy change are the same regardless of direction, as long as the speed and height are the same.

Yes, that makes sense. The final speed is sqrt(v0² + 2gh), independent of the launch angle.
```

## Notes on Consumption

When you use a reasoning model, the reasoning tokens are billed as part of your total consumption.

For the multi-agent model, all tokens consumed by both the leader agent and sub-agents are billed. Choosing 16 agents (via `"high"` / `"xhigh"`) will use significantly more tokens than 4 agents. See the [Multi Agent pricing section](/developers/model-capabilities/text/multi-agent#pricing) for details.



#### Model Capabilities

# Structured Outputs

Structured Outputs lets the API return responses in a specific format,
for example, a JSON object matching a schema you define instead of free-form
text. This feature is especially useful for tasks like document parsing, entity
extraction, and report generation.

When using supported schema features, the response is guaranteed to match your schema.

There are two ways to request structured outputs from the model.

The primary and most flexible method is to use the `response_format` parameter. By setting `response_format.type` to `"json_schema"` and providing your schema under `response_format.json_schema`, you can define exactly what structured output the model should return. The parameter also accepts `"json_object"` for any well-formed JSON when you don't need a specific structure, or `"text"` (the default) for free-form text.

The second way is through tool calling. When you define tools, xAI models will always generate tool call arguments that strictly conform to the tool’s input JSON Schema (the `strict` flag is implicitly always `true`).

Tool schemas follow the same JSON Schema support rules described on this page. See the [Function Calling](/developers/tools/function-calling) documentation for full details.

You can define schemas using libraries like
[Pydantic](https://pydantic.dev/) or [Zod](https://zod.dev/).

## JSON Schema support

We support a practical subset of JSON Schema. Schemas authored against Draft 2020-12 work best; Draft-07 schemas are also accepted.

### Supported types

* `string`
* `number`
* `integer`
* `boolean`
* `null`
* `enum`
* `const`
* `array`
* `object`
* `anyOf`
* `oneOf` (behaves identically to `anyOf`)
* `allOf` (single subschema only; see [Best-effort keywords](#best-effort-keywords) for multiple)
* `$ref` / `$defs` (non-circular references only)

`additionalProperties` defaults to `false` and must be set to `true` explicitly.

To make a field nullable, use a type array (`{"type": ["string", "null"]}`) or an `anyOf` variant that includes `null`. Fields not listed in `required` are treated as optional.

### String formats

The `format` keyword is enforced for these values:

`date` · `time` · `date-time` · `email` · `uuid` · `ipv4` · `ipv6` · `uri`

Other `format` values are accepted but not enforced (see [Best-effort keywords](#best-effort-keywords)).

### Constraint limits

The following constraints are enforced by the output engine up to
the thresholds below. Schemas exceeding these limits are still accepted,
but conformance relies on model behavior.

| Keyword | Guaranteed up to |
|---|---|
| `minimum` / `maximum` / `exclusiveMinimum` / `exclusiveMaximum` | No limit |
| `minLength` / `maxLength` | 2,048 |
| `minItems` / `maxItems` | 256 |
| `minProperties` / `maxProperties` | 64 |

### Best-effort keywords

These keywords are accepted but not structurally enforced; the model
handles them and does so reliably in practice, but outputs are not
guaranteed to satisfy these constraints. We recommend validating
if strict conformance is required.

* `not`
* `if` / `then` / `else`
* `allOf` with more than one subschema
* `format` values not listed under [String formats](#string-formats)
* Constraints exceeding the limits above

### Rejected schemas

The following will return a `400` error:

* `enum` or `anyOf` with zero variants
* Properties with a schema of `true` or `false`
* `maxContains` / `minContains`
* `items` as an array (use `prefixItems` for tuple validation)

### Regex support (`pattern`)

When using the `pattern` keyword on a string field, we support a practical subset of ECMAScript Regular Expressions (ECMA-262).

**Supported:**

* Literals and character classes (`[abc]`, `[a-z]`, `[^abc]`)
* `.` (matches any Unicode codepoint, including newlines)
* Alternation `|`, grouping `(...)`, and non-capturing groups `(?:...)`
* Quantifiers `*`, `+`, `?` and repetition ranges `{n}`, `{n,}`, `{n,m}`
* Shorthand classes `\d`, `\w`, `\s` (and their negations `\D`, `\W`, `\S`)
* Common escapes: `\n`, `\t`, `\r`, `\f`, `\xHH`, `\uHHHH`, `\u{HHHHHH}`

**Not supported:**

* Backreferences (`\1`, `\k<name>`, etc.)
* Unicode property escapes (`\p{L}`, `\P{Letter}`)
* Word boundaries (`\b`, `\B`)
* Lookahead and lookbehind (`(?=...)`, `(?<=...)`, etc.)
* Inline modifiers (`(?i)`, `(?m)`, etc.)
* Conditional expressions and other advanced constructs

**Semantic differences from standard JavaScript RegExp:**

* `.` matches newlines
* `^` and `$` are *implicit*—the pattern always matches the *entire string* (no need to add them)
* Capturing groups `(...)` have no semantic effect (they behave like non-capturing groups)
* The regex is evaluated with Unicode support

## Example: Invoice Parsing

A common use case for Structured Outputs is parsing raw documents. For example, invoices contain structured data like vendor details, amounts, and dates, but extracting this data from raw text can be error-prone. Structured Outputs ensure the extracted data matches a predefined schema.

Let's say you want to extract the following data from an invoice:

* Vendor name and address
* Invoice number and date
* Line items (description, quantity, price)
* Total amount and currency

We'll use structured outputs to have Grok generate a strongly-typed JSON for this.

### Step 1: Defining the Schema

You can use [Pydantic](https://pydantic.dev/) or [Zod](https://zod.dev/) to define your schema.

```pythonWithoutSDK
from datetime import date
from enum import Enum

from pydantic import BaseModel, Field

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class LineItem(BaseModel):
    description: str = Field(description="Description of the item or service")
    quantity: int = Field(description="Number of units", ge=1)
    unit_price: float = Field(description="Price per unit", ge=0)

class Address(BaseModel):
    street: str = Field(description="Street address")
    city: str = Field(description="City")
    postal_code: str = Field(description="Postal/ZIP code")
    country: str = Field(description="Country")

class Invoice(BaseModel):
    vendor_name: str = Field(description="Name of the vendor")
    vendor_address: Address = Field(description="Vendor's address")
    invoice_number: str = Field(description="Unique invoice identifier")
    invoice_date: date = Field(description="Date the invoice was issued")
    line_items: list[LineItem] = Field(description="List of purchased items/services")
    total_amount: float = Field(description="Total amount due", ge=0)
    currency: Currency = Field(description="Currency of the invoice")
```

```javascriptWithoutSDK
import { z } from "zod";

const CurrencyEnum = z.enum(["USD", "EUR", "GBP"]);

const LineItemSchema = z.object({
    description: z.string().describe("Description of the item or service"),
    quantity: z.number().int().min(1).describe("Number of units"),
    unit_price: z.number().min(0).describe("Price per unit"),
});

const AddressSchema = z.object({
    street: z.string().describe("Street address"),
    city: z.string().describe("City"),
    postal_code: z.string().describe("Postal/ZIP code"),
    country: z.string().describe("Country"),
});

const InvoiceSchema = z.object({
    vendor_name: z.string().describe("Name of the vendor"),
    vendor_address: AddressSchema.describe("Vendor's address"),
    invoice_number: z.string().describe("Unique invoice identifier"),
    invoice_date: z.string().date().describe("Date the invoice was issued"),
    line_items: z.array(LineItemSchema).describe("List of purchased items/services"),
    total_amount: z.number().min(0).describe("Total amount due"),
    currency: CurrencyEnum.describe("Currency of the invoice"),
});
```

### Step 2: Prepare The Prompts

### System Prompt

The system prompt instructs the model to extract invoice data from text. Since the schema is defined separately, the prompt can focus on the task without explicitly specifying the required fields in the output JSON.

```text
Given a raw invoice, carefully analyze the text and extract the relevant invoice data into JSON format.
```

### Example Invoice Text

```text
Vendor: Acme Corp, 123 Main St, Springfield, IL 62704
Invoice Number: INV-2025-001
Date: 2025-02-10
Items:
- Widget A, 5 units, $10.00 each
- Widget B, 2 units, $15.00 each
Total: $80.00 USD
```

### Step 3: The Final Code

Use the structured outputs feature of the SDK to parse the invoice.

```pythonXAI
import os
from datetime import date
from enum import Enum

from pydantic import BaseModel, Field

from xai_sdk import Client
from xai_sdk.chat import system, user

# Pydantic Schemas

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class LineItem(BaseModel):
    description: str = Field(description="Description of the item or service")
    quantity: int = Field(description="Number of units", ge=1)
    unit_price: float = Field(description="Price per unit", ge=0)

class Address(BaseModel):
    street: str = Field(description="Street address")
    city: str = Field(description="City")
    postal_code: str = Field(description="Postal/ZIP code")
    country: str = Field(description="Country")

class Invoice(BaseModel):
    vendor_name: str = Field(description="Name of the vendor")
    vendor_address: Address = Field(description="Vendor's address")
    invoice_number: str = Field(description="Unique invoice identifier")
    invoice_date: date = Field(description="Date the invoice was issued")
    line_items: list[LineItem] = Field(description="List of purchased items/services")
    total_amount: float = Field(description="Total amount due", ge=0)
    currency: Currency = Field(description="Currency of the invoice")

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(model="grok-4.3")

chat.append(system("Given a raw invoice, carefully analyze the text and extract the invoice data into JSON format."))
chat.append(
user("""
Vendor: Acme Corp, 123 Main St, Springfield, IL 62704
Invoice Number: INV-2025-001
Date: 2025-02-10
Items: - Widget A, 5 units, $10.00 each - Widget B, 2 units, $15.00 each
Total: $80.00 USD
""")
)

# The parse method returns a tuple of the full response object as well as the parsed pydantic object.

response, invoice = chat.parse(Invoice)
assert isinstance(invoice, Invoice)

# Can access fields of the parsed invoice object directly

print(invoice.vendor_name)
print(invoice.invoice_number)
print(invoice.invoice_date)
print(invoice.line_items)
print(invoice.total_amount)
print(invoice.currency)

# Can also access fields from the raw response object such as the content.

# In this case, the content is the JSON schema representation of the parsed invoice object

print(response.content)
```

```pythonOpenAISDK
from openai import OpenAI

from pydantic import BaseModel, Field
from datetime import date
from enum import Enum

# Pydantic Schemas

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class LineItem(BaseModel):
    description: str = Field(description="Description of the item or service")
    quantity: int = Field(description="Number of units", ge=1)
    unit_price: float = Field(description="Price per unit", ge=0)

class Address(BaseModel):
    street: str = Field(description="Street address")
    city: str = Field(description="City")
    postal_code: str = Field(description="Postal/ZIP code")
    country: str = Field(description="Country")

class Invoice(BaseModel):
    vendor_name: str = Field(description="Name of the vendor")
    vendor_address: Address = Field(description="Vendor's address")
    invoice_number: str = Field(description="Unique invoice identifier")
    invoice_date: date = Field(description="Date the invoice was issued")
    line_items: list[LineItem] = Field(description="List of purchased items/services")
    total_amount: float = Field(description="Total amount due", ge=0)
    currency: Currency = Field(description="Currency of the invoice")

client = OpenAI(
    api_key="<YOUR_XAI_API_KEY_HERE>",
    base_url="https://api.x.ai/v1",
)

completion = client.beta.chat.completions.parse(
    model="grok-4.3",
    messages=[
    {"role": "system", "content": "Given a raw invoice, carefully analyze the text and extract the invoice data into JSON format."},
    {"role": "user", "content": """
    Vendor: Acme Corp, 123 Main St, Springfield, IL 62704
    Invoice Number: INV-2025-001
    Date: 2025-02-10
    Items:

    - Widget A, 5 units, $10.00 each
    - Widget B, 2 units, $15.00 each
      Total: $80.00 USD
      """}
      ],
      response_format=Invoice,
  )

invoice = completion.choices[0].message.parsed
print(invoice)
```

```javascriptOpenAISDK
import OpenAI from "openai";
import { zodResponseFormat } from "openai/helpers/zod";
import { z } from "zod";

const CurrencyEnum = z.enum(["USD", "EUR", "GBP"]);

const LineItemSchema = z.object({
    description: z.string().describe("Description of the item or service"),
    quantity: z.number().int().min(1).describe("Number of units"),
    unit_price: z.number().min(0).describe("Price per unit"),
});

const AddressSchema = z.object({
    street: z.string().describe("Street address"),
    city: z.string().describe("City"),
    postal_code: z.string().describe("Postal/ZIP code"),
    country: z.string().describe("Country"),
});

const InvoiceSchema = z.object({
    vendor_name: z.string().describe("Name of the vendor"),
    vendor_address: AddressSchema.describe("Vendor's address"),
    invoice_number: z.string().describe("Unique invoice identifier"),
    invoice_date: z.string().date().describe("Date the invoice was issued"),
    line_items: z.array(LineItemSchema).describe("List of purchased items/services"),
    total_amount: z.number().min(0).describe("Total amount due"),
    currency: CurrencyEnum.describe("Currency of the invoice"),
});

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
});

const completion = await client.chat.completions.parse({
    model: "grok-4.3",
    messages: [
    { role: "system", content: "Given a raw invoice, carefully analyze the text and extract the invoice data into JSON format." },
    { role: "user", content: \`
    Vendor: Acme Corp, 123 Main St, Springfield, IL 62704
    Invoice Number: INV-2025-001
    Date: 2025-02-10
    Items:

    - Widget A, 5 units, $10.00 each
    - Widget B, 2 units, $15.00 each
      Total: $80.00 USD
      \` },
    ],
    response_format: zodResponseFormat(InvoiceSchema, "invoice"),
});

const invoice = completion.choices[0].message.parsed;
console.log(invoice);
```

```javascriptAISDK
import { xai } from '@ai-sdk/xai';
import { generateText, Output } from 'ai';
import { z } from 'zod';

const CurrencyEnum = z.enum(['USD', 'EUR', 'GBP']);

const LineItemSchema = z.object({
  description: z.string().describe('Description of the item or service'),
  quantity: z.number().int().min(1).describe('Number of units'),
  unit_price: z.number().min(0).describe('Price per unit'),
});

const AddressSchema = z.object({
  street: z.string().describe('Street address'),
  city: z.string().describe('City'),
  postal_code: z.string().describe('Postal/ZIP code'),
  country: z.string().describe('Country'),
});

const InvoiceSchema = z.object({
  vendor_name: z.string().describe('Name of the vendor'),
  vendor_address: AddressSchema.describe("Vendor's address"),
  invoice_number: z.string().describe('Unique invoice identifier'),
  invoice_date: z.string().date().describe('Date the invoice was issued'),
  line_items: z
    .array(LineItemSchema)
    .describe('List of purchased items/services'),
  total_amount: z.number().min(0).describe('Total amount due'),
  currency: CurrencyEnum.describe('Currency of the invoice'),
});

const result = await generateText({
  model: xai.responses('grok-4.3'),
  output: Output.object({ schema: InvoiceSchema }),
  system:
    'Given a raw invoice, carefully analyze the text and extract the invoice data into JSON format.',
  prompt: \`
  Vendor: Acme Corp, 123 Main St, Springfield, IL 62704
  Invoice Number: INV-2025-001
  Date: 2025-02-10
  Items:

  - Widget A, 5 units, $10.00 each
  - Widget B, 2 units, $15.00 each
    Total: $80.00 USD
    \`,
});

console.log(result._output);
```

### Step 4: Type-safe Output

When using supported schema features, the output will be type-safe and respect the input schema.

```json
{
  "vendor_name": "Acme Corp",
  "vendor_address": {
    "street": "123 Main St",
    "city": "Springfield",
    "postal_code": "62704",
    "country": "IL"
  },
  "invoice_number": "INV-2025-001",
  "invoice_date": "2025-02-10",
  "line_items": [
    { "description": "Widget A", "quantity": 5, "unit_price": 10.0 },
    { "description": "Widget B", "quantity": 2, "unit_price": 15.0 }
  ],
  "total_amount": 80.0,
  "currency": "USD"
}
```

## Structured Outputs with Tools

Structured outputs with tools is only available for supported Grok 4 family models.

You can combine structured outputs with tool calling to get type-safe responses from tool-augmented queries. This works with both:

* **[Agentic tool calling](/developers/tools/overview)**: Server-side tools like web search, X search, and code execution that the model orchestrates autonomously.
* **[Function calling](/developers/tools/function-calling)**: User-supplied tools where you define custom functions and handle tool execution yourself.

This combination enables workflows where the model can use tools to gather information and return results in a predictable, strongly-typed format.

### Example: Agentic Tools with Structured Output

This example uses web search to find the latest research on a topic and extracts structured data into a schema:

```python customLanguage="pythonWithoutSDK"
from pydantic import BaseModel, Field

class ProofInfo(BaseModel):
    name: str = Field(description="Name of the proof or paper")
    authors: str = Field(description="Authors of the proof")
    year: str = Field(description="Year published")
    summary: str = Field(description="Brief summary of the approach")
```

```javascript customLanguage="javascriptWithoutSDK"
import { z } from "zod";

const ProofInfoSchema = z.object({
    name: z.string().describe("Name of the proof or paper"),
    authors: z.string().describe("Authors of the proof"),
    year: z.string().describe("Year published"),
    summary: z.string().describe("Brief summary of the approach"),
});
```

```python customLanguage="pythonXAI"
import os
from pydantic import BaseModel, Field

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search

# ProofInfo schema defined above

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4.3",
    tools=[web_search()],
)

chat.append(user("Find the latest machine-checked proof of the four color theorem."))

response, proof = chat.parse(ProofInfo)

print(f"Name: {proof.name}")
print(f"Authors: {proof.authors}")
print(f"Year: {proof.year}")
print(f"Summary: {proof.summary}")
```

```python customLanguage="pythonOpenAISDK"
import os
from openai import OpenAI
from pydantic import BaseModel, Field

# ProofInfo schema defined above

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.responses.parse(
    model="grok-4.3",
    input="Find the latest machine-checked proof of the four color theorem.",
    tools=[
        {"type": "web_search"}
    ],
    text_format=ProofInfo,
)

proof = response.output_parsed
print(f"Name: {proof.name}")
print(f"Authors: {proof.authors}")
print(f"Year: {proof.year}")
print(f"Summary: {proof.summary}")
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";
import { zodResponseFormat } from "openai/helpers/zod";
import { z } from "zod";

// ProofInfoSchema defined above

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: "https://api.x.ai/v1",
});

// Convert Zod schema to JSON schema format
const format = zodResponseFormat(ProofInfoSchema, "proof_info");

const response = await client.responses.create({
    model: "grok-4.3",
    input: "Find the latest machine-checked proof of the four color theorem.",
    tools: [
        { type: "web_search" }
    ],
    text: {
        format: {
            type: "json_schema",
            name: format.json_schema.name,
            schema: format.json_schema.schema,
            strict: true,
        }
    }
});

// Find the message in the output array
const message = response.output.find((item) => item.type === "message");
const textContent = message?.content?.find((c) => c.type === "output_text");

if (textContent) {
    const proof = JSON.parse(textContent.text);
    console.log(`Name: ${proof.name}`);
    console.log(`Authors: ${proof.authors}`);
    console.log(`Year: ${proof.year}`);
    console.log(`Summary: ${proof.summary}`);
}
```

### Example: Client-side Tools with Structured Output

This example uses a client-side function tool to compute Collatz sequence steps and returns the result in a structured format:

```python customLanguage="pythonWithoutSDK"
from pydantic import BaseModel, Field

class CollatzResult(BaseModel):
    starting_number: int = Field(description="The input number")
    steps: int = Field(description="Number of steps to reach 1")
```

```javascript customLanguage="javascriptWithoutSDK"
const CollatzResultSchema = {
    type: "object",
    properties: {
        starting_number: { type: "integer", description: "The input number" },
        steps: { type: "integer", description: "Number of steps to reach 1" },
    },
    required: ["starting_number", "steps"],
    additionalProperties: false,
};
```

```python customLanguage="pythonXAI"
import os
import json
from pydantic import BaseModel, Field

from xai_sdk import Client
from xai_sdk.chat import tool, tool_result, user

# CollatzResult schema defined above

def collatz_steps(n: int) -> int:
    """Returns the number of steps for n to reach 1 in the Collatz sequence."""
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps

collatz_tool = tool(
    name="collatz_steps",
    description="Compute the number of steps for a number to reach 1 in the Collatz sequence",
    parameters={
        "type": "object",
        "properties": {
            "n": {"type": "integer", "description": "The starting number"},
        },
        "required": ["n"],
    },
)

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4.3",
    tools=[collatz_tool],
)

chat.append(user("Use the collatz_steps tool to find how many steps it takes for 20250709 to reach 1."))

# Handle tool calls until we get a final response
while True:
    response = chat.sample()
    
    if not response.tool_calls:
        break
    
    chat.append(response)
    for tc in response.tool_calls:
        args = json.loads(tc.function.arguments)
        result = collatz_steps(args["n"])
        chat.append(tool_result(str(result)))

# Parse the final response into structured output
response, result = chat.parse(CollatzResult)

print(f"Starting number: {result.starting_number}")
print(f"Steps to reach 1: {result.steps}")
```

```python customLanguage="pythonOpenAISDK"
import os
import json
from openai import OpenAI
from pydantic import BaseModel, Field

# CollatzResult schema defined above

def collatz_steps(n: int) -> int:
    """Returns the number of steps for n to reach 1 in the Collatz sequence."""
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "collatz_steps",
            "description": "Compute the number of steps for a number to reach 1 in the Collatz sequence",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {"type": "integer", "description": "The starting number"},
                },
                "required": ["n"],
            },
        },
    }
]

messages = [
    {"role": "user", "content": "Use the collatz_steps tool to find how many steps it takes for 20250709 to reach 1."}
]

# Handle tool calls until we get a final response
while True:
    completion = client.chat.completions.create(
        model="grok-4.3",
        messages=messages,
        tools=tools,
    )
    
    message = completion.choices[0].message
    
    if not message.tool_calls:
        break
    
    messages.append(message)
    for tc in message.tool_calls:
        args = json.loads(tc.function.arguments)
        result = collatz_steps(args["n"])
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": str(result),
        })

# Final call with structured output
completion = client.beta.chat.completions.parse(
    model="grok-4.3",
    messages=messages,
    response_format=CollatzResult,
)

result = completion.choices[0].message.parsed
print(f"Starting number: {result.starting_number}")
print(f"Steps to reach 1: {result.steps}")
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";

// CollatzResultSchema defined above

function collatzSteps(n) {
    let steps = 0;
    while (n !== 1) {
        n = n % 2 === 0 ? n / 2 : 3 * n + 1;
        steps++;
    }
    return steps;
}

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: "https://api.x.ai/v1",
});

const tools = [
    {
        type: "function",
        function: {
            name: "collatz_steps",
            description: "Compute the number of steps for a number to reach 1 in the Collatz sequence",
            parameters: {
                type: "object",
                properties: {
                    n: { type: "integer", description: "The starting number" },
                },
                required: ["n"],
            },
        },
    },
];

let messages = [
    { role: "user", content: "Use the collatz_steps tool to find how many steps it takes for 20250709 to reach 1." }
];

// Handle tool calls until we get a final response
while (true) {
    const completion = await client.chat.completions.create({
        model: "grok-4.3",
        messages,
        tools,
    });

    const message = completion.choices[0].message;

    if (!message.tool_calls) {
        break;
    }

    messages.push(message);
    for (const tc of message.tool_calls) {
        const args = JSON.parse(tc.function.arguments);
        const result = collatzSteps(args.n);
        messages.push({
            role: "tool",
            tool_call_id: tc.id,
            content: String(result),
        });
    }
}

// Final call with structured output
const completion = await client.chat.completions.create({
    model: "grok-4.3",
    messages,
    response_format: {
        type: "json_schema",
        json_schema: {
            name: "collatz_result",
            schema: CollatzResultSchema,
            strict: true,
        },
    },
});

const result = JSON.parse(completion.choices[0].message.content);
console.log("Starting number:", result.starting_number);
console.log("Steps to reach 1:", result.steps);
```

## Alternative: Using `response_format` with `sample()` or `stream()`

When using the xAI Python SDK, there's an alternative way to retrieve structured outputs. Instead of using the `parse()` method, you can pass your Pydantic model directly to the `response_format` parameter when creating a chat, and then use `sample()` or `stream()` to get the response.

### How It Works

When you pass a Pydantic model to `response_format`, the SDK automatically:

1. Converts your Pydantic model to a JSON schema
2. Constrains the model's output to conform to that schema
3. Returns the response as a JSON string, that is conforming to the Pydantic model, in `response.content`

You then manually parse the JSON string into your Pydantic model instance.

### Key Differences

| Approach | Method | Returns | Parsing |
|----------|--------|---------|---------|
| **Using `parse()`** | `chat.parse(Model)` | Tuple of `(Response, Model)` | Automatic - SDK parses for you |
| **Using `response_format`** | `chat.sample()` or `chat.stream()` | `Response` with JSON string | Manual - You parse `response.content` |

### When to Use Each Approach

* **Use `parse()`** when you want the simplest, most convenient experience with automatic parsing
* **Use `response_format` + `sample()` or `stream()`** when you:
  * Want more control over the parsing process
  * Need to handle the raw JSON string before parsing
  * Want to use streaming with structured outputs
  * Are integrating with existing code that expects to work with `sample()` or `stream()`

### Example Using `response_format`

```pythonXAI
import os
from datetime import date
from enum import Enum

from pydantic import BaseModel, Field
from xai_sdk import Client
from xai_sdk.chat import system, user

# Pydantic Schemas
class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


class LineItem(BaseModel):
    description: str = Field(description="Description of the item or service")
    quantity: int = Field(description="Number of units", ge=1)
    unit_price: float = Field(description="Price per unit", ge=0)


class Address(BaseModel):
    street: str = Field(description="Street address")
    city: str = Field(description="City")
    postal_code: str = Field(description="Postal/ZIP code")
    country: str = Field(description="Country")


class Invoice(BaseModel):
    vendor_name: str = Field(description="Name of the vendor")
    vendor_address: Address = Field(description="Vendor's address")
    invoice_number: str = Field(description="Unique invoice identifier")
    invoice_date: date = Field(description="Date the invoice was issued")
    line_items: list[LineItem] = Field(description="List of purchased items/services")
    total_amount: float = Field(description="Total amount due", ge=0)
    currency: Currency = Field(description="Currency of the invoice")


client = Client(api_key=os.getenv("XAI_API_KEY"))

# Pass the Pydantic model to response_format instead of using parse()
chat = client.chat.create(
    model="grok-4.3",
    response_format=Invoice,  # Pass the Pydantic model here
)

chat.append(system("Given a raw invoice, carefully analyze the text and extract the invoice data into JSON format."))
chat.append(
    user("""
Vendor: Acme Corp, 123 Main St, Springfield, IL 62704
Invoice Number: INV-2025-001
Date: 2025-02-10
Items: - Widget A, 5 units, $10.00 each - Widget B, 2 units, $15.00 each
Total: $80.00 USD
""")
)

# Use sample() instead of parse() - returns Response object
response = chat.sample()

# The response.content is a valid JSON string conforming to your schema
print(response.content)
# Output: {"vendor_name": "Acme Corp", "vendor_address": {...}, ...}

# Manually parse the JSON string into your Pydantic model
invoice = Invoice.model_validate_json(response.content)
assert isinstance(invoice, Invoice)

# Access fields of the parsed invoice object
print(invoice.vendor_name)
print(invoice.invoice_number)
print(invoice.total_amount)
```

### Streaming with Structured Outputs

You can also use `stream()` with `response_format` to get streaming structured output. The chunks will progressively build up the JSON string:

```pythonXAI
import os

from pydantic import BaseModel, Field
from xai_sdk import Client
from xai_sdk.chat import system, user


class Summary(BaseModel):
    title: str = Field(description="A brief title")
    key_points: list[str] = Field(description="Main points from the text")
    sentiment: str = Field(description="Overall sentiment: positive, negative, or neutral")


client = Client(api_key=os.getenv("XAI_API_KEY"))

chat = client.chat.create(
    model="grok-4.3",
    response_format=Summary,  # Pass the Pydantic model here
)

chat.append(system("Analyze the following text and provide a structured summary."))
chat.append(user("The new product launch exceeded expectations with record sales..."))


# Stream the response - chunks contain partial JSON
for response, chunk in chat.stream():
    print(chunk.content, end="", flush=True)


# Parse the complete JSON string into your model
summary = Summary.model_validate_json(response.content)
print(f"Title: {summary.title}")
print(f"Sentiment: {summary.sentiment}")
```



#### Model Capabilities

# Streaming

Streaming outputs is **supported by all models with text output capability** (Chat, Image Understanding, etc.). It is **not supported by models with image output capability** (Image Generation).

Streaming outputs uses [Server-Sent Events (SSE)](https://en.wikipedia.org/wiki/Server-sent_events) that let the server send back the delta of content in event streams.

Streaming responses are beneficial for providing real-time feedback, enhancing user interaction by allowing text to be displayed as it's generated.

To enable streaming, you must set `"stream": true` in your request.

When using streaming output with reasoning models, you might want to **manually override request
timeout** to avoid prematurely closing connection.

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(
    api_key=os.getenv('XAI_API_KEY'),
    timeout=3600, # Override default timeout with longer timeout for reasoning models
)

chat = client.chat.create(model="grok-4.3")
chat.append(
    system("You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."),
)
chat.append(
    user("What is the meaning of life, the universe, and everything?")
)

for response, chunk in chat.stream():
    print(chunk.content, end="", flush=True) # Each chunk's content
    print(response.content, end="", flush=True) # The response object auto-accumulates the chunks

print(response.content) # The full response
```

```pythonOpenAISDK
import os
import httpx
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0) # Timeout after 3600s for reasoning models
)

stream = client.chat.completions.create(
    model="grok-4.3",
    messages=[
        {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."},
        {"role": "user", "content": "What is the meaning of life, the universe, and everything?"},
    ],
    stream=True # Set streaming here
)

for chunk in stream:
    print(chunk.choices[0].delta.content, end="", flush=True)
```

```javascriptOpenAISDK
import OpenAI from "openai";
const openai = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000, // Timeout after 3600s for reasoning models
});

const stream = await openai.chat.completions.create({
    model: "grok-4.3",
    messages: [
        { role: "system", content: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy." },
        {
            role: "user",
            content: "What is the meaning of life, the universe, and everything?",
        }
    ],
    stream: true
});

for await (const chunk of stream) {
    console.log(chunk.choices[0].delta.content);
}
```

```javascriptAISDK
import { xai } from '@ai-sdk/xai';
import { streamText } from 'ai';

const result = streamText({
  model: xai.responses('grok-4.3'),
  system:
    "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy.",
  prompt: 'What is the meaning of life, the universe, and everything?',
});

for await (const chunk of result.textStream) {
  process.stdout.write(chunk);
}
```

```bash
curl https://api.x.ai/v1/chat/completions \\
-H "Content-Type: application/json" \\
-H "Authorization: Bearer $XAI_API_KEY" \\
-m 3600 \\
-d '{
    "messages": [
        {
            "role": "system",
            "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."
        },
        {
            "role": "user",
            "content": "What is the meaning of life, the universe, and everything?"
        }
    ],
    "model": "grok-4.3",
    "stream": true
}'
```

You'll get the event streams like these:

```json
data: {
    "id":"<completion_id>","object":"chat.completion.chunk","created":<creation_time>,
    "model":"grok-4.3",
    "choices":[{"index":0,"delta":{"content":"Ah","role":"assistant"}}],
    "usage":{"prompt_tokens":41,"completion_tokens":1,"total_tokens":42,
    "prompt_tokens_details":{"text_tokens":41,"audio_tokens":0,"image_tokens":0,"cached_tokens":0}},
    "system_fingerprint":"fp_xxxxxxxxxx"
}

data: {
    "id":"<completion_id>","object":"chat.completion.chunk","created":<creation_time>,
    "model":"grok-4.3",
    "choices":[{"index":0,"delta":{"content":",","role":"assistant"}}],
    "usage":{"prompt_tokens":41,"completion_tokens":2,"total_tokens":43,
    "prompt_tokens_details":{"text_tokens":41,"audio_tokens":0,"image_tokens":0,"cached_tokens":0}},
    "system_fingerprint":"fp_xxxxxxxxxx"
}

data: [DONE]
```

It is recommended that you use a client SDK to parse the event stream.

Example streaming responses in Python/Javascript:

```
Ah, the ultimate question! According to Douglas Adams, the answer is **42**. However, the trick lies in figuring out what the actual question is. If you're looking for a bit more context or a different perspective:

- **Philosophically**: The meaning of life might be to seek purpose, happiness, or to fulfill one's potential.
- **Biologically**: It could be about survival, reproduction, and passing on genes.
- **Existentially**: You create your own meaning through your experiences and choices.

But let's not forget, the journey to find this meaning might just be as important as the answer itself! Keep exploring, questioning, and enjoying the ride through the universe. And remember, don't panic!
```


#### Model Capabilities

# Comparison with Chat Completions API

The Responses API is the recommended way to interact with xAI models. Here's how it compares to the legacy Chat Completions API:

| Feature | Responses API | Chat Completions API (Deprecated) |
|---------|---------------|-----------------------------------|
| **Stateful Conversations** |  Built-in support via `previous_response_id` |  Stateless - must resend full history |
| **Server-side Storage** |  Responses stored for 30 days |  No storage - manage history yourself |
| **Reasoning Models** |  Full support with encrypted reasoning content |  Limited - only `grok-3-mini` returns `reasoning_content` |
| **Agentic Tools** |  Native support for tools (search, code execution, MCP) |  Function calling only |
| **Billing Optimization** |  Automatic caching of conversation history |  Full history billed on each request |
| **Future Features** |  All new capabilities delivered here first |  Legacy endpoint, limited updates |

## Key API Changes

### Parameter Mapping

| Chat Completions | Responses API | Notes |
|-----------------|---------------|-------|
| `messages` | `input` | Array of message objects |
| `max_tokens` | `max_output_tokens` | Maximum tokens to generate |
| — | `previous_response_id` | Continue a stored conversation |
| — | `store` | Control server-side storage (default: `true`) |
| — | `include` | Request additional data like `reasoning.encrypted_content` |

### Response Structure

The response format differs between the two APIs:

**Chat Completions** returns content in `choices[0].message.content`:

```json
{
  "id": "chatcmpl-123",
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Hello! How can I help you?"
    }
  }]
}
```

**Responses API** returns content in an `output` array with typed items:

```json
{
  "id": "resp_123",
  "output": [{
    "type": "message",
    "role": "assistant",
    "content": [{
      "type": "output_text",
      "text": "Hello! How can I help you?"
    }]
  }]
}
```

### Multi-turn Conversations

With Chat Completions, you must resend the entire conversation history with each request. With Responses API, you can use `previous_response_id` to continue a conversation:

```pythonWithoutSDK
# First request
response = client.responses.create(
    model="grok-4",
    input=[{"role": "user", "content": "What is 2+2?"}],
)

# Continue the conversation - no need to resend history
second_response = client.responses.create(
    model="grok-4",
    previous_response_id=response.id,
    input=[{"role": "user", "content": "Now multiply that by 10"}],
)
```

## Migration Path

Migrating from Chat Completions to Responses API is straightforward. Here's how to update your code for each SDK:

### Vercel AI SDK

Switch from `xai()` to `xai.responses()`:

```javascriptAISDK deletedLines="1" addedLines="2"
  model: xai('grok-4'),
  model: xai.responses('grok-4'),
```

### OpenAI SDK (JavaScript)

Switch from `client.chat.completions.create` to `client.responses.create`, and rename `messages` to `input`:

```javascriptWithoutSDK deletedLines="1,3" addedLines="2,4"
const response = await client.chat.completions.create({
const response = await client.responses.create({
    messages: [
    input: [
        { role: "user", content: "Hello!" }
    ],
});

```

### OpenAI SDK (Python)

Switch from `client.chat.completions.create` to `client.responses.create`, and rename `messages` to `input`:

```pythonWithoutSDK deletedLines="1,3" addedLines="2,4"
response = client.chat.completions.create(
response = client.responses.create(
    messages=[
    input=[
        {"role": "user", "content": "Hello!"}
    ],
)
```

### cURL

Change the endpoint from `/v1/chat/completions` to `/v1/responses`, and rename `messages` to `input`:

```bash deletedLines="1,5" addedLines="2,6"
curl https://api.x.ai/v1/chat/completions \
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{ "model": "grok-4", "messages": [{"role": "user", "content": "Hello!"}] }'
  -d '{ "model": "grok-4", "input": [{"role": "user", "content": "Hello!"}] }'
```

This will work for most use cases. If you have a unique integration, refer to the [Responses API documentation](/developers/model-capabilities/text/generate-text) for detailed guidance.



#### Model Capabilities

# Multi Agent

This feature is currently in **beta**. The API interface and behavior may change as we iterate. Please bear in mind that the API interface is not final and may include breaking changes down the line.

Realtime Multi-agent Research enables Grok to orchestrate multiple AI agents that work together in real time to perform deep, multi-step research tasks. Each agent specializes in a particular aspect of the research (searching the web, analyzing data, synthesizing findings) and they collaborate to deliver comprehensive, well-sourced answers.

## Overview

Multi-agent research goes beyond single-turn tool use by coordinating a team of specialized agents that can:

* **Search and gather** information from multiple sources simultaneously
* **Analyze and cross-reference** findings across different domains
* **Synthesize** comprehensive answers with citations and supporting evidence
* **Iterate** on research in real time, refining results based on intermediate findings

## Getting Started

To use Realtime Multi-agent Research, specify `grok-4.20-multi-agent` as the model name in your API requests. This model is optimized for orchestrating multiple agents that collaborate on research tasks.

```python customLanguage="pythonXAI" highlightedLines="9"
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search, x_search

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4.20-multi-agent",
    tools=[web_search(), x_search()],
    include=["verbose_streaming"],
)

chat.append(user("Research the latest breakthroughs in quantum computing and summarize the key findings."))

is_thinking = True
for response, chunk in chat.stream():
    if response.usage.reasoning_tokens and is_thinking:
        print(f"\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
    if chunk.content and is_thinking:
        print("\n\nFinal Response:")
        is_thinking = False
    if chunk.content and not is_thinking:
        print(chunk.content, end="", flush=True)

print("\n\nUsage:")
print(response.usage)
```

```python customLanguage="pythonOpenAISDK" highlightedLines="10"
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4.20-multi-agent",
    input=[
        {
            "role": "user",
            "content": "Research the latest breakthroughs in quantum computing and summarize the key findings.",
        },
    ],
    tools=[
        {"type": "web_search"},
        {"type": "x_search"},
    ],
)

print(response)
```

```python customLanguage="pythonRequests" highlightedLines="10"
import os
import requests

url = "https://api.x.ai/v1/responses"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"
}
payload = {
    "model": "grok-4.20-multi-agent",
    "input": [
        {
            "role": "user",
            "content": "Research the latest breakthroughs in quantum computing and summarize the key findings."
        }
    ],
    "tools": [
        {"type": "web_search"},
        {"type": "x_search"}
    ]
}
response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

```bash customLanguage="bash" highlightedLines="5"
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
  "model": "grok-4.20-multi-agent",
  "input": [
    {
      "role": "user",
      "content": "Research the latest breakthroughs in quantum computing and summarize the key findings."
    }
  ],
  "tools": [
    {"type": "web_search"},
    {"type": "x_search"}
  ]
}'
```

```typescript customLanguage="javascriptAISDK" highlightedLines="5"
import { xai } from "@ai-sdk/xai";
import { generateText } from "ai";

const { text } = await generateText({
  model: xai.responses("grok-4.20-multi-agent"),
  prompt:
    "Research the latest breakthroughs in quantum computing and summarize the key findings.",
  tools: {
    web_search: xai.tools.webSearch(),
    x_search: xai.tools.xSearch(),
  },
});

console.log(text);
```

## How Multi-agent Works

When you send a request to the multi-agent model, multiple agents are launched to discuss and collaborate on your query. Each agent contributes its own perspective, reasoning, and findings. A designated **leader agent** is responsible for synthesizing the discussion and presenting the final answer back to you.

### Supported Models

* `grok-4.20-multi-agent`

### Built-in Tools Support

xAI provides a set of built-in tools you can enable in the request to help with the most common use cases, e.g., `web_search`, `x_search`, `code_execution`, `collections_search`. Check out [this doc](/developers/tools/overview) for more information.

Once you enable those tools in the request, the server will perform the agent loop to invoke those tools on the server side based on your query until the final answer is generated.

Using built-in tools will incur an additional cost. Please review the [pricing details for built-in tools](/developers/models#tools-pricing).

### Output Behavior

Only the **tool calls** and the **final response** from the leader agent are sent back to the user. All sub-agent state — including their intermediate reasoning, tool calls, and outputs — is encrypted and included in the response only when `use_encrypted_content` is set to `True` in the xAI SDK. This keeps the default response clean and focused while still allowing you to preserve the full multi-agent context for multi-turn conversations.

## Configuration

You can configure how many agents collaborate on a request. The two available setups are **4 agents** and **16 agents**. More agents means deeper, more thorough research at the cost of higher token usage and latency.

| SDK / API | Parameter | 4 Agents | 16 Agents |
|---|---|---|---|
| xAI SDK | `agent_count` | `4` | `16` |
| OpenAI SDK | `reasoning.effort` | `"low"` or `"medium"` | `"high"` or `"xhigh"` |
| Vercel AI SDK | `reasoningEffort` | `"low"` or `"medium"` | `"high"` or `"xhigh"` |
| REST API | `reasoning.effort` | `"low"` or `"medium"` | `"high"` or `"xhigh"` |

**Best For:** Use 4 agents for quick research and focused queries. Use 16 agents for deep research and complex multi-faceted topics.

### 4-Agent Setup

```python customLanguage="pythonXAI" highlightedLines="8,9"
import os

from xai_sdk import Client
from xai_sdk.chat import user

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4.20-multi-agent",
    agent_count=4,
)

chat.append(user("What are the key differences between TCP and UDP?"))
for response, chunk in chat.stream():
    if chunk.content:
        print(chunk.content, end="", flush=True)
```

```python customLanguage="pythonOpenAISDK" highlightedLines="10,11"
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4.20-multi-agent",
    reasoning={"effort": "low"},
    input=[
        {
            "role": "user",
            "content": "What are the key differences between TCP and UDP?",
        },
    ],
)

print(response.output_text)
```

```python customLanguage="pythonRequests" highlightedLines="10,11"
import os
import requests

url = "https://api.x.ai/v1/responses"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"
}
payload = {
    "model": "grok-4.20-multi-agent",
    "reasoning": {"effort": "low"},
    "input": [
        {
            "role": "user",
            "content": "What are the key differences between TCP and UDP?"
        }
    ]
}
response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

```bash customLanguage="bash" highlightedLines="5,6"
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
  "model": "grok-4.20-multi-agent",
  "reasoning": {"effort": "low"},
  "input": [
    {
      "role": "user",
      "content": "What are the key differences between TCP and UDP?"
    }
  ]
}'
```

```typescript customLanguage="javascriptAISDK" highlightedLines="5,8"
import { xai } from "@ai-sdk/xai";
import { generateText } from "ai";

const { text } = await generateText({
  model: xai.responses("grok-4.20-multi-agent"),
  prompt: "What are the key differences between TCP and UDP?",
  providerOptions: {
    xai: { reasoningEffort: "low" },
  },
});

console.log(text);
```

### 16-Agent Setup

```python customLanguage="pythonXAI" highlightedLines="8,9"
import os

from xai_sdk import Client
from xai_sdk.chat import user

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4.20-multi-agent",
    agent_count=16,
)

chat.append(user("Analyze the design trade-offs in modern programming languages: compare Rust's ownership model, Go's simplicity philosophy, and Haskell's pure functional approach. Cover memory safety, concurrency, developer productivity, and ecosystem maturity."))
for response, chunk in chat.stream():
    if chunk.content:
        print(chunk.content, end="", flush=True)
```

```python customLanguage="pythonOpenAISDK" highlightedLines="10,11"
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4.20-multi-agent",
    reasoning={"effort": "high"},
    input=[
        {
            "role": "user",
            "content": "Analyze the design trade-offs in modern programming languages: compare Rust's ownership model, Go's simplicity philosophy, and Haskell's pure functional approach. Cover memory safety, concurrency, developer productivity, and ecosystem maturity.",
        },
    ],
)

print(response.output_text)
```

```python customLanguage="pythonRequests" highlightedLines="10,11"
import os
import requests

url = "https://api.x.ai/v1/responses"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"
}
payload = {
    "model": "grok-4.20-multi-agent",
    "reasoning": {"effort": "high"},
    "input": [
        {
            "role": "user",
            "content": "Analyze the design trade-offs in modern programming languages: compare Rust's ownership model, Go's simplicity philosophy, and Haskell's pure functional approach. Cover memory safety, concurrency, developer productivity, and ecosystem maturity."
        }
    ]
}
response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

```bash customLanguage="bash" highlightedLines="5,6"
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
  "model": "grok-4.20-multi-agent",
  "reasoning": {"effort": "high"},
  "input": [
    {
      "role": "user",
      "content": "Analyze the design trade-offs in modern programming languages: compare Rust'\''s ownership model, Go'\''s simplicity philosophy, and Haskell'\''s pure functional approach. Cover memory safety, concurrency, developer productivity, and ecosystem maturity."
    }
  ]
}'
```

```typescript customLanguage="javascriptAISDK" highlightedLines="5,9"
import { xai } from "@ai-sdk/xai";
import { generateText } from "ai";

const { text } = await generateText({
  model: xai.responses("grok-4.20-multi-agent"),
  prompt:
    "Analyze the design trade-offs in modern programming languages: compare Rust's ownership model, Go's simplicity philosophy, and Haskell's pure functional approach. Cover memory safety, concurrency, developer productivity, and ecosystem maturity.",
  providerOptions: {
    xai: { reasoningEffort: "high" },
  },
});

console.log(text);
```

The 16-agent setup uses significantly more tokens than the 4-agent setup. Choose the agent count based on the complexity of your research task — use 4 agents for focused queries and 16 agents when you need comprehensive, multi-perspective analysis.

## Common Patterns

### Without Built-in Tools

Multi-agent works without any built-in tools — the agents rely purely on their collective knowledge and reasoning to collaborate on a response.

```python customLanguage="pythonXAI"
import os

from xai_sdk import Client
from xai_sdk.chat import user

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4.20-multi-agent",
    include=["verbose_streaming"],
)

chat.append(user("Compare the major approaches to distributed consensus in computer science: Paxos, Raft, and Byzantine fault tolerance. Analyze the trade-offs in safety guarantees, performance, and implementation complexity."))

is_thinking = True
for response, chunk in chat.stream():
    if response.usage.reasoning_tokens and is_thinking:
        print(f"\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
    if chunk.content and is_thinking:
        print("\n\nFinal Response:")
        is_thinking = False
    if chunk.content and not is_thinking:
        print(chunk.content, end="", flush=True)

print("\n\nUsage:")
print(response.usage)
```

```python customLanguage="pythonOpenAISDK"
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4.20-multi-agent",
    input=[
        {
            "role": "user",
            "content": "Compare the major approaches to distributed consensus in computer science: Paxos, Raft, and Byzantine fault tolerance. Analyze the trade-offs in safety guarantees, performance, and implementation complexity.",
        },
    ],
)

print(response)
```

```python customLanguage="pythonRequests"
import os
import requests

url = "https://api.x.ai/v1/responses"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"
}
payload = {
    "model": "grok-4.20-multi-agent",
    "input": [
        {
            "role": "user",
            "content": "Compare the major approaches to distributed consensus in computer science: Paxos, Raft, and Byzantine fault tolerance. Analyze the trade-offs in safety guarantees, performance, and implementation complexity."
        }
    ]
}
response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

```bash customLanguage="bash"
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
  "model": "grok-4.20-multi-agent",
  "input": [
    {
      "role": "user",
      "content": "Compare the major approaches to distributed consensus in computer science: Paxos, Raft, and Byzantine fault tolerance. Analyze the trade-offs in safety guarantees, performance, and implementation complexity."
    }
  ]
}'
```

```typescript customLanguage="javascriptAISDK"
import { xai } from "@ai-sdk/xai";
import { generateText } from "ai";

const { text } = await generateText({
  model: xai.responses("grok-4.20-multi-agent"),
  prompt:
    "Compare the major approaches to distributed consensus in computer science: Paxos, Raft, and Byzantine fault tolerance. Analyze the trade-offs in safety guarantees, performance, and implementation complexity.",
});

console.log(text);
```

### Multi-turn Conversation

Multi-agent research supports multi-turn conversations using `previous_response_id`, just like any other model. You can ask follow-up questions to refine or expand on previous research results, and the agents will use the prior context to deliver more targeted answers.

For the full multi-turn conversation pattern with reusable functions and code examples, see [Chaining the conversation](/developers/model-capabilities/text/generate-text#chaining-the-conversation).

## Pricing

All tokens consumed by both the **leader agent** and **sub-agents** are billed, including input tokens, output tokens, and reasoning tokens. Similarly, all **server-side tool calls** made by any agent — whether the leader or a sub-agent — count toward your tool usage and are billed accordingly.

Because multiple agents may run in parallel and each can independently invoke tools, a single multi-agent request may use significantly more tokens and tool calls than a standard single-agent request. You can monitor your usage via the `usage` and `server_side_tool_usage` fields in the response.

For detailed pricing information, see the [Models and Pricing](/developers/models) page and the [Tool Pricing](/developers/models#tools-pricing) page.

## Prompting Guide

Getting the most out of multi-agent research starts with how you frame your request. Here are patterns that work well:

**Set the scope and depth explicitly**

Rather than asking a broad question, tell the agents exactly what dimensions to cover:

```text
❌  "Tell me about electric vehicles."
✅  "Compare the top 3 EV manufacturers by battery technology, range, charging infrastructure, and 2025 sales projections."
```

**Ask for structured output**

Multi-agent research excels when you request organized, structured responses:

```text
✅  "Research the pros and cons of microservices vs monolithic architecture. Present your findings as a comparison table with categories: scalability, complexity, deployment, and team size requirements."
```

**Specify sources or perspectives**

Guide the agents toward the types of evidence you value:

```text
✅  "Analyze the environmental impact of large language model training, citing recent academic papers and industry reports from 2024-2025."
```

**Break complex research into a conversation**

For deep topics, start broad and narrow down with follow-ups rather than packing everything into one prompt:

```text
Turn 1: "What are the leading approaches to carbon capture technology?"
Turn 2: "Which of those has the best cost-per-ton economics today?"
Turn 3: "What are the main engineering challenges preventing that approach from scaling?"
```

**Provide context when relevant**

If your research builds on prior knowledge or specific constraints, include that context in the prompt:

```text
✅  "I'm building a fintech app targeting Southeast Asian markets. Research the regulatory requirements for digital payments in Singapore, Indonesia, and the Philippines."
```

## Limitations

* **Only leader agent output is exposed:** Only the leader agent's output is returned, including its tool calls and response content. Sub-agent state is encrypted and only included when `use_encrypted_content` is enabled — see [Output Behavior](#output-behavior) for details.
* **No client-side or custom tools:** Client-side tools (function calling) and custom tools are not currently supported by the multi-agent model variant. We do support a set of built-in tools (e.g., `web_search`, `x_search`) and remote MCP tools. See our [built-in tool docs](/developers/tools/overview) for more details.
* **Chat Completions API not supported:** The multi-agent model does **not** work with the OpenAI Chat Completions API. Use the [xAI SDK](/developers/sdk) or the [Responses API](/developers/responses-api) instead.
* **`max_tokens` is not supported:** The `max_tokens` parameter is not currently supported by the multi-agent model variant.


#### Model Capabilities

# Chat with Files

You can attach files to chat conversations using a public URL or an uploaded file ID. When files are attached, the system automatically enables document search capabilities, transforming your request into an agentic workflow.

## Attaching Files

There are two ways to attach a file to a message:

**Public URL (`file_url`)** — reference any publicly accessible file directly, no upload step needed:

```json
{"type": "input_file", "file_url": "https://example.com/document.pdf"}
```

**Uploaded file (`file_id`)** — [upload](/developers/files/managing-files) files first via the Files API and reference by ID. Useful for files that aren't publicly accessible, such as private or sensitive documents:

```json
{"type": "input_file", "file_id": "file-abc123"}
```

The examples below use `file_url` for simplicity. You can replace with `file_id` to use uploaded files instead.

## Basic Chat with a Single File

Attach a file to a conversation to let the model search through it for relevant information.

```pythonXAI
import os
from xai_sdk import Client
from xai_sdk.chat import user, file

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Attach a file by public URL (or use file(file_id) for uploaded files)
chat = client.chat.create(model="grok-4.3")
chat.append(user(
    "What was the total revenue in this report?",
    file(url="https://docs.x.ai/assets/api-examples/documents/sales-report.txt"),
))

# Get the response
response = chat.sample()

print(f"Answer: {response.content}")
```

```pythonOpenAISDK
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

# Attach a file by public URL (or use file_id for uploaded files)
response = client.responses.create(
    model="grok-4.3",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "What was the total revenue in this report?"},
                {"type": "input_file", "file_url": "https://docs.x.ai/assets/api-examples/documents/sales-report.txt"}
            ]
        }
    ]
)

final_answer = response.output[-1].content[0].text
print(f"Answer: {final_answer}")
```

```pythonRequests
import os
import requests

api_key = os.getenv("XAI_API_KEY")
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Attach a file by public URL (or use file_id for uploaded files)
chat_url = "https://api.x.ai/v1/responses"
payload = {
    "model": "grok-4.3",
    "input": [
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "What was the total revenue in this report?"},
                {"type": "input_file", "file_url": "https://docs.x.ai/assets/api-examples/documents/sales-report.txt"}
            ]
        }
    ]
}
response = requests.post(chat_url, headers=headers, json=payload)
print(response.json())
```

```javascriptOpenAISDK
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: "https://api.x.ai/v1",
});

// Attach a file by public URL (or use file_id for uploaded files)
const response = await client.responses.create({
    model: "grok-4.3",
    input: [
        {
            role: "user",
            content: [
                { type: "input_text", text: "What was the total revenue in this report?" },
                { type: "input_file", file_url: "https://docs.x.ai/assets/api-examples/documents/sales-report.txt" },
            ],
        },
    ],
});

const finalAnswer = response.output[response.output.length - 1].content[0].text;
console.log("Answer: " + finalAnswer);
```

```bash
# Attach a file by public URL (or use file_id for uploaded files)
curl -X POST "https://api.x.ai/v1/responses" \\
  -H "Authorization: Bearer $XAI_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "grok-4.3",
    "input": [
      {
        "role": "user",
        "content": [
          {"type": "input_text", "text": "What was the total revenue in this report?"},
          {"type": "input_file", "file_url": "https://docs.x.ai/assets/api-examples/documents/sales-report.txt"}
        ]
      }
    ]
  }'
```

## Streaming Chat with Files

Get real-time responses while the model searches through your documents.

```pythonXAI
import os
from xai_sdk import Client
from xai_sdk.chat import user, file

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Attach a file by public URL (or use file(file_id) for uploaded files)
chat = client.chat.create(model="grok-4.3")
chat.append(user(
    "What is the weight of the XR-2000?",
    file(url="https://docs.x.ai/assets/api-examples/documents/product-specs.txt"),
))

# Stream the response
is_thinking = True
for response, chunk in chat.stream():
    # Show tool calls as they happen
    for tool_call in chunk.tool_calls:
        print(f"\\nSearching: {tool_call.function.name}")
    
    if response.usage.reasoning_tokens and is_thinking:
        print(f"\\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
    
    if chunk.content and is_thinking:
        print("\\n\\nAnswer:")
        is_thinking = False
    
    if chunk.content:
        print(chunk.content, end="", flush=True)

print(f"\\n\\nUsage: {response.usage}")
```

```javascriptOpenAISDK
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: "https://api.x.ai/v1",
});

// Attach a file by public URL (or use file_id for uploaded files)
const stream = await client.responses.create({
    model: "grok-4.3",
    input: [
        {
            role: "user",
            content: [
                { type: "input_text", text: "What is the weight of the XR-2000?" },
                { type: "input_file", file_url: "https://docs.x.ai/assets/api-examples/documents/product-specs.txt" },
            ],
        },
    ],
    stream: true,
});

for await (const event of stream) {
    if (event.type === "response.output_text.delta") {
        process.stdout.write(event.delta);
    }
}

console.log();
```

## Multiple File Attachments

Query across multiple documents simultaneously.

```pythonXAI
import os
from xai_sdk import Client
from xai_sdk.chat import user, file

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Attach files by public URL (or use file(file_id) for uploaded files)
chat = client.chat.create(model="grok-4.3")
chat.append(
    user(
        "Based on these documents, when did the project start, what is the budget, and how many people are on the team?",
        file(url="https://docs.x.ai/assets/api-examples/documents/project-timeline.txt"),
        file(url="https://docs.x.ai/assets/api-examples/documents/project-budget.txt"),
        file(url="https://docs.x.ai/assets/api-examples/documents/project-team.txt"),
    )
)

response = chat.sample()

print(f"Answer: {response.content}")
print("\\nDocuments searched: 3")
```

```javascriptOpenAISDK
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: "https://api.x.ai/v1",
});

// Attach files by public URL (or use file_id for uploaded files)
const response = await client.responses.create({
    model: "grok-4.3",
    input: [
        {
            role: "user",
            content: [
                {
                    type: "input_text",
                    text: "Based on these documents, when did the project start, what is the budget, and how many people are on the team?",
                },
                { type: "input_file", file_url: "https://docs.x.ai/assets/api-examples/documents/project-timeline.txt" },
                { type: "input_file", file_url: "https://docs.x.ai/assets/api-examples/documents/project-budget.txt" },
                { type: "input_file", file_url: "https://docs.x.ai/assets/api-examples/documents/project-team.txt" },
            ],
        },
    ],
});

const finalAnswer = response.output[response.output.length - 1].content[0].text;
console.log("Answer: " + finalAnswer);
console.log("Documents searched: 3");
```

## Multi-Turn Conversations with Files

Maintain context across multiple questions about the same documents. Use encrypted content to preserve file context efficiently across multiple turns.

```pythonXAI
import os
from xai_sdk import Client
from xai_sdk.chat import user, file

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Create a multi-turn conversation with encrypted content
chat = client.chat.create(
    model="grok-4.3",
    use_encrypted_content=True,  # Enable encrypted content for efficient multi-turn
)

# First turn: Attach a file by public URL (or use file(file_id) for uploaded files)
chat.append(user(
    "What is the employee's name?",
    file(url="https://docs.x.ai/assets/api-examples/documents/employee-info.txt"),
))
response1 = chat.sample()
print("Q1: What is the employee's name?")
print(f"A1: {response1.content}\\n")

# Add the response to conversation history
chat.append(response1)

# Second turn: Ask about department (agentic context is retained via encrypted content)
chat.append(user("What department does this employee work in?"))
response2 = chat.sample()
print("Q2: What department does this employee work in?")
print(f"A2: {response2.content}\\n")

# Add the response to conversation history
chat.append(response2)

# Third turn: Ask about skills
chat.append(user("What skills does this employee have?"))
response3 = chat.sample()
print("Q3: What skills does this employee have?")
print(f"A3: {response3.content}\\n")
```

```javascriptOpenAISDK
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: "https://api.x.ai/v1",
});

// Attach a file by public URL (or use file_id for uploaded files)

// First turn: Ask about the document
const response1 = await client.responses.create({
    model: "grok-4.3",
    input: [
        {
            role: "user",
            content: [
                { type: "input_text", text: "What is the employee's name?" },
                { type: "input_file", file_url: "https://docs.x.ai/assets/api-examples/documents/employee-info.txt" },
            ],
        },
    ],
});

console.log("Q1: What is the employee's name?");
console.log("A1: " + response1.output[response1.output.length - 1].content[0].text + "\\n");

// Second turn: Ask about department (uses previous_response_id for context)
const response2 = await client.responses.create({
    model: "grok-4.3",
    previous_response_id: response1.id,
    input: [
        { role: "user", content: "What department does this employee work in?" },
    ],
});

console.log("Q2: What department does this employee work in?");
console.log("A2: " + response2.output[response2.output.length - 1].content[0].text + "\\n");

// Third turn: Ask about skills
const response3 = await client.responses.create({
    model: "grok-4.3",
    previous_response_id: response2.id,
    input: [
        { role: "user", content: "What skills does this employee have?" },
    ],
});

console.log("Q3: What skills does this employee have?");
console.log("A3: " + response3.output[response3.output.length - 1].content[0].text + "\\n");
```

## Combining Files with Other Modalities

You can combine file attachments with images and other content types in a single message.

```pythonXAI
import os
from xai_sdk import Client
from xai_sdk.chat import user, file, image

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Attach files by public URL (or use file(file_id) for uploaded files)
chat = client.chat.create(model="grok-4.3")
chat.append(
    user(
        "Based on the attached care guide, do you have any advice about the pictured cat?",
        file(url="https://docs.x.ai/assets/api-examples/documents/cat-care.txt"),
        image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg"),
    )
)

response = chat.sample()

print(f"Analysis: {response.content}")
```

```javascriptOpenAISDK
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: "https://api.x.ai/v1",
});

// Attach files by public URL (or use file_id for uploaded files)
const response = await client.responses.create({
    model: "grok-4.3",
    input: [
        {
            role: "user",
            content: [
                {
                    type: "input_text",
                    text: "Based on the attached care guide, do you have any advice about the pictured cat?",
                },
                { type: "input_file", file_url: "https://docs.x.ai/assets/api-examples/documents/cat-care.txt" },
                {
                    type: "input_image",
                    image_url: "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg",
                },
            ],
        },
    ],
});

const analysis = response.output[response.output.length - 1].content[0].text;
console.log("Analysis: " + analysis);
```

## Combining Files with Code Execution

For data analysis tasks, you can attach data files and enable the code execution tool. This allows Grok to write and run Python code to analyze and process your data.

```pythonXAI
import os
from xai_sdk import Client
from xai_sdk.chat import user, file
from xai_sdk.tools import code_execution

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Attach a file by public URL (or use file(file_id) for uploaded files)
chat = client.chat.create(
    model="grok-4.3",
    tools=[code_execution()],  # Enable code execution
)

chat.append(
    user(
        "Analyze this sales data and calculate: 1) Total revenue by product, 2) Average units sold by region, 3) Which product-region combination has the highest revenue",
        file(url="https://docs.x.ai/assets/api-examples/documents/sales-data.csv"),
    )
)

# Stream the response to see code execution in real-time
is_thinking = True
for response, chunk in chat.stream():
    for tool_call in chunk.tool_calls:
        if tool_call.function.name == "code_execution":
            print("\\n[Executing Code]")
    
    if response.usage.reasoning_tokens and is_thinking:
        print(f"\\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
    
    if chunk.content and is_thinking:
        print("\\n\\nAnalysis Results:")
        is_thinking = False
    
    if chunk.content:
        print(chunk.content, end="", flush=True)

print(f"\\n\\nUsage: {response.usage}")
```

```javascriptOpenAISDK
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: "https://api.x.ai/v1",
});

// Attach a file by public URL (or use file_id for uploaded files)
const stream = await client.responses.create({
    model: "grok-4.3",
    input: [
        {
            role: "user",
            content: [
                {
                    type: "input_text",
                    text: "Analyze this sales data and calculate: 1) Total revenue by product, " +
                        "2) Average units sold by region, " +
                        "3) Which product-region combination has the highest revenue",
                },
                { type: "input_file", file_url: "https://docs.x.ai/assets/api-examples/documents/sales-data.csv" },
            ],
        },
    ],
    tools: [{ type: "code_interpreter" }],
    stream: true,
});

for await (const event of stream) {
    if (event.type === "response.output_text.delta") {
        process.stdout.write(event.delta);
    }
}

console.log();
```

The model will:

1. Access the attached data file
2. Write Python code to load and analyze the data
3. Execute the code in a sandboxed environment
4. Perform calculations and statistical analysis
5. Return the results and insights in the response

## Limitations and Considerations

### Request Constraints

* **No batch requests**: File attachments with document search are agentic requests and do not support batch mode (`n > 1`)
* **Streaming recommended**: Use streaming mode for better observability of document search process

### Document Complexity

* Highly unstructured or very long documents may require more processing
* Well-organized documents with clear structure are easier to search
* Large documents with many searches can result in higher token usage

### Model Compatibility

* **Recommended models**: `grok-4-fast`, `grok-4`, `grok-4.3` for best document understanding
* **Agentic requirement**: File attachments require [agentic-capable](/developers/tools/overview) models that support server-side tools.

## Next Steps

Learn more about managing your files:





