
Omni-Video (O1)
Create Task
POST
/v1/videos/omni-video
The Omni model can achieve various capabilities through Prompt with elements, images, videos, and other content.

Request Header
Content-Type
string
Required
Default to application/json
Data Exchange Format

Authorization
string
Required
Authentication information, refer to API authentication

Request Body
model_name
string
Optional
Default to kling-video-o1
Model Name

Enum values：
kling-video-o1
prompt
string
Required
Text prompt words, which can include positive and negative descriptions.

The prompt words can be templated to meet different video generation needs
Must not exceed 2,500 characters
The Omni model can achieve various capabilities through Prompt with elements, images, videos, and other content:

Specify elements/images/videos using <<<>>> format, e.g.: <<<element_1>>>, <<<image_1>>>, <<<video_1>>>
For detailed capabilities, see: KLING Omni Model User Guide
image_list
array
Optional
Reference Image List, including element, scene, style reference images.

First/End Frame Usage:

Can be used as first frame or end frame to generate video
Use type parameter to define: first_frame for first frame, end_frame for end frame
End frame only is NOT supported - first frame is required when using end frame
Video editing function cannot be used when generating video with first/end frame
Image Requirements:

Supports Base64 encoding or image URL (ensure accessibility)
Formats: .jpg / .jpeg / .png
File size: ≤10MB
Dimensions: min 300px, aspect ratio 1:2.5 ~ 2.5:1
Quantity Limits:

With reference video: max 4 images
Without reference video: max 7 images
Setting end frame is NOT supported when >2 images in array
image_url parameter value must not be empty
▾
Hide child attributes
image_url
string
Required
Image URL or Base64

type
string
Optional
Frame type: first_frame or end_frame

Enum values：
first_frame
end_frame
element_list
array
Optional
Reference Element List, based on element ID from element library.

Quantity Limits (combined with image_list):

With reference video: image count + element count ≤ 4
Without reference video: image count + element count ≤ 7
Load with key:value format as follows:
"element_list":[
  { "element_id": 829836802793406551 }
]
▾
Hide child attributes
element_id
long
Required
Element ID from element library

video_list
array
Optional
Reference Video, obtained via URL.

Video Types:

Can be used as feature reference video OR base video for editing (default: base)
Use refer_type parameter: feature for feature reference, base for video to be edited
When reference video is base type, first/end frames cannot be defined
Use keep_original_sound to keep original sound: yes to keep, no to discard (also applies to feature type)
Video Requirements:

Format: MP4/MOV only
Duration: 3-10 seconds
Resolution: 720px-2160px (width and height)
Frame rate: 24-60fps (output will be 24fps)
Max 1 video, size ≤200MB
video_url parameter value must not be empty
▾
Hide child attributes
video_url
string
Required
Video URL

refer_type
string
Optional
Default to base
Reference type: feature (feature reference) or base (video to be edited)

Enum values：
feature
base
base - Transformation (Video Edit):
Edit video content - add/remove/modify elements, change shot composition, angles, styles, colors, weather, etc.

feature - Video Reference:
Reference video content to generate next/previous shot, or reference video style/camera movement.

keep_original_sound
string
Optional
Keep original sound: yes to keep, no to discard

Enum values：
yes
no
mode
string
Optional
Default to pro
Video generation mode

Enum values：
std
pro
std: Standard mode, cost-effective
pro: Professional mode (high quality), better video quality output
The support range for different model versions and video modes varies. For details, see Capability Map

aspect_ratio
string
Optional
Aspect ratio of generated video frame (width:height)

Enum values：
16:9
9:16
1:1
This parameter is required when NOT using first-frame reference or video editing function.
Support Matrix:

Scenario	Supported
Text-to-video	✓
Image/Element reference	✓
Video reference (Other)	✓
Video reference (Generate next/previous shot)	✓
Transformation (video edit, base)	✗
Image-to-video (first/end frame)	✗
duration
string
Optional
Default to 5
Video duration in seconds

Enum values：
3
4
5
6
7
8
9
10
Support Matrix:

Scenario	Supported Values
Text-to-video, Image-to-video (without first/end frame)	3-10
Video editing (refer_type: base)	Follows input video duration (parameter ignored)
Other cases (image+element without video, or video with refer_type: feature)	3-10
When using video editing function, billing is calculated by rounding the input video duration to the nearest integer.

watermark_info
object
Optional
Whether to generate watermarked results simultaneously

Defined by the enabled parameter, format:
  "watermark_info": { "enabled": boolean } 
