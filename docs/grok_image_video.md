#### Model Capabilities

# Image Understanding

When sending images, it is advised to not store request/response history on the server. Otherwise the request may fail.
See .

Some models allow images in the input. The model will consider the image context when generating the response.

## Constructing the message body - difference from text-only prompt

The request message to image understanding is similar to text-only prompt. The main difference is that instead of text input:

```json
[
  {
    "role": "user",
    "content": "What is in this image?"
  }
]
```

We send in `content` as a list of objects:

```json
[
  {
    "role": "user",
    "content": [
      {
        "type": "input_image",
        "image_url": "data:image/jpeg;base64,<base64_image_string>"
      },
      {
        "type": "input_text",
        "text": "What is in this image?"
      }
    ]
  }
]
```

The `image_url.url` can also be the image's url on the Internet.

### Image understanding example

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
from xai_sdk.chat import user, image

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    management_api_key=os.getenv("XAI_MANAGEMENT_API_KEY"),
    timeout=3600,
)

image_url = "https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png"
chat = client.chat.create(model="grok-4.3")
chat.append(
    user(
        "What's in this image?",
        image(image_url=image_url, detail="high"),
    )
)

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
image_url = (
    "https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png"
)

response = client.responses.create(
    model="grok-4.3",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": image_url,
                    "detail": "high",
                },
                {
                    "type": "input_text",
                    "text": "What's in this image?",
                },
            ],
        },
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

const image_url =
    "https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png";

const response = await client.responses.create({
    model: "grok-4.3",
    input: [
        {
            role: "user",
            content: [
                {
                    type: "input_image",
                    image_url: image_url,
                    detail: "high",
                },
                {
                    type: "input_text",
                    text: "What's in this image?",
                },
            ],
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
    messages: [
        {
            role: 'user',
            content: [
                {
                    type: 'image',
                    image: new URL('https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png'),
                },
                {
                    type: 'text',
                    text: "What's in this image?",
                },
            ],
        },
    ]
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
        "role": "user",
        "content": [
          {
            "type": "input_image",
            "image_url": "https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png",
            "detail": "high"
          },
          {
            "type": "input_text",
            "text": "What'\''s in this image?"
          }
        ]
      }
    ]
  }'
```

### Image input general limits

* Maximum image size: `20MiB`
* Maximum number of images: No limit
* Supported image file types: `jpg/jpeg` or `png`.
* Any image/text input order is accepted (e.g. text prompt can precede image prompt)



#### Model Capabilities

# Image Generation

Generate images from text prompts, edit existing images with natural language, or iteratively refine images through multi-turn conversations. The API supports batch generation of multiple images, and control over aspect ratio and resolution.

**`grok-imagine-image-pro` will be deprecated as of May 15, 2025.** Use `grok-imagine-image-quality` for all new image generation requests. Existing `-pro` requests will continue to work during a transition period, but we recommend migrating promptly.

## Quick Start

Generate an image with a single API call:

```python customLanguage="pythonXAI"
import xai_sdk

client = xai_sdk.Client()

response = client.image.sample(
    prompt="A collage of London landmarks in a stenciled street‑art style",
    model="grok-imagine-image",
)

print(response.url)
```

```bash
curl -X POST https://api.x.ai/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-image",
    "prompt": "A collage of London landmarks in a stenciled street‑art style"
  }'
```

```python customLanguage="pythonOpenAISDK"
from openai import OpenAI

client = OpenAI(
    base_url="https://api.x.ai/v1",
    api_key="YOUR_API_KEY",
)

response = client.images.generate(
    model="grok-imagine-image",
    prompt="A collage of London landmarks in a stenciled street‑art style",
)

print(response.data[0].url)
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: 'https://api.x.ai/v1',
});

const response = await client.images.generate({
    model: "grok-imagine-image",
    prompt: "A collage of London landmarks in a stenciled street‑art style",
});

console.log(response.data[0].url);
```

```javascript customLanguage="javascriptAISDK"
import { xai } from "@ai-sdk/xai";
import { generateImage } from "ai";

const { image } = await generateImage({
    model: xai.image("grok-imagine-image"),
    prompt: "A collage of London landmarks in a stenciled street‑art style",
});

console.log(image.base64);
```

Images are returned as URLs by default. URLs are temporary, so download or process promptly. You can also request [base64 output](#base64-output) for embedding images directly.

## Image Editing

Edit an existing image by providing a source image along with your prompt. The model understands the image content and applies your requested changes.

The OpenAI SDK's `images.edit()` method is not supported for image editing because it uses `multipart/form-data`, while the xAI API requires `application/json`. Use the xAI SDK, Vercel AI SDK, or direct HTTP requests instead.

With the xAI SDK, use the same `sample()` method — just add the `image_url` parameter:

```python customLanguage="pythonXAI"
import base64
import xai_sdk

client = xai_sdk.Client()

# Load image from file and encode as base64
with open("photo.png", "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

response = client.image.sample(
    prompt="Render this as a pencil sketch with detailed shading",
    model="grok-imagine-image",
    image_url=f"data:image/png;base64,{image_data}",
)

print(response.url)
```

```bash
# Using a public URL as the source image
curl -X POST https://api.x.ai/v1/images/edits \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-image",
    "prompt": "Render this as a pencil sketch with detailed shading",
    "image": {
      "url": "https://docs.x.ai/assets/api-examples/images/style-realistic.png",
      "type": "image_url"
    }
  }'
```

```javascript customLanguage="javascriptAISDK"
import { xai } from "@ai-sdk/xai";
import { generateImage } from "ai";
import fs from "fs";

// Load image and encode as base64
const imageBuffer = fs.readFileSync("photo.png");
const base64Image = imageBuffer.toString("base64");

const { image } = await generateImage({
    model: xai.image("grok-imagine-image"),
    prompt: "Render this as a pencil sketch with detailed shading",
    providerOptions: {
        xai: {
            image: `data:image/png;base64,${base64Image}`,
        },
    },
});

