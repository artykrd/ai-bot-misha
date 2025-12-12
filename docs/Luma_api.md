Welcome

Build and scale creative products with the world's most popular and intuitive generation models using the Dream Machine API
Introduction

Dream Machine API let's developers use image and video generation capabilities.
How to use

Documentation - https://docs.lumalabs.ai/

API docs - API

Python SDK

    Image Generation Python
    Video Generation Python

Javascript SDK

    Image Generation Javascript
    Video Generation Javascript

Keys and Billing

Get API key - https://lumalabs.ai/dream-machine/api/keys

Billing Dashboard - https://lumalabs.ai/dream-machine/api/billing/overview


API

Use the API directly

With the Dream Machine API, you can generate images and videos. Both processes work in a similar way: you create a request, which returns an ID, and you use this ID to check its status until it is ready.
You can use this API to generate images and videos using different conditions:

    Videos:
        Text to video
        Image to video

    Images:
        Text to image
        Character reference
        Image reference
        Style reference
        Image to image (modify image)


Image Generation
Authentication

    Get a key from https://lumalabs.ai/dream-machine/api/keys
    Use the key as Bearer token to call any of the API endpoints

Authorization: Bearer <luma_api_key>

API Reference

Open
Downloading an image

curl -o image.jpg https://example.com/image.jpg

Aspect Ratio and Model

For all your requests, you can specify the aspect ratio you want and also the model to be used.
Aspect ratio

You can choose between the following aspect ratios:

    1:1
    3:4
    4:3
    9:16
    16:9 (default)
    9:21
    21:9

To use it, simply include a new key under your payload:

{
  "prompt": "A teddy bear in sunglasses playing electric guitar and dancing",
  "aspect_ratio": "3:4"
}

Model

You can choose from our two model versions:

    photon-1 (default)
    photon-flash-1

To use it, simply include a new key under your payload:

{
  "prompt": "A teddy bear in sunglasses playing electric guitar and dancing",
  "model": "photon-flash-1"
}

Text to Image

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations/image \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "A teddy bear in sunglasses playing electric guitar and dancing"
}
'

With aspect ratio and model

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations/image \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "A teddy bear in sunglasses playing electric guitar and dancing",
  "aspect_ratio": "3:4",
  "model": "photon-1"
}
'

Image Reference

    ☁️
    Image URL

    You should upload and use your own cdn image urls, currently this is the only way to pass an image

This feature allows you to guide your generation using a combination between images and prompt. You can use up to 4 images as references. This feature is very useful when you want to create variations of an image or when you have a concept that is hard to describe, but easy to visualize. You can use the weight key to tune the influence of the images.

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations/image \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "sunglasses",
  "image_ref": [
      {
        "url": "https://storage.cdn-luma.com/dream_machine/7e4fe07f-1dfd-4921-bc97-4bcf5adea39a/video_0_thumb.jpg",
        "weight": 0.85
      }
    ]
}
'

Style Reference

    ☁️
    Image URL

    You should upload and use your own cdn image urls, currently this is the only way to pass an image

As the name suggests, this feature is used when you want to apply an specific style to your generation. You can use the weight key to tune the influence of the style image reference.

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations/image \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "dog",
  "style_ref": [
      {
        "url": "https://staging.storage.cdn-luma.com/dream_machine/400460d3-cc24-47ae-a015-d4d1c6296aba/38cc78d7-95aa-4e6e-b1ac-4123ce24725e_image0c73fa8a463114bf89e30892a301c532e.jpg",
        "weight": 0.8
      }
    ]
}
'

Character Reference

    ☁️
    Image URL

    You should upload and use your own cdn image urls, currently this is the only way to pass an image

Character Reference is a feature that allows you to create consistent and personalized characters. Below, you can see how to use it. One thing important to say is that you can use up to 4 images of the same person to build one identity. More images, better the character representation will be.

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations/image \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "man as a warrior",
  "character_ref": {
        "identity0": {
          "images": [
            "https://staging.storage.cdn-luma.com/dream_machine/400460d3-cc24-47ae-a015-d4d1c6296aba/38cc78d7-95aa-4e6e-b1ac-4123ce24725e_image0c73fa8a463114bf89e30892a301c532e.jpg"
          ]
        }
      }
}
'


Modify Image

    ☁️
    Image URL

    You should upload and use your own cdn image urls, currently this is the only way to pass an image

    🚧
    Changing colors of images

    This feature works really well to change objects, shapes, etc. But when it comes to changing colors, it is harder to get it right. One recommendation is to use a lower weight value, something between 0.0 and 0.1.