true: generate watermarked result, false: do not generate
Custom watermarks are not currently supported
callback_url
string
Optional
Callback notification URL for task result. If configured, server will actively notify when task status changes.

For specific message schema, see Callback Protocol
external_task_id
string
Optional
Custom task ID defined by user.

Will not overwrite system-generated task ID, but supports querying task by this ID.
Must be unique within a single user account.
cURL

Copy

Collapse
curl --request POST \
  --url https://api-singapore.klingai.com/v1/videos/omni-video \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
  "model_name": "kling-video-o1",
  "prompt": "Make the person in <<<image_1>>> wave to the camera",
  "image_list": [
    {
      "image_url": "https://p2-kling.klingai.com/kcdn/cdn-kcdn112452/kling-qa-test/multi-1.png"
    }
  ],
  "duration": "5",
  "mode": "pro",
  "aspect_ratio": "16:9",
  "callback_url": "",
  "external_task_id": ""
}'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, is used for tracking requests and troubleshooting
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_info": { //Task creation parameters
      "external_task_id": "string" //User-defined task ID
    },
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, unit: ms
  }
}
Scenario invocation examples
The following is an example of scene code. For more effects and prompt words, please refer to: Kling Omni Model Example

Image/Element Reference
Image/Element Reference：Supports reference images/elements, including characters, items, backgrounds, and more, to generate with more creativity and consistency.
cURL

Copy

Collapse
curl --location 'https://api-singapore.klingai.com/v1/videos/omni-video' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data '{
    "model_name": "kling-video-o1",
    "prompt": "<<<image_1>>> strolling through the streets of Tokyo, encountered <<<element_1>>> and <<<element_2>>>, and jumped into the arms of <<<element_2>>>. The video style matches that of <<<image_2>>>",
    "image_list": [
        {
        	"image_url": "xxxxx"
        },
        {
        	"image_url": "xxxxx"
        }
    ],
    "element_list": [
        {
        	"element_id": long
        },
        {
        	"element_id": long
        }
    ],
    "mode": "pro",
    "aspect_ratio": "1:1",
    "duration": "7"
}'
Transformation
Input-based Modification: Supports Inpainting/outpainting, or changing shot compositions or angles. It also supports localized or full-scale adjustments, such as modifying/swapping subjects, backgrounds, partial areas, styles, colors, weather, and more.
cURL

Copy

Collapse
curl --location 'https://api-singapore.klingai.com/v1/videos/omni-video' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data '{
    "model_name": "kling-video-o1",
    "prompt": "Put the crown from <<<image_1>>> on the girl in blue from <<<video_1>>>.",
    "image_list": [
      {
      	"image_url": "xxx"
      }
    ],
    "video_list": [
      {
        "video_url":"xxxxxxxx",
        "refer_type":"base",
        "keep_original_sound":"yes"
      }
    ],
    "mode": "pro"
}'
Video Reference
Video Reference: Supports using reference video content to generate previous or next shots within the same context or set. It can also reference video actions or camera movements for generation.
cURL

Copy

Collapse
curl --location 'https://api-singapore.klingai.com/v1/videos/omni-video' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data '{
    "model_name": "kling-video-o1",
    "prompt": "Referring to the camera movement style in <<<video_1>>>, generate a video: <<<element_1>>> and <<<element_2>>> strolling through the streets of Tokyo, encountering <<<image_1>>> by chance.",
    "image_list": [
      {
      	"image_url": "xxx"
      }
    ],
    "element_list": [
      {
      	"element_id": long
      },
      {
      	"element_id": long
      }
    ],
    "video_list": [
      {
        "video_url":"xxxxxxxx",
        "refer_type":"feature",
        "keep_original_sound":"yes"
      }
    ],
    "mode": "pro",
    "aspect_ratio": "1:1",
    "duration": "7"
}'
cURL

Copy

Collapse
curl --location 'https://api-singapore.klingai.com/v1/videos/omni-video' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data '{
    "model_name": "kling-video-o1",
    "prompt": "Based on <<<video_1>>>, generate the next shot.",
    "video_list": [
      {
        "video_url":"xxxxxxxx",
        "refer_type":"feature",
        "keep_original_sound":"yes"
      }
    ],
    "mode": "pro"
}'
Start & End Frames
cURL

Copy

Collapse
curl --location 'https://api-singapore.klingai.com/v1/videos/omni-video' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data '{
    "model_name": "kling-video-o1",
    "prompt": "The person in the video is dancing.",
    "image_list": [
      {
      	"image_url": "xxx",
        "type": "first_frame"
      },
      {
      	"image_url": "xxx",
        "type": "end_frame"
      }
    ],
    "mode": "pro"
}'
Text To Video
cURL