console.log(image.base64);
```

You can provide the source image as:

* A **public URL** pointing to an image
* A **base64-encoded data URI** (e.g., `data:image/jpeg;base64,...`)

## Editing with Multiple Images

You can add up to 5 images for editing. You can specify the images in the order they are sent in the request. By default, the aspect ratio of the output image follows the first input image. You can override this by setting the `aspect_ratio` parameter to a specific ratio (e.g., `"1:1"`, `"16:9"`).

## Multi-Turn Editing

Chain multiple edits together by using each output as the input for the next. This enables iterative refinement — start with a base image and progressively add details, adjust styles, or make corrections.

## Style Transfer

The `grok-imagine-image` model excels across a wide range of visual styles — from ultra-realistic photography to anime, oil paintings, pencil sketches, and beyond. Transform existing images by simply describing the desired aesthetic in your prompt.

## Concurrent Requests

When you need to generate multiple images with **different prompts** — such as applying various style transfers to the same source image, or generating unrelated images in parallel — use `AsyncClient` with `asyncio.gather` to fire requests concurrently. This is significantly faster than issuing them one at a time.

If you want multiple variations from the **same prompt**, use [`sample_batch()` with the `n` parameter](#multiple-images) instead. That generates all images in a single request and is the most efficient approach for same-prompt generation.

```python customLanguage="pythonXAI"
import asyncio
import xai_sdk

async def generate_concurrently():
    client = xai_sdk.AsyncClient()

    source_image = "https://docs.x.ai/assets/api-examples/images/style-realistic.png"

    # Each request uses a different prompt
    prompts = [
        "Render this image as an oil painting in the style of impressionism",
        "Render this image as a pencil sketch with detailed shading",
        "Render this image as pop art with bold colors and halftone dots",
        "Render this image as a watercolor painting with soft edges",
    ]

    # Fire all requests concurrently
    tasks = [
        client.image.sample(
            prompt=prompt,
            model="grok-imagine-image",
            image_url=source_image,
        )
        for prompt in prompts
    ]

    results = await asyncio.gather(*tasks)

    for prompt, result in zip(prompts, results):
        print(f"{prompt}: {result.url}")

asyncio.run(generate_concurrently())
```

## Configuration

### Multiple Images

Generate multiple images in a single request using the `sample_batch()` method and the `n` parameter. This returns a list of `ImageResponse` objects.

```python customLanguage="pythonXAI"
import xai_sdk

client = xai_sdk.Client()

responses = client.image.sample_batch(
    prompt="A futuristic city skyline at night",
    model="grok-imagine-image",
    n=4,
)

for i, image in enumerate(responses):
    print(f"Variation {i + 1}: {image.url}")
```

```python customLanguage="pythonOpenAISDK"
from openai import OpenAI

client = OpenAI(
    base_url="https://api.x.ai/v1",
    api_key="YOUR_API_KEY",
)

response = client.images.generate(
    model="grok-imagine-image",
    prompt="A futuristic city skyline at night",
    n=4,
)

for i, image in enumerate(response.data):
    print(f"Variation {i + 1}: {image.url}")
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: "https://api.x.ai/v1",
});

const response = await client.images.generate({
    model: "grok-imagine-image",
    prompt: "A futuristic city skyline at night",
    n: 4,
});

response.data.forEach((image, i) => {
    console.log(`Variation ${i + 1}: ${image.url}`);
});

```

```javascript customLanguage="javascriptAISDK"
import { xai } from "@ai-sdk/xai";
import { generateImage } from "ai";

const { images } = await generateImage({
    model: xai.image("grok-imagine-image"),
    prompt: "A futuristic city skyline at night",
    n: 4,
});

images.forEach((image, i) => {
    console.log(`Variation ${i + 1}: ${image.base64.slice(0, 50)}...`);
});

```

```bash
curl -X POST https://api.x.ai/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-image",
    "prompt": "A futuristic city skyline at night",
    "n": 4
  }'
```

### Aspect Ratio

Control image dimensions with the `aspect_ratio` parameter. This works for image generation and image editing with multiple images.
For image editing with single image, the output aspect ratio respects the input image's aspect ratio.

| Ratio | Use case |
|-------|----------|
| `1:1` | Social media, thumbnails |
| `16:9` / `9:16` | Widescreen, mobile, stories |
| `4:3` / `3:4` | Presentations, portraits |
| `3:2` / `2:3` | Photography |
| `2:1` / `1:2` | Banners, headers |
| `19.5:9` / `9:19.5` | Modern smartphone displays |
| `20:9` / `9:20` | Ultra-wide displays |
| `auto` | Model auto-selects the best ratio for the prompt |

```python customLanguage="pythonXAI"
import xai_sdk

client = xai_sdk.Client()

response = client.image.sample(
    prompt="Mountain landscape at sunrise",
    model="grok-imagine-image",
    aspect_ratio="16:9",
)

print(response.url)
```

```python customLanguage="pythonOpenAISDK"
from openai import OpenAI

client = OpenAI(
    base_url="https://api.x.ai/v1",
    api_key="YOUR_API_KEY",
)

response = client.images.generate(
    model="grok-imagine-image",
    prompt="Mountain landscape at sunrise",
    extra_body={"aspect_ratio": "16:9"},
)

print(response.data[0].url)
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: "https://api.x.ai/v1",
});

const response = await client.images.generate({
    model: "grok-imagine-image",
    prompt: "Mountain landscape at sunrise",
    // @ts-expect-error — xAI-specific parameter
    aspect_ratio: "16:9",
});

console.log(response.data[0].url);
```

```javascript customLanguage="javascriptAISDK"
import { xai } from "@ai-sdk/xai";
import { generateImage } from "ai";

const { image } = await generateImage({
    model: xai.image("grok-imagine-image"),
    prompt: "Mountain landscape at sunrise",
    aspectRatio: "16:9",
});

console.log(image.base64);
```

```bash
curl -X POST https://api.x.ai/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-image",
    "prompt": "Mountain landscape at sunrise",
    "aspect_ratio": "16:9"
  }'