Modify feature allows you to refine your images by simply prompting what change you want to make. You can use the weight key to specify the influence of the input image. Higher the weight, closer to the input image but less diverse (and creative).

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations/image \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "transform all the flowers to sunflowers",
  "modify_image_ref": {
      "url": "https://staging.storage.cdn-luma.com/dream_machine/400460d3-cc24-47ae-a015-d4d1c6296aba/38cc78d7-95aa-4e6e-b1ac-4123ce24725e_image0c73fa8a463114bf89e30892a301c532e.jpg",
      "weight": 1.0
    }
}
'

Generations
Get generation with id

curl --request GET \
     --url https://api.lumalabs.ai/dream-machine/v1/generations/123e4567-e89b-12d3-a456-426614174000 \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx'

List all generations

curl --request GET \
     --url 'https://api.lumalabs.ai/dream-machine/v1/generations?limit=10&offset=10' \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx'

Delete generation

curl --request DELETE \
     --url https://api.lumalabs.ai/dream-machine/v1/generations/123e4567-e89b-12d3-a456-426614174000 \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx'

Example Response

{
  "id": "3ce343aa-5746-4ab3-b167-4e29f83d3f42",
  "type": "image",
  "state": "completed",
  "failure_reason": null,
  "created_at": "2024-12-02T15:34:40.388000Z",
  "assets": {
    "video": null,
    "image": "https://image.jpg"
  },
  "model": "photon-v1.0",
  "request": {
    "type": "image",
    "model": "photon-1",
    "prompt": "man as a warrior",
    "aspect_ratio": "16:9",
    "callback_url": null,
    "image_ref": null,
    "style_ref": null,
    "character_ref": {
      "identity0": {
        "images": [
          "https://input_image.jpg"
        ]
      }
    },
    "modify_image_ref": null
  }
}


How to get a callback when generation has an update

    It will get status updates (dreaming/completed/failed)
    It will also get the image url as part of it when completed
    It's a POST endpoint you can pass, and request body will have the generation object in it
    It expected to be called multiple times for a status
    If the endpoint returns a status code other than 200, it will be retried max 3 times with 100ms delay and the request has a 5s timeout

example

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations/image \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "an old lady laughing underwater, wearing a scuba diving suit",
  "callback_url": "<your_api_endpoint_here>"
}
'

Video Generation
Authentication

    Get a key from https://lumalabs.ai/dream-machine/api/keys
    Use the key as Bearer token to call any of the API endpoints

Authorization: Bearer <luma_api_key>

Models
name	model param
Ray 2 Flash	ray-flash-2
Ray 2	ray-2
Ray 1.6	ray-1-6
API Reference

Open
Ray 2 Text to Video

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "an old lady laughing underwater, wearing a scuba diving suit",
  "model": "ray-2",
  "resolution": "720p",
  "duration": "5s"
}
'

Resolution can be 540p, 720p, 1080, 4k
Ray 2 Image to Video

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "A tiger walking in snow",
  "model": "ray-2",
  "keyframes": {
    "frame0": {
      "type": "image",
      "url": "https://storage.cdn-luma.com/dream_machine/7e4fe07f-1dfd-4921-bc97-4bcf5adea39a/video_0_thumb.jpg"
    }
  }
}
'

How to use concepts

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "a car",
  "model": "ray-2",
  "resolution": "720p",
  "duration": "5s",
  "concepts": [
  	{
    	"key": "dolly_zoom"
    }
  ]
}
'

We have this new /concepts/list api one can hit to get list of concepts available

https://api.lumalabs.ai/dream-machine/v1/generations/concepts/list
Text to Video

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "an old lady laughing underwater, wearing a scuba diving suit",
  "model": "ray-2"
}
'

Downloading a video

curl -o video.mp4 https://example.com/video.mp4

With loop, aspect ratio

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "an old lady laughing underwater, wearing a scuba diving suit",
  "model": "ray-2",
  "aspect_ratio": "16:9",
  "loop": true
}
'


Image to Video

    ☁️
    Image URL

    You should upload and use your own cdn image urls, currently this is the only way to pass an image

With start frame

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "A tiger walking in snow",
  "model": "ray-2",
  "keyframes": {
    "frame0": {
      "type": "image",
      "url": "https://storage.cdn-luma.com/dream_machine/7e4fe07f-1dfd-4921-bc97-4bcf5adea39a/video_0_thumb.jpg"
    }
  }
}
'

With start frame, loop, aspect ratio

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "A tiger walking in snow",
  "model": "ray-2",
  "keyframes": {
    "frame0": {
      "type": "image",
      "url": "https://storage.cdn-luma.com/dream_machine/7e4fe07f-1dfd-4921-bc97-4bcf5adea39a/video_0_thumb.jpg"
    }
  },
  "loop": false,
  "aspect_ratio": "16:9"
}
'