Copy

Collapse
curl --location 'https://api-singapore.klingai.com/v1/videos/omni-video' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data '{
    "model_name": "kling-video-o1",
    "prompt": "The person in the video is dancing.",
    "mode": "pro",
    "aspect_ratio": "1:1",
    "duration": "7"
}'
FAQ
1、 Video Duration Support

Text-to-video and image-to-video (NOT including first/last frame): Optional duration of 3~10s.
When video input is provided (video_list is not empty) and video editing functionality (type = base) is used: Duration cannot be specified and will align with the input video.
Other cases (when no video is provided but an image + subject is used for video generation, or when a video is provided with video type = feature): Optional duration of 3-10s.
2、 How to Extend a Video?

This can be achieved via “video reference”.
By inputting a video and using a prompt to direct the model to “generate the next shot” or “generate the previous shot”.
cURL

Copy

Collapse
curl --location 'https://api-singapore.klingai.com/v1/videos/omni-video' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data '{
    "model_name": "kling-video-o1",
    "prompt": "Based on <<<video_1>>>, generate the next shot.",
    "video_list": [
      {
        "video_url":"xxxxxxxx",
        "refer_type":"feature",
        "keep_original_sound":"yes"
      }
    ],
    "mode": "pro"
}'
3、 Aspect Ratio Support

Not Supported: Instruction-based transformation (video editing), image-to-video (not including first/last frame).
Supported: Text-to-video, image/subject reference, video reference (other scenarios), video reference (generating next/previous shot).
Query Task (Single)
GET
/v1/videos/omni-video/{id}
Query the status and result of a single task by ID.

Request Header
Content-Type
string
Required
Default to application/json
Data Exchange Format

Authorization
string
Required
Authentication information, refer to API authentication

Path Parameters
task_id
string
Optional
Task ID for video generation task.

Request path parameter, fill the value directly in the request path. Choose either task_id OR external_task_id for querying.

external_task_id
string
Optional
Custom Task ID for video generation task.

The external_task_id provided when creating the task. Choose either task_id OR external_task_id for querying.

cURL

Copy

Collapse
curl --request GET \
  --url https://api-singapore.klingai.com/v1/videos/omni-video/{task_id} \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, is used for tracking requests and troubleshooting
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "task_status_msg": "string", // Task status message, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
    "final_unit_deduction": "string", // Final unit deduction for the task
    "watermark_info": {
      "enabled": boolean
    },
    "task_info": { //Task creation parameters
      "external_task_id": "string" //User-defined task ID
    },
    "task_result": {
      "videos": [
        {
          "id": "string", // Generated video ID; globally unique
          "url": "string", // Generated video URL, anti-leech format (Please note that for security purposes, generated images/videos will be deleted after 30 days. Please save them promptly.)
          "watermark_url": "string", // Watermarked video download URL, anti-leech format
          "duration": "string" //Total video duration, unit: s (seconds)
        }
      ]
    },
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, unit: ms
  }
}
Query Task (List)
GET
/v1/videos/omni-video
Query a list of tasks with pagination.

Request Header
Content-Type
string
Required
Default to application/json
Data Exchange Format

Authorization
string
Required
Authentication information, refer to API authentication

Query Parameters
pageNum
int
Optional
Default to 1
Page number

Value range: [1, 1000]

pageSize
int
Optional
Default to 30
Data volume per page

Value range: [1, 500]

cURL

Copy

Collapse
curl --request GET \
  --url 'https://api-singapore.klingai.com/v1/videos/omni-video?pageNum=1&pageSize=30' \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, is used for tracking requests and troubleshooting
  "data": [
    {
      "task_id": "string", // Task ID, generated by the system
      "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
      "task_status_msg": "string", // Task status message, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
      "final_unit_deduction": "string", // Final unit deduction for the task
      "watermark_info": {
        "enabled": boolean
      },
      "task_info": { //Task creation parameters
        "external_task_id": "string" //User-defined task ID, choose either task_id or external_task_id for querying
      },
      "task_result": {
        "videos": [
          {
            "id": "string", // Generated video ID; globally unique
            "url": "string", // Generated video URL, anti-leech format (Please note that for security purposes, generated images/videos will be deleted after 30 days. Please save them promptly.)
            "watermark_url": "string", // Watermarked video download URL, anti-leech format
            "duration": "string" //Total video duration, unit: s (seconds)
          }
        ]
      },
      "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
      "updated_at": 1722769557708 //Task update time, Unix timestamp, unit: ms
    }
  ]
}