```

### Resolution

You can specify different resolutions of the output image. Currently supported image resolutions are:

* 1k
* 2k

```python customLanguage="pythonXAI"
import xai_sdk

client = xai_sdk.Client()

response = client.image.sample(
    prompt="An astronaut performing EVA in LEO.",
    model="grok-imagine-image",
    resolution="2k"
)

print(response.url)
```

```python customLanguage="pythonOpenAISDK"
from openai import OpenAI

client = OpenAI(
    base_url="https://api.x.ai/v1",
    api_key="YOUR_API_KEY",
)

response = client.images.generate(
    model="grok-imagine-image",
    prompt="An astronaut performing EVA in LEO.",
    extra_body={"resolution": "2k"},
)

print(response.data[0].url)
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: "https://api.x.ai/v1",
});

const response = await client.images.generate({
    model: "grok-imagine-image",
    prompt: "An astronaut performing EVA in LEO.",
    // @ts-expect-error — xAI-specific parameter
    resolution: "2k",
});

console.log(response.data[0].url);
```

```bash
curl -X POST https://api.x.ai/v1/images/generations \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $XAI_API_KEY" \
-d '{
    "model": "grok-imagine-image",
    "prompt": "An astronaut performing EVA in LEO.",
    "resolution": "2k"
}'
```

### Base64 Output

For embedding images directly without downloading, request base64:

```python customLanguage="pythonXAI"
import xai_sdk

client = xai_sdk.Client()

response = client.image.sample(
    prompt="A serene Japanese garden",
    model="grok-imagine-image",
    image_format="base64",
)

# Save to file
with open("garden.jpg", "wb") as f:
    f.write(response.image)
```

```python customLanguage="pythonOpenAISDK"
import base64
from openai import OpenAI

client = OpenAI(
    base_url="https://api.x.ai/v1",
    api_key="YOUR_API_KEY",
)

response = client.images.generate(
    model="grok-imagine-image",
    prompt="A serene Japanese garden",
    response_format="b64_json",
)

# Save to file
image_bytes = base64.b64decode(response.data[0].b64_json)
with open("garden.jpg", "wb") as f:
    f.write(image_bytes)
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";
import fs from "fs";

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: "https://api.x.ai/v1",
});

const response = await client.images.generate({
    model: "grok-imagine-image",
    prompt: "A serene Japanese garden",
    response_format: "b64_json",
});

// Save to file
const imageBuffer = Buffer.from(response.data[0].b64_json, "base64");
fs.writeFileSync("garden.jpg", imageBuffer);
```

```javascript customLanguage="javascriptAISDK"
import { xai } from "@ai-sdk/xai";
import { generateImage } from "ai";
import fs from "fs";

const { image } = await generateImage({
    model: xai.image("grok-imagine-image"),
    prompt: "A serene Japanese garden",
});

// Save to file (AI SDK returns base64 by default)
const imageBuffer = Buffer.from(image.base64, "base64");
fs.writeFileSync("garden.jpg", imageBuffer);
```

```bash
curl -X POST https://api.x.ai/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-image",
    "prompt": "A serene Japanese garden",
    "response_format": "b64_json"
  }'
```

### Response Details

The xAI SDK exposes additional metadata on the response object beyond the image URL or base64 data.

**Moderation** — Check whether the generated image passed content moderation:

```python customLanguage="pythonXAI"
if response.respect_moderation:
    print(response.url)
else:
    print("Image filtered by moderation")
```

**Model** — Get the actual model used (resolving any aliases):

```python customLanguage="pythonXAI"
print(f"Model: {response.model}")
```

## Pricing

Image generation uses flat per-image pricing rather than token-based pricing like text models. Each generated image incurs a fixed fee regardless of prompt length.

For image editing, you are charged for both the input image and the generated output image.

For full pricing details on the `grok-imagine-image` model, see the [model page](/developers/models/grok-imagine-image).

## Limitations

* **Maximum images per request:** 10
* **URL expiration:** Generated URLs are temporary
* **Content moderation:** Images are subject to content policy review

## Related

* [Models](/developers/models) — Available image models
* [Video Generation](/developers/model-capabilities/video/generation) — Animate generated images
* [API Reference](/developers/rest-api-reference) — Full endpoint documentation
* [Imagine API Landing Page](https://x.ai/api/imagine) — Showcase of the Imagine API in action


#### Model Capabilities

# Video Generation

Generate videos from text prompts, animate still images, use reference images to guide style and content, edit existing videos, or extend them with natural language. The API supports configurable duration, aspect ratio, and resolution for generated videos — with the SDK handling the asynchronous polling automatically.

## Quick Start

Generate a video with a single API call:

```python customLanguage="pythonXAI"
import os
import xai_sdk

client = xai_sdk.Client(api_key=os.getenv("XAI_API_KEY"))

response = client.video.generate(
    prompt="A glowing crystal-powered rocket launching from the red dunes of Mars, ancient alien ruins lighting up in the background as it soars into a sky full of unfamiliar constellations",
    model="grok-imagine-video",
    duration=10,
    aspect_ratio="16:9",
    resolution="720p",
)

print(response.url)
```

```python customLanguage="pythonRequests"
import os
import time
import requests

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['XAI_API_KEY']}",
}

response = requests.post(
    "https://api.x.ai/v1/videos/generations",
    headers=headers,
    json={
        "model": "grok-imagine-video",
        "prompt": "A glowing crystal-powered rocket launching from the red dunes of Mars, ancient alien ruins lighting up in the background as it soars into a sky full of unfamiliar constellations",
        "duration": 10,
        "aspect_ratio": "16:9",
        "resolution": "720p",
    },
)

request_id = response.json()["request_id"]

# Poll until the video is ready
while True:
    result = requests.get(
        f"https://api.x.ai/v1/videos/{request_id}",
        headers={"Authorization": headers["Authorization"]},
    )
    data = result.json()
    if data["status"] == "done":
        print(data["video"]["url"])
        break
    elif data["status"] == "expired":
        print("Request expired")
        break
    time.sleep(5)