With ending frame

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "A tiger walking in snow",
  "model": "ray-2",
  "keyframes": {
    "frame1": {
      "type": "image",
      "url": "https://storage.cdn-luma.com/dream_machine/7e4fe07f-1dfd-4921-bc97-4bcf5adea39a/video_0_thumb.jpg"
    }
  },
  "loop": false,
  "aspect_ratio": "16:9"
}
'

With start and end keyframes

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "A tiger walking in snow",
  "model": "ray-2",
  "keyframes": {
    "frame0": {
    	"type": "image",
      "url": "https://storage.cdn-luma.com/dream_machine/7e4fe07f-1dfd-4921-bc97-4bcf5adea39a/video_0_thumb.jpg",
    },
    "frame1": {
      "type": "image",
      "url": "https://storage.cdn-luma.com/dream_machine/7e4fe07f-1dfd-4921-bc97-4bcf5adea39a/video_0_thumb.jpg",
    }
  },
  "loop": false,
  "aspect_ratio": "16:9"
}
'

Extend Video
Extend video

    Extend is currently supported only for generated videos. Please make sure the generation is in completed state before passing it

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "The tiger rolls around",
  "model": "ray-2",
  "keyframes": {
    "frame0": {
      "type": "generation",
      "id": "123e4567-e89b-12d3-a456-426614174000"
    }
  }
}
'

Reverse extend video

    Generate video leading up to the provided video.

    Extend is currently supported only for generated videos. Please make sure the generation is in completed state before passing it

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "The tiger rolls around",
  "model": "ray-2",
  "keyframes": {
    "frame1": {
      "type": "generation",
      "id": "123e4567-e89b-12d3-a456-426614174000"
    }
  }
}
'

Extend a video with an end-frame

    Extend is currently supported only for generated videos. Please make sure the generation is in completed state before passing it

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "The tiger rolls around",
  "model": "ray-2",
  "keyframes": {
    "frame0": {
      "type": "generation",
      "id": "123e4567-e89b-12d3-a456-426614174000"
    },
    "frame1": {
      "type": "image",
      "url": "https://storage.cdn-luma.com/dream_machine/7e4fe07f-1dfd-4921-bc97-4bcf5adea39a/video_0_thumb.jpg"
    }
  }
}
'

Reverse extend a video with a start-frame

    Extend is currently supported only for generated videos. Please make sure the generation is in completed state before passing it

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "The tiger rolls around",
  "model": "ray-2",
  "keyframes": {
    "frame0": {
      "type": "image",
      "url": "https://storage.cdn-luma.com/dream_machine/7e4fe07f-1dfd-4921-bc97-4bcf5adea39a/video_0_thumb.jpg"
    },
    "frame1": {
      "type": "generation",
      "id": "123e4567-e89b-12d3-a456-426614174000"
    }
  }
}
'

Interpolate between 2 videos

    Interpolate is currently supported only for generated videos. Please make sure the generation is in completed state before passing it

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "The tiger rolls around",
  "model": "ray-2",
  "keyframes": {
    "frame0": {
      "type": "generation",
      "id": "123e4567-e89b-12d3-a456-426614174000"
    },
    "frame1": {
      "type": "generation",
      "id": "123e4567-e89b-12d3-a456-426614174000"
    }
  }
}
'

Generations
Get generation with id

curl --request GET \
     --url https://api.lumalabs.ai/dream-machine/v1/generations/123e4567-e89b-12d3-a456-426614174000 \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx'

List all generations

curl --request GET \
     --url 'https://api.lumalabs.ai/dream-machine/v1/generations?limit=10&offset=10' \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx'

Delete generation

curl --request DELETE \
     --url https://api.lumalabs.ai/dream-machine/v1/generations/123e4567-e89b-12d3-a456-426614174000 \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx'

Camera Motions

    📘
    How to use camera motion

    Just add the camera motion value as part of prompt itself

Get all supported camera motions

curl --request GET \
     --url https://api.lumalabs.ai/dream-machine/v1/generations/camera_motion/list \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx'

How to use camera motion

Camera is controlled by language in Dream Machine. You can find supported camera moves by calling the Camera Motions endpoint. This will return an array of supported camera motion strings (like "camera orbit left") which can be used in prompts. In addition to these exact strings, syntactically similar phrases also work, though there can be mismatches sometimes.
Example Response

{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "state": "completed",
  "failure_reason": null,
  "created_at": "2023-06-01T12:00:00Z",
  "assets": {
    "video": "https://example.com/video.mp4"
  },
  "version": "v1.6",
  "request": {
    "prompt": "A serene lake surrounded by mountains at sunset",
    "aspect_ratio": "16:9",
    "loop": true,
    "keyframes": {
      "frame0": {
        "type": "image",
        "url": "https://example.com/image.jpg"
      },
      "frame1": {
        "type": "generation",
        "id": "123e4567-e89b-12d3-a456-426614174000"
      }
    }
  }
}


