# Getting started

Welcome to Recraft image generation and editing API.

Learn the basics of the Recraft API, including raster and vector image generation, style creation, image generation in your brand style and colors, image vectorization, and background removal.

**Authenticate and interact with our API in a matter of minutes.**

## Authentication

We use [Bearer](https://swagger.io/docs/specification/authentication/bearer-authentication/) API tokens for authentication. To access your API key, log in to Recraft, [enter your profile](https://app.recraft.ai/profile/api) and hit 'Generate' (available only if your API units balance is above zero). All requests should include your API key in an Authorization HTTP header as follows:\
‍\
‍`Authorization: Bearer RECRAFT_API_TOKEN`

A user may create multiple API tokens; however, all tokens share the same API units balance.

## Swagger

Interactive API documentation is available via [Swagger](https://external.api.recraft.ai/doc/#/). You can explore all available endpoints, test API calls, and view request/response schemas directly in your browser.

### REST / Python Library

The Recraft API adheres to REST principles, allowing you to interact using any utilities (e.g., curl), programming languages, or libraries of your choice.

One of the easiest of available alternatives is [OpenAI Python library](https://github.com/openai/openai-python) which is also compatible with Recraft API, but it’s important to remember that not all parameters/options are supported or implemented. Additionally, some parameters may have different meanings, or they may be quietly ignored if they are not applicable to the Recraft API.

Future examples will be shown using that library, for example, once installed, you can use the following code to be authenticated:

```python  theme={null}
from openai import OpenAI

client = OpenAI(
    base_url='https://external.api.recraft.ai/v1',
    api_key=<TOKEN>,
)
```

## Features

### Styles

A *style* is a descriptor that defines the visual appearance and feel of generated images. This includes a wide array of elements such as textures and visual effects, shapes and colors, composition and lines, etc. There are four classes of base styles: realistic image, digital illustration, vector illustration and icon.

<Accordion title="Realistic">
  Images of style “*realistic*” are expected to look like just ordinary photographs made with a digital camera or a smartphone or a film camera.

  ![](https://cdn.prod.website-files.com/655727fe69827d9a402de12c/679b8295b59b980127d7e306_cute-girl-portrait%20\(1\)%201.png)

  ![](https://cdn.prod.website-files.com/655727fe69827d9a402de12c/679b828dff13038000193303_a-good-aluminium-suitcase-on-the-floor%201.png)
</Accordion>

<Accordion title="Digital illustration">
  Images of style “*digital illustration*” are pictures drawn by hand or using computers - virtually everything except photos and vector illustrations. The most crucial difference from “*realistic images*” is that illustrations possess simplified textures (like in 3D-rendered or manually drawn images) - or they are stylized in a certain creative way. The difference from “*vector illustration*” is that “*digital illustrations*” allow for more complex color transitions, shades, fine textures.

  ![](https://cdn.prod.website-files.com/655727fe69827d9a402de12c/679b8318c6f6ecaf608531da_unicorn%20\(8\).png)

  ![](https://cdn.prod.website-files.com/655727fe69827d9a402de12c/679b82f54ef9617939df9d8e_motorcycle--going-fast.png)
</Accordion>

<Accordion title="Vector illustration">
  Images of style “*vector illustration”* are expected to look like those drawn using vector graphics (see [Wikipedia](https://en.wikipedia.org/wiki/Vector_graphics)). Usually, they use only a few different colors at once, shapes are filled with flat colors or simple color gradients. Shapes of objects can be arbitrarily complex.

  ![](https://cdn.prod.website-files.com/655727fe69827d9a402de12c/679b82fb365f45ed1a743d43_a-man-working-in-his-workshop--standing-straight-a%20\(1\)%202.png)

  ![](https://cdn.prod.website-files.com/655727fe69827d9a402de12c/679b830165533469004467d9_create-a-minimal-character-illustration-of-a-resea.png)
</Accordion>

<Accordion title="Icon">
  Images of style “*icon*” are small digital images or symbols used in the graphical user interface. They are designed to be simple and recognizable at small sizes, often visually summarizing the action or object they stand for, or they can act as the visual identity for an app or a website and are crucial in branding.

  ![](https://cdn.prod.website-files.com/655727fe69827d9a402de12c/679b830d1720fd793595cf40_Group%204291.png)

  ![](https://cdn.prod.website-files.com/655727fe69827d9a402de12c/679b831e6ee14a2f933f112c_Group%204254.png)
</Accordion>

Realistic images and digital illustrations are generated in raster formats such as PNG, WEBP, or JPG. These formats use pixels to represent details, making them ideal for photos and complex artwork. On the other hand, vector illustrations and icons are generated in the SVG format. Unlike raster images, SVGs are made of mathematical paths and shapes, allowing them to scale to any size without losing quality.

A *style* can be refined by adding a *substyle* for more precise definition. You can find a list of supported *styles* and corresponding *substyles* in [Appendix](/api-reference/appendix). Please note that the available *styles* and *substyles* may vary depending on the *model*. Additionally, you have an option to create [your own style](/api-reference/usage#create-style) by combining a base *style* (e.g. realistic image, digital illustration, vector illustration or icon) with a collection of reference images.

### Models

Recraft has developed two models, Recraft V2 (aka Recraft 20B) and Recraft V3 (aka Red Panda).

The Recraft V2 model, released in February 2024, was the first AI model built specifically for designers. It enabled the creation of both vector and raster images with anatomical accuracy, consistent brand styling, and precise iteration control.

The Recraft V3 model, released in October 2024, was a new state-of-the-art model trained from scratch that introduced major advances in photorealism and text rendering. V3 ranked first on the Hugging Face Text-to-Image leaderboard for five consecutive months.

Both models are available through the Recraft API.


---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://www.recraft.ai/docs/llms.txt


# Usage

Dig into the details of using the Recraft API.

## Generate image

Creates an image given a prompt.

```javascript  theme={null}
POST https://external.api.recraft.ai/v1/images/generations
```

### Example

```python  theme={null}
response = client.images.generate(
    prompt='race car on a track',
    style='digital_illustration',
)
print(response.data[0].url)
```

### Output

```bash  theme={null}
https://img.recraft.ai/-dSeKnnWTUbG9wnzpV6OjN7I7PlFxAFmg6nyhvd3qSE/rs:fit:1024:1024:0/raw:1/plain/abs://external/images/cbb1770e-3e7e-49fd-bf17-7c689f6906c1
```

### Parameters

| Parameter         | Type                                         | Description                                                                                                                                                                |
| ----------------- | -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| prompt (required) | string                                       | A text description of the desired image(s). The maximum length is 1000 bytes.                                                                                              |
| text\_layout      | Array of objects or null                     | Available in `recraftv3` model only. This topic is covered [below](#text-layout).                                                                                          |
| n                 | integer or null, default is 1                | The number of images to generate, must be between 1 and 6.                                                                                                                 |
| style\_id         | UUID or null                                 | Use a previously uploaded style as a reference, this topic is covered in [Getting Started](/api-reference/getting-started#styles) and [Appendix](/api-reference/appendix). |
| style             | string or null, default is `realistic_image` | The style of the generated images, this topic is covered in [Styles](/api-reference/getting-started#styles).                                                               |
| substyle          | string or null                               | This topic is covered in [Styles](/api-reference/getting-started#styles).                                                                                                  |
| model             | string or null, default is `recraftv3`       | The model to use for image generation. Must be one of `recraftv3` or `recraftv2`.                                                                                          |
| response\_format  | string or null, default is `url`             | The format in which the generated images are returned. Must be one of `url` or `b64_json`.                                                                                 |
| size              | string or null, default is `1024x1024`       | The size of the generated images in `WxH` format, supported values are published in [Appendix](/api-reference/appendix#list-of-image-sizes).                               |
| negative\_prompt  | string or null                               | A text description of undesired elements on an image.                                                                                                                      |
| controls          | object or null                               | A set of custom parameters to tweak generation process, this topic is covered [below](#controls).                                                                          |

**Note**: `style_id` and `style` parameters are mutually exclusive. If neither of the two parameters is specified, the default style of `any` will be used

‍**Hint:** if OpenAI Python Library is used, non-standard parameters can be passed using the `extra_body` argument. For example:

```python  theme={null}
response = client.images.generate(
    prompt='race car on a track',
    extra_body={
        'style_id': style_id,
        'controls': {
            ...
        }
    }
)
print(response.data[0].url)
```

## Create style

Upload a set of images to create a style reference.

```javascript  theme={null}
POST https://external.api.recraft.ai/v1/styles
```

### Example

```python  theme={null}
response = client.post(
    path='/styles',
    cast_to=object,
    options={'headers': {'Content-Type': 'multipart/form-data'}},
    body={'style': 'digital_illustration'},
    files={'file1': open('image.png', 'rb')},
)
print(response['id'])
```

### Output

```javascript  theme={null}
{"id": "229b2a75-05e4-4580-85f9-b47ee521a00d"} 
```

### Request body

Upload a set of images to create a style reference.

| Parameter        | Type   | Description                                                                                                                                 |
| ---------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| style (required) | string | The base style of the generated images, this topic is covered in [Styles](/api-reference/getting-started#styles).                           |
| files (required) | files  | Images in PNG, JPG, or WEBP format for use as style references. The max number of images is 5. Total size of all images is limited to 5 MB. |

## Image to image

Image-to-image generates a new image using the input image and prompt as reference. The model reinterprets the entire image while generally preserving the original composition. The prompt should describe the new image to be produced, inspired by the input.

```javascript  theme={null}
POST https://external.api.recraft.ai/v1/images/imageToImage
```

### Example

```python  theme={null}
response = client.post(
    path='/images/imageToImage',
    cast_to=object,
    options={'headers': {'Content-Type': 'multipart/form-data'}},
    files={
        'image': open('image.png', 'rb'),
    },
    body={
        'prompt': 'winter',
        'strength': 0.2,
    },
)
print(response['data'][0]['url'])
```

### Output

```python  theme={null}
https://img.recraft.ai/f1LAVICjQjTDUbVlwlA4AbE_JBjEQU2t6ho6YhI0J8M/rs:fit:1024:1024:0/raw:1/plain/abs://external/images/6d85db5d-912f-4711-957c-15cbebc8cb24
```

### Parameters

| Parameter           | Type                                         | Description                                                                                                                                                                |
| ------------------- | -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| image (required)    | file                                         | An image to modify, must be less than 5 MB in size, have resolution less than 16 MP, and max dimension less than 4096 pixels.                                              |
| prompt (required)   | string                                       | A text description of areas to change. The maximum length is 1000 bytes.                                                                                                   |
| strength (required) | float                                        | Defines the difference with the original image, should lie in `[0, 1]`, where `0` means almost identical, and `1` means minimal similarity.                                |
| n                   | integer or null, default is 1                | The number of images to generate, must be between 1 and 6.                                                                                                                 |
| style\_id           | UUID or null                                 | Use a previously uploaded style as a reference, this topic is covered in [Getting Started](/api-reference/getting-started#styles) and [Appendix](/api-reference/appendix). |
| style               | string or null, default is `realistic_image` | The style of the generated images, this topic is covered in [Styles](/api-reference/getting-started#styles).                                                               |
| substyle            | string or null                               | This topic is covered in [Styles](/api-reference/getting-started#styles).                                                                                                  |
| model               | string or null, default is `recraftv3`       | The model to use for image generation. Only `recraftv3` is supported at the moment.                                                                                        |
| response\_format    | string or null, default is `url`             | The format in which the generated images are returned. Must be one of `url` or `b64_json`.                                                                                 |
| negative\_prompt    | string or null                               | A text description of undesired elements on an image.                                                                                                                      |
| controls            | object or null                               | A set of custom parameters to tweak generation process, this topic is covered [below](#controls).                                                                          |

**Note**: `style_id` and `style` parameters are mutually exclusive. If neither of the two parameters is specified, the default style of `any` will be used

## Image inpainting

Inpainting replaces or modifies specific parts of an image. It uses a mask to identify the areas to be filled in, where white pixels represent the regions to inpaint, and black pixels indicate the areas to keep intact, i.e. the white pixels are filled based on the input provided in the prompt.

```javascript  theme={null}
POST https://external.api.recraft.ai/v1/images/inpaint
```

### Example

```python  theme={null}
response = client.post(
    path='/images/inpaint',
    cast_to=object,
    options={'headers': {'Content-Type': 'multipart/form-data'}},
    files={
        'image': open('image.png', 'rb'),
        'mask': open('mask.png', 'rb'),
    },
    body={
        'prompt': 'winter',
    },
)
print(response['data'][0]['url'])
```

### Output

```bash  theme={null}
https://img.recraft.ai/HMd15RTSXeRfEluSPq828pZ7DW9NaI4oR2adSVk_wXc/rs:fit:1024:1024:0/raw:1/plain/abs://external/images/a97b9cc2-4498-41d8-9904-1d58e04b239b
```

### Parameters

Body of a request should contains an image file and a mask in PNG, JPG or WEBP format and parameters passed as content type `'multipart/form-data'`. The image must be no more than 5 MB in size, have resolution no more than 16 MP, max dimension no more than 4096 pixels and min dimension no less than 256 pixels.

| Parameter         | Type                                         | Description                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ----------------- | -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| image (required)  | file                                         | An image to modify, must be less than 5 MB in size, have resolution less than 16 MP, and max dimension less than 4096 pixels.                                                                                                                                                                                                                                                                                               |
| mask (required)   | file                                         | An image encoded in **grayscale color mode**, used to define the specific regions of an image that need modification. The white pixels represent the parts of the image that will be inpainted, while black pixels indicate the parts of the image that will remain unchanged. Should have exactly the same size as the image. Each pixel of the image should be either pure black (value `0`) or pure white (value `255`). |
| prompt (required) | string                                       | A text description of areas to change. The maximum length is 1000 bytes.                                                                                                                                                                                                                                                                                                                                                    |
| n                 | integer or null, default is 1                | The number of images to generate, must be between 1 and 6.                                                                                                                                                                                                                                                                                                                                                                  |
| style\_id         | UUID or null                                 | Use a previously uploaded style as a reference, this topic is covered in [Getting Started](/api-reference/getting-started#styles) and [Appendix](/api-reference/appendix).                                                                                                                                                                                                                                                  |
| style             | string or null, default is `realistic_image` | The style of the generated images, this topic is covered in [Styles](/api-reference/getting-started#styles).                                                                                                                                                                                                                                                                                                                |
| substyle          | string or null                               | This topic is covered in [Styles](/api-reference/getting-started#styles).                                                                                                                                                                                                                                                                                                                                                   |
| model             | string or null, default is `recraftv3`       | The model to use for image generation. Only `recraftv3` is supported at the moment.                                                                                                                                                                                                                                                                                                                                         |
| response\_format  | string or null, default is `url`             | The format in which the generated images are returned. Must be one of `url` or `b64_json`.                                                                                                                                                                                                                                                                                                                                  |
| negative\_prompt  | string or null                               | A text description of undesired elements on an image.                                                                                                                                                                                                                                                                                                                                                                       |

**Note**: `style_id` and `style` parameters are mutually exclusive. If neither of the two parameters is specified, the default style of `any` will be used

## Replace background

Replace Background operation detects background of an image and modifies it according to given prompt.

```javascript  theme={null}
POST https://external.api.recraft.ai/v1/images/replaceBackground
```

### Example

```python  theme={null}
response = client.post(
    path='/images/replaceBackground',
    cast_to=object,
    options={'headers': {'Content-Type': 'multipart/form-data'}},
    files={
        'image': open('image.png', 'rb'),
    },
    body={
        'prompt': 'winter',
    },
)
print(response['data'][0]['url'])
```

### Output

```python  theme={null}
https://img.recraft.ai/59eRxsKN87Tr-LLFleTm01RZSsSTuoZcHTzT9b1r_XM/rs:fit:1024:1024:0/raw:1/plain/abs://external/images/234453e8-6abf-472f-9ac7-9b8c7eca2f80
```

### Parameters

Body of a request should contains an image file in PNG, JPG or WEBP format and parameters passed as content type `'multipart/form-data'`. The image must be no more than 5 MB in size, have resolution no more than 16 MP, max dimension no more than 4096 pixels and min dimension no less than 256 pixels.

| Parameter         | Type                                         | Description                                                                                                                                                                |
| ----------------- | -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| image (required)  | file                                         | An image to modify, must be less than 5 MB in size, have resolution less than 16 MP, and max dimension less than 4096 pixels.                                              |
| prompt (required) | string                                       | A text description of areas to change. The maximum length is 1000 bytes.                                                                                                   |
| n                 | integer or null, default is 1                | The number of images to generate, must be between 1 and 6.                                                                                                                 |
| style\_id         | UUID or null                                 | Use a previously uploaded style as a reference, this topic is covered in [Getting Started](/api-reference/getting-started#styles) and [Appendix](/api-reference/appendix). |
| style             | string or null, default is `realistic_image` | The style of the generated images, this topic is covered in [Styles](/api-reference/getting-started#styles).                                                               |
| substyle          | string or null                               | This topic is covered in [Styles](/api-reference/getting-started#styles).                                                                                                  |
| model             | string or null, default is `recraftv3`       | The model to use for image generation. Only `recraftv3` is supported at the moment.                                                                                        |
| response\_format  | string or null, default is `url`             | The format in which the generated images are returned. Must be one of `url` or `b64_json`.                                                                                 |
| negative\_prompt  | string or null                               | A text description of undesired elements on an image.                                                                                                                      |

**Note**: `style_id` and `style` parameters are mutually exclusive. If neither of the two parameters is specified, the default style of `any` will be used

## Generate background

Generate Background operation generates a background for a given image, based on a prompt and a mask that specifies the regions to fill.

```javascript  theme={null}
POST https://external.api.recraft.ai/v1/images/generateBackground
```

### Example

```python  theme={null}
response = client.post(
    path='/images/generateBackground',
    cast_to=object,
    options={'headers': {'Content-Type': 'multipart/form-data'}},
    files={
        'image': open('image.png', 'rb'),
        'mask': open('mask.png', 'rb'),
    },
    body={
        'prompt': 'winter',
    },
)
print(response['data'][0]['url'])
```

### Output

```python  theme={null}
https://img.recraft.ai/59eRxsKN87Tr-LLFleTm01RZSsSTuoZcHTzT9b1r_XM/rs:fit:1024:1024:0/raw:1/plain/abs://external/images/234453e8-6abf-472f-9ac7-9b8c7eca2f80
```

### Parameters

Body of a request should contains an image file and a mask file, both in PNG, JPG or WEBP format, and parameters passed as content type `'multipart/form-data'`. The image must be no more than 5 MB in size, have resolution no more than 16 MP, max dimension no more than 4096 pixels and min dimension no less than 256 pixels.

| Parameter         | Type                                         | Description                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ----------------- | -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| image (required)  | file                                         | An image to modify, must be less than 5 MB in size, have resolution less than 16 MP, and max dimension less than 4096 pixels.                                                                                                                                                                                                                                                                                               |
| mask (required)   | file                                         | An image encoded in **grayscale color mode**, used to define the specific regions of an image that need modification. The white pixels represent the parts of the image that will be inpainted, while black pixels indicate the parts of the image that will remain unchanged. Should have exactly the same size as the image. Each pixel of the image should be either pure black (value `0`) or pure white (value `255`). |
| prompt (required) | string                                       | A text description of areas to change. The maximum length is 1000 bytes.                                                                                                                                                                                                                                                                                                                                                    |
| n                 | integer or null, default is 1                | The number of images to generate, must be between 1 and 6.                                                                                                                                                                                                                                                                                                                                                                  |
| style\_id         | UUID or null                                 | Use a previously uploaded style as a reference, this topic is covered in [Getting Started](/api-reference/getting-started#styles) and [Appendix](/api-reference/appendix).                                                                                                                                                                                                                                                  |
| style             | string or null, default is `realistic_image` | The style of the generated images, this topic is covered in [Styles](/api-reference/getting-started#styles).                                                                                                                                                                                                                                                                                                                |
| substyle          | string or null                               | This topic is covered in [Styles](/api-reference/getting-started#styles).                                                                                                                                                                                                                                                                                                                                                   |
| model             | string or null, default is `recraftv3`       | The model to use for image generation. Only `recraftv3` is supported at the moment.                                                                                                                                                                                                                                                                                                                                         |
| response\_format  | string or null, default is `url`             | The format in which the generated images are returned. Must be one of `url` or `b64_json`.                                                                                                                                                                                                                                                                                                                                  |
| negative\_prompt  | string or null                               | A text description of undesired elements on an image.                                                                                                                                                                                                                                                                                                                                                                       |

**Note**: `style_id` and `style` parameters are mutually exclusive. If neither of the two parameters is specified, the default style of `any` will be used

## Vectorize image

Converts a given raster image to SVG format.

```javascript  theme={null}
POST https://external.api.recraft.ai/v1/images/vectorize
```

### Example

```javascript  theme={null}
response = client.post(
    path='/images/vectorize',
    cast_to=object,
    options={'headers': {'Content-Type': 'multipart/form-data'}},
    files={'file': open('image.png', 'rb')},
)
print(response['image']['url'])
```

### Output

```bash  theme={null}
https://img.recraft.ai/fZm6nwEjI9Qy94LukIKbxRm4w2i5crwqu459qKg7ZWY/rs:fit:1341:1341:0/raw:1/plain/abs://external/images/2835e19f-282b-419b-b80c-9231a3d51517
```

### **Parameters**

Body of a request should be a file in PNG, JPG or WEBP format and parameters passed as content type `'multipart/form-data'`. The image must be no more than 5 MB in size, have resolution no more than 16 MP, max dimension no more than 4096 pixels and min dimension no less than 256 pixels.

| Parameter        | Type                             | Description                                                                                |
| ---------------- | -------------------------------- | ------------------------------------------------------------------------------------------ |
| response\_format | string or null, default is `url` | The format in which the generated images are returned. Must be one of `url` or `b64_json`. |

## Remove background

Removes background of a given raster image.

```javascript  theme={null}
POST https://external.api.recraft.ai/v1/images/removeBackground
```

### Example

```javascript  theme={null}
response = client.post(
    path='/images/removeBackground',
    cast_to=object,
    options={'headers': {'Content-Type': 'multipart/form-data'}},
    files={'file': open('image.png', 'rb')},
)
print(response['image']['url'])
```

### Output

```bash  theme={null}
https://img.recraft.ai/EYOLjpky-2-uClelfP61kzK-SEpIhKgLfjLFFGxmM_U/rs:fit:0:0:0/raw:1/plain/abs://external/images/e2d0cba6-12df-4141-aa21-43bfd5889990
```

### **Parameters**

Body of a request should be a file in PNG, JPG or WEBP format and parameters passed as content type `'multipart/form-data'`. The image must be no more than 5 MB in size, have resolution no more than 16 MP, max dimension no more than 4096 pixels and min dimension no less than 256 pixels.

| Parameter        | Type                             | Description                                                                                |
| ---------------- | -------------------------------- | ------------------------------------------------------------------------------------------ |
| response\_format | string or null, default is `url` | The format in which the generated images are returned. Must be one of `url` or `b64_json`. |

## Crisp upscale

Enhances a given raster image using ‘crisp upscale’ tool, increasing image resolution, making the image sharper and cleaner.

```javascript  theme={null}
POST https://external.api.recraft.ai/v1/images/crispUpscale
```

### Example

```javascript  theme={null}
response = client.post(
    path='/images/crispUpscale',
    cast_to=object,
    options={'headers': {'Content-Type': 'multipart/form-data'}},
    files={'file': open('image.png', 'rb')},
)
print(response['image']['url'])
```

### Output

```bash  theme={null}
https://img.recraft.ai/LtCo_bs3chC8zhrku0CWLpCBKv4iOODprEdeD_MY1dw/rs:fit:1760:2348:0/raw:1/plain/abs://external/images/f7d01b15-0eba-4439-a5fb-38af38fb524e
```

### Request body

Body of a request should be a file in PNG, JPG or WEBP format and parameters passed as content type `multipart/form-data`. The image must be no more than 5 MB in size, have resolution no more than 4 MP, max dimension no more than 4096 pixels and min dimension no less than 32 pixels.

| Parameter        | Type                             | Description                                                                                |
| ---------------- | -------------------------------- | ------------------------------------------------------------------------------------------ |
| response\_format | string or null, default is `url` | The format in which the generated images are returned. Must be one of `url` or `b64_json`. |

## Creative upscale

Enhances a given raster image using ‘creative upscale’ tool, boosting resolution with a focus on refining small details and faces.

```javascript  theme={null}
POST https://external.api.recraft.ai/v1/images/creativeUpscale
```

### Example

```javascript  theme={null}
response = client.post(
    path='/images/creativeUpscale',
    cast_to=object,
    options={'headers': {'Content-Type': 'multipart/form-data'}},
    files={'file': open('image.png', 'rb')},
)
print(response['image']['url'])
```

### Output

```bash  theme={null}
https://img.recraft.ai/DV4d9pMeq5lIluqS7m8qHyg-mb6hf5uCqEPPC8t8wy4/rs:fit:4740:3536:0/raw:1/plain/abs://external/images/fb576169-8a66-4270-a566-35713ad72020
```

### Request body

Body of a request should be a file in PNG, JPG or WEBP format and parameters passed as content type `multipart/form-data`. The image must be no more than 5 MB in size, have resolution no more than 16 MP, max dimension no more than 4096 pixels and min dimension no less than 256 pixels.

| Parameter        | Type                             | Description                                                                                |
| ---------------- | -------------------------------- | ------------------------------------------------------------------------------------------ |
| response\_format | string or null, default is `url` | The format in which the generated images are returned. Must be one of `url` or `b64_json`. |

## Erase region

Erases a region of a given raster image following a given mask, where white pixels represent the regions to erase, and black pixels indicate the areas to keep intact.

```javascript  theme={null}
POST https://external.api.recraft.ai/v1/images/eraseRegion
```

### Example

```javascript  theme={null}
response = client.post(
    path='/images/eraseRegion',
    cast_to=object,
    options={'headers': {'Content-Type': 'multipart/form-data'}},
    files={'image': open('image.png', 'rb'), 'mask': open('mask.png', 'rb')},
)
print(response['image']['url'])
```

### Output

```bash  theme={null}
https://img.recraft.ai/LtCo_bs3chC8zhrku0CWLpCBKv4iOODprEdeD_MY1dw/rs:fit:1760:2348:0/raw:1/plain/abs://external/images/f7d01b15-0eba-4439-a5fb-38af38fb524e
```

### Request body

Body of a request should contain a file and a mask, both in PNG, JPG or WEBP format, and parameters passed as content type `multipart/form-data`. The images must be no more than 5 MB in size, have resolution no more than 4 MP, max dimension no more than 4096 pixels and min dimension no less than 32 pixels. The mask and image must have the same dimensions.

| Parameter        | Type                             | Description                                                                                                                                                                                                                                                                                                                                                                                                     |
| ---------------- | -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| image (required) | file                             | An image to modify, must be less than 5 MB in size, have resolution less than 16 MP, and max dimension less than 4096 pixels.                                                                                                                                                                                                                                                                                   |
| mask (required)  | file                             | An image encoded in **grayscale color mode**, used to define the specific regions of the image to be erased. The white pixels represent the parts of the image that will be erased, while black pixels indicate the parts of the image that will remain unchanged. Should have exactly the same size as the image. Each pixel of the image should be either pure black (value `0`) or pure white (value `255`). |
| response\_format | string or null, default is `url` | The format in which the generated images are returned. Must be one of `url` or `b64_json`.                                                                                                                                                                                                                                                                                                                      |

## Get user information

Returns information of the current user including credits balance.

```javascript  theme={null}
GET https://external.api.recraft.ai/v1/users/me
```

### Example

```python  theme={null}
response = client.get(path='/users/me', cast_to=object)
print(response)
```

### Output

```javascript  theme={null}
{
    "credits": 1000,
    "email": "test@example.com",
    "id": "c18a1988-45e7-4c00-82c4-4ad7d3dbce3a",
    "name": "Recraft Test"
}
```

## Auxiliary

### Controls

The generation process can be adjusted with a number of tweaks.

| Parameter         | Type                       | Description                                                                                                                                                                                                                                 |
| ----------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| artistic\_level   | integer or null            | Defines the artistic tone of your image. At a simple level, the person looks straight at the camera in a static and clean style. Dynamic and eccentric levels introduce movement and creativity. The value should be in the range `[0..5]`. |
| colors            | array of color definitions | An array of preferable colors.                                                                                                                                                                                                              |
| background\_color | color definition           | Use the given color as a desired background color.                                                                                                                                                                                          |
| no\_text          | bool                       | Do not embed text layouts.                                                                                                                                                                                                                  |

#### Colors

Color type is defined as an object with the following fields

| Parameter      | Description                                                                  |
| -------------- | ---------------------------------------------------------------------------- |
| rgb (required) | An array of 3 integer values in range of `0...255` defining RGB color model. |

**Example**

```python  theme={null}
response = client.images.generate(
    prompt='race car on a track',
    style='realistic_image',
    extra_body={
        'controls': {
            'colors': [
                {'rgb': [0, 255, 0]}
            ]
        }
    }
)
print(response.data[0].url)
```

### Text Layout

Text layout is used to define spatial and textual attributes for individual text elements. Each text element consists of an individual word and its bounding box (bbox).

| Parameter       | Description                                                                                                   |
| --------------- | ------------------------------------------------------------------------------------------------------------- |
| text (required) | A single word containing only supported characters.                                                           |
| bbox (required) | A bounding box representing a 4-angled polygon. Each point in the polygon is defined by relative coordinates. |

**Bounding box**: The bounding box (bbox) is a list of 4 points representing a 4-angled figure (not necessarily a rectangle). Each point specifies its coordinates relative to the layout dimensions, where (0, 0) is the top-left corner, (1, 1) is the bottom-right corner.

**Coordinates**: Coordinates are **relative** to the layout dimensions. Coordinates can extend beyond the \[0, 1] range, such values indicate that the shape will be cropped.

**Points**: The bounding box must always have **exactly 4 points**. Each point is an array of two floats \[x, y] representing the relative position.

**Supported characters**

The `text` field must contain a single word composed only of the following characters:

```text  theme={null}
! " # $ % & ' ( ) * + , - . / 
0 1 2 3 4 5 6 7 8 9 
: ; < > ? @ 
A B C D E F G H I J K L M N O P Q R S T U V W X Y Z 
_ { } 
Ø Đ Ħ Ł Ŋ Ŧ 
Α Β Ε Ζ Η Ι Κ Μ Ν Ο Ρ Τ Υ Χ 
І 
А В Е К М Н О Р С Т У Х 
ß ẞ
 
```

Any character not listed above will result in validation errors.

**Example**

```python  theme={null}
response = client.images.generate(
    prompt="cute red panda with a sign",
    style="digital_illustration",
    extra_body={
        "text_layout": [
            {
                "text": "Recraft",
                "bbox": [[0.3, 0.45], [0.6, 0.45], [0.6, 0.55], [0.3, 0.55]],
            },
            {
                "text": "AI",
                "bbox": [[0.62, 0.45], [0.70, 0.45], [0.70, 0.55], [0.62, 0.55]],
            },
        ]
    },
)
print(response.data[0].url)
```

## Variate image

Generates variations of a given raster image.

```javascript  theme={null}

POST https://external.api.recraft.ai/v1/images/variateImage
```

### Example

```python  theme={null}
response = client.post(
    path='/images/variateImage',
    cast_to=object,
    options={'headers': {'Content-Type': 'multipart/form-data'}},
    files={'image': open('image.png', 'rb')},
    body={'size': '1024x1024'}
)
print(response['data'][0]['url'])
```

### Output

```bash  theme={null}
https://img.recraft.ai/LtCo_bs3chC8zhrku0CWLpCBKv4iOODprEdeD_MY1dw/rs:fit:1760:2348:0/raw:1/plain/abs://external/images/f7d01b15-0eba-4439-a5fb-38af38fb524e
```

### Parameters

The request body must be a file in PNG, JPG, or WEBP format, submitted with the content type 'multipart/form-data'. The image must not exceed 5 MB in size, with a maximum resolution of 16 MP, a maximum dimension of 4096 px, and a minimum dimension of 256 px.

| Parameter        | Type                             | Description                                                                                                                                  |
| ---------------- | -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| image (required) | file                             | The input image in PNG, WEBP or JPEG format.                                                                                                 |
| image\_format    | string or null                   | Format of the output image. Supported values: png, webp.                                                                                     |
| size (required)  | string                           | The size of the generated images in `WxH` format, supported values are published in [Appendix](/api-reference/appendix#list-of-image-sizes). |
| random\_seed     | string or null                   | Optional random seed for reproducibility.                                                                                                    |
| n                | integer or null, default is 1    | Number of variations to generate \[1–6].                                                                                                     |
| response\_format | string or null, default is `url` | The format in which the generated images are returned. Must be one of `url` or `b64_json`.                                                   |


---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://www.recraft.ai/docs/llms.txt


# Examples

Generate AI images using cURL or Python and create your own styles programmatically.

### Generate a digital illustration using RecraftV3 model

<CodeGroup>
  ```bash generate_recraftv3.sh theme={null}
  curl https://external.api.recraft.ai/v1/images/generations \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $RECRAFT_API_TOKEN" \
      -d '{
          "prompt": "two race cars on a track",
          "style": "digital_illustration",
          "model": "recraftv3"
      }'
  ```

  ```python generate_recraftv3.py theme={null}
  from openai import OpenAI

  client = OpenAI(base_url='https://external.api.recraft.ai/v1', api_key=_RECRAFT_API_TOKEN)

  response = client.images.generate(
    prompt='two race cars on a track',
    style='digital_illustration',
    model='recraftv3',
  )
  print(response.data[0].url)
  ```
</CodeGroup>

### Generate a realistic image with specific size

<CodeGroup>
  ```bash generate_with_size.sh theme={null}
  curl https://external.api.recraft.ai/v1/images/generations \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $RECRAFT_API_TOKEN" \
      -d '{
          "prompt": "red point siamese cat",
          "style": "realistic_image",
          "size": "1280x1024"
      }'
  ```

  ```python generate_with_size.py theme={null}
  from openai import OpenAI

  client = OpenAI(base_url='https://external.api.recraft.ai/v1', api_key=_RECRAFT_API_TOKEN)

  response = client.images.generate(
    prompt='red point siamese cat',
    style='realistic_image',
    size='1280x1024',
  )
  print(response.data[0].url)
  ```
</CodeGroup>

### Generate a digital illustration with specific substyle

<CodeGroup>
  ```bash generate_digital_illustration.sh theme={null}
  curl https://external.api.recraft.ai/v1/images/generations \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $RECRAFT_API_TOKEN" \
      -d '{
          "prompt": "a monster with lots of hands",
          "style": "digital_illustration",
          "substyle": "hand_drawn"
      }'
  ```

  ```python generate_digital_illustration.py theme={null}
  from openai import OpenAI

  client = OpenAI(base_url='https://external.api.recraft.ai/v1', api_key=_RECRAFT_API_TOKEN)

  response = client.images.generate(
    prompt='a monster with lots of hands',
    style='digital_illustration',
    extra_body={'substyle': 'hand_drawn'},
  )
  print(response.data[0].url)
  ```
</CodeGroup>

### Image to image with digital illustration style

<CodeGroup>
  ```bash image_to_image.sh theme={null}
  curl -X POST https://external.api.recraft.ai/v1/images/imageToImage \
      -H "Content-Type: multipart/form-data" \
      -H "Authorization: Bearer $RECRAFT_API_TOKEN" \
      -F "image=@image.png" \
      -F "prompt=winter" \
      -F "strength=0.2" \
      -F "style=digital_illustration"
  ```

  ```python image_to_image.py theme={null}
  from openai import OpenAI

  client = OpenAI(base_url='https://external.api.recraft.ai/v1', api_key=_RECRAFT_API_TOKEN)

  response = client.post(
      path='/images/imageToImage',
      cast_to=object,
      options={'headers': {'Content-Type': 'multipart/form-data'}},
      files={
          'image': open('image.png', 'rb'),
      },
      body={
          'prompt': 'winter',
          'strength': 0.2,
          'style': 'digital_illustration',
      },
  )
  print(response['data'][0]['url'])
  ```
</CodeGroup>

### Inpaint an image with digital illustration style

<CodeGroup>
  ```bash inpaint.sh theme={null}
  curl -X POST https://external.api.recraft.ai/v1/images/inpaint \
      -H "Content-Type: multipart/form-data" \
      -H "Authorization: Bearer $RECRAFT_API_TOKEN" \
      -F "prompt=moon" \
      -F "style=digital_illustration" \
      -F "image=@image.png" -F "mask=@mask.png"
  ```

  ```python inpaint.py theme={null}
  from openai import OpenAI

  client = OpenAI(base_url='https://external.api.recraft.ai/v1', api_key=_RECRAFT_API_TOKEN)

  response = client.post(
      path='/images/inpaint',
      cast_to=object,
      options={'headers': {'Content-Type': 'multipart/form-data'}},
      files={
          'image': open('image.png', 'rb'),
          'mask': open('mask.png', 'rb'),
      },
      body={
          'style': 'digital_illustration',
          'prompt': 'moon',
      },
  )
  print(response['data'][0]['url'])
  ```
</CodeGroup>

### Create own style by uploading reference images and use them for generation

<CodeGroup>
  ```bash create_style_and_generate.sh theme={null}
  curl -X POST https://external.api.recraft.ai/v1/styles \
      -H "Content-Type: multipart/form-data" \
      -H "Authorization: Bearer $RECRAFT_API_TOKEN" \
      -F "style=digital_illustration" \
      -F "file=@image.png"

  # response: {"id":"095b9f9d-f06f-4b4e-9bb2-d4f823203427"}

  curl https://external.api.recraft.ai/v1/images/generations \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $RECRAFT_API_TOKEN" \
      -d '{
          "prompt": "wood potato masher",
          "style_id": "095b9f9d-f06f-4b4e-9bb2-d4f823203427"
      }'
  ```

  ```python create_style_and_generate.py theme={null}
  from openai import OpenAI

  client = OpenAI(base_url='https://external.api.recraft.ai/v1', api_key=_RECRAFT_API_TOKEN)

  style = client.post(
      path='/styles',
      cast_to=object,
      options={'headers': {'Content-Type': 'multipart/form-data'}},
      body={'style': 'digital_illustration'},
      files={'file': open('image.png', 'rb')},
  )
  print(style['id'])

  response = client.images.generate(
    prompt='wood potato masher',
    extra_body={'style_id': style['id']},
  )
  print(response.data[0].url)
  ```
</CodeGroup>

### Vectorize an image in PNG format

<CodeGroup>
  ```bash vectorize.sh theme={null}
  curl -X POST https://external.api.recraft.ai/v1/images/vectorize \
      -H "Content-Type: multipart/form-data" \
      -H "Authorization: Bearer $RECRAFT_API_TOKEN" \
      -F "file=@image.png"
  ```

  ```python vectorize.py theme={null}
  from openai import OpenAI

  client = OpenAI(base_url='https://external.api.recraft.ai/v1', api_key=_RECRAFT_API_TOKEN)

  response = client.post(
      path='/images/vectorize',
      cast_to=object,
      options={'headers': {'Content-Type': 'multipart/form-data'}},
      files={'file': open('image.png', 'rb')},
  )
  print(response['image']['url'])
  ```
</CodeGroup>

### Remove background from a PNG image, get the result in B64 JSON

<CodeGroup>
  ```bash remove_background_b64.sh theme={null}
  curl -X POST https://external.api.recraft.ai/v1/images/removeBackground \
      -H "Content-Type: multipart/form-data" \
      -H "Authorization: Bearer $RECRAFT_API_TOKEN" \
      -F "response_format=b64_json" \
      -F "file=@image.png"
  ```

  ```python remove_background_b64.py theme={null}
  from openai import OpenAI

  client = OpenAI(base_url='https://external.api.recraft.ai/v1', api_key=_RECRAFT_API_TOKEN)

  response = client.post(
      path='/images/removeBackground',
      cast_to=object,
      options={'headers': {'Content-Type': 'multipart/form-data'}},
      body={'response_format': 'b64_json'},
      files={'file': open('image.png', 'rb')},
  )
  print(response['image']['url'])
  ```
</CodeGroup>

### Run crisp upscale tool for a PNG image, get the result in B64 JSON

<CodeGroup>
  ```bash crisp_upscale_b64.sh theme={null}
  curl -X POST https://external.api.recraft.ai/v1/images/crispUpscale \
      -H "Content-Type: multipart/form-data" \
      -H "Authorization: Bearer $RECRAFT_API_TOKEN" \
      -F "response_format=b64_json" \
      -F "file=@image.png"
  ```

  ```python crisp_upscale_b64.py theme={null}
  from openai import OpenAI

  client = OpenAI(base_url='https://external.api.recraft.ai/v1', api_key=_RECRAFT_API_TOKEN)

  response = client.post(
      path='/images/crispUpscale',
      cast_to=object,
      options={'headers': {'Content-Type': 'multipart/form-data'}},
      body={'response_format': 'b64_json'},
      files={'file': open('image.png', 'rb')},
  )
  print(response['image']['url'])
  ```
</CodeGroup>

### Run creative upscale tool for a PNG image

<CodeGroup>
  ```bash creative_upscale.sh theme={null}
  curl -X POST https://external.api.recraft.ai/v1/images/creativeUpscale \
      -H "Content-Type: multipart/form-data" \
      -H "Authorization: Bearer $RECRAFT_API_TOKEN" \
      -F "file=@image.png"
  ```

  ```python creative_upscale.py theme={null}
  from openai import OpenAI

  client = OpenAI(base_url='https://external.api.recraft.ai/v1', api_key=_RECRAFT_API_TOKEN)

  response = client.post(
      path='/images/creativeUpscale',
      cast_to=object,
      options={'headers': {'Content-Type': 'multipart/form-data'}},
      files={'file': open('image.png', 'rb')},
  )
  print(response['image']['url'])
  ```
</CodeGroup>

### Variate PNG image, get the result in WEBP format

<CodeGroup>
  ```bash variate_image.sh theme={null}
  curl -X POST https://external.api.recraft.ai/v1/images/variateImage \
      -H "Content-Type: multipart/form-data" \
      -H "Authorization: Bearer $RECRAFT_API_TOKEN" \
      -F "response_format=url" \
      -F "size=1024x1024" \
      -F "n=1" \
      -F "seed=13191922" \
      -F "image_format=webp" \
      -F "file=@image.png"
  ```

  ```python variate_image.py theme={null}
  from openai import OpenAI

  client = OpenAI(base_url='https://external.api.recraft.ai/v1', api_key=_RECRAFT_API_TOKEN)

  response = client.post(
      path='/images/variateImage',
      cast_to=object,
      options={'headers': {'Content-Type': 'multipart/form-data'}},
      body={"size": "1024x1024", "n": 1, "response_format": "url", "seed": 13191922, "image_format": "webp"},
      files={'file': open('image.png', 'rb')},
  )
  print(response['data'][0]["url"])
  ```
</CodeGroup>


---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://www.recraft.ai/docs/llms.txt


# Pricing

## API unit package pricing

The following are the API Unit packages available from Recraft for the use of the Recraft API Service. API Unit packages must be purchased in advance and all API Unit packages are non-cancellable and non-refundable. Any number of unit packages can be bought, and purchased unit packages do not expire.

| Price      | API units |
| ---------- | --------- |
| USD \$1.00 | 1,000     |

## API unit charges for API services

The following are the service charges (in API Units) for use of the API Services. API Units will be automatically deducted from Member’s pre-purchased API Unit package upon use of the described Service by the Member.

| Service description                           | Cost (USD) | API units charged |
| --------------------------------------------- | ---------- | ----------------- |
| Raster image generation – Recraft V3          | \$0.04     | 40                |
| Raster image generation – Recraft V2          | \$0.022    | 22                |
| Vector image generation – Recraft V3          | \$0.08     | 80                |
| Vector image generation – Recraft V2          | \$0.044    | 44                |
| Raster image to image (per single image)      | \$0.04     | 40                |
| Vector image to image (per single image)      | \$0.08     | 80                |
| Raster image inpainting (per single image)    | \$0.04     | 40                |
| Vector image inpainting (per single image)    | \$0.08     | 80                |
| Replace raster background (per single image)  | \$0.04     | 40                |
| Replace vector background (per single image)  | \$0.08     | 80                |
| Generate raster background (per single image) | \$0.04     | 40                |
| Generate vector background (per single image) | \$0.08     | 80                |
| Image style creation                          | \$0.04     | 40                |
| Image vectorization                           | \$0.01     | 10                |
| Image background removal                      | \$0.01     | 10                |
| Crisp upscale                                 | \$0.004    | 4                 |
| Creative upscale                              | \$0.25     | 250               |
| Erase region                                  | \$0.002    | 2                 |


---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://www.recraft.ai/docs/llms.txt


# Appendix

### List of styles

| Style                  | Recraft V3 substyles                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Recraft V2 substyles                                                                                                                                                                                                                           |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `any`                  | (not applicable)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | (not available)                                                                                                                                                                                                                                |
| `realistic_image`      | `b_and_w`, `enterprise`, `evening_light`, `faded_nostalgia`, `forest_life`, `hard_flash`, `hdr`, `motion_blur`, `mystic_naturalism`, `natural_light`, `natural_tones`, `organic_calm`, `real_life_glow`, `retro_realism`, `retro_snapshot`, `studio_portrait`, `urban_drama`, `village_realism`, `warm_folk`                                                                                                                                                                                                                                                                                                                                | `b_and_w`, `enterprise`, `hard_flash`, `hdr`, `motion_blur`, `natural_light`, `studio_portrait`                                                                                                                                                |
| `digital_illustration` | `2d_art_poster`, `2d_art_poster_2`, `antiquarian`, `bold_fantasy`, `child_book`, `cover`, `crosshatch`, `digital_engraving`, `engraving_color`, `expressionism`, `freehand_details`, `grain`, `grain_20`, `graphic_intensity`, `hand_drawn`, `hand_drawn_outline`, `handmade_3d`, `hard_comics`, `infantile_sketch`, `long_shadow`, `modern_folk`, `multicolor`, `neon_calm`, `noir`, `nostalgic_pastel`, `outline_details`, `pastel_gradient`, `pastel_sketch`, `pixel_art`, `plastic`, `pop_art`, `pop_renaissance`, `seamless`, `street_art`, `tablet_sketch`, `urban_glow`, `urban_sketching`, `young_adult_book`, `young_adult_book_2` | `2d_art_poster`, `2d_art_poster_2`, `3d`, `80s`, `engraving_color`, `glow`, `grain`, `hand_drawn`, `hand_drawn_outline`, `handmade_3d`, `infantile_sketch`, `kawaii`, `pixel_art`, `plastic`, `psychedelic`, `seamless`, `voxel`, `watercolor` |
| `vector_illustration`  | `bold_stroke`, `chemistry`, `colored_stencil`, `cosmics`, `cutout`, `depressive`, `editorial`, `emotional_flat`, `engraving`, `line_art`, `line_circuit`, `linocut`, `marker_outline`, `mosaic`, `naivector`, `roundish_flat`, `seamless`, `segmented_colors`, `sharp_contrast`, `thin`, `vector_photo`, `vivid_shapes`                                                                                                                                                                                                                                                                                                                     | `cartoon`, `doodle_line_art`, `engraving`, `flat_2`, `kawaii`, `line_art`, `line_circuit`, `linocut`, `seamless`                                                                                                                               |
| `icon`                 | (not available)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | `broken_line`, `colored_outline`, `colored_shapes`, `colored_shapes_gradient`, `doodle_fill`, `doodle_offset_fill`, `offset_fill`, `outline`, `outline_gradient`, `pictogram`                                                                  |
| `logo_raster`          | `emblem_graffiti`, `emblem_pop_art`, `emblem_punk`, `emblem_stamp`, `emblem_vintage`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | (not available)                                                                                                                                                                                                                                |

### List of image sizes

* 1024x1024
* 1365x1024
* 1024x1365
* 1536x1024
* 1024x1536
* 1820x1024
* 1024x1820
* 1024x2048
* 2048x1024
* 1434x1024
* 1024x1434
* 1024x1280
* 1280x1024
* 1024x1707
* 1707x1024

### Policies

* All generated images are currently stored for approx. 24 hours, this policy may change in the future, and you should not rely on it remaining constant.
* Images are publicly accessible via direct links without authentication. However, since the URLs include unique image identifiers and are cryptographically signed, restoring lost links is nearly impossible.
* Currently, image generation rates are defined on a per-user basis and set at **100 images per minute**. These rate limits may be adjusted in the future.

Need help or have suggestions for improving our docs? [Contact support](mailto:\[help@recraft.ai]\(mailto:help@recraft.ai\))


---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://www.recraft.ai/docs/llms.txt