```

```javascript customLanguage="javascriptAISDK"
import { xai } from "@ai-sdk/xai";
import { experimental_generateVideo as generateVideo } from "ai";

const result = await generateVideo({
    model: xai.video("grok-imagine-video"),
    prompt: "A glowing crystal-powered rocket launching from the red dunes of Mars, ancient alien ruins lighting up in the background as it soars into a sky full of unfamiliar constellations",
    duration: 10,
    aspectRatio: "16:9",
    providerOptions: {
        xai: { resolution: "720p" },
    },
});

const videoUrl = result.providerMetadata?.xai?.videoUrl;
console.log(videoUrl);
```

```bash
curl -X POST https://api.x.ai/v1/videos/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-video",
    "prompt": "A glowing crystal-powered rocket launching from the red dunes of Mars, ancient alien ruins lighting up in the background as it soars into a sky full of unfamiliar constellations",
    "duration": 10,
    "aspect_ratio": "16:9",
    "resolution": "720p"
  }'
```

Video generation is an **asynchronous process** that typically takes up to several minutes to complete. The exact time varies based on:

* **Prompt complexity** — More detailed scenes require additional processing
* **Duration** — Longer videos take more time to generate
* **Resolution** — Higher resolutions (720p vs 480p) increase processing time
* **Video editing** — Editing existing videos adds overhead compared to image-to-video or text-to-video

### How it works

Under the hood, video generation is a two-step process:

1. **Start** — Submit a generation request and receive a `request_id`
2. **Poll** — Repeatedly check the status using the `request_id` until the video is ready

The xAI SDK's `generate()` and `extend()` methods abstract this entirely — they submit your request, poll for the result, and return the completed video response. You don't need to manage request IDs or implement polling logic. For long-running generations, you can [customize the polling behavior](#customize-polling-behavior) with timeout and interval parameters, or [handle polling manually](#handle-polling-manually) for full control over the generation lifecycle.

**REST API users** must implement this two-step flow manually:

**Step 1: Start the generation request**

```bash
curl -X POST https://api.x.ai/v1/videos/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-video",
    "prompt": "A glowing crystal-powered rocket launching from Mars"
  }'
```

Response:

```json
{"request_id": "d97415a1-5796-b7ec-379f-4e6819e08fdf"}
```

**Step 2: Poll for the result**

Use the `request_id` to check the status. Keep polling every few seconds until the video is ready:

```bash
curl -X GET "https://api.x.ai/v1/videos/{request_id}" \
  -H "Authorization: Bearer $XAI_API_KEY"
```

The response includes a `status` field with one of these values:

| Status | Description |
|--------|-------------|
| `pending` | Video is still being generated |
| `done` | Video is ready |
| `expired` | Request has expired |
| `failed` | Video generation failed |

Response (when complete):

```json
{
  "status": "done",
  "video": {
    "url": "https://vidgen.x.ai/.../video.mp4",
    "duration": 8,
    "respect_moderation": true
  },
  "model": "grok-imagine-video"
}
```

Videos are returned as temporary URLs. Access the xAI-hosted URL directly when you need it, or download/process it promptly if you need to keep a copy.

## Generate Videos from Images

Transform a still image into a video by providing a source image along with your prompt. The model animates the image content based on your instructions.

You can provide the source image as:

* A **public URL** pointing to an image
* A **base64-encoded data URI** (e.g., `data:image/jpeg;base64,...`)

The demo below shows this in action — hold to animate a still image:

In the Vercel AI SDK, the `prompt` parameter accepts an object with `image` and `text` fields for image-to-video generation. The `image` field can be a URL string, base64-encoded string, `Uint8Array`, `ArrayBuffer`, or `Buffer`.

## Edit Existing Videos

Edit an existing video by providing a source video along with your prompt. The model understands the video content and applies your requested changes.

The demo below shows video editing in action — `grok-imagine-video` delivers high-fidelity edits with strong scene preservation, modifying only what you ask for while keeping the rest of the video intact:

In the Vercel AI SDK, video editing is triggered by setting `providerOptions.xai.mode` to `"edit-video"` and passing `providerOptions.xai.videoUrl` with a source video URL. The `prompt` describes the desired modifications; `duration`, `aspectRatio`, and `resolution` are ignored because the output inherits these properties from the input video, capped at 720p.

## Generate Videos using Reference Images

Provide one or more reference images to incorporate specific people, objects, clothing, or other visual elements into the generated video. The model uses the reference images as a visual guide, producing a video that features the content from those images — making it ideal for use cases like virtual try-on, product placement, or character-consistent storytelling.

Unlike [image-to-video](#generate-videos-from-images) where the source image becomes the starting frame, reference images influence what appears in the video without locking in the first frame.

Each reference image can be provided as a public HTTPS URL or a base64-encoded data URI. In the AI SDK, set `providerOptions.xai.mode` to `"reference-to-video"` and pass the images with `providerOptions.xai.referenceImageUrls`.

```python customLanguage="pythonXAI"
import os
import xai_sdk

client = xai_sdk.Client(api_key=os.getenv("XAI_API_KEY"))

response = client.video.generate(
    prompt="slow zoom in on the white fashion runway stage. then, the model from <IMAGE_1> walks in from the back of the shot from the white opening, and gracefully walk out onto the front of the white stage platform. they wear the shirt from <IMAGE_2> and black flared jeans. they look dramatically at the camera. high quality slow motion shot. fun, playful. skin pores. highly detailed faces. perfect shot. they reach the end of the runway and look at the camera as the camera slowly zooms. subtle smile.",
    model="grok-imagine-video",
    reference_image_urls=[
        "<IMAGE_URL_1>",
        "<IMAGE_URL_2>",
        "<IMAGE_URL_3>",
    ],
    duration=10,
    aspect_ratio="16:9",
    resolution="720p",
)

print(response.url)
```

```python customLanguage="pythonRequests"
import os
import time
import requests

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['XAI_API_KEY']}",
}