How to get a callback when generation has an update

    It will get status updates (dreaming/completed/failed)
    It will also get the video url as part of it when completed
    It's a POST endpoint you can pass, and request body will have the generation object in it
    It expected to be called multiple times for a status
    If the endpoint returns a status code other than 200, it will be retried max 3 times with 100ms delay and the request has a 5s timeout

example

curl --request POST \
     --url https://api.lumalabs.ai/dream-machine/v1/generations \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx' \
     --header 'content-type: application/json' \
     --data '
{
  "prompt": "an old lady laughing underwater, wearing a scuba diving suit",
  "callback_url": "<your_api_endpoint_here>"
}
'

Python SDK

https://github.com/lumalabs/lumaai-python

With the Dream Machine Python SDK, you can generate images and videos. Both processes work in a similar way: you create a request, which returns an ID, and you use this ID to check its status until it is ready.
You can use this SDK to generate images and videos using different conditions:

    Videos:
        Text to video
        Image to video

    Images:
        Text to image
        Character reference
        Image reference
        Style reference
        Image to image (modify image)



Image Generation
Installation

pip install lumaai

https://pypi.org/project/lumaai/
Authentication

    Get a key from https://lumalabs.ai/dream-machine/api/keys
    Pass it to client sdk by either
        setting LUMAAI_API_KEY
        or passing auth_token to the client


Setting up client

Using LUMAAI_API_KEY env variable

from lumaai import LumaAI

client = LumaAI()

Using auth_token parameter

import os
from lumaai import LumaAI

client = LumaAI(
    auth_token=os.environ.get("LUMAAI_API_KEY"),
)


How do I get the image for a generation?

    Right now the only supported way is via polling
    The create endpoint returns an id which is an UUID V4
    You can use it to poll for updates (you can see the image at generation.assets.image)

Usage Example

import requests
import time
from lumaai import LumaAI

client = LumaAI()

generation = client.generations.image.create(
  prompt="A teddy bear in sunglasses playing electric guitar and dancing",
)
completed = False
while not completed:
  generation = client.generations.get(id=generation.id)
  if generation.state == "completed":
    completed = True
  elif generation.state == "failed":
    raise RuntimeError(f"Generation failed: {generation.failure_reason}")
  print("Dreaming")
  time.sleep(2)

image_url = generation.assets.image

# download the image
response = requests.get(image_url, stream=True)
with open(f'{generation.id}.jpg', 'wb') as file:
    file.write(response.content)
print(f"File downloaded as {generation.id}.jpg")

Async library

Import and use AsyncLumaai

import os
from lumaai import AsyncLumaAI

client = AsyncLumaAI(
    auth_token=os.environ.get("LUMAAI_API_KEY"),
)

For all the functions add await (eg. below)

generation = await client.generations.image.create(
    prompt="A teddy bear in sunglasses playing electric guitar and dancing",
)

Aspect Ratio and Model

For all your requests, you can specify the aspect ratio you want and also the model to be used.
Aspect ratio

You can choose between the following aspect ratios:

    1:1
    3:4
    4:3
    9:16
    16:9 (default)
    9:21
    21:9

To use it, simply include a new key under your payload:

  prompt="A teddy bear in sunglasses playing electric guitar and dancing",
  aspect_ratio="3:4"

Model

You can choose from our two model versions:

    photon-1 (default)
    photon-flash-1

To use it, simply include a new key under your payload:

  prompt="A teddy bear in sunglasses playing electric guitar and dancing",
  model="photon-flash-1"

Text to Image

generation = client.generations.image.create(
    prompt="A teddy bear in sunglasses playing electric guitar and dancing",
)

With aspect ratio and model

generation = client.generations.image.create(
    prompt="A teddy bear in sunglasses playing electric guitar and dancing",
    aspect_ratio="3:4",
    model="photon-1"
)

Image Reference

    ☁️
    Image URL

    You should upload and use your own cdn image urls, currently this is the only way to pass an image

This feature allows you to guide your generation using a combination between images and prompt. You can use up to 4 images as references. This feature is very useful when you want to create variations of an image or when you have a concept that is hard to describe, but easy to visualize. You can use the weight key to tune the influence of the images.

generation = client.generations.image.create(
    prompt="sunglasses",
    image_ref=[
      {
        "url": "https://storage.cdn-luma.com/dream_machine/7e4fe07f-1dfd-4921-bc97-4bcf5adea39a/video_0_thumb.jpg",
        "weight": 0.85
      }
    ]
)

Style Reference

    ☁️
    Image URL

    You should upload and use your own cdn image urls, currently this is the only way to pass an image

