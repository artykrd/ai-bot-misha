POST
/api/v1/mj/generate
Generate Midjourney Image
Create a new image generation task using the Midjourney AI model

Request Parameters
The API accepts a JSON payload with the following parameters:

taskType
Required
string
Task type for generation mode. Options: mj_txt2img (Text-to-image), mj_img2img (Image-to-image), mj_video (Image-to-video), mj_style_reference (Style reference), mj_omni_reference (Omni reference)

Available options:

mj_txt2img
mj_img2img
mj_video
mj_style_reference
mj_omni_reference
Example:

"mj_txt2img"
prompt
Required
string
Text prompt describing the desired image content. Should be detailed and specific in describing image content. Can include style, composition, lighting and other visual elements.

Max length: 2000 characters
Example:

"Help me generate a sci-fi themed fighter jet in a beautiful sky, to be used as a computer wallpaper"
speed
Optional
string
Generation speed mode. Can be "fast", "relaxed" or "turbo", which corresponds to different speed of Midjourney. Not required when taskType is mj_video or mj_omni_reference

Available options:

relaxed
fast
turbo
Example:

"relaxed"
fileUrl
Optional
string
Input image URL (required for image-to-image and image-to-video generation). Use either fileUrl or fileUrls field. Must be a valid image URL. Image must be accessible to the API server. Leave empty for text-to-image generation.

Example:

"https://example.com/image.jpg"
fileUrls
Optional
array
Input image URL array (required for image-to-image and image-to-video generation). Use either fileUrl or fileUrls field. For backward compatibility, fileUrl field is currently retained. When generating videos, fileUrls can only have one image link. Recommended to use fileUrls field going forward.

Example:

"[\"https://example.com/image.jpg\"]"
aspectRatio
Optional
string
Output image/video aspect ratio

Available options:

1:2
9:16
2:3
3:4
5:6
6:5
4:3
3:2
1:1
16:9
2:1
Example:

"16:9"
version
Optional
string
Midjourney model version to use. Midjourney routinely releases new model versions to improve efficiency, coherency, and quality. The latest model is the default, but each model excels at producing different types of images.

Available options:

7
6.1
6
5.2
5.1
niji6
niji7
Example:

"7"
variety
Optional
integer
Controls the diversity of generated images. Increment by 5 each time, such as (0, 5, 10, 15...). Higher values create more diverse results. Lower values create more consistent results.

Range: 0-100
Example:

10
stylization
Optional
integer
Stylization level (0-1000). Controls the artistic style intensity. Higher values create more stylized results. Lower values create more realistic results. Suggested to be a multiple of 50.

Range: 0-1000
Example:

1
weirdness
Optional
integer
Weirdness level (0-3000). Controls the creativity and uniqueness. Higher values create more unusual results. Lower values create more conventional results. Suggested to be a multiple of 100.

Range: 0-3000
Example:

1
ow
Optional
integer
Omni intensity parameter. Controls the strength of the omni reference effect. Only used when taskType is "mj_omni_reference". Using an Omni Reference allows you to put characters, objects, vehicles, or non-human creatures from a reference image into your Midjourney creations. Higher values result in stronger reference influence. Lower values allow for more creative interpretation.

Range: 1-1000
Example:

500
waterMark
Optional
string
Watermark identifier. Optional parameter. If provided, a watermark will be added to the generated content.

Example:

"my_watermark"
callBackUrl
Optional
string
Callback URL to receive task completion updates. Optional but recommended for production use. System will POST task completion status to this URL. Alternatively, use the Get Midjourney Task Details endpoint to check status.

Example:

"https://api.example.com/callback"
Request Example

cURL

JavaScript

Python
curl -X POST "/api/v1/mj/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
        "taskType": "mj_txt2img",
        "speed": "relaxed",
        "prompt": "Help me generate a sci-fi themed fighter jet in a beautiful sky, to be used as a computer wallpaper",
        "fileUrls": [
            "https://example.com/image.jpg"
        ],
        "aspectRatio": "16:9",
        "version": "7",
        "variety": 10,
        "stylization": 1,
        "weirdness": 1,
        "waterMark": "",
        "callBackUrl": "https://api.example.com/callback",
        "ow": 500
    }'
Response Example
{
  "code": 200,
  "msg": "success",
  "data": {
    "taskId": "mj_task_abcdef123456"
  }
}
Response Fields
code
Status code, 200 for success
msg
Response message
data.taskId
Task ID, can be used with Get Image Details endpoint to query task status
Callback Notifications
When you provide the callBackUrl parameter when creating a task, the system will send POST requests to the specified URL upon task completion (success or failure).

Callback Method
• HTTP Method: POST
• Content Type: application/json
• Timeout Setting: 15 seconds
• Retry Mechanism: Retry 3 times after failure, with intervals of 1 minute, 5 minutes, and 15 minutes
Success Callback Example
{
  "code": 200,
  "msg": "success",
  "data": {
    "taskId": "mj_task_12345",
    "promptJson": "{\"prompt\":\"a beautiful landscape\",\"model\":\"midjourney\"}",
    "resultUrls": [
      "https://example.com/mj_result1.png",
      "https://example.com/mj_result2.png",
      "https://example.com/mj_result3.png",
      "https://example.com/mj_result4.png"
    ]
  }
}
Failure Callback Example
{
  "code": 500,
  "msg": "Image generation failed",
  "data": {
    "taskId": "mj_task_12345",
    "promptJson": "{\"prompt\":\"a beautiful landscape\",\"model\":\"midjourney\"}",
    "resultUrls": []
  }
}


Authentication
All APIs require authentication via Bearer Token.

Authorization: Bearer YOUR_API_KEY