response = requests.post(
    "https://api.x.ai/v1/videos/generations",
    headers=headers,
    json={
        "model": "grok-imagine-video",
        "prompt": "slow zoom in on the white fashion runway stage. then, the model from <IMAGE_1> walks in from the back of the shot from the white opening, and gracefully walk out onto the front of the white stage platform. they wear the shirt from <IMAGE_2> and black flared jeans. they look dramatically at the camera. high quality slow motion shot. fun, playful. skin pores. highly detailed faces. perfect shot. they reach the end of the runway and look at the camera as the camera slowly zooms. subtle smile.",
        "reference_images": [
            {"url": "<IMAGE_URL_1>"},
            {"url": "<IMAGE_URL_2>"},
            {"url": "<IMAGE_URL_3>"},
        ],
        "duration": 10,
        "aspect_ratio": "16:9",
        "resolution": "720p",
    },
)

request_id = response.json()["request_id"]

while True:
    result = requests.get(
        f"https://api.x.ai/v1/videos/{request_id}",
        headers={"Authorization": headers["Authorization"]},
    )
    data = result.json()
    if data["status"] == "done":
        print(data["video"]["url"])
        break
    elif data["status"] == "expired":
        print("Request expired")
        break
    time.sleep(5)
```

```javascript customLanguage="javascriptAISDK"
import { xai, type XaiVideoModelOptions } from "@ai-sdk/xai";
import { experimental_generateVideo as generateVideo } from "ai";

const result = await generateVideo({
    model: xai.video("grok-imagine-video"),
    prompt: "slow zoom in on the white fashion runway stage. then, the model from <IMAGE_1> walks in from the back of the shot from the white opening, and gracefully walk out onto the front of the white stage platform. they wear the shirt from <IMAGE_2> and black flared jeans. they look dramatically at the camera. high quality slow motion shot. fun, playful. skin pores. highly detailed faces. perfect shot. they reach the end of the runway and look at the camera as the camera slowly zooms. subtle smile.",
    duration: 10,
    aspectRatio: "16:9",
    providerOptions: {
        xai: {
            mode: "reference-to-video",
            referenceImageUrls: [
                "<IMAGE_URL_1>",
                "<IMAGE_URL_2>",
                "<IMAGE_URL_3>",
            ],
            resolution: "720p",
            pollTimeoutMs: 600000,
        } satisfies XaiVideoModelOptions,
    },
});

const videoUrl = result.providerMetadata?.xai?.videoUrl;
console.log(videoUrl);
```

```bash
curl -X POST https://api.x.ai/v1/videos/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-video",
    "prompt": "slow zoom in on the white fashion runway stage. then, the model from <IMAGE_1> walks in from the back of the shot from the white opening, and gracefully walk out onto the front of the white stage platform. they wear the shirt from <IMAGE_2> and black flared jeans. they look dramatically at the camera. high quality slow motion shot. fun, playful. skin pores. highly detailed faces. perfect shot. they reach the end of the runway and look at the camera as the camera slowly zooms. subtle smile.",
    "reference_images": [
      {"url": "<IMAGE_URL_1>"},
      {"url": "<IMAGE_URL_2>"},
      {"url": "<IMAGE_URL_3>"}
    ],
    "duration": 10,
    "aspect_ratio": "16:9",
    "resolution": "720p"
  }'
```

## Extend Existing Videos

Extend an existing video by providing a source video and a text prompt describing what should happen next. The result is a single video that picks up seamlessly from the last frame of the input and continues with the generated content.

The `duration` parameter controls the length of the **extended portion only**, not the total output. For example, if your input video is 10 seconds and you set `duration` to 5, the returned video will be 15 seconds long (10s original + 5s extension).

```python customLanguage="pythonXAI"
import os
import xai_sdk

client = xai_sdk.Client(api_key=os.getenv("XAI_API_KEY"))

response = client.video.extend(
    prompt="The shot pans to an over the shoulder perspective. Calm controlled scene.",
    model="grok-imagine-video",
    video_url="<VIDEO_URL>",
    duration=10,
)

print(response.url)
```

```python customLanguage="pythonRequests"
import os
import time
import requests

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['XAI_API_KEY']}",
}

response = requests.post(
    "https://api.x.ai/v1/videos/extensions",
    headers=headers,
    json={
        "model": "grok-imagine-video",
        "prompt": "The shot pans to an over the shoulder perspective. Calm controlled scene.",
        "duration": 10,
        "video": {"url": "<VIDEO_URL>"},
    },
)

request_id = response.json()["request_id"]

while True:
    result = requests.get(
        f"https://api.x.ai/v1/videos/{request_id}",
        headers={"Authorization": headers["Authorization"]},
    )
    data = result.json()
    if data["status"] == "done":
        print(data["video"]["url"])
        break
    elif data["status"] == "expired":
        print("Request expired")
        break
    time.sleep(5)
```

```javascript customLanguage="javascriptAISDK"
import { xai, type XaiVideoModelOptions } from "@ai-sdk/xai";
import { experimental_generateVideo as generateVideo } from "ai";

const source = await generateVideo({
    model: xai.video("grok-imagine-video"),
    prompt: "A cat sitting on a sunlit windowsill, tail gently swishing.",
    duration: 5,
    aspectRatio: "16:9",
    providerOptions: {
        xai: {
            pollTimeoutMs: 600000,
        } satisfies XaiVideoModelOptions,
    },
});

const sourceUrl = source.providerMetadata?.xai?.videoUrl as string;

const extended = await generateVideo({
    model: xai.video("grok-imagine-video"),
    prompt: "The cat turns its head, notices a butterfly, and leaps off.",
    duration: 6,
    providerOptions: {
        xai: {
            mode: "extend-video",
            videoUrl: sourceUrl,
            pollTimeoutMs: 600000,
        } satisfies XaiVideoModelOptions,
    },
});