As the name suggests, this feature is used when you want to apply an specific style to your generation. You can use the weight key to tune the influence of the style image reference.

generation = client.generations.image.create(
    prompt="dog",
    style_ref=[
      {
        "url": "https://staging.storage.cdn-luma.com/dream_machine/400460d3-cc24-47ae-a015-d4d1c6296aba/38cc78d7-95aa-4e6e-b1ac-4123ce24725e_image0c73fa8a463114bf89e30892a301c532e.jpg",
        "weight": 0.8
      }
    ]
)

Character Reference

    ☁️
    Image URL

    You should upload and use your own cdn image urls, currently this is the only way to pass an image

Character Reference is a feature that allows you to create consistent and personalized characters. Below, you can see how to use it. One thing important to say is that you can use up to 4 images of the same person to build one identity. More images, better the character representation will be.

generation = client.generations.image.create(
    prompt="man as a warrior",
    character_ref={
        "identity0": {
          "images": [
            "https://staging.storage.cdn-luma.com/dream_machine/400460d3-cc24-47ae-a015-d4d1c6296aba/38cc78d7-95aa-4e6e-b1ac-4123ce24725e_image0c73fa8a463114bf89e30892a301c532e.jpg"
          ]
        }
      }
)


Modify Image

    ☁️
    Image URL

    You should upload and use your own cdn image urls, currently this is the only way to pass an image

    🚧
    Changing colors of images

    This feature works really well to change objects, shapes, etc. But when it comes to changing colors, it is harder to get it right. One recommendation is to use a lower weight value, something between 0.0 and 0.1.

Modify feature allows you to refine your images by simply prompting what change you want to make. You can use the weight key to specify the influence of the input image. Higher the weight, closer to the input image but less diverse (and creative).

generation = client.generations.image.create(
    prompt="transform all the flowers to sunflowers",
    modify_image_ref={
      "url": "https://staging.storage.cdn-luma.com/dream_machine/400460d3-cc24-47ae-a015-d4d1c6296aba/38cc78d7-95aa-4e6e-b1ac-4123ce24725e_image0c73fa8a463114bf89e30892a301c532e.jpg",
      "weight": 1.0
    }
)

Generations
Get generation with id

generation = client.generations.get(id="d1968551-6113-4b46-b567-09210c2e79b0")

List all generations

generation = client.generations.list(limit=100, offset=0)

Delete generation

generation = client.generations.delete(id="d1968551-6113-4b46-b567-09210c2e79b0")

How to get a callback when generation has an update

    It will get status updates (dreaming/completed/failed)
    It will also get the image url as part of it when completed
    It's a POST endpoint you can pass, and request body will have the generation object in it
    It expected to be called multiple times for a status
    If the endpoint returns a status code other than 200, it will be retried max 3 times with 100ms delay and the request has a 5s timeout

Example

generation = await client.generations.image.create(
    prompt="A teddy bear in sunglasses playing electric guitar and dancing",
    callback_url="<your_api_endpoint_here>"
)


Video Generation
Installation

pip install lumaai

https://pypi.org/project/lumaai/
Authentication

    Get a key from https://lumalabs.ai/dream-machine/api/keys
    Pass it to client sdk by either
        setting LUMAAI_API_KEY
        or passing auth_token to the client

Models
name	model param
Ray 2 Flash	ray-flash-2
Ray 2	ray-2
Ray 1.6	ray-1-6
Setting up client

Using LUMAAI_API_KEY env variable

from lumaai import LumaAI

client = LumaAI()

Using auth_token parameter

import os
from lumaai import LumaAI

client = LumaAI(
    auth_token=os.environ.get("LUMAAI_API_KEY"),
)


How do I get the video for a generation?

    Right now the only supported way is via polling
    The create endpoint returns an id which is an UUID V4
    You can use it to poll for updates (you can see the video at generation.assets.video)

Usage Example

import requests
import time
from lumaai import LumaAI

client = LumaAI()

generation = client.generations.create(
  prompt="A teddy bear in sunglasses playing electric guitar and dancing",
)
completed = False
while not completed:
  generation = client.generations.get(id=generation.id)
  if generation.state == "completed":
    completed = True
  elif generation.state == "failed":
    raise RuntimeError(f"Generation failed: {generation.failure_reason}")
  print("Dreaming")
  time.sleep(3)

video_url = generation.assets.video

# download the video
response = requests.get(video_url, stream=True)
with open(f'{generation.id}.mp4', 'wb') as file:
    file.write(response.content)
print(f"File downloaded as {generation.id}.mp4")

Async library

Import and use AsyncLumaai

import os
from lumaai import AsyncLumaAI

client = AsyncLumaAI(
    auth_token=os.environ.get("LUMAAI_API_KEY"),
)

For all the functions add await (eg. below)