const extendedVideoUrl = extended.providerMetadata?.xai?.videoUrl;
console.log(extendedVideoUrl);
```

```bash
curl -X POST https://api.x.ai/v1/videos/extensions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-video",
    "prompt": "The shot pans to an over the shoulder perspective. Calm controlled scene.",
    "duration": 10,
    "video": {"url": "<VIDEO_URL>"}
  }'
```

Video editing uses the `/v1/videos/edits` endpoint and `client.video.generate(video_url=...)` in the Python SDK. In the AI SDK, set `providerOptions.xai.mode` to `"edit-video"` or `"extend-video"` and pass `providerOptions.xai.videoUrl`. The same asynchronous polling pattern applies to both flows, and the AI SDK returns the xAI-hosted output URL in `providerMetadata.xai.videoUrl`.

## Configuration

The video generation API lets you control the output format of your generated videos. You can specify the duration, aspect ratio, and resolution to match your specific use case.

### Duration

Control video length with the `duration` parameter. The allowed range is 1–15 seconds.

Video editing does not support custom `duration`. The edited video retains the duration of the original, which is capped at 8.7 seconds.

### Aspect Ratio

| Ratio | Use case |
|-------|----------|
| `1:1` | Social media, thumbnails |
| `16:9` / `9:16` | Widescreen, mobile, stories (default: `16:9`) |
| `4:3` / `3:4` | Presentations, portraits |
| `3:2` / `2:3` | Photography |

For image-to-video generation, the output defaults to the input image's aspect ratio. If you specify the `aspect_ratio` parameter, it will override this and stretch the image to the desired aspect ratio.

Video editing does not support custom `aspect_ratio` — the output matches the input video's aspect ratio.

### Resolution

| Resolution | Description |
|------------|-------------|
| `720p` | HD quality |
| `480p` | Standard definition, faster processing (default) |

Video editing does not support custom `resolution`. The output resolution matches the input video's resolution, capped at 720p (e.g., a 1080p input will be downsized to 720p).

### Example

```python customLanguage="pythonXAI"
import os
import xai_sdk

client = xai_sdk.Client(api_key=os.getenv("XAI_API_KEY"))

response = client.video.generate(
    prompt="Timelapse of a flower blooming in a sunlit garden",
    model="grok-imagine-video",
    duration=10,
    aspect_ratio="16:9",
    resolution="720p",
)

print(f"Video URL: {response.url}")
print(f"Duration: {response.duration}s")
```

```python customLanguage="pythonRequests"
import os
import time
import requests

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['XAI_API_KEY']}",
}

response = requests.post(
    "https://api.x.ai/v1/videos/generations",
    headers=headers,
    json={
        "model": "grok-imagine-video",
        "prompt": "Timelapse of a flower blooming in a sunlit garden",
        "duration": 10,
        "aspect_ratio": "16:9",
        "resolution": "720p",
    },
)

request_id = response.json()["request_id"]

while True:
    result = requests.get(
        f"https://api.x.ai/v1/videos/{request_id}",
        headers={"Authorization": headers["Authorization"]},
    )
    data = result.json()
    if data["status"] == "done":
        print(f"Video URL: {data['video']['url']}")
        print(f"Duration: {data['video']['duration']}s")
        break
    elif data["status"] == "expired":
        print("Request expired")
        break
    time.sleep(5)
```

```javascript customLanguage="javascriptAISDK"
import { xai } from "@ai-sdk/xai";
import { experimental_generateVideo as generateVideo } from "ai";

const result = await generateVideo({
    model: xai.video("grok-imagine-video"),
    prompt: "Timelapse of a flower blooming in a sunlit garden",
    duration: 10,
    aspectRatio: "16:9",
    providerOptions: {
        xai: { resolution: "720p" },
    },
});

const videoUrl = result.providerMetadata?.xai?.videoUrl;
console.log(videoUrl);
```

```bash
curl -X POST https://api.x.ai/v1/videos/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-video",
    "prompt": "Timelapse of a flower blooming in a sunlit garden",
    "duration": 10,
    "aspect_ratio": "16:9",
    "resolution": "720p"
  }'
```

### Request Modes

The video generation endpoint supports multiple modes, determined by which fields are set. Only one mode can be active per request:

| Mode | REST API fields | AI SDK shape | Description |
|------|-----------------|--------------|-------------|
| Text-to-video | `prompt` only | `prompt: "..."` | Generates video from a text prompt alone. |
| Image-to-video | `prompt` + `image` | `prompt: { image, text }` | Generates video with the provided image as the starting frame. |
| Reference-to-video | `prompt` + `reference_images` | `prompt: "..."` + `providerOptions.xai.{ mode: "reference-to-video", referenceImageUrls }` | Generates video guided by one or more reference images. |
| Edit-video | `/v1/videos/edits` + `video_url` | `prompt: "..."` + `providerOptions.xai.{ mode: "edit-video", videoUrl }` | Modifies an existing video based on the prompt. |
| Extend-video | `/v1/videos/extensions` + `video` | `prompt: "..."` + `providerOptions.xai.{ mode: "extend-video", videoUrl }` | Extends an existing video from its last frame. |

The following combination is **not allowed** and will return a `400 Bad Request` error:

* `image` + `reference_images` — use one or the other
* Mixing `mode` values in the AI SDK — each request supports exactly one of `"edit-video"`, `"extend-video"`, or `"reference-to-video"`

When you omit `mode`, the AI SDK uses standard generation.

## Customize Polling Behavior

When using the SDK's `generate()` or `extend()` methods, you can control how long to wait and how frequently to check for results:

| Python SDK | AI SDK (`providerOptions.xai`) | Description | Default |
|-----------|-------------|-------------|---------|
| `timeout` | `pollTimeoutMs` | Maximum time to wait for the video to complete | 10 minutes |
| `interval` | `pollIntervalMs` | Time between status checks | 100 milliseconds |

```python customLanguage="pythonXAI"
import os
from datetime import timedelta
import xai_sdk

client = xai_sdk.Client(api_key=os.getenv("XAI_API_KEY"))

response = client.video.generate(
    prompt="Epic cinematic drone shot flying through mountain peaks",
    model="grok-imagine-video",
    duration=15,
    timeout=timedelta(minutes=15),  # Wait up to 15 minutes
    interval=timedelta(seconds=5),  # Check every 5 seconds
)

print(response.url)
```

```javascript customLanguage="javascriptAISDK"
import { xai } from "@ai-sdk/xai";
import { experimental_generateVideo as generateVideo } from "ai";

const result = await generateVideo({
    model: xai.video("grok-imagine-video"),
    prompt: "Epic cinematic drone shot flying through mountain peaks",
    duration: 15,
    providerOptions: {
        xai: {
            pollTimeoutMs: 15 * 60 * 1000,  // Wait up to 15 minutes
            pollIntervalMs: 5 * 1000,        // Check every 5 seconds
        },
    },
});

const videoUrl = result.providerMetadata?.xai?.videoUrl;
console.log(videoUrl);
```

If the video isn't ready within the timeout period, the Python SDK raises a `TimeoutError` and the AI SDK aborts via its `AbortSignal`. For even finer control, use the [manual polling approach](#handle-polling-manually) — the Python SDK provides `start()` and `get()` methods, while the AI SDK supports a custom `abortSignal` for cancellation.

## Handle Polling Manually

For fine-grained control over the generation lifecycle, use `start()` or `extend_start()` to initiate generation/extension requests respectively and `get()` to check status.

The `get()` method returns a response with a `status` field. Import the status enum from the SDK:

```python customLanguage="pythonXAI"
import os
import time
import xai_sdk
from xai_sdk.proto import deferred_pb2

client = xai_sdk.Client(api_key=os.getenv("XAI_API_KEY"))

# Start the generation request
start_response = client.video.start(
    prompt="A cat lounging in a sunbeam, tail gently swishing",
    model="grok-imagine-video",
    duration=5,
)

print(f"Request ID: {start_response.request_id}")

# Poll for results
while True:
    result = client.video.get(start_response.request_id)
    
    if result.status == deferred_pb2.DeferredStatus.DONE:
        print(f"Video URL: {result.response.video.url}")
        break
    elif result.status == deferred_pb2.DeferredStatus.EXPIRED:
        print("Request expired")
        break
    elif result.status == deferred_pb2.DeferredStatus.FAILED:
        print("Video generation failed")
        break
    elif result.status == deferred_pb2.DeferredStatus.PENDING:
        print("Still processing...")
        time.sleep(5)
```

```python customLanguage="pythonRequests"
import os
import time
import requests

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['XAI_API_KEY']}",
}

# Step 1: Start generation
response = requests.post(
    "https://api.x.ai/v1/videos/generations",
    headers=headers,
    json={
        "model": "grok-imagine-video",
        "prompt": "A cat lounging in a sunbeam, tail gently swishing",
        "duration": 5,
    },
)

request_id = response.json()["request_id"]
print(f"Request ID: {request_id}")

# Step 2: Poll for results
while True:
    result = requests.get(
        f"https://api.x.ai/v1/videos/{request_id}",
        headers={"Authorization": headers["Authorization"]},
    )
    data = result.json()

    if data["status"] == "done":
        print(f"Video URL: {data['video']['url']}")
        break
    elif data["status"] == "expired":
        print("Request expired")
        break
    elif data["status"] == "failed":
        print("Video generation failed")
        break
    else:
        print("Still processing...")
        time.sleep(5)
```

```javascript customLanguage="javascriptWithoutSDK"
// Step 1: Start generation
const response = await fetch("https://api.x.ai/v1/videos/generations", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${process.env.XAI_API_KEY}`,
    },
    body: JSON.stringify({
        model: "grok-imagine-video",
        prompt: "A cat lounging in a sunbeam, tail gently swishing",
        duration: 5,
    }),
});

const { request_id } = await response.json();
console.log(`Request ID: ${request_id}`);

// Step 2: Poll for results
while (true) {
    const result = await fetch(`https://api.x.ai/v1/videos/${request_id}`, {
        headers: { "Authorization": `Bearer ${process.env.XAI_API_KEY}` },
    });

    const data = await result.json();

    if (data.status === "done") {
        console.log(`Video URL: ${data.video.url}`);
        break;
    } else if (data.status === "expired") {
        console.log("Request expired");
        break;
    } else if (data.status === "failed") {
        console.log("Video generation failed");
        break;
    } else {
        console.log("Still processing...");
        await new Promise(resolve => setTimeout(resolve, 5000));
    }
}
```

```bash
# Step 1: Start generation
curl -X POST https://api.x.ai/v1/videos/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-video",
    "prompt": "A cat lounging in a sunbeam, tail gently swishing",
    "duration": 5
  }'

# Response: {"request_id": "{request_id}"}

# Step 2: Poll for results
curl -X GET https://api.x.ai/v1/videos/{request_id} \
  -H "Authorization: Bearer $XAI_API_KEY"
```

The available status values are:

| Proto Value | Description |
|-------------|-------------|
| `deferred_pb2.DeferredStatus.PENDING` | Video is still being generated |
| `deferred_pb2.DeferredStatus.DONE` | Video is ready |
| `deferred_pb2.DeferredStatus.EXPIRED` | Request has expired |
| `deferred_pb2.DeferredStatus.FAILED` | Video generation failed |

## Error Handling

When using the SDK's `generate()` or `extend()` methods, video generation failures are raised as a `VideoGenerationError` exception. This exception includes a `code` and `message` describing what went wrong. Import it from `xai_sdk.video`:

```python customLanguage="pythonXAI"
import os
import xai_sdk
from xai_sdk.video import VideoGenerationError

client = xai_sdk.Client(api_key=os.getenv("XAI_API_KEY"))

try:
    response = client.video.generate(
        prompt="A cat lounging in a sunbeam, tail gently swishing",
        model="grok-imagine-video",
        duration=5,
    )
    print(response.url)
except VideoGenerationError as e:
    print(f"Error code: {e.code}")
    print(f"Error message: {e.message}")