generation = await client.generations.create(
    prompt="A teddy bear in sunglasses playing electric guitar and dancing",
    model="ray-2"
)


Ray 2 Text to Video

generation = client.generations.create(
    prompt="A teddy bear in sunglasses playing electric guitar and dancing",
    model="ray-2",
    resolution="720p",
    duration="5s"
)

Resolution can be 540p, 720p, 1080, 4k
Ray 2 Image to Video

generation = client.generations.create(
    prompt="Low-angle shot of a majestic tiger prowling through a snowy landscape, leaving paw prints on the white blanket",
    model="ray-2",
    keyframes={
      "frame0": {
        "type": "image",
        "url": "https://storage.cdn-luma.com/dream_machine/7e4fe07f-1dfd-4921-bc97-4bcf5adea39a/video_0_thumb.jpg"
      }
    }
)

How to use concepts

generation = client.generations.create(
    prompt="a car",
    model="ray-2",
    resolution="720p",
    duration="5s",
    concepts=[
      {
      	"key": "handheld"
      }
    ]
)

We have this new /concepts/list api one can hit to get list of concepts available

https://api.lumalabs.ai/dream-machine/v1/generations/concepts/list
Text to Video

generation = client.generations.create(
    prompt="A teddy bear in sunglasses playing electric guitar and dancing",
    model="ray-2"
)

Downloading a video

import requests

url = 'https://example.com/video.mp4'
response = requests.get(url, stream=True)

file_name = 'video.mp4'
with open('video.mp4', 'wb') as file:
    file.write(response.content)
print(f"File downloaded as {file_name}")

With loop, aspect ratio

generation = client.generations.create(
    prompt="A teddy bear in sunglasses playing electric guitar and dancing",
    model="ray-2"
    loop=True,
    aspect_ratio="3:4"
)

Image to Video

    ☁️
    Image URL

    You should upload and use your own cdn image urls, currently this is the only way to pass an image

With start frame

generation = client.generations.create(
    prompt="Low-angle shot of a majestic tiger prowling through a snowy landscape, leaving paw prints on the white blanket",
    model="ray-2"
    keyframes={
      "frame0": {
        "type": "image",
        "url": "https://storage.cdn-luma.com/dream_machine/7e4fe07f-1dfd-4921-bc97-4bcf5adea39a/video_0_thumb.jpg"
      }
    }
)

With start frame, loop

generation = client.generations.create(
    prompt="Low-angle shot of a majestic tiger prowling through a snowy landscape, leaving paw prints on the white blanket",
    model="ray-2"
    loop=True,
    keyframes={
      "frame0": {
        "type": "image",
        "url": "https://storage.cdn-luma.com/dream_machine/7e4fe07f-1dfd-4921-bc97-4bcf5adea39a/video_0_thumb.jpg"
      }
    }
)

With ending frame

generation = client.generations.create(
    prompt="Low-angle shot of a majestic tiger prowling through a snowy landscape, leaving paw prints on the white blanket",
    model="ray-2"
    keyframes={
      "frame1": {
        "type": "image",
        "url": "https://storage.cdn-luma.com/dream_machine/7e4fe07f-1dfd-4921-bc97-4bcf5adea39a/video_0_thumb.jpg"
      }
    }
)

With start and end keyframes

generation = client.generations.create(
    prompt="Low-angle shot of a majestic tiger prowling through a snowy landscape, leaving paw prints on the white blanket",
    model="ray-2"
    keyframes={
      "frame0": {
        "type": "image",
        "url": "https://storage.cdn-luma.com/dream_machine/7e4fe07f-1dfd-4921-bc97-4bcf5adea39a/video_0_thumb.jpg"
      },
      "frame1": {
        "type": "image",
        "url": "https://storage.cdn-luma.com/dream_machine/12d17326-a7b6-4538-b9b7-4a2e146d4488/video_0_thumb.jpg"
      }
    }
)

Extend Video
Extend video

    Extend is currently supported only for generated videos. Please make sure the generation is in completed state before passing it

generation = client.generations.create(
    prompt="A teddy bear in sunglasses playing electric guitar and dancing",
    model="ray-2"
    keyframes={
      "frame0": {
        "type": "generation",
        "id": "d1968551-6113-4b46-b567-09210c2e79b0"
      }
    }
)

Reverse extend video

    Generate video leading up to the provided video.

    Extend is currently supported only for generated videos. Please make sure the generation is in completed state before passing it

generation = client.generations.create(
    prompt="A teddy bear in sunglasses playing electric guitar and dancing",
    model="ray-2"
    keyframes={
      "frame1": {
        "type": "generation",
        "id": "d1968551-6113-4b46-b567-09210c2e79b0"
      }
    }
)

Extend a video with an end-frame

    Extend is currently supported only for generated videos. Please make sure the generation is in completed state before passing it

generation = client.generations.create(
    prompt="Low-angle shot of a majestic tiger prowling through a snowy landscape, leaving paw prints on the white blanket",
    model="ray-2"
    keyframes={
      "frame0": {
        "type": "generation",
        "id": "d1968551-6113-4b46-b567-09210c2e79b0"
      },
      "frame1": {
        "type": "image",
        "url": "https://storage.cdn-luma.com/dream_machine/12d17326-a7b6-4538-b9b7-4a2e146d4488/video_0_thumb.jpg"
      }
    }
)

Reverse extend a video with a start-frame

    Extend is currently supported only for generated videos. Please make sure the generation is in completed state before passing it

generation = client.generations.create(
    prompt="Low-angle shot of a majestic tiger prowling through a snowy landscape, leaving paw prints on the white blanket",
    model="ray-2"
    keyframes={
      "frame0": {
        "type": "image",
        "url": "https://storage.cdn-luma.com/dream_machine/12d17326-a7b6-4538-b9b7-4a2e146d4488/video_0_thumb.jpg"
      },
      "frame1": {
        "type": "generation",
        "id": "d1968551-6113-4b46-b567-09210c2e79b0"
      }
    }
)

Interpolate between 2 videos

    Interpolate is currently supported only for generated videos. Please make sure the generation is in completed state before passing it

generation = client.generations.create(
    prompt="A teddy bear in sunglasses playing electric guitar and dancing",
    model="ray-2"
    keyframes={
      "frame1": {
        "type": "generation",
        "id": "d312d37a-7ff4-49f2-94f8-218f3fe2a4bd"
      },
      "frame1": {
        "type": "generation",
        "id": "d1968551-6113-4b46-b567-09210c2e79b0"
      }
    }
)

Generations
Get generation with id

generation = client.generations.get(id="d1968551-6113-4b46-b567-09210c2e79b0")

List all generations

generation = client.generations.list(limit=100, offset=0)

Delete generation

generation = client.generations.delete(id="d1968551-6113-4b46-b567-09210c2e79b0")

Camera Motions

    📘
    How to use camera motion

    Just add the camera motion value as part of prompt itself

Get all supported camera motions

supported_camera_motions = client.generations.camera_motion.list()

How to use camera motion

Camera is controlled by language in Dream Machine. You can find supported camera moves by calling the Camera Motions endpoint. This will return an array of supported camera motion strings (like "camera orbit left") which can be used in prompts. In addition to these exact strings, syntactically similar phrases also work, though there can be mismatches sometimes.

How to get a callback when generation has an update

    It will get status updates (dreaming/completed/failed)
    It will also get the video url as part of it when completed
    It's a POST endpoint you can pass, and request body will have the generation object in it
    It expected to be called multiple times for a status
    If the endpoint returns a status code other than 200, it will be retried max 3 times with 100ms delay and the request has a 5s timeout

example

generation = await client.generations.create(
    prompt="A teddy bear in sunglasses playing electric guitar and dancing",
    callback_url="<your_api_endpoint_here>"
)


Rate Limits

For each account on "Build" tier these limits are in effect
Model	Concurrent generations	Create API requests/min
Ray (Video)	10	20
Photon & Photon Flash (Image)	40	80

These limits exist to help us maintain a high quality of service for everyone and we are working to increase these further. If you'd like higher limits please talk to us - Scale Plan
Usage Tiers

The "Build" tier has a usage limit of $5000 per month. If you'd like higher limits please talk to us - Scale Plan
Month	Usage Limits
Build	$5,000 / month
Scale	Higher usage limits


Errors

These are the possible error messages from Dream Machine API
Before submission

generation request object

this is returned as errors in https://api.lumalabs.ai/dream-machine/v1/generations / create sdk function calls itself

Prompt is required

When image is not provided as keyframes, prompt is required.

Prompt is too short, minimum length is 3 characters

Prompt should be minimum 3 characters

Prompt is too long, maximum length is 5000 characters

Prompt should be maximum 5000 characters

Loop is not supported for keyframes

When both frame0 and frame1 image urls are passed, loop is not supported

Loop is not supported for extend reverse