```

The `VideoGenerationError` exception has the following attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `code` | `str` | An error code identifying the failure reason |
| `message` | `str` | A human-readable message describing the failure |

When polling manually, a failed generation returns `status: "failed"` with an `error` object:

```json
{
  "status": "failed",
  "error": {
    "code": "invalid_argument",
    "message": "Prompt cannot be empty. Please provide a prompt."
  }
}
```

The possible `error.code` values are:

| Code | Meaning | What to do |
|------|---------|------------|
| `invalid_argument` | The request input is invalid, such as an unsupported duration, an invalid image or video input, a prompt that is too long, conflicting request modes, or content blocked by moderation. | Fix the request parameters or input media, then submit a new request. |
| `permission_denied` | The API key or team does not have permission for the requested video operation. | Confirm the API key belongs to the right team and that the team has access to the requested capability. |
| `failed_precondition` | The requested operation is not available for the selected model or settings, such as video editing, video extension, or a requested resolution that the model cannot process. | Change the model, mode, resolution, or other request settings. |
| `internal_error` | The service could not complete the generation because of an internal failure. | Retry the request. If the error persists, contact xAI support with the `request_id`. |

Authentication errors, missing models, and rate limits are returned synchronously as standard API errors before a video job is created, so they do not appear in the `error.code` field of a failed video result.

You can combine this with `TimeoutError` handling for comprehensive error coverage:

```python customLanguage="pythonXAI"
import os
import xai_sdk
from xai_sdk.video import VideoGenerationError

client = xai_sdk.Client(api_key=os.getenv("XAI_API_KEY"))

try:
    response = client.video.generate(
        prompt="A cat lounging in a sunbeam, tail gently swishing",
        model="grok-imagine-video",
        duration=5,
    )
    print(response.url)
except VideoGenerationError as e:
    print(f"Generation failed [{e.code}]: {e.message}")
except TimeoutError:
    print("Generation timed out — try increasing the timeout or simplifying the prompt")
```

## Response Details

The SDK response includes the generated video and provider-specific metadata. In the AI SDK, the xAI-hosted output URL is available at `providerMetadata.xai.videoUrl`.

```python customLanguage="pythonXAI"
if response.respect_moderation:
    print(response.url)
else:
    print("Video filtered by moderation")

print(f"Duration: {response.duration} seconds")
print(f"Model: {response.model}")
```

```javascript customLanguage="javascriptAISDK"
const result = await generateVideo({
    model: xai.video("grok-imagine-video"),
    prompt: "A futuristic city skyline at dusk",
    duration: 5,
});

console.log(result.providerMetadata?.xai?.videoUrl);
```

## Concurrent Requests

When you need to generate multiple videos or apply several edits to the same source video, run requests concurrently. This is especially useful for branching multiple edits from the same intermediate result.

The examples below show both Python concurrency and the AI SDK pattern for chaining one edit into concurrent follow-up edits.

```python customLanguage="pythonXAI"
import os
import asyncio
import xai_sdk

async def edit_concurrently():
    client = xai_sdk.AsyncClient(api_key=os.getenv("XAI_API_KEY"))

    source_video = "https://data.x.ai/docs/video-generation/portrait-wave.mp4"

    prompts = [
        "Give the woman a silver necklace",
        "Change the color of the woman's outfit to red",
        "Give the woman a wide-brimmed black hat",
    ]

    tasks = [
        client.video.generate(
            prompt=prompt,
            model="grok-imagine-video",
            video_url=source_video,
        )
        for prompt in prompts
    ]

    results = await asyncio.gather(*tasks)

    for prompt, result in zip(prompts, results):
        print(f"{prompt}: {result.url}")

asyncio.run(edit_concurrently())
```

```javascript customLanguage="javascriptAISDK"
import { xai, type XaiVideoModelOptions } from "@ai-sdk/xai";
import { experimental_generateVideo as generateVideo } from "ai";

const providerOptions = {
    xai: {
        mode: "edit-video",
        videoUrl: "https://example.com/source-video.mp4",
        pollTimeoutMs: 600000,
    } satisfies XaiVideoModelOptions,
};

const step1 = await generateVideo({
    model: xai.video("grok-imagine-video"),
    prompt: "Add a party hat to the person",
    providerOptions,
});

const step1VideoUrl = step1.providerMetadata?.xai?.videoUrl as string;

const [withSunglasses, withScarf] = await Promise.all([
    generateVideo({
        model: xai.video("grok-imagine-video"),
        prompt: "Add sunglasses",
        providerOptions: {
            xai: {
                mode: "edit-video",
                videoUrl: step1VideoUrl,
                pollTimeoutMs: 600000,
            } satisfies XaiVideoModelOptions,
        },
    }),
    generateVideo({
        model: xai.video("grok-imagine-video"),
        prompt: "Add a scarf",
        providerOptions: {
            xai: {
                mode: "edit-video",
                videoUrl: step1VideoUrl,
                pollTimeoutMs: 600000,
            } satisfies XaiVideoModelOptions,
        },
    }),
]);

console.log(withSunglasses.providerMetadata?.xai?.videoUrl);
console.log(withScarf.providerMetadata?.xai?.videoUrl);
```

## Pricing

Video generation uses per-second pricing. Longer videos cost more, and both duration and resolution affect the total cost.

For full pricing details on the `grok-imagine-video` model, see the [model page](/developers/models).

## Limitations

* **Maximum duration:** 15 seconds for generation, 8.7 seconds for editing input videos, 2–10 seconds for video extensions (input video must be 2–15 seconds)
* **URL expiration:** Generated URLs are ephemeral and should not be relied upon for long-term storage
* **Resolutions:** 480p or 720p
* **Content moderation:** Videos are subject to content policy review

## Related

* [Models](/developers/models) — Available video models and pricing
* [Image Generation](/developers/model-capabilities/images/generation) — Generate still images from text
* [API Reference](/developers/rest-api-reference) — Full endpoint documentation
* [Imagine API Landing Page](https://x.ai/api/imagine) — Showcase of the Imagine API in action

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