when frame1 is given (aka extend reverse) loop is not support`

Loop is not supported for interpolate video to image

Loop is not supported for interpolate image to video

Loop is not supported for interpolate between two videos

loop is not supported when doing interpolations

No keyframes provided

When frame0 and frame1 is passed as None/null

Unknown request type

When our server did not understand the request type.
After submission

generation object's failure_reason

Moderation

Contains blacklisted words

If the prompt provided has has any blacklisted words

Failed to read user input frames

The images provided as keyframes are not accessible by our servers.

Frame moderation failed

Our image moderation system we run in our servers have determined that image url given for a keyframe is not suitable to proceed (in case you think other wise, please reach out to us via the form in our website)

Advanced prompt moderation failed

Our language moderation we run in our servers have determined that prompt given for the generation is not suitable to proceed (in case you think other wise, please reach out to us via the form in our website)

Prompt

Prompt processing failed

Our language system ran into issues processing the prompt

Job

Error dispatching job

Our api failed to dispatch the job for the generation

Job failed

The job failed on the GPU server (please report to use via the form in website if you see this)

Error processing callback

The job server failed to process the callback (please report to use via the form in website if you see this)



FAQ
How to use camera motion

Camera is controlled by language in Dream Machine. You can find supported camera moves by calling the Camera Motions endpoint, like so

curl --request GET \
     --url https://api.lumalabs.ai/dream-machine/v1/generations/camera_motion/list \
     --header 'accept: application/json' \
     --header 'authorization: Bearer luma-xxxx'

This will return an array of supported camera motion strings (like "camera orbit left") which can be used in prompts. In addition to these exact strings, syntactically similar phrases also work, though there can be mismatches sometimes.
What if my generation fails

Generations may fail due to prompting errors, keyframe errors, or other issues. Rest assured, you won't be charged for failed generations.
Our billing process:

    We pre-charge your account to ensure sufficient credits for the generation.
    If the generation fails, we fully refund the amount to your credit balance.

This system ensures you only pay for successful generations.
Watermarks

Images & Videos created using the API have no watermarks of any sorts
Commercial Use

Images & Videos created using the API are allowed for commercial use


Reframe
Now available in API & SDKs
Models	Max Duration	Max Size
ray-2	10s	100 mb
ray-flash-2	30s	100 mb
photon-1	n/a	10 mb
photon-flash-1	n/a	10 mb
API Reference

image

video
Basic Usage

    by default one can just pass the url of image/video to reframe with
        model
        target aspect ratio
    it fits the image horizontally and vertically and make a new video/image
    optionally provide prompts on how to steer what content goes into the reframed new area
    target width and height are standard based on chosen aspect ratio

Pricing

Same as cost of the models (ray-2, ray-flash-2, photon-1, photon-flash-1)

learn more
Advanced Usage

aspect_ratio_map = {
    "1:1": [1536, 1536],
    "4:3": [1792, 1344],
    "3:4": [1344, 1792],
    "16:9": [2048, 1152],
    "9:16": [1152, 2048],
    "21:9": [2432, 1024],
    "9:21": [1024, 2432],
}

grid_position_x, grid_position_y, x_start, x_end, y_start, y_end, resized_width, resized_height are in pixel values.

Modify Video
Now available in API & SDKs
Models	Max Duration	Max Size
ray-2	10s	100 mb
ray-flash-2	15s	100mb
API Reference

image

video
Basic Usage

    prompt: text value to guide how to modify the video
    media.url: url of the video file
    first_frame.url: optional (but preferred) provide the first frame of the modified video (to guide it)
    mode: adhere_1, adhere_2, adhere_3, flex_1, flex_2, flex_3, reimagine_1, reimagine_2, reimagine_3
    model: ray-2, ray-flash-2

Pricing
Model	Cost
ray-2	$0.01582 / million pixels
ray-flash-2	$0.00544 / million pixels

Example
Config	Cost
ray-2, 720p, 5s, 16:9	$1.75
ray-flash-2, 720p, 5s, 16:9	$0.60

learn more
Example

{
    "prompt": "you can direct how to modify the video by providing a text prompt here",
    "media": {
        "url": "https://example.com/video.mp4"
    },
    "first_frame": {
        "url": "https://example.com/image.png"
    },
    "mode": "flex_1",
    "model": "ray-2" # or ray-flash-2
}

Modes

a) Adhere — The output adheres very closely to the source video. This is ideal for subtle enhancements, minor retexturing, or applying a light stylistic filter without drastically altering the original content.

b) Flex — The output flexibly adheres somewhat to the shapes, characters, and details of the source video. This range allows for more significant stylistic changes while still maintaining recognizable elements from the original footage.

c) Reimagine — The output adheres much more loosely to the source video. This setting is best for fundamentally changing the world and style to something entirely new, even transforming the characters or objects into completely different forms.
What can I achieve with Modify Video?

Preserve full-body motion and facial performance, including choreography, lip sync, and nuanced expression

Restyle or retexture the entire shot, from turning live-action into CG or stylized animation, to changing wardrobe, props, or the overall aesthetic

Swap environments or time periods, giving you control over background, location, or even weather

Edit at the element level, like isolating just the outfit, face, or prop — or adding generative FX (smoke, fire, water, etc.) on top
API Reference

https://docs.lumalabs.ai/reference/modifyvideo

