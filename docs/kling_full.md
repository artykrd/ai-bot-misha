General Information
API Domain
https://api-singapore.klingai.com
💡
Notice: The API endpoint for the new system has been updated from https://api.klingai.com to https://api-singapore.klingai.com. This API is suitable for users whose servers are located outside of China.

API Authentication
Step-1：Obtain AccessKey + SecretKey
Step-2：Every time you request the API, you need to generate an API Token according to the fixed encryption method; put Authorization = Bearer <API Token> in the Request Header
Encryption Method：Follow JWT（Json Web Token, RFC 7519）standard
JWT consists of three parts：Header、Payload、Signature
Python
Java

Copy

Collapse
import time
import jwt

ak = "" # fill access key
sk = "" # fill secret key

def encode_jwt_token(ak, sk):
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        "iss": ak,
        "exp": int(time.time()) + 1800, # The valid time, in this example, represents the current time+1800s(30min)
        "nbf": int(time.time()) - 5 # The time when it starts to take effect, in this example, represents the current time -5s
    }
    token = jwt.encode(payload, sk, headers=headers)
    return token

authorization = encode_jwt_token(ak, sk)
print(authorization) # Printing the generated API_TOKEN
Step-3: Use the API Token generated in Step 2 to assemble the Authorization and include it in the Request Header.
Assembly format: Authorization = “Bearer XXX”, where XXX is the API Token generated in Step 2.
Note: There should be a space between Bearer and XXX.
Error Code
HTTP Status Code	Service Code	Definition of Service Code	Explaination of Service Code	Suggested Solutions
200	0	Request successful	-	-
401	1000	Authentication failed	Authentication failed	Check if the Authorization is correct
401	1001	Authentication failed	Authorization is empty	Fill in the correct Authorization in the Request Header
401	1002	Authentication failed	Authorization is invalid	Fill in the correct Authorization in the Request Header
401	1003	Authentication failed	Authorization is not yet valid	Check the start effective time of the token, wait for it to take effect or reissue
401	1004	Authentication failed	Authorization has expired	Check the validity period of the token and reissue it
429	1100	Account exception	Account exception	Verifying account configuration information
429	1101	Account exception	Account in arrears (postpaid scenario)	Recharge the account to ensure sufficient balance
429	1102	Account exception	Resource pack depleted or expired (prepaid scenario)	Purchase additional resource packages, or activate the post-payment service (if available)
403	1103	Account exception	Unauthorized access to requested resource, such as API/model	Verifying account permissions
400	1200	Invalid request parameters	Invalid request parameters	Check whether the request parameters are correct
400	1201	Invalid request parameters	Invalid parameters, such as incorrect key or illegal value	Refer to the specific information in the message field of the returned body and modify the request parameters
404	1202	Invalid request parameters	The requested method is invalid	Review the API documentation and use the correct request method
404	1203	Invalid request parameters	The requested resource does not exist, such as the model	Refer to the specific information in the message field of the returned body and modify the request parameters
400	1300	Trigger strategy	Trigger strategy of the platform	Check if any platform policies have been triggered
400	1301	Trigger strategy	Trigger the content security policy of the platform	Check the input content, modify it, and resend the request
429	1302	Trigger strategy	The API request is too fast, exceeding the platform’s rate limit	Reduce the request frequency, try again later, or contact customer service to increase the limit
429	1303	Trigger strategy	Concurrency or QPS exceeds the prepaid resource package limit	Reduce the request frequency, try again later, or contact customer service to increase the limit
429	1304	Trigger strategy	Trigger the platform’s IP whitelisting policy	Contact customer service
500	5000	Internal error	Server internal error	Try again later, or contact customer service
503	5001	Internal error	Server temporarily unavailable, usually due to maintenance	Try again later, or contact customer service
504	5002	Internal error	Server internal timeout, usually due to a backlog	Try again later, or contact customer service


Concurrency Rules
What is Kling API concurrency?
Kling API concurrency refers to the maximum number of generation tasks that an account can process in parallel at any given time. This capability is determined by the resource package. A higher concurrency level allows you to submit more API generation requests simultaneously (each call to the task creation interface initiates a new generation task).

💡
Notes

This only applies to the task creation interface; query interfaces do not consume concurrency.
This limitation concerns the number of concurrent tasks and is unrelated to Queries Per Second(QPS)— the system imposes no QPS limit.
Core Rules
Dimension	Rule Description
Application Scope	Applied at the account level. Calculated independently per resource pack type (video/image/virtual try-on). All API keys under the same account share the same concurrency quota.
Occupancy Logic	A task occupies concurrency from entering submitted status until completion (including failures). Released immediately after task ends.
Quota Calculation	Determined by the highest concurrency value among all active resource packages of the same type. Example: If a 5-concurrency + 10-concurrency video package are both active → video concurrency capacity = 10
Special Notes

Video / Virtual Try-on tasks: Each task occupies 1 concurrency.
Image generation tasks: Concurrency used = the n value in the API request parameter. (Example: n = 9 → occupies 9 concurrency)
Over-limit Error Mechanism
When the number of running tasks reaches the concurrency limit, submitting a request will return an error.

JSON

Copy

Collapse
{
	"code": 1303,
	"message": "parallel task over resource pack limit",
	"request_id": "9984d27b-a408-4073-ae28-17ca6a13622d" //uuid
}
Recommended Approach
Since this error is triggered by system load (not by parameter issues), it is recommended to:

Backoff Retry Strategy: Use an exponential backoff algorithm to delay retries (recommended initial delay ≥ 1 second).
Queue Management: Control the submission rate through a task queue and dynamically adapt to available concurrency.


Callback Protocol
As for the Async task（image generation / video generation / virtual try-on），if you actively set the callback_url when you Create Task, the server will actively notify you when the task status changes, and the protocol is as follows:

JSON

Copy

Collapse
{
  "task_id": "string",               // Task ID, generated by the system
  "task_status": "string",           // Task status, Enum values: submitted, processing, succeed, failed
  "task_status_msg": "string",       // Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
  "created_at": 1722769557708,       // Task creation time, Unix timestamp, unit ms
  "updated_at": 1722769557708,       // Task update time, Unix timestamp, unit ms
  "final_unit_deduction": "string",   // The deduction units of task
  "task_info": {                     // Task creation parameters. Detailed information provided by the user during task creation.
    "parent_video": {
      "id": "string",                // Generated video ID; globally unique
      "url": "string",               // URL for generating images (To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
      "duration": "string"           // Total duration of the video before continuation, in s
    },
    "external_task_id": "string"     // Customer-defined task ID
  },
  "task_result": {
    "images": [                      // The result of image-related tasks
      {
        "index": int,                // Image Number
        "url": "string"              // URL for generating images, such as: https://h1.inkwai.com/bs2/upload-ylab-stunt/xxx.png (To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
      }
    ],
    "videos": [                      // The result of video-related tasks
      {
        "id": "string",              // Generated video ID; globally unique
        "url": "string",             // URL for generating videos (To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
        "duration": "string"         // Total video duration, unit: s (seconds)
      }
    ]
  }
}


Video Models
kling-video-o1

std（3s～10s）

pro（3s～10s）

text to video

single-shot-video generation

✅（only 5s、10s）

✅（only 5s、10s）

voice control

❌

❌

others

-

-

image to video

single-shot-video generation

（only start frame）

✅（only 5s、10s）

✅（only 5s、10s）

start & end frame

✅

✅

element control

（only multi-image elements）

✅

✅

cideo reference

(including multi-image elements)

✅

✅

voice control

❌

❌

others

-

-

kling-v3-omni

std（3s～15s）

pro（3s～15s）

text to video

single-shot-video generation

✅

✅

multi-shot-video generation

✅

✅

voice control

❌

❌

others

-

-

image to video

single-shot-video generation

✅

✅

multi-shot-video generation

✅

✅

start & end frame

✅

✅

element control

（video character elements & multi-image elements）

✅

✅

reference video

✅（only 3s～10s）

✅（only 3s～10s）

voice control

❌

❌

others

-

-

kling-v1

std 5s

std 10s

pro 5s

pro10s

text

to video

video generation

✅

✅

✅

✅

camera control

✅

-

-

-

image

to video

video generation

✅

✅

✅

✅

start/end frame

✅

-

✅

-

motion brush

✅

-

✅

-

others

-

-

-

-

video extension

（Not supported negative_prompt and cfg_scale)

✅

✅

✅

✅

video effects

Dual-character: Hug, Kiss, heart_gesture

✅

✅

✅

✅

others

-

-

-

-

kling-v1-5

std 5s

std 10s

pro 5s

pro10s

text

to video

video generation

-

-

-

-

others

-

-

-

-

image

to video

video generation

✅

✅

✅

✅

start/end frame

-

-

✅

✅

end frame

-

-

✅

✅

motion brush

-

-

✅

-

camera control

（simple only）

-

-

✅

-

others

-

-

-

-

video extension

✅

✅

✅

✅

video effects

Dual-character: Hug, Kiss, heart_gesture

✅

✅

✅

✅

others

-

-

-

-

kling-v1-6

std 5s

std 10s

pro 5s

pro10s

text

to video

video generation

✅

✅

✅

✅

others

-

-

-

-

image

to video

video generation

✅

✅

✅

✅

start/end frame

-

-

✅

✅

end frame

-

-

✅

✅

others

-

-

-

-

multi-image2video

✅

✅

✅

✅

multi-elements

✅

✅

✅

✅

video extension

✅

✅

✅

✅

video effects

Dual-character: Hug, Kiss, heart_gesture

✅

✅

✅

✅

kling-v2-master

5s

10s

text

to video

video generation

✅

✅

others

-

-

image

to video

video generation

✅

✅

others

-

-

others

-

-

kling-v2-1

std 5s

std 10s

pro 5s

pro10s

text

to video

all

-

-

-

-

image

to video

video generation

✅

✅

✅

✅

start/end frame

-

-

✅

✅

others

-

-

-

-

others

-

-

-

-

kling-v2-1-master

5s

10s

text

to video

video generation

✅

✅

others

-

-

image

to video

video generation

✅

✅

others

-

-

others

-

-

kling-v2-5-turbo

std 5s

std 10s

pro 5s

pro10s

text

to video

video generation

✅

✅

✅

✅

others

-

-

-

-

image

to video

video generation

✅

✅

✅

✅

start/end frame

-

-

✅

✅

others

-

-

-

-

others

-

-

-

-

kling-v2-6

std 5s

std 10s

std x other duration

pro 5s

pro10s

pro x other duration

text to video

video generation

✅ (only no audio)

✅ (only no audio)

-

✅

✅

-

others

-

-

-

-

-

-

image to video

video generation

✅ (only no audio)

✅ (only no audio)

-

✅

✅

-

start/end frame

-

-

-

✅ (only no audio)

✅ (only no audio)

-

voice control

-

-

-

✅

✅

-

motion control

-

-

✅

-

-

✅

others

-

-

-

-

-

-

kling-v3

std（3～15s）

pro（3～15s）

text to video

single-shot-video generation

✅

✅

multi-shot-video generation

✅

✅

voice control

❌

❌

others

-

-

image to video

single-shot-video generation （only start frame）

✅

✅

multi-shot-video generation

✅

✅

start & end frame

✅

✅

element control

（video character elements & multi-image elements）

✅

✅

motion control

✅

✅

voice control

❌

❌

others

-

-

no related of model

support or not

description

avatar

✅

Generate digital human broadcast-style videos with just one photo

lip sync

✅

Can be combined with text or audio to drive the mouth shape of characters in the video

video to audio

✅

Supports adding audio to all videos generated by Kling models and user-uploaded videos

text to audio

-

Supports generating audio by text prompts

others

-

-

Model

kling-v1

kling-v1-5

kling-v1-6

Image to Video

kling-v1-6

Text to Video

kling-v2 Master

Mode

STD

PRO

STD

PRO

STD

PRO

STD

PRO

-

Resolution

720p

720p

720p

1080p

720p

1080p

720p

1080p

720p

Frame Rate

30fps

30fps

30fps

30fps

30fps

30fps

24fps

24fps

24fps

Model

kling-v2-1

Image to Video

kling-v2-1 Master

kling-v2-5

Image to Video

kling-v2-5

Text to Video

Mode

STD

PRO

-

PRO

PRO

Resolution

720p

1080p

1080p

1080p

1080p

Frame Rate

24fps

24fps

24fps

24fps

24fps


Omni-Video
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
kling-v3-omni
multi_shot
boolean
Optional
Default to false
Whether to generate multi-shot video.

When true: the prompt parameter is invalid, and it does not support setting the start & end frames to generate videos

When false: the shot_type and multi_prompt parameters are invalid.

shot_type
string
Optional
Storyboard method.

Enum values：
customize
intelligence
When multi_shot is true, this parameter is required.

prompt
string
Optional
Text prompt words, which can include positive and negative descriptions.

The prompt words can be templated to meet different video generation needs
Must not exceed 2,500 characters
When the "multi_shot" parameter is set to false or when the "multi_shot" parameter is set to true and the "shot-type" parameter is set to intelligence, the current parameter must not be empty.

💡
The Omni model can achieve various capabilities through Prompt with elements, images, videos, and other content:

Specify elements/images/videos using <<<>>> format, e.g.: <<<element_1>>>, <<<image_1>>>, <<<video_1>>>
For detailed capabilities, see: KLING Omni Model User Guide, Kling VIDEO 3.0 Omni Model User Guide
The support range for different model versions and video modes varies. For details, see Capability Map

multi_prompt
array
Optional
Information about each storyboard, such as prompts and duration.

Define shot sequence number, corresponding prompt and duration via index, prompt, and duration parameters.

Supports up to 6 storyboards, minimum 1.
Max length per storyboard content: 512.
Each storyboard duration must not exceed total task duration and must be ≥ 1.
Sum of all storyboard durations must equal total task duration.
When multi_shot is true and shot_type is customize, this parameter is required. Format:

"multi_prompt":[
  { "index": int, "prompt": "string", "duration": "5" },
  { "index": int, "prompt": "string", "duration": "5" }
]
image_list
array
Optional
Reference Image List, including element, scene, style reference images.

Including reference images of the element, scene, style, etc., it can also be used as the start or end frame to generate videos; When generating a video as the start or end frame:
Define whether the image is in the first and last frames using the type parameter: first_frame is the start frame, end_frame is the end frame.
Currently does not support only the end frame, which means that when there is a end frame image, there must be a first frame image.
If the image is not the start & end frame, do not configure the type parameter.
When generating a video using the first frame or the first and last frames, video editing functions cannot be used.
Load with key:value, details as follows:

"image_list":[
  { "image_url": "image_url"},
  { "image_url": "image_url" }
]
Image Requirements:

Supports Base64 encoding or image URL (ensure accessibility)
Formats: .jpg / .jpeg / .png
File size: ≤10MB
Dimensions: min 300px, aspect ratio 1:2.5 ~ 2.5:1
Quantity Limits:

When there are reference video, the sum of the amount of reference image and the amount of reference element shall not exceed 4.
When there is no reference video, the sum of the amount of reference image and the amount of reference element shall not exceed 7.
When using the O1 model, setting the start & end frame is not supported when there are more than two images in the array.
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

When generating a video using the first frame, a maximum of 3 elements are supported.
When generating videos using the start & end frames, the kling-v3-omni model supports up to 3 elements, while the kling-video-o1 model does not support 1 element.
When there is a reference video, the sum of the number of reference images and the number of reference subjects must not exceed 4, and the use of video subjects is not supported.
When there is no reference video, the sum of the number of reference images and the number of reference subjects must not exceed 7.
Elements are categorized into video character elements and Multi-Image Elements, with different scopes. See Kling Element Library User Guide.

Load with key:value format as follows:
"element_list":[
  { "element_id": long },
  { "element_id": long }
]
The support range for different model versions and video modes varies. For details, see Capability Map

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
When there is a reference video, the value of the sound parameter can only be off.

Load with key:value format as follows:
"video_list":[
  { "video_url": "video_url", "refer_type": "base", "keep_original_sound": "yes" }
]
Video Requirements:

Format: MP4/MOV only
Duration: ≥3 seconds, upper limit depends on model version (see Capability Map)
Resolution: 720px-2160px (width and height)
Frame rate: 24-60fps (output will be 24fps)
Max 1 video, size ≤200MB
video_url parameter value must not be empty
The support range for different model versions and video modes varies. For details, see Capability Map

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
sound
string
Optional
Default to off
Whether to generate sound simultaneously when generating videos.

Enum values：
on
off
The support range for different model versions and video modes varies. For details, see Capability Map

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
11
12
13
14
15
When using the video editing function ("refer_type": "base"), the output result is the same as the duration of the incoming video, and the current parameter is invalid. Calculate billing by rounding the input video duration to the nearest integer.
The support range for different model versions and video modes varies. For details, see Capability Map

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
Single shot and multiple shot
Image To Video with Multiple Shot
curl --location 'https://xxx/v1/videos/omni-video/' \
--header 'Authorization: Bearer xxx' \
--header 'Content-Type: application/json' \
--data '{
    "model_name": "kling-v3-omni",
    "multi_shot": true,
    "shot_type": "customize",
    "prompt": "",
    "multi_prompt": [
      {
        "index": 1,
        "prompt": "In the early morning café, sunlight streams through the glass windows, casting its warmth on the wooden tabletop. Coffee cups exhale hot steam, while the background is filled with the indistinct chatter of customers. The camera gradually zooms in, focusing on a young couple <<<image_1>>> (male: 25 years old, with curly hair and wearing a light blue shirt; female: 23 years old, with a ponytail and wearing thin-framed glasses) seated across the table. Their fingers unconsciously touch the same poetry anthology.",
        "duration": "2"
      },
      {
        "index": 2,
        "prompt": "The girl was flipping through the pages of a book with her head down, while the boy <<<image_2>>> suddenly looked up. Their gazes met, causing the girl's cheeks to blush slightly and the boy's mouth to curve upwards. The camera panned through the two of them, capturing the retro clock hanging on the wall behind them (with the hands pointing to 9:15).",
        "duration": "3"
      }
    ],
    "image_list": [
      {
        "image_url": "xx"
      } ,
      {
        "image_url": "xxx"
      }
    ],
    "video_list": [],
    "mode": "pro",
    "sound": "on",
    "aspect_ratio": "16:9",
    "duration": "5",  
    "callback_url": "xx",
    "external_task_id": ""
  }'
Text To Video with Multiple Shot
curl --location 'https://xxx/v1/videos/omni-video/' \
--header 'Authorization: Bearer xxx' \
--header 'Content-Type: application/json; charset=utf-8' \
--data '{
    "model_name": "kling-v3-omni",
    "multi_shot": true,
    "shot_type": "customize",
    "prompt": "",
    "multi_prompt": [
      {
        "index": 1,
        "prompt": "Two friends talking under a streetlight at night. Warm glow, casual poses, no dialogue.",
        "duration": "2"
      },
      {
        "index": 2,
        "prompt": "A runner sprinting through a forest, leaves flying. Low-angle shot, focus on movement.",
        "duration": "3"
      },
      {
        "index": 3,
        "prompt": "A woman hugging a cat, smiling. Soft sunlight, cozy home setting, emphasize warmth.",
        "duration": "3"
      },
      {
        "index": 4,
        "prompt": "A door creaking open, shadowy hallway. Dark tones, minimal details, eerie mood.",
        "duration": "3"
      },
      {
        "index": 5,
        "prompt": "A man slipping on a banana peel, shocked expression. Exaggerated pose, bright colors.",
        "duration": "3"
      },
      {
        "index": 6,
        "prompt": "A sunset over mountains, small figure walking away. Wide angle, peaceful atmosphere.",
        "duration": "1"
      }
    ],
    "image_list": [],
    "sound":"on",
    "element_list": [],
    "video_list": [],
    "mode": "pro",
    "aspect_ratio": "16:9",
    "duration": "15",
    "callback_url": "xxx",
    "external_task_id": ""
  }'
Text To Video with Single Shot
curl --location 'https://api-singapore.klingai.com/v1/videos/omni-video' \
--header 'Authorization: Bearer xxx' \
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
    "watermark_info": {
      "enabled": boolean
    },
    "final_unit_deduction": "string", // Final unit deduction for the task
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
      "watermark_info": {
        "enabled": boolean
      },


Text to Video
Create Task
POST
/v1/videos/text2video
💡
Please note that in order to maintain naming consistency, the original model field has been changed to model_name, so in the future, please use this field to specify the version of the model that needs to be called.
At the same time, we keep the behavior forward-compatible. If you continue to use the original model field, it will not have any impact on the interface call, there will not be any exception, which is equivalent to the default behavior when model_name is empty (i.e., call the V1 model).

Request Header
Content-Type
string
Required
Default to application/json
Data Exchange Format

Authorization
string
Required
Authentication information, refer to API authorization

Request Body
model_name
string
Optional
Default to kling-v1
Model Name

Enum values：
kling-v1
kling-v1-6
kling-v2-master
kling-v2-1-master
kling-v2-5-turbo
kling-v2-6
kling-v3
multi_shot
boolean
Optional
Default to false
Whether to generate multi-shot video

When true: the prompt parameter is invalid, and the first/end frame generation is not supported.

When false: the shot_type and multi_prompt parameters are invalid

shot_type
string
Optional
Storyboard method

Enum values：
customize
intelligence
When multi_shot is true, this parameter is required

prompt
string
Optional
Positive text prompt

💡
The Omni model can achieve various capabilities through Prompt with elements, images, videos, and other content:

Specify elements/images/videos using <<<>>> format, e.g.: <<<element_1>>>, <<<image_1>>>, <<<video_1>>>
For detailed capabilities, see: KLING Omni Model User Guide, Kling VIDEO 3.0 Omni Model User Guide
Cannot exceed 2500 characters
Use <<<voice_1>>> to specify voice, same sequence as voice_list. Up to 2 voices; when specifying voice, sound must be on. Simpler grammar is better. For example: The man <<<voice_1>>> said, "Hello.".
When voice_list is not empty and prompt references voice ID, task is billed as "with voice generation".
When multi_shot is false or shot_type is intelligence, this parameter must not be empty.
The support range for different model versions and video modes varies. For details, see Capability Map

multi_prompt
array
Optional
Each storyboard cue can include both positive and negative descriptions

Define the shot sequence number, corresponding prompt word, and duration through the index, prompt, and duration parameters, where:

Supports up to 6 storyboards, with a minimum of 1 storyboard.
The maximum length of the prompt for each storyboard 512 characters.
The duration of each storyboard should not exceed the total duration, but should not be less than 1.
The sum of the durations of all storyboards equals the total duration of the current task.
Load with key:value format as follows:

"multi_prompt":[
{"index":int,"prompt":"string","duration":"5"},
{"index":int,"prompt":"string","duration":"5"}
]
When multi_shot is true and shot_type is customize, this parameter is required.

negative_prompt
string
Optional
Negative text prompt

Cannot exceed 2500 characters
It is recommended to supplement negative prompt via negative sentences within positive prompts
sound
string
Optional
Default to off
Is sound generated simultaneously when generating videos

Enum values：
on
off
The support range for different model versions and video modes varies. For details, see Capability Map

cfg_scale
float
Optional
Default to 0.5
The degree of freedom for generating video; the larger the value, the smaller the degree of freedom of the model

Value range: [0, 1]
kling-v2.x models do not support this parameter

mode
string
Optional
Default to std
Video generation mode

Enum values：
std
pro
std: Standard mode, basic mode, cost-effective
pro: Expert mode (high quality), high performance mode, better video quality
The support range for different model versions and video modes varies. For details, see Capability Map

camera_control
object
Optional
Terms of controlling camera movement (if not specified, the model will intelligently match based on the input text/images)

The support range for different model versions and video modes varies. For details, see Capability Map

▾
Hide child attributes
type
string
Optional
Predefined camera movements type

Enum values：
simple
down_back
forward_up
right_turn_forward
left_turn_forward
simple: Simple camera movement, you can choose one of six options in "config"
down_back: Camera descends and moves backward ➡️ Pan down and zoom out. The config parameter must be set to "None" under this type.
forward_up: Camera moves forward and tilts up ➡️ Zoom in and pan up. The config parameter must be set to "None" under this type.
right_turn_forward: Rotate right then move forward ➡️ Rotate right and advance. The config parameter must be set to "None" under this type.
left_turn_forward: Rotate left then move forward ➡️ Rotate left and advance. The config parameter must be set to "None" under this type.
config
object
Optional
Contains 6 fields, used to specify the camera's movement or change in different directions

Required when type is simple, not required for other types
Choose 1 of the following 6 parameters, only one can be non-zero, others must be 0
▾
Hide child attributes
horizontal
float
Optional
Horizontal, controls the camera's movement along the horizontal axis (translation along the x-axis)

Value range: [-10, 10]
Negative value indicates a translation to the left, positive value indicates a translation to the right
vertical
float
Optional
Vertical, controls the camera's movement along the vertical axis (translation along the y-axis)

Value range: [-10, 10]
Negative value indicates a downward translation, positive value indicates an upward translation
pan
float
Optional
Pan, controls the camera's rotation in the horizontal plane (rotation around the y-axis)

Value range: [-10, 10]
Negative value indicates rotation to the left around y-axis, positive value indicates rotation to the right around y-axis
tilt
float
Optional
Tilt, controls the camera's rotation in the vertical plane (rotation around the x-axis)

Value range: [-10, 10]
Negative value indicates rotation down around x-axis, positive value indicates rotation up around x-axis
roll
float
Optional
Roll, controls the camera's roll (rotation around the z-axis)

Value range: [-10, 10]
Negative value indicates counterclockwise rotation around z-axis, positive value indicates clockwise rotation around z-axis
zoom
float
Optional
Zoom, controls the camera's focal length change, affecting the distance of the field of view

Value range: [-10, 10]
Negative value indicates longer focal length, smaller field of view; positive value indicates shorter focal length, larger field of view
aspect_ratio
string
Optional
Default to 16:9
The aspect ratio of the generated video frame (width:height)

Enum values：
16:9
9:16
1:1
duration
string
Optional
Default to 5
Video Length, unit: s (seconds)

Enum values：
3
4
5
6
7
8
9
10
11
12
13
14
15
The support range for different model versions and video modes varies. For details, see Capability Map

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
Callback notification URL for this task result. If configured, the server will actively notify when the task status changes

For specific message schema, see Callback Protocol
external_task_id
string
Optional
Customized Task ID

Users can provide a customized task ID, which will not overwrite the system-generated task ID but can be used for task queries
Must be unique within a single user account
cURL

Copy

Collapse
curl --request POST \
  --url https://api-singapore.klingai.com/v1/videos/text2video \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "model_name": "kling-v2-6",
    "prompt": "A cute little rabbit wearing glasses, sitting at a table, reading a newspaper, with a cup of cappuccino on the table",
    "negative_prompt": "",
    "duration": "5",
    "mode": "pro",
    "sound": "on",
    "aspect_ratio": "1:1",
    "callback_url": "",
    "external_task_id": ""
  }'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_info": { // Task creation parameters
      "external_task_id": "string" // Customer-defined task ID
    },
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit ms
    "updated_at": 1722769557708 // Task update time, Unix timestamp, unit ms
  }
}
More Scene Invocation Examples
Text To Video with Multiple Shot
curl --location 'https://xxx/v1/videos/text2video' \
--header 'Authorization: Bearer xxx' \
--header 'Content-Type: application/json' \
--data '{
    "model_name": "kling-v3",
    "prompt": "",
    "multi_prompt": [
        {
            "index": 1,
            "prompt": "Two friends talking under a streetlight at night.  Warm glow, casual poses, no dialogue.",
            "duration": "2"
        },
        {
            "index": 2,
            "prompt": "A runner sprinting through a forest, leaves flying.  Low-angle shot, focus on movement.",
            "duration": "3"
        },
        {
            "index": 3,
            "prompt": "A woman hugging a cat, smiling.  Soft sunlight, cozy home setting, emphasize warmth.",
            "duration": "3"
        },
        {
            "index": 4,
            "prompt": "A door creaking open, shadowy hallway.  Dark tones, minimal details, eerie mood.",
            "duration": "3"
        },
        {
            "index": 5,
            "prompt": "A man slipping on a banana peel, shocked expression.  Exaggerated pose, bright colors.",
            "duration": "3"
        },
        {
            "index": 6,
            "prompt": "A sunset over mountains, small figure walking away.  Wide angle, peaceful atmosphere.",
            "duration": "1"
        }
    ],
    "multi_shot": true,
    "shot_type": "customize",
    "duration": "15",
    "mode": "pro",
    "sound": "on",
    "aspect_ratio": "9:16",
    "callback_url": "",
    "external_task_id": ""
}'
Query Task (Single)
GET
/v1/videos/text2video/{id}
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
Task ID for text-to-video. Fill the value directly in the request path. Choose either task_id or external_task_id for querying.

external_task_id
string
Optional
Customized Task ID for text-to-video. Fill the value directly in the request path. Choose either task_id or external_task_id for querying.

cURL

Copy

Collapse
curl --request GET \
  --url https://api-singapore.klingai.com/v1/videos/text2video/{task_id} \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "task_status_msg": "string", // Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
    "task_info": { // Task creation parameters
      "external_task_id": "string" // Customer-defined task ID
    },
    "task_result": {
      "videos": [
        {
          "id": "string", // Generated video ID; globally unique
          "url": "string", // URL for generating videos (To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
          "watermark_url": "string", // Watermarked video download URL, anti-leech format
          "duration": "string" // Total video duration, unit: s (seconds)
        }
      ]
    },
    "watermark_info": {
      "enabled": boolean
    },
    "final_unit_deduction": "string", // The deduction units of task
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 // Task update time, Unix timestamp, unit: ms
  }
}
Query Task (List)
GET
/v1/videos/text2video
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
Number of items per page

Value range: [1, 500]
cURL

Copy

Collapse
curl --request GET \
  --url 'https://api-singapore.klingai.com/v1/videos/text2video?pageNum=1&pageSize=30' \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in Error codes
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, to track requests and troubleshoot problems
  "data": [
    {
      "task_id": "string", // Task ID, generated by the system
      "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
      "task_status_msg": "string", // Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
      "task_info": { // Task creation parameters
        "external_task_id": "string" // Customer-defined task ID
      },
      "task_result": {
        "videos": [
          {
            "id": "string", // Generated video ID; globally unique
            "url": "string", // URL for generating videos (To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
            "watermark_url": "string", // Watermarked video download URL, anti-leech format
            "duration": "string" // Total video duration, unit: s (seconds)
          }
        ]
      },
      "watermark_info": {
        "enabled": boolean
      },
      "final_unit_deduction": "string", // The deduction units of task
      "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
      "updated_at": 1722769557708 // Task update time, Unix timestamp, unit: ms
    }
  ]
}



Image to Video
Create Task
POST
/v1/videos/image2video
💡
Please note that in order to maintain naming consistency, the original model field has been changed to model_name. Please use this field to specify the model version in the future.
We maintain backward compatibility. If you continue using the original model field, it will not affect API calls and will be equivalent to the default behavior when model_name is empty (i.e., calling the V1 model).

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
Default to kling-v1
Model Name

Enum values：
kling-v1
kling-v1-5
kling-v1-6
kling-v2-master
kling-v2-1
kling-v2-1-master
kling-v2-5-turbo
kling-v2-6
kling-v3
image
string
Optional
Reference Image

Supports image Base64 encoding or image URL (ensure accessibility)
Important: When using Base64, do NOT add any prefix like data:image/png;base64,. Submit only the raw Base64 string.
Correct Base64 format:
iVBORw0KGgoAAAANSUhEUgAAAAUA...
Incorrect Base64 format (with data: prefix):
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA...
Supported image formats: .jpg / .jpeg / .png
File size: ≤10MB, dimensions: min 300px, aspect ratio: 1:2.5 ~ 2.5:1
At least one of image or image_tail must be provided; both cannot be empty
Support varies by model version and video mode. See Capability Map for details.

image_tail
string
Optional
Reference Image - End frame control

Supports image Base64 encoding or image URL (ensure accessibility)
Important: When using Base64, do NOT add any prefix like data:image/png;base64,. Submit only the raw Base64 string.
Supported image formats: .jpg / .jpeg / .png
File size: ≤10MB, dimensions: min 300px
At least one of image or image_tail must be provided; both cannot be empty
image_tail, dynamic_masks/static_mask, and camera_control are mutually exclusive - only one can be used at a time
Support varies by model version and video mode. See Capability Map for details.

multi_shot
boolean
Optional
Default to false
Whether to generate multi-shot video

When true: the prompt parameter is invalid, and the first/end frame generation is not supported.

When false: the shot_type and multi_prompt parameters are invalid

shot_type
string
Optional
Storyboard method

Enum values：
customize
intelligence
When multi_shot is true, this parameter is required

prompt
string
Optional
Positive text prompt

💡
The Omni model can achieve various capabilities through Prompt with elements, images, videos, and other content:

Specify elements/images/videos using <<<>>> format, e.g.: <<<element_1>>>, <<<image_1>>>, <<<video_1>>>
For detailed capabilities, see: KLING Omni Model User Guide, Kling VIDEO 3.0 Omni Model User Guide
Cannot exceed 2500 characters
When multi_shot is false or shot_type is intelligence, this parameter must not be empty.
Use <<<voice_1>>> to specify voice, with the sequence matching the voice_list parameter order
A video generation task can reference up to 2 voices; when specifying a voice, the sound parameter must be "on"
The simpler the syntax structure, the better. Example: The man<<<voice_1>>> said: "Hello"
When voice_list is not empty and prompt references voice ID, the task will be billed as "with specified voice"
Support varies by model version and video mode. See Capability Map for details.

multi_prompt
array
Optional
Information about each storyboard, such as prompts and duration

Define the shot sequence number, corresponding prompt word, and duration through the index, prompt, and duration parameters, where:

Supports up to 6 storyboards, with a minimum of 1 storyboard.
The maximum length of the prompt for each storyboard 512 characters.
The duration of each storyboard should not exceed the total duration, but should not be less than 1.
The sum of the durations of all storyboards equals the total duration of the current task.
Load with key:value format as follows:

"multi_prompt":[
{"index":int,"prompt":"string","duration":"5"},
{"index":int,"prompt":"string","duration":"5"}
]
When multi_shot is true and shot_type is customize, this parameter is required.

negative_prompt
string
Optional
Negative text prompt

Cannot exceed 2500 characters
It is recommended to supplement negative prompt via negative sentences within positive prompts
element_list
array
Optional
Reference Element List, based on element ID from element library

Supports up to 3 reference elements
The elements are categorized into video customization element (named as Video Character Elements) and image customization elements (named as Multi-Image Elements), each with distinct scopes of application. Please exercise caution in distinguishing between them. See Kling Element Library User Guide.

Load with key:value format as follows:
"element_list":[
  { "element_id": long },
  { "element_id": long }
]
Support varies by model version and video mode. See Capability Map for details.

▾
Hide child attributes
element_id
long
Required
Element ID from element library

voice_list
array
Optional
List of voices referenced when generating videos

A video generation task can reference up to 2 voices
When voice_list is not empty and prompt references voice ID, the task will be billed as "with specified voice"
voice_id is returned through the voice customization API, or use system preset voices. See Custom Voices API; NOT the voice_id of Lip-Sync API
element_list and voice_list are mutually exclusive and cannot coexist
Example:

"voice_list":[
  {"voice_id":"voice_id_1"},
  {"voice_id":"voice_id_2"}
]
The support range for different model versions and video modes varies. For details, see Capability Map

sound
string
Optional
Default to off
Whether to generate sound when generating video

Enum values：
on
off
The support range for different model versions and video modes varies. For details, see Capability Map

cfg_scale
float
Optional
Default to 0.5
Flexibility in video generation; higher value means lower model flexibility and stronger relevance to user prompt

Value range: [0, 1]
kling-v2.x models do not support this parameter

mode
string
Optional
Default to std
Video generation mode

Enum values：
std
pro
std: Standard Mode - basic mode, cost-effective
pro: Professional Mode (High Quality) - high performance mode, better video quality
Support varies by model version and video mode. See Capability Map for details.

static_mask
string
Optional
Static brush mask area (mask image created by user using motion brush)

The "Motion Brush" feature includes Dynamic Brush (dynamic_masks) and Static Brush (static_mask)

Supports image Base64 encoding or image URL (same format requirements as image field)
Supported image formats: .jpg / .jpeg / .png
Aspect ratio must match the input image (image field), otherwise task will fail
Resolution of static_mask and dynamic_masks.mask must be identical, otherwise task will fail
Support varies by model version and video mode. See Capability Map for details.

dynamic_masks
array
Optional
Dynamic brush configuration list

Can configure multiple groups (up to 6), each containing "mask area" and "motion trajectory" sequence
Support varies by model version and video mode. See Capability Map for details.

▾
Hide child attributes
mask
string
Required
Dynamic brush mask area (mask image created by user using motion brush)

Supports image Base64 encoding or image URL (same format requirements as image field)
Supported image formats: .jpg / .jpeg / .png
Aspect ratio must match the input image (image field), otherwise task will fail
Resolution of static_mask and dynamic_masks.mask must be identical, otherwise task will fail
trajectories
array
Required
Motion trajectory coordinate sequence

For 5s video, trajectory length ≤77, coordinate count range: [2, 77]
Coordinate system uses bottom-left corner of image as origin
Note 1: More coordinate points = more accurate trajectory. 2 points = straight line between them

Note 2: Trajectory direction follows input order. First coordinate is start point, subsequent coordinates are connected sequentially

▾
Hide child attributes
x
int
Required
X coordinate of trajectory point (pixel coordinate with image bottom-left as origin)

y
int
Required
Y coordinate of trajectory point (pixel coordinate with image bottom-left as origin)

camera_control
object
Optional
Camera movement control protocol (if not specified, model will intelligently match based on input text/images)

Support varies by model version and video mode. See Capability Map for details.

▾
Hide child attributes
type
string
Required
Predefined camera movement type

Enum values：
simple
down_back
forward_up
right_turn_forward
left_turn_forward
simple: Simple camera movement, can choose one of six options in "config"
down_back: Camera descends and moves backward ➡️ Pan down and zoom out. config parameter not required
forward_up: Camera moves forward and tilts up ➡️ Zoom in and pan up. config parameter not required
right_turn_forward: Rotate right then move forward ➡️ Right rotation advance. config parameter not required
left_turn_forward: Rotate left then move forward ➡️ Left rotation advance. config parameter not required
config
object
Optional
Contains 6 fields to specify camera movement in different directions

Required when type is "simple"; leave empty for other types
Choose only one parameter to be non-zero; rest must be 0
▾
Hide child attributes
horizontal
float
Optional
Horizontal movement - camera translation along x-axis

Value range: [-10, 10]. Negative = left, Positive = right
vertical
float
Optional
Vertical movement - camera translation along y-axis

Value range: [-10, 10]. Negative = down, Positive = up
pan
float
Optional
Horizontal pan - camera rotation around y-axis

Value range: [-10, 10]. Negative = rotate left, Positive = rotate right
tilt
float
Optional
Vertical tilt - camera rotation around x-axis

Value range: [-10, 10]. Negative = tilt down, Positive = tilt up
roll
float
Optional
Roll - camera rotation around z-axis

Value range: [-10, 10]. Negative = counterclockwise, Positive = clockwise
zoom
float
Optional
Zoom - controls camera focal length change, affects field of view

Value range: [-10, 10]. Negative = longer focal length (narrower FOV), Positive = shorter focal length (wider FOV)
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
11
12
13
14
15
Support varies by model version and video mode. See Capability Map for details.

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
Callback notification URL for task result. If configured, server will notify when task status changes.

For specific message schema, see Callback Protocol
external_task_id
string
Optional
Customized Task ID

Will not overwrite system-generated task ID, but supports querying task by this ID
Must be unique within a single user account
cURL

Copy

Collapse
curl --location --request POST 'https://api-singapore.klingai.com/v1/videos/image2video' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
    "model_name": "kling-v2-6",
    "image": "https://p2-kling.klingai.com/kcdn/cdn-kcdn112452/kling-qa-test/multi-2.png",
    "image_tail": "https://p2-kling.klingai.com/kcdn/cdn-kcdn112452/kling-qa-test/multi-1.png",
    "prompt": "Camera zooms out, the girl smiles",
    "negative_prompt": "",
    "duration": "5",
    "mode": "pro",
    "sound": "off",
    "callback_url": "",
    "external_task_id": ""
}'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_info": { // Task creation parameters
      "external_task_id": "string" // Customer-defined task ID
    },
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit ms
    "updated_at": 1722769557708 // Task update time, Unix timestamp, unit ms
  }
}
Scenario invocation examples
Image to video with multi-shot
curl --location 'https://xxx/v1/videos/image2video' \
--header 'Authorization: Bearer xxx' \
--header 'Content-Type: application/json' \
--data '{
    "model_name": "kling-v3",
    "image": "xxx",
    "prompt": "",
    "multi_shot": "true",
    "shot_type": "customize",
    "multi_prompt": [
        {
            "index": 1,
            "prompt": "Two friends talking under a streetlight at night.  Warm glow, casual poses, no dialogue.",
            "duration": "2"
        },
        {
            "index": 2,
            "prompt": "A runner sprinting through a forest, leaves flying.  Low-angle shot, focus on movement.",
            "duration": "3"
        },
        {
            "index": 3,
            "prompt": "A woman hugging a cat, smiling.  Soft sunlight, cozy home setting, emphasize warmth.",
            "duration": "3"
        },
        {
            "index": 4,
            "prompt": "A door creaking open, shadowy hallway.  Dark tones, minimal details, eerie mood.",
            "duration": "3"
        },
        {
            "index": 5,
            "prompt": "A man slipping on a banana peel, shocked expression.  Exaggerated pose, bright colors.",
            "duration": "3"
        },
        {
            "index": 6,
            "prompt": "A sunset over mountains, small figure walking away.  Wide angle, peaceful atmosphere.",
            "duration": "1"
        }
    ],
    "negative_prompt": "",
    "duration": "15",
    "mode": "pro",
    "sound": "on",
    "callback_url": "",
    "external_task_id": ""
}'
Image to video with element
curl --location 'https://api-singapore.klingai.com/v1/images/generations' \
--header 'Authorization: Bearer xxx' \
--header 'Content-Type: application/json' \
--data '{
    "model_name": "kling-v3",
    "prompt": "Merge all the characters from the images into the <<<object_2>>> diagram",
    "element_list": [
        {
            "element_id": "160"
        },
        {
            "element_id": "161"
        },
        {
            "element_id": "159"
        }
    ],
    "image": "xxx",
    "resolution": "2k",
    "n": "9",
    "aspect_ratio": "3:2",
    "external_task_id": "",
    "callback_url": ""
}'
curl --location 'https://xxx/v1/videos/text2video' \
--header 'Authorization: Bearer xxx' \
--header 'Content-Type: application/json' \
--data '{
    "model_name": "kling-v3",
    "prompt": "",
    "multi_prompt": [
        {
            "index": 1,
            "prompt": "Two friends talking under a streetlight at night.  Warm glow, casual poses, no dialogue.",
            "duration": "2"
        },
        {
            "index": 2,
            "prompt": "A runner sprinting through a forest, leaves flying.  Low-angle shot, focus on movement.",
            "duration": "3"
        },
        {
            "index": 3,
            "prompt": "A woman hugging a cat, smiling.  Soft sunlight, cozy home setting, emphasize warmth.",
            "duration": "3"
        },
        {
            "index": 4,
            "prompt": "A door creaking open, shadowy hallway.  Dark tones, minimal details, eerie mood.",
            "duration": "3"
        },
        {
            "index": 5,
            "prompt": "A man slipping on a banana peel, shocked expression.  Exaggerated pose, bright colors.",
            "duration": "3"
        },
        {
            "index": 6,
            "prompt": "A sunset over mountains, small figure walking away.  Wide angle, peaceful atmosphere.",
            "duration": "1"
        }
    ],
    "multi_shot": true,
    "shot_type": "customize",
    "duration": "15",
    "mode": "pro",
    "sound": "on",
    "aspect_ratio": "9:16",
    "callback_url": "",
    "external_task_id": ""
}'
Generate video with voice control
curl --location 'https://api-singapore.klingai.com/v1/videos/image2video/' \
--header 'Authorization: Bearer {Replace your token}' \
--header 'Content-Type: application/json; charset=utf-8' \
--data '{
    "model_name": "kling-v2-6",
    "image": "Replace the URL of image",
    "prompt": "<<<voice_1>>>Ask the people in the picture to say the following words, '\''Welcome everyone'\''",    //If a specific dialogue needs to be enclosed in quotation marks
    "voice_list": [
        {
            "voice_id": "Replace the ID of voice"
        }
    ],
    "duration": "5",
    "mode": "pro",
    "sound": "on",
    "callback_url": "",
    "external_task_id": ""
}'
Query Task (Single)
GET
/v1/videos/image2video/{id}
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
Task ID for image to video

Request path parameter, fill value directly in request path
Choose one between task_id and external_task_id for querying
external_task_id
string
Optional
Customized Task ID for image to video

The external_task_id provided when creating the task
Choose one between task_id and external_task_id for querying
cURL

Copy

Collapse
curl --request GET \
  --url https://api-singapore.klingai.com/v1/videos/image2video/{task_id} \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "task_status_msg": "string", // Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
    "watermark_info": {
      "enabled": boolean
    },
    "task_result": {
      "videos": [
        {
          "id": "string", // Generated video ID; globally unique
          "url": "string", // URL for generating videos (To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
          "watermark_url": "string", // Watermarked video download URL, anti-leech format
          "duration": "string" // Total video duration, unit: s
        }
      ]
    },
    "task_info": { // Task creation parameters
      "external_task_id": "string" // Customer-defined task ID
    },
    "final_unit_deduction": "string", // The deduction units of task
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 // Task update time, Unix timestamp, unit: ms
  }
}
Query Task (List)
GET
/v1/videos/image2video
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
  --url 'https://api-singapore.klingai.com/v1/videos/image2video?pageNum=1&pageSize=30' \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in Error codes
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, to track requests and troubleshoot problems
  "data": [
    {
      "task_id": "string", // Task ID, generated by the system
      "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
      "task_status_msg": "string", // Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
      "task_info": { // Task creation parameters
        "external_task_id": "string" // Customer-defined task ID
      },
      "task_result": {
        "videos": [
          {
            "id": "string", // Generated video ID; globally unique
            "url": "string", // URL for generating videos (To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
            "watermark_url": "string", // Watermarked video download URL, anti-leech format
            "duration": "string" // Total video duration, unit: s (seconds)
          }
        ]
      },
      "watermark_info": {


Multi-Image to Video
Create Task
POST
/v1/videos/multi-image2video
Generate video from multiple reference images (elements).

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
Default to kling-v1-6
Model Name

Enum values：
kling-v1-6
image_list
array
Required
Reference Image List

Support up to 4 images, load with key:value format as follows:
"image_list":[
  { "image":"image_url" },
  { "image":"image_url" },
  { "image":"image_url" },
  { "image":"image_url" }
]
Please directly upload the image with selected subject since there is no cropping logic on the API side
Supports image input as either Base64-encoded string or URL (ensure the URL is publicly accessible)
Important: When using Base64, do NOT add any prefix like data:image/png;base64,. Submit only the raw Base64 string.
Correct Base64 format:
iVBORw0KGgoAAAANSUhEUgAAAAUA...
Incorrect Base64 format (with data: prefix):
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA...
Supported image formats: .jpg / .jpeg / .png
Image file size must not exceed 10MB. Image dimensions must be at least 300px. Aspect ratio must be between 1:2.5 and 2.5:1
▾
Hide child attributes
image
string
Required
Image URL or Base64 string

prompt
string
Required
Positive text prompt

Cannot exceed 2500 characters
negative_prompt
string
Optional
Negative text prompt

Cannot exceed 2500 characters
mode
string
Optional
Default to std
Video generation mode

Enum values：
std
pro
std: Standard Mode, which is cost-effective
pro: Professional Mode, generates higher quality video output
Different model versions and video modes have different support ranges. For details, see Capability Map

duration
string
Optional
Default to 5
Video Length, unit: s (seconds)

Enum values：
5
10
aspect_ratio
string
Optional
Default to 16:9
The aspect ratio of the generated video frame (width:height)

Enum values：
16:9
9:16
1:1
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
The callback notification address for the result of this task. If configured, the server will actively notify when the task status changes

The specific message schema of the notification can be found in Callback Protocol
external_task_id
string
Optional
Customized Task ID

User-defined task ID. It will not override the system-generated task ID, but supports querying tasks by this ID
Please note that it must be unique for each user
cURL

Copy

Collapse
curl --request POST \
  --url https://api-singapore.klingai.com/v1/videos/multi-image2video \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "model_name": "kling-v1-6",
    "image_list": [
      { "image": "https://p1-kling.klingai.com/kcdn/cdn-kcdn112452/kling-qa-test/dog.png" },
      { "image": "https://p1-kling.klingai.com/kcdn/cdn-kcdn112452/kling-qa-test/dog_cloth.png" }
    ],
    "prompt": "A white Bichon Frise wearing a red Northeast-style floral cotton jacket, licking its paw",
    "negative_prompt": "",
    "mode": "pro",
    "duration": "5",
    "aspect_ratio": "16:9",
    "callback_url": "",
    "external_task_id": ""
  }'
200

Copy

Collapse
{
  "code": 0, // Error code; Specific definitions can be found in "Error Code"
  "message": "string", // Error message
  "request_id": "string", // Request ID, generated by the system, used to track requests and troubleshoot problems
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, unit: ms
  }
}
Query Task (Single)
GET
/v1/videos/multi-image2video/{id}
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
Task ID for Multi-Image to Video

Request path parameter, fill the value directly in the request path
You can choose to query by external_task_id or task_id
external_task_id
string
Optional
Customized Task ID for Multi-Image to Video

Request path parameter, fill the value directly in the request path
The external_task_id filled in when creating the task. You can choose to query by external_task_id or task_id
cURL

Copy

Collapse
curl --request GET \
  --url https://api-singapore.klingai.com/v1/videos/multi-image2video/{task_id} \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error code; Specific definitions can be found in "Error Code"
  "message": "string", // Error message
  "request_id": "string", // Request ID, generated by the system, used to track requests and troubleshoot problems
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "task_status_msg": "string", // Task status message, displays failure reason when task fails (such as content moderation triggers)
    "task_info": { //Task creation parameters
      "external_task_id": "string" //User-defined task ID
    },
    "task_result": {
      "videos": [
        {
          "id": "string", // Generated video ID; globally unique
          "url": "string", // URL for generating videos (Please note that for security purposes, generated images/videos will be deleted after 30 days. Please save them promptly.)
          "watermark_url": "string", // Watermarked video download URL, anti-hotlinking format
          "duration": "string" //Total video duration, unit: s (seconds)
        }
      ]
    },
    "watermark_info": {
      "enabled": boolean
    },
    "final_unit_deduction": "string", // Final unit deduction for the task
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, unit: ms
  }
}
Query Task (List)
GET
/v1/videos/multi-image2video
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
Number of items per page

Value range: [1, 500]
cURL

Copy

Collapse
curl --request GET \
  --url 'https://api-singapore.klingai.com/v1/videos/multi-image2video?pageNum=1&pageSize=30' \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error code; Specific definitions can be found in "Error Code"
  "message": "string", // Error message
  "request_id": "string", // Request ID, generated by the system, used to track requests and troubleshoot problems
  "data": [
    {
      "task_id": "string", // Task ID, generated by the system
      "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
      "task_status_msg": "string", // Task status message, displays failure reason when task fails (such as content moderation triggers)
      "task_info": { //Task creation parameters
        "external_task_id": "string" //User-defined task ID
      },
      "task_result": {
        "videos": [
          {


Motion Control
Create Task
POST
/v1/videos/motion-control
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
Default to kling-v2-6
Model Name

Enum values：
kling-v2-6
kling-v3
prompt
string
Optional
Text prompt, can include positive and negative descriptions

Can add elements to the scene, achieve camera movement effects, etc. See Kling "Motion Control" User Guide
Cannot exceed 2500 characters
image_url
string
Required
Reference image. Characters, background and other elements in generated video will follow this reference.

Video content requirements:
Character proportions should match the reference motion as much as possible; avoid driving half-body characters with full-body motions
Character should show clear upper body or full body including limbs and head, avoid occlusion
Avoid extreme orientations (upside down, lying flat, etc.). Character should occupy sufficient screen area
Supports realistic/stylized characters (including humans/humanoid animals/some pure animals/some humanoid body proportion characters)
Supports image Base64 encoding or image URL (ensure accessibility)
Important: When using Base64, do NOT add any prefix like data:image/png;base64,. Submit only the raw Base64 string.
Correct Base64 format:
iVBORw0KGgoAAAANSUhEUgAAAAUA...
Incorrect Base64 format (with data: prefix):
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA...
Supported image formats: .jpg / .jpeg / .png
File size: ≤10MB, dimensions: 300px ~ 65536px, aspect ratio: 1:2.5 ~ 2.5:1
video_url
string
Required
URL of reference video. Character actions in generated video will follow this reference.

Video content requirements:
Character should show clear upper body or full body including all limbs and head, avoid occlusion
Recommend uploading single-person action video; for 2+ people, actions will be taken from the character with largest screen proportion
Recommend using real person actions; some stylized characters/humanoid body proportions may work
Video should be single continuous shot with character always visible, avoid cuts or camera movements (will be truncated otherwise)
Avoid overly fast actions; relatively stable actions produce better results
Supported formats: .mp4 / .mov, file size: ≤100MB, dimensions: 340px ~ 3850px. Validation failures will return error codes.
Duration limits: minimum 3 seconds, maximum depends on character_orientation:
When character_orientation is "video": maximum 30 seconds
When character_orientation is "image": maximum 10 seconds
The duration range of the uploaded motion reference is from 3 to 30 seconds, in which the generated video length will align with the duration of the uploaded video. If motions are complex or fast-paced, there is a chance that the output may be shorter than the uploaded video duration, as the model can only extract the valid action duration for generation. The minimum extractable continuous action duration is 3 seconds. Please note that in such cases, the consumed credits cannot be refunded. It is recommended to adjust the complexity and speed of the actions accordingly.
System will validate video content and return error codes if issues are found
element_list
array
Optional
Reference Element List based on element ID configuration

Load with key:value format as follows:
"element_list":[
  { "element_id": 829836802793406551 }
]
When referencing the element, the generated video can only temporarily refer to the orientation of the person in the video.
Currently, only one element can be introduced.
▾
Hide child attributes
element_id
long
Required
Element ID from element library

keep_original_sound
string
Optional
Default to yes
Whether to keep the original sound of the video

Enum values：
yes
no
character_orientation
string
Required
Character orientation in generated video, can match image or video

Enum values：
image
video
image: Match character orientation in the image; reference video duration must not exceed 10 seconds
video: Match character orientation in the video; reference video duration must not exceed 30 seconds
When referencing the element, the generated video can only temporarily refer to the orientation of the person in the video.
mode
string
Required
Video generation mode

Enum values：
std
pro
std: Standard Mode - basic mode, cost-effective
pro: Professional Mode (High Quality) - high performance mode, better video quality
Support varies by model version and video mode. See Capability Map for details.

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
Callback notification URL for task result. If configured, server will notify when task status changes.

For specific message schema, see Callback Protocol
external_task_id
string
Optional
Customized Task ID

Will not overwrite system-generated task ID, but supports querying task by this ID
Must be unique within a single user account
cURL

Copy

Collapse
curl --request POST \
  --url https://api-singapore.klingai.com/v1/videos/motion-control \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json; charset=utf-8' \
  --data-raw '{
    "model_name": "kling-v2-6",
    "image_url": "https://p2-kling.klingai.com/kcdn/cdn-kcdn112452/kling-qa-test/multi-3.ng.png",
    "prompt": "The girl is wearing a loose gray T-shirt and denim shorts",
    "video_url": "https://p2-kling.klingai.com/kcdn/cdn-kcdn112452/kling-qa-test/dance.mp4",
    "keep_original_sound": "yes",
    "character_orientation": "image",
    "mode": "pro",
    "callback_url": "",
    "external_task_id": "xxx"
  }'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, used to track requests and troubleshoot problems
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_info": { //Task creation parameters
      "external_task_id": "string" //Customer-defined task ID
    },
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, unit: ms
  }
}
Query Task (Single)
GET
/v1/videos/motion-control/{id}
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
Task ID for Motion Control. Fill the value directly in the request path. Choose either task_id or external_task_id for querying.

external_task_id
string
Optional
Customized Task ID for Motion Control. Fill the value directly in the request path. Choose either task_id or external_task_id for querying.

cURL

Copy

Collapse
curl --request GET \
  --url https://api-singapore.klingai.com/v1/videos/motion-control/{task_id} \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, used to track requests and troubleshoot problems
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "task_status_msg": "string", // Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
    "task_info": { //Task creation parameters
      "external_task_id": "string" //Customer-defined task ID
    },
    "task_result": {
      "videos": [
        {
          "id": "string", // Generated video ID; globally unique
          "url": "string", // URL for generating videos, anti-leech format (To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
          "watermark_url": "string", // Watermarked video download URL, anti-leech format
          "duration": "string" //Total video duration, unit: s (seconds)
        }
      ]
    },
    "watermark_info": {
      "enabled": boolean
   	},
    "final_unit_deduction": "string", // The deduction units of task
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, unit: ms
  }
}
Query Task (List)
GET
/v1/videos/motion-control
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
  --url 'https://api-singapore.klingai.com/v1/videos/motion-control?pageNum=1&pageSize=30' \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, used to track requests and troubleshoot problems
  "data": [
    {
      "task_id": "string", // Task ID, generated by the system
      "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
      "task_status_msg": "string", // Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
      "task_info": { //Task creation parameters
        "external_task_id": "string" //Customer-defined task ID
      },
      "task_result": {
        "videos": [
          {


Multi-Elements
Initialize Video for Editing
POST
/v1/videos/multi-elements/init-selection
💡
Initialize the original video before using Multi-elements feature. When replacing or removing elements within the existing video, the relevant elements need to be marked in the video beforehand.

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
video_id
string
Optional
The ID of the video generated by the Kling AI

Only videos generated within the last 30 days are supported
Only supports videos with a duration of ≥2 seconds and ≤5 seconds, or ≥7 seconds and ≤10 seconds
Related to the video_url parameter: both video_id and video_url cannot be empty at the same time, and cannot both have values at the same time
video_url
string
Optional
Get link for uploaded video

Only .mp4/.mov formats are supported
Only supports videos with a duration of ≥2 seconds and ≤5 seconds, or ≥7 seconds and ≤10 seconds
Video resolution must be between 720px and 2160px (inclusive) in both width and height
Only supports videos with frame rates of 24, 30, or 60 fps
Related to the video_id parameter: both video_id and video_url cannot be empty at the same time, and cannot both have values at the same time
cURL

Copy

Collapse
curl --request POST \
  --url https://api-singapore.klingai.com/v1/videos/multi-elements/init-selection \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "video_id": "",
    "video_url": "https://v1-kling.klingai.com/kcdn/cdn-kcdn112452/kling-qa-test/animals-output-5s.mp4"
  }'
200

Copy

Collapse
{
  "code": 0, // Error code; Specific definitions can be found in "Error Code"
  "message": "string", // Error message
  "request_id": "string", // Request ID, generated by the system, used for tracking requests and troubleshooting
  "data": {
    "status": 0, // Rejection code, non-zero indicates recognition failure
    "session_id": "id", // Session ID, generated during video initialization task, remains unchanged during editing operations, valid for 24 hours
    "final_unit_deduction": "string", // The deduction units of task
    "fps": 30.0, // Frame rate of parsed video, required when fetching selection preview video
    "original_duration": 1000, // Duration of parsed video, required when creating task
    "width": 720, // Width of parsed video, currently unused
    "height": 1280, // Height of parsed video, currently unused
    "total_frame": 300, // Total frame count of parsed video, required when creating task
    "normalized_video": "url" // URL of initialized video
}
Add Video Selection Area
POST
/v1/videos/multi-elements/add-selection
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
session_id
string
Required
Session ID, generated during the video initialization task and remains unchanged during editing operations

frame_index
int
Required
Frame Number

A maximum of 10 frames can be marked. That is, up to 10 frames can be used to define selection areas in the video
Only supports marking 1 frame at a time
points
array
Required
Click Coordinates, represented by x and y

Value range: [0, 1], expressed as percentages; [0, 1] represents the top-left corner of the frame
Multiple points can be marked at once; up to 10 points can be marked on a single frame
▾
Hide child attributes
x
float
Required
X coordinate [0-1]

y
float
Required
Y coordinate [0-1]

cURL

Copy

Collapse
curl --request POST \
  --url https://api-singapore.klingai.com/v1/videos/multi-elements/add-selection \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "session_id": "847570360458960960",
    "frame_index": 0,
    "points": [
      {
        "x": 0.7738498789346246,
        "y": 0.297142857142857
      }
    ]
  }'
200

Copy

Collapse
{
  "code": 0, // Error code; Specific definitions can be found in "Error Code"
  "message": "string", // Error message
  "request_id": "string", // Request ID, generated by the system, used for tracking requests and troubleshooting
  "data": {
    "status": 0, // Rejection code, non-zero indicates recognition failure
    "session_id": "id", // Session ID, generated during video initialization task, remains unchanged during editing operations, valid for 24 hours
    "final_unit_deduction": "string", // The deduction units of task
    "res": {
      "frame_index": 0,
      "rle_mask_list": [{
        "object_id": 0,
        "rle_mask": {
          "size": [720, 1280],
          "counts": "string"
        },
        "png_mask": {
          "size": [720, 1280],
          "base64": "string"
        }
      }]
    }
  }
}
Sample Code
Decoding Image Segmentation Result
export type RLEObject = {
  size: [h: number, w: number]
  counts: string
}
type RLE = {
  h: number
  w: number
  m: number
  binaries: number[]
}
export function decode(rleObj: RLEObject) {
  const [h, w] = rleObj.size
  const R: RLE = { h, w, m: 0, binaries: [0] }
  rleFrString(R, rleObj.counts)
  const unitArray = new Uint8Array(h * w)
  rleDecode(R, unitArray)
  return unitArray
}
function rleDecode(R: RLE, M: Uint8Array) {
  let j
  let k
  let p = 0
  let v = false
  for (j = 0; j < R.m; j++) {
    for (k = 0; k < R.binaries[j]; k++) {
      const x = Math.floor(p / R.h)
      const y = p % R.h
      M[y * R.w + x] = v === false ? 0 : 1 // Note: y * width + x indicates row-major (horizontal) layout.
      p++
    }
    v = !v
  }
}
function rleFrString(R: RLE, s: string) {
  let m = 0
  let p = 0
  let k
  let x
  let more
  const binaries = []
  while (s[p]) {
    x = 0
    k = 0
    more = 1
    while (more) {
      const c = s.charCodeAt(p) - 48
      x |= (c & 0x1f) << (5 * k)
      more = c & 0x20
      p++
      k++
      if (!more && c & 0x10) {
        x |= -1 << (5 * k)
      }
    }
    if (m > 2) {
      x += binaries[m - 2]
    }
    binaries[m++] = x
  }
  R.m = m
  R.binaries = binaries
}
Rendering the Segmentation Mask Layer
// height refers to the video height and width refers to the video width
function drawMask(rleMask: string, height: number, width: number) {
  if (!canvasRef.value) return
  const ctx = canvasRef.value.getContext('2d')
  if (!ctx) return

  const decodeData = decode({ counts: rleMask, size: [height, width] })
  const imageData = ctx.createImageData(width, height)
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const index = y * width + x
      if (decodeData[index]) {
        const imageIndex = index * 4
        // Set pixel color: red, green, blue, alpha
        imageData.data[imageIndex] = 116 // red
        imageData.data[imageIndex + 1] = 255 // green
        imageData.data[imageIndex + 2] = 82 // blue
        imageData.data[imageIndex + 3] = 163 // alpha
      }
    }
  }
  ctx.putImageData(imageData, 0, 0)
}
Delete Video Selection Area
POST
/v1/videos/multi-elements/delete-selection
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
session_id
string
Required
Session ID, generated during the video initialization task and remains unchanged during editing operations

frame_index
int
Required
Frame Number

points
array
Required
Click Coordinates to delete, represented by x and y

Value range: [0, 1], expressed as percentages; [0, 1] represents the top-left corner of the frame
Multiple points can be provided at once
Coordinates must exactly match those used when adding the video selection area
▾
Hide child attributes
x
float
Required
X coordinate [0-1]

y
float
Required
Y coordinate [0-1]

cURL

Copy

Collapse
curl --request POST \
  --url https://api-singapore.klingai.com/v1/videos/multi-elements/delete-selection \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "session_id": "847570360458960960",
    "frame_index": 0,
    "points": [
      {
        "x": 0.7738498789346246,
        "y": 0.297142857142857
      }
    ]
  }'
200

Copy

Collapse
{
  "code": 0, // Error code; Specific definitions can be found in "Error Code"
  "message": "string", // Error message
  "request_id": "string", // Request ID, generated by the system, used for tracking requests and troubleshooting
  "data": {
    "status": 0, // Rejection code, non-zero indicates recognition failure
    "session_id": "id", // Session ID, generated during video initialization task, remains unchanged during editing operations, valid for 24 hours
    "final_unit_deduction": "string", // The deduction units of task
    "res": {
      "frame_index": 0,
      "rle_mask_list": [{
        "object_id": 0,
        "rle_mask": {
          "size": [720, 1280],
          "counts": "string"
        },
        "png_mask": {
          "size": [720, 1280],
          "base64": "string"
        }
      }]
    }
  }
}
Clear Video Selection
POST
/v1/videos/multi-elements/clear-selection
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
session_id
string
Required
Session ID, generated during the video initialization task and remains unchanged during editing operations

cURL

Copy

Collapse
curl --request POST \
  --url https://api-singapore.klingai.com/v1/videos/multi-elements/clear-selection \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "session_id": "847570360458960960"
  }'
200

Copy

Collapse
{
  "code": 0, // Error code; Specific definitions can be found in "Error Code"
  "message": "string", // Error message
  "request_id": "string", // Request ID, generated by the system, used for tracking requests and troubleshooting
  "data": {
    "status": 0, // Rejection code, non-zero indicates recognition failure
    "session_id": "id" // Session ID, generated during video initialization task, remains unchanged during editing operations, valid for 24 hours
    "final_unit_deduction": "string", // The deduction units of task
  }
}
Preview Video with Selected Areas
POST
/v1/videos/multi-elements/preview-selection
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
session_id
string
Required
Session ID, generated during the video initialization task and remains unchanged during editing operations

cURL

Copy

Collapse
curl --request POST \
  --url https://api-singapore.klingai.com/v1/videos/multi-elements/preview-selection \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "session_id": "847570360458960960"
  }'
200

Copy

Collapse
{
  "code": 0, // Error code; Specific definitions can be found in "Error Code"
  "message": "string", // Error message
  "request_id": "string", // Request ID, generated by the system, used for tracking requests and troubleshooting
  "data": {
    "status": 0, // Rejection code, non-zero indicates recognition failure
    "session_id": "id", // Session ID, generated during video initialization task, remains unchanged during editing operations, valid for 24 hours
    "final_unit_deduction": "string", // The deduction units of task
    "res": {
      "video": "url", // Video with mask
      "video_cover": "url", // Cover image of video with mask
      "tracking_output": "url" // Mask result for each frame in image segmentation results
    }
  }
}
Create Task
POST
/v1/videos/multi-elements
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
Default to kling-v1-6
Model Name

Enum values：
kling-v1-6
session_id
string
Required
Session ID, generated during the video initialization task and remains unchanged during editing operations

edit_mode
string
Required
Operation Type

Enum values：
addition
swap
removal
addition: Add an element
swap: Replace an element
removal: Remove an element
image_list
array
Optional
Cropped Reference Images

For adding video elements: This parameter is required; upload 1–2 images
For editing (swapping) video elements: This parameter is required; upload 1 image only
For deleting video elements: This parameter is not required
Use key:value format as follows:
"image_list":[
  { "image":"image_url" },
  { "image":"image_url" }
]
The API does not perform cropping, please upload images with subjects already cropped
Supports image input as either Base64-encoded string or URL (ensure the URL is publicly accessible)
Important: When using Base64, do NOT add any prefix like data:image/png;base64,. Submit only the raw Base64 string.
Correct Base64 format:
iVBORw0KGgoAAAANSUhEUgAAAAUA...
Incorrect Base64 format (with data: prefix):
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA...
Supported image formats: .jpg / .jpeg / .png
Image file size must not exceed 10MB. Image dimensions must be at least 300px. Aspect ratio must be between 1:2.5 and 2.5:1
▾
Hide child attributes
image
string
Required
Image URL or Base64 string

prompt
string
Required
Positive Prompt

Use the format <<<xxx>>> to explicitly refer to a specific video or image, such as <<<video_1>>> or <<<image_1>>>
To ensure optimal results, the prompt must include references to the video and image(s) required for the editing
Must not exceed 2,500 characters
💡
Recommended Prompt Templates:

Adding Elements:

EN: Using the context of <<<video_1>>>, seamlessly add [x] from <<<image_1>>>
ZH: 基于<<<video_1>>>中的原始内容，以自然生动的方式，将<<<image_1>>>中的【】，融入<<<video_1>>>的【】
Replacing Elements:

EN: swap [x] from <<<image_1>>> for [x] from <<<video_1>>>
ZH: 使用<<<image_1>>>中的【】，替换<<<video_1>>>中的【】
Removing Elements:

EN: Delete [x] from <<<video_1>>>
ZH: 删除<<<video_1>>>中的【】
Note: [x] or 【】 are placeholders where you should fill in specific content.

negative_prompt
string
Optional
Negative Prompt

Must not exceed 2,500 characters
mode
string
Optional
Default to std
Video Generation Mode

Enum values：
std
pro
std: Standard mode, basic rendering, cost-effective
pro: Professional mode, high-quality, enhanced rendering, better video output quality
duration
string
Optional
Default to 5
Video Duration (in seconds)

Enum values：
5
10
Only 5-second and 10-second videos are supported
To generate a 5-second video, the input video must be ≥2 seconds and ≤5 seconds
To generate a 10-second video, the input video must be ≥7 seconds and ≤10 seconds
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
Callback URL for Task Result Notification. If configured, the server will actively send notifications when the task status changes

For the message schema, refer to the Callback Protocol
external_task_id
string
Optional
Custom Task ID

A user-defined task ID; it will not overwrite the system-generated task ID, but can be used to query the task
Please ensure uniqueness of the task ID within a single user account
cURL

Copy

Collapse
curl --request POST \
  --url https://api-singapore.klingai.com/v1/videos/multi-elements \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "model_name": "kling-v1-6",
    "session_id": "847570360458960960",
    "edit_mode": "removal",
    "image_list": [],
    "prompt": "Delete the chick from <<<video_1>>>",
    "negative_prompt": "",
    "mode": "std",
    "duration": "5",
    "callback_url": "",
    "external_task_id": ""
  }'
200

Copy

Collapse
{
  "code": 0, // Error code; Specific definitions can be found in "Error Code"
  "message": "string", // Error message
  "request_id": "string", // Request ID, generated by the system, used for tracking requests and troubleshooting
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "task_info": {
      "external_task_id": "string" // User-defined task ID
    },
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 // Task update time, Unix timestamp, unit: ms
  }
}
Query Task (Single)
GET
/v1/videos/multi-elements/{id}
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
Task ID for Multi-Elements video editing

Request path parameter, fill the value directly in the request path
You can choose to query by external_task_id or task_id
external_task_id
string
Optional
Custom Task ID for Multi-Elements video editing

The external_task_id filled in when creating the task. You can choose to query by external_task_id or task_id
cURL

Copy

Collapse
curl --request GET \
  --url https://api-singapore.klingai.com/v1/videos/multi-elements/{task_id} \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error code; Specific definitions can be found in "Error Code"
  "message": "string", // Error message
  "request_id": "string", // Request ID, generated by the system, used for tracking requests and troubleshooting
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "task_status_msg": "string", // Task status message, displays failure reason when task fails (e.g., triggered platform content moderation)
    "task_info": { // Task creation parameters
      "external_task_id": "string" // User-defined task ID
    },
    "task_result": {
      "videos": [
        {
          "id": "string", // Generated video ID, globally unique
          "session_id": "id", // Session ID, generated during video initialization task, remains unchanged during editing operations, valid for 24 hours
          "url": "string", // URL of generated video (Note: For security purposes, generated images/videos will be deleted after 30 days, please save them promptly)
          "watermark_url": "string", // Watermarked video download URL, anti-hotlinking format
          "duration": "string" // Total video duration, unit: s
        }
      ]
    },
    "watermark_info": {
      "enabled": boolean
    },
    "final_unit_deduction": "string", // Final unit deduction for the task
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 // Task update time, Unix timestamp, unit: ms
  }
}
Query Task (List)
GET
/v1/videos/multi-elements
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
Number of items per page

Value range: [1, 500]
cURL

Copy

Collapse
curl --request GET \
  --url 'https://api-singapore.klingai.com/v1/videos/multi-elements?pageNum=1&pageSize=30' \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error code; Specific definitions can be found in "Error Code"
  "message": "string", // Error message
  "request_id": "string", // Request ID, generated by the system, used for tracking requests and troubleshooting
  "data": [
    {
      "task_id": "string", // Task ID, generated by the system
      "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
      "task_status_msg": "string", // Task status message, displays failure reason when task fails (e.g., triggered platform content moderation)
      "task_info": { // Task creation parameters
        "external_task_id": "string" // User-defined task ID
      },
      "task_result": {
        "videos": [
          {
            "id": "string", // Generated video ID, globally unique
            "session_id": "id", // Session ID, generated during video initialization task, remains unchanged during editing operations, valid for 24 hours
            "url": "string", // URL of generated video (Note: For security purposes, generated images/videos will be deleted after 30 days, please save them promptly)
            "watermark_url": "string", // Watermarked video download URL, anti-hotlinking format
            "duration": "string" // Total video duration, unit: s
          }
        ]



Video Extension
Create Task
POST
/v1/videos/video-extend
Note 1: Video extension refers to extending the duration of text-to-video/image-to-video results. Each extension can add 4 to 5 seconds, and the model and mode used cannot be selected; they must be the same as the source video.
Note 2: Videos that have been extended can be extended again, but the total video duration cannot exceed 3 minutes.
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
video_id
string
Required
Video ID

Supports video IDs generated by the text-to-video, the image-to-video and the video extension interface (it cannot exceed 3 minutes).
Only videos generated by V1.0, V1.5, and V1.6 models are supported.
Please note that based on the current cleanup policy, videos will be cleared 30 days after generation, and extension will not be possible.

prompt
string
Optional
Text Prompt

Cannot exceed 2500 characters

negative_prompt
string
Optional
Negative text prompt

Cannot exceed 2500 characters

cfg_scale
float
Optional
Default to 0.5
Prompt reference strength. The higher the value, the stronger the reference to the prompt.

Value range: [0, 1]

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
The callback notification address for the task results. If configured, the server will actively notify when the task status changes.

For specific message schema, see Callback Protocol
external_task_id
string
Optional
Customized Task ID

User-defined task ID. It will not override the system-generated task ID, but supports querying tasks by this ID
Please note that it must be unique for each user
cURL

Copy

Collapse
curl --request POST \
  --url https://api-singapore.klingai.com/v1/videos/video-extend \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "prompt": "A puppy appears",
    "video_id": "743211632612511839",
    "negative_prompt": "",
    "callback_url": ""
  }'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in Error codes
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "task_info":{ // Task creation parameters
      "external_task_id": "string" // Customer-defined task ID
    },
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, unit: ms
  }
}
Query Task (Single)
GET
/v1/videos/video-extend/{id}
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
Task ID for Video Generation. Fill the value directly in the request path. Choose either task_id or external_task_id for querying.

external_task_id
string
Optional
Customized Task ID for Video Generation. Fill the value directly in the request path. Choose either task_id or external_task_id for querying.

cURL

Copy

Collapse
curl --request GET \
  --url https://api-singapore.klingai.com/v1/videos/video-extend/{task_id} \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in Error codes
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "task_status_msg": "string", // Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
    "task_info": {
      "parent_video": { //Parameters information when the task is created
        "id": "string", //Video ID before the extension；globally unique
        "url": "string", //URL for generating images(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
        "duration": "string" //Original video duration, unit: s (seconds)
      },
      "external_task_id": "string" // Customer-defined task ID
    },
    "task_result": {
      "videos": [
        {
          "id": "string", // Generated video ID; globally unique, will be cleared after 30 days
          "url": "string", // URL for generating videos (To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
          "watermark_url": "string", // Watermarked video download URL, anti-leech format
          "duration": "string" //Total video duration, unit: s (seconds)
        }
      ]
    },
    "watermark_info": {
      "enabled": boolean
    },
    "final_unit_deduction": "string", // The deduction units of task
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, unit: ms
  }
}
Query Task (List)
GET
/v1/videos/video-extend
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
Number of items per page

Value range: [1, 500]

cURL

Copy

Collapse
curl --request GET \
  --url 'https://api-singapore.klingai.com/v1/videos/video-extend?pageNum=1&pageSize=30' \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in Error codes
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data": [
    {
      "task_id": "string", // Task ID, generated by the system
      "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
      "task_status_msg": "string", // Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
      "task_info": {
        "parent_video": { //Parameters information when the task is created
          "id": "string", //Video ID before the extension；globally unique
          "url": "string", //URL for generating images(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
          "duration": "string" //Original video duration, unit: s (seconds)
        },
        "external_task_id": "string" // Customer-defined task ID
      },
      "task_result": {
        "videos": [
          {
            "id": "string", // Generated video ID; globally unique, will be cleared after 30 days
            "url": "string", // URL for generating videos (To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
            "watermark_url": "


Lip-Sync
Identify Face
POST
/v1/videos/identify-face
Identify faces in the video for lip-sync processing.

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
video_id
string
Optional
The ID of the video generated by Kling AI

Used to specify the video and determine whether it can be used for lip-sync services.
This parameter and 'video_url' are mutually exclusive—only one can be filled, and neither can be left empty.
Only supports videos generated within the last 30 days with a duration of no more than 60 seconds.
video_url
string
Optional
The URL of the video

Used to specify the video and determine whether it can be used for lip-sync services.
This parameter and 'video_id' are mutually exclusive—only one can be filled, and neither can be left empty.
Supported video formats: .mp4/.mov, file size ≤100MB, duration 2s–60s, resolution 720p or 1080p, with both width and height between 512px–2160px. If validation fails, an error code will be returned.
The system checks video content—if issues are detected, an error code will be returned.
cURL

Copy

Collapse
curl --request POST \
  --url https://api-singapore.klingai.com/v1/videos/identify-face \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "video_url": "https://p1-kling.klingai.com/kcdn/cdn-kcdn112452/kling-qa-test/kling20260206mp4.mp4",
    "video_id": ""
  }'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, used to track requests and troubleshoot problems
  "data": {
    "session_id": "id", // Session ID
    "final_unit_deduction": "string", // The deduction units of task
    "face_data": [ //Face data list
      {
        "face_id": "string", // Face ID
        "face_image": "url", // Face image URL
        "start_time": 0, // Face appearance start time, unit: ms
        "end_time": 5200 //Face appearance end time, unit: ms
      }
    ]
  }
}
Create Task
POST
/v1/videos/advanced-lip-sync
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
session_id
string
Required
Session ID generated during the identify face API. It remains unchanged during the selection/editing process.

face_choose
array
Required
Specified Face for Lip-Sync

Includes Face ID, lip movement reference data, etc.
Currently only supports one person lip-sync.
▾
Hide child attributes
face_id
string
Required
Face ID

Returned by the facial recognition interface.
audio_id
string
Optional
Sound ID Generated via TTS API

Only supports audio generated within the last 30 days with a duration of no less than 2 seconds and no more than 60 seconds.
Either audio_id or sound_file must be provided (mutually exclusive; cannot be empty or both populated).
sound_file
string
Optional
Sound File

Supports Base64-encoded audio or accessible audio URL.
Accepted formats: .mp3/.wav/.m4a/.aac (max 5MB). Format mismatches or oversized files will return error codes.
Only supports audio with a duration of no less than 2 seconds and no more than 60 seconds.
Either audio_id or sound_file must be provided (mutually exclusive; cannot be empty or both populated).
The system will verify the audio content and return error codes if there are any problems.
sound_start_time
long
Required
Time point to start cropping sound

Based on the original sound start time, the start time is 0'0", units: ms
The sound before the starting point will be cropped, and the cropped sound must not be shorter than 2 seconds.
sound_end_time
long
Required
Time point to stop cropping sound

Based on the original sound start time, the start time is 0'0", units: ms
The sound after the end point will be cropped, and the cropped sound must not be shorter than 2 seconds.
The end point time shouldn't be later than the total duration of the original sound.
sound_insert_time
long
Required
The time for inserting cropped sound

Based on the original video start time, the start time is 0'0", units: ms
The time range for inserting sound should overlap with the face's lip-sync time interval for at least 2 seconds.
The start time for inserting sound must not be earlier than the start time of the video, and the end time for inserting sound must not be later than the end time of the video.
sound_volume
float
Optional
Default to 1
Volume Controls (higher values = louder)

Value range: [0, 2]
original_audio_volume
float
Optional
Default to 1
Original video volume (higher values = louder)

Value range: [0, 2]
No effect if source video is silent.
watermark_info
object
Optional
Whether to generate watermarked results simultaneously

Defined by the enabled parameter, format:
  "watermark_info": { "enabled": boolean } 
true: generate watermarked result, false: do not generate
Custom watermarks are not currently supported
external_task_id
string
Optional
Custom Task ID

User-defined task ID. It will not override the system-generated task ID, but supports querying tasks by this ID.
Please note that uniqueness must be ensured for each user.
callback_url
string
Optional
The callback notification address for the result of this task. If configured, the server will actively notify when the task status changes.

For specific message schema, see Callback Protocol
cURL

Copy

Collapse
curl --request POST \
  --url https://api-singapore.klingai.com/v1/videos/advanced-lip-sync \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "session_id": "850508686686064678",
    "face_choose": [
      {
        "face_id": "0",
        "sound_file": "https://p1-kling.klingai.com/kcdn/cdn-kcdn112452/kling-qa-test/go-to-world.mp3",
        "sound_insert_time": 1000,
        "sound_start_time": 0,
        "sound_end_time": 3000,
        "sound_volume": 2,
        "original_audio_volume": 2
      }
    ],
    "external_task_id": "",
    "callback_url": ""
  }'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, used to track requests and troubleshoot problems
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
Query Task (Single)
GET
/v1/videos/advanced-lip-sync/{id}
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
Task ID for Video Generation - Lip-Sync. Fill the value directly in the request path.

cURL

Copy

Collapse
curl --request GET \
  --url https://api-singapore.klingai.com/v1/videos/advanced-lip-sync/{task_id} \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, used to track requests and troubleshoot problems
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "task_status_msg": "string", // Task status message, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
    "task_info": { //Task creation parameters
      "parent_video": { //Original video information
        "id": "string", // Original video ID
        "url": "string", // Original video URL
        "duration": "string" //Original video duration, unit: s
      }
    },
    "task_result": { //Task result
      "videos": [ //Generated video list
        {
          "id": "string", // Generated video ID; globally unique
          "url": "string", // URL for generating videos (Please note that for security purposes, generated images/videos will be deleted after 30 days. Please save them promptly.)
          "watermark_url": "string", // Watermarked video download URL, anti-hotlinking format
          "duration": "string" //Total video duration, unit: s
        }
      ]
    },
    "watermark_info": {
      "enabled": boolean //Whether watermark is enabled
    },
    "final_unit_deduction": "string", // The deduction units of task
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, unit: ms
  }
}
Query Task (List)
GET
/v1/videos/advanced-lip-sync
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
Number of items per page

Value range: [1, 500]
cURL

Copy

Collapse
curl --request GET \
  --url 'https://api-singapore.klingai.com/v1/videos/advanced-lip-sync?pageNum=1&pageSize=30' \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, used to track requests and troubleshoot problems
  "data": [
    {
      "task_id": "string", // Task ID, generated by the system
      "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
      "task_status_msg": "string", // Task status message, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
      "task_info": { //Task creation parameters
        "parent_video": { //Original video information
          "id": "string", // Original video ID
          "url": "string", // Original video URL
          "duration": "string" //Original video duration, unit: s
        }
      },
      "task_result": { //Task result
        "videos": [ //Generated video list
          {
            "id": "string", // Generated video ID; globally unique
            "url": "string", // URL for generating videos (Please note that for security purposes, generated images/videos will be deleted after 30 days. Please save them promptly.)
            "watermark_url": "string", // Watermarked video download URL, anti-hotlinking format
            "duration": "string" //Total video duration, unit: s
          }
        ]
      },
      "watermark_info": {
        "enabled": boolean //Whether watermark is enabled
      },
      "final_unit_deduction": "string", // The deduction units of task
      "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
      "updated_at": 1722769557708 //Task update time, Unix timestamp, unit: ms
    }
  ]
}



Avatar
Create Task
POST
/v1/videos/avatar/image2video
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
image
string
Required
Avatar Reference Image

Support inputting image Base64 encoding or image URL (ensure accessibility).
Base64 Encoding Note:
Please note, if you use the Base64 method, make sure all image data parameters you pass are in Base64 encoding format. When using Base64, do NOT add any prefix like data:image/png;base64,. Only provide the Base64-encoded string.

Correct:

iVBORw0KGgoAAAANSUhEUgAAAAUA...
Incorrect:

data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA...
Supported image formats: .jpg / .jpeg / .png
Image file size ≤ 10MB, dimensions ≥ 300px, aspect ratio between 1:2.5 ~ 2.5:1
audio_id
string
Optional
Audio ID Generated via TTS API

Only supports audio generated within the last 30 days, duration between 2-300 seconds
Either audio_id or sound_file must be provided (mutually exclusive)
sound_file
string
Optional
Sound File

Supports Base64-encoded audio or accessible audio URL
Accepted formats: .mp3/.wav/.m4a/.aac, max 5MB, format mismatch or file too large will return error codes and other information
Duration must be between 2-300 seconds
Either audio_id or sound_file must be provided (mutually exclusive)
System will verify audio content and return error codes if there are problems
prompt
string
Optional
Positive text prompt

Can be used to define avatar actions, emotions, and camera movements
Cannot exceed 2500 characters
mode
string
Optional
Default to std
Video generation mode

Enum values：
std
pro
std: Standard Mode, cost-effective
pro: Professional Mode, higher quality video output
Different model versions and video modes have different support ranges. For details, see Capability Map

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
The callback notification address for the result of this task. If configured, the server will actively notify when the task status changes

For the specific message schema, see Callback Protocol
external_task_id
string
Optional
Customized Task ID

Will not overwrite system-generated task ID, but can be used for task queries
Must be unique within a single user account
cURL

Copy

Collapse
curl --request POST \
  --url https://api-singapore.klingai.com/v1/videos/avatar/image2video \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "image": "https://p1-kling.klingai.com/kcdn/cdn-kcdn112452/kling-qa-test/pink_boy.png",
    "sound_file": "https://p1-kling.klingai.com/kcdn/cdn-kcdn112452/kling-qa-test/go-to-world.mp3",
    "prompt": "While talking, excitedly shaking head, finally reaching out and making a fist, deciding to set off, hopping happily",
    "mode": "std",
    "external_task_id": "",
    "callback_url": ""
  }'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "task_info": { // Task creation parameters
      "external_task_id": "string" // Customer-defined task ID
    },
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit ms
    "updated_at": 1722769557708 // Task update time, Unix timestamp, unit ms
  }
}
Query Task (Single)
GET
/v1/videos/avatar/image2video/{id}
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
Task ID for avatar, fill the value directly in the request path

external_task_id
string
Optional
Customized Task ID for avatar. Fill the value directly in the request path. Choose either task_id or external_task_id for querying.

cURL

Copy

Collapse
curl --request GET \
  --url https://api-singapore.klingai.com/v1/videos/avatar/image2video/{task_id} \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "task_status_msg": "string", // Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
    "task_info": { // Task creation parameters
      "external_task_id": "string" // Customer-defined task ID
    },
    "task_result": {
      "videos": [
        {
          "id": "string", // Generated video ID; globally unique
          "url": "string", // URL for generating videos (To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
          "watermark_url": "string", // Watermarked video download URL, anti-leech format
          "duration": "string" // Total video duration, unit: s (seconds)
        }
      ]
    },
    "watermark_info": {
      "enabled": boolean
    },
    "final_unit_deduction": "string", // The deduction units of task
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 // Task update time, Unix timestamp, unit: ms
  }
}
Query Task (List)
GET
/v1/videos/avatar/image2video
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
Number of items per page

Value range: [1, 500]
cURL

Copy

Collapse
curl --request GET \
  --url 'https://api-singapore.klingai.com/v1/videos/avatar/image2video?pageNum=1&pageSize=30' \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in Error codes
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, to track requests and troubleshoot problems
  "data": [
    {
      "task_id": "string", // Task ID, generated by the system
      "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
      "task_status_msg": "string", // Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
      "task_info": { // Task creation parameters
        "external_task_id": "string" // Customer-defined task ID
      },
      "task_result": {
        "videos": [
          {


Text to Audio
Create Task
POST
/v1/audio/text-to-audio
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
prompt
string
Required
Text prompt

Cannot exceed 200 characters
duration
float
Required
Generated audio duration

Value range: 3.0s - 10.0s, supports one decimal place precision
external_task_id
string
Optional
Customized Task ID

Users can provide a customized task ID, which will not overwrite the system-generated task ID but can be used for task queries.
Please note that the customized task ID must be unique within a single user account.
callback_url
string
Optional
The callback notification address for the result of this task. If configured, the server will actively notify when the task status changes

The specific message schema of the notification can be found in Callback Protocol
cURL

Copy

Collapse
curl --request POST \
  --url https://api-singapore.klingai.com/v1/audio/text-to-audio \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "prompt": "Fireworks sound during Chinese New Year celebration",
    "duration": 3,
    "external_task_id": "",
    "callback_url": ""
  }'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, used to track requests and troubleshoot problems
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_info": { // Task creation parameters
      "external_task_id": "string" // Customer-defined task ID
    },
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 // Task update time, Unix timestamp, unit: ms
  }
}
Query Task (Single)
GET
/v1/audio/text-to-audio/{id}
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
The task ID for audio generation

Request path parameter, fill the value directly in the request path
You can choose to query by external_task_id or task_id
external_task_id
string
Optional
Customized Task ID for audio generation

The external_task_id filled in when creating the task. You can choose to query by external_task_id or task_id
cURL

Copy

Collapse
curl --request GET \
  --url https://api-singapore.klingai.com/v1/audio/text-to-audio/{task_id} \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, used to track requests and troubleshoot problems
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "task_status_msg": "string", // Task status message, displaying the failure reason when the task fails (such as triggering the platform's content risk control, etc.)
    "task_info": { // Task creation parameters
      "external_task_id": "string" // Customer-defined task ID
    },
    "task_result": {
      "audios": [
        {
          "id": "string", // Audio ID; globally unique
          "url_mp3": "string", // URL for generated audio in MP3 format (Please note that for information security, generated audios will be cleared after 30 days. Please save them promptly.)
          "url_wav": "string", // URL for generated audio in WAV format (Please note that for information security, generated audios will be cleared after 30 days. Please save them promptly.)
          "duration_mp3": "string", // Total duration of the audio in MP3 format, unit: s
          "duration_wav": "string" // Total duration of the audio in WAV format, unit: s
        }
      ]
    },
    "final_unit_deduction": "string", // The deduction units of task
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 // Task update time, Unix timestamp, unit: ms
  }
}
Query Task (List)
GET
/v1/audio/text-to-audio
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
Number of items per page

Value range: [1, 500]
cURL

Copy

Collapse
curl --request GET \
  --url 'https://api-singapore.klingai.com/v1/audio/text-to-audio?pageNum=1&pageSize=30' \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, used to track requests and troubleshoot problems
  "data": [
    {
      "task_id": "string", // Task ID, generated by the system
      "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
      "task_status_msg": "string", // Task status message, displaying the failure reason when the task fails (such as triggering the platform's content risk control, etc.)
      "task_info": { // Task creation parameters
        "external_task_id": "string" // Customer-defined task ID
      },
      "task_result": {
        "audios": [
          {
            "id": "string", // Audio ID; globally unique
            "url_mp3": "string", // URL for generated audio in MP3 format (Please note that for information security, generated audios will be cleared after 30 days. Please save them promptly.)
            "url_wav": "string", // URL for generated audio in WAV format (Please note that for information security, generated audios will be cleared after 30 days. Please save them promptly.)
            "duration_mp3": "string", // Total duration of the audio in MP3 format, unit: s
            "duration_wav": "string" // Total duration of the audio in WAV format, unit: s
          }
        ]


Video to Audio
Create Task
POST
/v1/audio/video-to-audio
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
video_id
string
Optional
The ID of the video generated by the Kling AI

Either the video_id parameter or the video_url parameter, cannot be empty or have a value at the same time.
Only supports videos generated within 30 days and with a duration between 3.0s and 20.0s.
video_url
string
Optional
Link for uploaded video

Either the video_id parameter or the video_url parameter, cannot be empty or have a value at the same time.
Only .mp4/.mov formats are supported. File size does not exceed 100MB. Video duration between 3.0s and 20.0s.
sound_effect_prompt
string
Optional
Sound effect prompt

Cannot exceed 200 characters
bgm_prompt
string
Optional
BGM prompt

Cannot exceed 200 characters
asmr_mode
boolean
Optional
Default to false
Enable ASMR mode; This mode enhances detailed sound effects and is suitable for highly immersive content scenarios

true means enabled, false means disabled (default)
external_task_id
string
Optional
Customized Task ID

Users can provide a customized task ID, which will not overwrite the system-generated task ID but can be used for task queries.
Please note that the customized task ID must be unique within a single user account.
callback_url
string
Optional
The callback notification address for the result of this task. If configured, the server will actively notify when the task status changes

The specific message schema of the notification can be found in Callback Protocol
cURL

Copy

Collapse
curl --request POST \
  --url https://api-singapore.klingai.com/v1/audio/video-to-audio \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "video_url": "https://p1-kling.klingai.com/kcdn/cdn-kcdn112452/kling-qa-test/20fps-7s.mov",
    "external_task_id": "",
    "callback_url": ""
  }'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_info": { // Task creation parameters
      "external_task_id": "string" // Customer-defined task ID
    },
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 // Task update time, Unix timestamp, unit: ms
  }
}
Query Task (Single)
GET
/v1/audio/video-to-audio/{id}
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
The task ID for audio generation

Request path parameter, fill the value directly in the request path
You can choose to query by external_task_id or task_id
external_task_id
string
Optional
Customized Task ID for audio generation

The external_task_id filled in when creating the task. You can choose to query by external_task_id or task_id
cURL

Copy

Collapse
curl --request GET \
  --url https://api-singapore.klingai.com/v1/audio/video-to-audio/{task_id} \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "task_status_msg": "string", // Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
    "task_info": { // Task creation parameters
      "external_task_id": "string", // Customer-defined task ID
      "parent_video": { // Original video information
        "id": "string", // Original video ID
        "url": "string", // Original video URL
        "duration": "string" // Original video duration, unit: s (seconds)
      }
    },
    "task_result": {
      "videos": [
        {
          "id": "string", // Generated video ID; globally unique
          "url": "string", // URL for generating videos (To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
          "duration": "string" // Total video duration, unit: s (seconds)
        }
      ],
      "audios": [
        {
          "id": "string", // Generated audio ID; globally unique, will be cleared after 30 days
          "url_mp3": "string", // URL for generating audio in MP3 format (To ensure information security, generated audio will be cleared after 30 days. Please make sure to save them promptly.)
          "url_wav": "string", // URL for generating audio in WAV format (To ensure information security, generated audio will be cleared after 30 days. Please make sure to save them promptly.)
          "duration_mp3": "string", // Total MP3 audio duration, unit: s (seconds)
          "duration_wav": "string" // Total WAV audio duration, unit: s (seconds)
        }
      ]
    },
    "final_unit_deduction": "string", // The deduction units of task
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 // Task update time, Unix timestamp, unit: ms
  }
}
Query Task (List)
GET
/v1/audio/video-to-audio
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
Number of items per page

Value range: [1, 500]
cURL

Copy

Collapse
curl --request GET \
  --url 'https://api-singapore.klingai.com/v1/audio/video-to-audio?pageNum=1&pageSize=30' \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in Error codes
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, to track requests and troubleshoot problems
  "data": [
    {
      "task_id": "string", // Task ID, generated by the system
      "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
      "task_status_msg": "string", // Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
      "task_info": { // Task creation parameters
        "external_task_id": "string", // Customer-defined task ID
        "parent_video": { // Original video information
          "id": "string", // Original video ID
          "url": "string", // Original video URL
          "duration": "string" // Original video duration, unit: s (seconds)
        }
      },
      "task_result": {
        "videos": [
          {
            "id": "string", // Generated video ID; globally unique
            "url": "string", // URL for generating videos (To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
            "duration": "string" // Total video duration, unit: s (seconds)
          }
        ],
        "audios": [
          {
            "id": "string", // Generated audio ID; globally unique, will be cleared after 30 days
            "url_mp3": "string", // URL for generating audio in MP3 format (To ensure information security, generated audio will be cleared after 30 days. Please make sure to save them promptly.)
            "url_wav": "string", // URL for generating audio in WAV format (To ensure information security, generated audio will be cleared after 30 days. Please make sure to save them promptly.)
            "duration_mp3": "string", // Total MP3 audio duration, unit: s (seconds)
            "duration_wav": "string" // Total WAV audio duration, unit: s (seconds)
          }
        ]
      },
      "final_unit_deduction": "string", // The deduction units of task
      "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
      "updated_at": 1722769557708 // Task update time, Unix timestamp, unit: ms
    }
  ]
}



TTS
Create Task
POST
/v1/audio/tts
Text-to-Speech synthesis API for generating audio from text.

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
text
string
Required
Text Content for Audio Synthesis

The maximum length of the text content is 1000 characters; content that is too long will return an error code and other information.
The system will validate the text content; if there are issues, it will return an error code and other information.
voice_id
string
Required
Voice ID

The system offers a variety of voice options to choose from. For specific voice effects, voice IDs, and corresponding voice languages, see Voice Guide. Voice previews do not support custom scripts.
Voice preview file naming convention: Voice Name#Voice ID#Voice Language
voice_language
string
Required
Default to zh
Voice Language

Enum values：
zh
en
The voice language corresponds to the Voice ID, as detailed above.
voice_speed
float
Optional
Default to 1.0
Speech Rate

Valid range: [0.8, 2.0], accurate to one decimal place; values outside this range will be automatically rounded.
cURL

Copy

Collapse
curl --request POST \
  --url https://api-singapore.klingai.com/v1/audio/tts \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "text": "Throughout my time in college, several memorable event left a significant impact on my life",
    "voice_id": "oversea_male1",
    "voice_language": "en",
    "voice_speed": 1
  }'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in Error codes
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_status": "string", // Task status, Enum values: submitted, processing, succeed, failed
    "task_status_msg": "string", // Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
    "task_result": {
      "audios": [
        {
          "id": "string", // Generated sound ID; globally unique, will be cleared after 30 days
          "url": "string", // URL for generating sounds，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.mp3(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
          "duration": "string" // Total audio duration, unit: s (seconds)
        }
      ]
    },
    "final_unit_deduction": "string", // The deduction units of task
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 // Task update time, Unix timestamp, unit: ms
  }
}


Custom Voice
Create Custom Voice
POST
/v1/general/custom-voices
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
voice_name
string
Required
Voice Name

The maximum length of text content is 20 characters
The voices that are no longer used after creation can be deleted through the API
voice_url
string
Optional
The URL of voice data file

Supports .mp3 / .wav audio file and .mp4 / .mov video file
The voice needs to be clean and free of noise, with only one type of human voice present, with a duration of no less than 5 seconds and no longer than 30 seconds
video_id
string
Optional
Generated video ID, which can provide audio materials by referencing historical works

Only videos that meet the following conditions can be used to customize voice:
The video is generated on V2.6 model and the value of sound parameter is on
The video is generated through Avatar API
The video is generated through Lip-Sync API
The voice needs to be clean and free of noise, with only one type of human voice present, with a duration of no less than 5 seconds and no longer than 30 seconds
callback_url
string
Optional
The callback notification address for the result of this task. If configured, the server will actively notify when the task status changes.

For specific message schema, see Callback Protocol
external_task_id
string
Optional
Customized Task ID

Will not overwrite system-generated task ID, but supports querying task by this ID
Please note that the customized task ID must be unique within a single user account.
cURL

Copy

Collapse
curl --request POST \
  --url https://api-singapore.klingai.com/v1/general/custom-voices \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "video_id": "",
    "voice_url": "https://p2-kling.klingai.com/kcdn/cdn-kcdn112452/kling-qa-test/out.mp3",
    "voice_name": "Custom Voice",
    "callback_url": ""
  }'
200

Copy

Collapse
{
  "code": 0, // Error Codes；Specific definitions can be found in Error codes
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_info": { // Task creation parameters
      "external_task_id": "string" // Customer-defined task ID
    },
    "task_status": "string", // Task status, Enum values：submitted、processing、succeed、failed
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit ms
    "updated_at": 1722769557708 // Task update time, Unix timestamp, unit ms
  }
}
Query Custom Voice (Single)
GET
/v1/general/custom-voices/{id}
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
Required
The task ID of the element creation task. Request path parameter, directly fill the value in the request path.

external_task_id
string
Optional
Customized Task ID for audio generation

The external_task_id filled in when creating the task. You can choose to query by external_task_id or task_id
When creating a task, you can choose to query by external_task_id or task_id.
cURL

Copy

Collapse
curl --request GET \
  --url 'https://api-singapore.klingai.com/v1/general/custom-voices/{id}' \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error codes；Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_status": "string", // Task status, Enum values：submitted、processing、succeed、failed
    "task_status_msg": "string", // Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
    "task_info": { // Task creation parameters
      "external_task_id": "string" // Customer-defined task ID
    },
    "task_result": {
      "voices": [
        {
          "voice_id": "string", // Generated voice ID; globally unique
          "voice_name": "string", // Generated voice name
          "trial_url": "string", // URL for generating videos
          "owned_by": "kling" // Voice source, kling is the official voice library, and others are the creator's ID
        }
      ]
    },
    "final_unit_deduction": "string", // The deduction units of task
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 // Task update time, Unix timestamp, unit: ms
  }
}
Query Custom Voice (List)
GET
/v1/general/custom-voices
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

Value range: [1, 1000]

cURL

Copy

Collapse
curl --request GET \
  --url 'https://api-singapore.klingai.com/v1/general/custom-voices?pageNum=1&pageSize=30' \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error codes；Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data": [
    {
      "task_id": "string", // Task ID, generated by the system
      "task_status": "string", // Task status, Enum values：submitted、processing、succeed、failed
      "task_status_msg": "string", // Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
      "task_info": { // Task creation parameters
        "external_task_id": "string" // Customer-defined task ID
      },
      "task_result": {
        "voices": [
          {
            "voice_id": "string", // Generated voice ID; globally unique
            "voice_name": "string", // Generated voice name
            "trial_url": "string", // URL for generating videos
            "owned_by": "kling" // Voice source, kling is the official voice library, and others are the creator's ID
          }
        ]
      }
      "final_unit_deduction": "string", // The deduction units of task
      "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
      "updated_at": 1722769557708, // Task update time, Unix timestamp, unit: ms
    }
  ]
}
Query Presets Voice (List)
GET
/v1/general/presets-voices
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

Value range: [1, 1000]

cURL

Copy

Collapse
curl --request GET \
  --url 'https://api-singapore.klingai.com/v1/general/presets-voices?pageNum=1&pageSize=30' \
  --header 'Authorization: Bearer <token>'
200

Copy

Collapse
{
  "code": 0, // Error codes；Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data": [
    {
      "task_id": "string", // Task ID, generated by the system
      "task_status": "string", // Task status, Enum values：submitted、processing、succeed、failed
      "task_status_msg": "string", // Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
      "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
      "updated_at": 1722769557708, // Task update time, Unix timestamp, unit: ms
      "task_result": {
        "voices": [
          {
            "voice_id": "string", // Official voice ID; globally unique
            "voice_name": "string", // Official voice name
            "trial_url": "string", // URL for official videos
            "owned_by": "kling" // Voice source, kling is the official voice library, and others are the creator's ID
          }
        ]
      }
    }
  ]
}
Delete Custom Voice
POST
/v1/general/delete-voices
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
voice_id
string
Required
The ID of the voice to be deleted, only supports deleting custom voices

cURL

Copy

Collapse
curl --request POST \
  --url https://api-singapore.klingai.com/v1/general/delete-voices \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "voice_id": "850087542757535834"
  }'
200

Copy

Collapse
{
  "code": 0, // Error codes；Specific definitions can be found in "Error Code"
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system
  "data": {
    "task_id": "string", // Task ID, generated by the system
    "task_status": "string" // Task status, Enum values：submitted、processing、succeed、failed
  }
}


Image Recognize
Image Recognize
POST
/v1/videos/image-recognize
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
image
string
Required
Image to be recognized

Support inputting image Base64 encoding or image URL (ensure accessibility).

Please note, if you use the Base64 method, make sure all image data parameters you pass are in Base64 encoding format. When submitting data, do not add any prefixes to the Base64-encoded string, such as data:image/png;base64,. The correct parameter format should be the Base64-encoded string itself. Please provide only the Base64-encoded string portion so that the system can correctly process and parse your data.

Supported image formats: .jpg / .jpeg / .png. The image file size cannot exceed 10MB, and the width and height dimensions of the image shall not be less than 300px, and the aspect ratio of the image should be between 1:2.5 ~ 2.5:1.

cURL

Copy

Collapse
curl --request POST \
  --url https://api-singapore.klingai.com/v1/videos/image-recognize \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "image": "https://p2-kling.klingai.com/kcdn/cdn-kcdn112452/kling-qa-test/multi-1.png"
  }'
200

Copy

Collapse
{
  "code": 0, // Error codes; Specific definitions can be found in Error codes
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data": {
    "final_unit_deduction": "string", //  The deduction units of task
    "task_result": {
      "images": [
        {
          "type": "object_seg", // Identification of subject recognition results
          "is_contain": true, // Has the subject been identified; Boolean value
          "url": "string" //URL for generating videos，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.png（请注意，为保障信息安全，生成的图片/视频会在30天后被清理，请及时转存）
        },
        {
          "type": "head_seg", // Identification of facial recognition results for individuals with hair included
          "is_contain": true, // Has the subject been identified; Boolean value
          "url": "string" //URL for generating videos，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.png（请注意，为保障信息安全，生成的图片/视频会在30天后被清理，请及时转存）
        },
        {
          "type": "face_seg", // Identification of facial recognition results for individuals without hair included
          "is_contain": true, // Has the subject been identified; Boolean value
          "url": "string" //URL for generating videos，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.png（请注意，为保障信息安全，生成的图片/视频会在30天后被清理，请及时转存）
        },
        {
          "type": "cloth_seg", // Identification of clothing recognition results
          "is_contain": true, // Has the subject been identified; Boolean value
          "url": "string" //URL for generating videos，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.png（请注意，为保障信息安全，生成的图片/视频会在30天后被清理，请及时转存）
        }
      ]
    },
    "final_unit_deduction": "string" // The deduction units of task
  }
}


Element
Create Element
POST
/v1/general/advanced-custom-elements
💡
The service related to creating entities has been upgraded to a brand new version. If you need to browse the old version, please proceed to:Kling AI (OLD VERSION) ELEMENTS API Specification

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
element_name
string
Required
Element Name

Must not exceed 20 characters.

element_description
string
Required
Element Description

Must not exceed 100 characters.

reference_type
string
Required
Reference Method

Enum values：
video_refer
image_refer
video_refer: Video Character Elements, at this time, the subject's appearance will be defined with reference to element_video_list.

image_refer: Multi-Image Elements, whose appearance will be defined with reference to the element_image_list.

The scope of availability differs between entities customized through videos and those customized through images. Please refer to the capability map and parameter specifications for details.

element_image_list
object
Optional
Default to None
The main reference image allows for the setting of the element and its details through multiple images.

Include front reference images and reference images from other angles or close-ups: at least one frontal reference image (frontal_image), and 1 to 3 additional reference images (image_url) that differ from the front.

Load with key:value format as follows:

"element_image_list": {
"frontal_image": "image_url_0", 
"refer_images": [{ "image_url": "image_url_1" }, ...] 
}
Supports inputting image Base64 encoding or image URL (ensure accessibility).

Supported image formats: .jpg / .jpeg / .png. Image file size cannot exceed 10MB, dimensions not less than 300px, aspect ratio between 1:2.5 ~ 2.5:1.

When reference_type is image_refer, this parameter is required.

element_video_list
object
Optional
Default to None
The element is referenced by the video, and its details can be set through the video.

Audio videos can be uploaded. If the audio video contains human voice, it will trigger voice customization (customization + inclusion in voice library + binding with the element).

Currently, only realistic-style humanoid figures can be customized through video.

Required when referencing videos; invalid when referencing images.

Structure: element_video_list: { refer_videos: [{ video_url: "video_url_1" }] }. Only .mp4/.mov formats. Duration 3s–8s, 1080P, aspect ratio 16:9 or 9:16. At most 1 video, size not exceeding 200MB. video_url must not be empty.

"element_video_list": {
"refer_videos": [{ "video_url": "video_url_1" }, ...] 
}
Video-customized elements are only supported for kling-video-o3 and later models.

element_voice_id
string
Optional
Default to None
The tone of element can be bound to existing tone colors in the tone library

When empty, the current entity is not bound to a tone color.

ID can be obtained through the voice-related API. See Voice Guide

Only the elements customized for video support binding with voice.

tag_list
array
Optional
Default to None
Configure tags for the subject, one subject can configure multiple tags.

Structure: tag_list: [{ tag_id: "o_101" }, { tag_id: "o_102" }, ...]. Tag ID and name: o_101 Hottest, o_102 Character, o_103 Animal, o_104 Item, o_105 Costume, o_106 Scene, o_107 Effect, o_108 Others.

"tag_list": [ { "tag_id": "o_101" }, { "tag_id": "o_102" } ]
Tag and tag_id correspondence:

tag_id	tag_name
o_101	Hottest
o_102	Character
o_103	Animal
o_104	Item
o_105	Costume
o_106	Scene
o_107	Effect
o_108	Others
callback_url
string
Optional
The callback notification address for the result of this task. If configured, the server will actively notify when the task status changes.

For the specific message schema, see Callback Protocol
external_task_id
string
Optional
Customized Task ID. Users can provide a customized task ID, which will not overwrite the system-generated task ID but can be used for task queries. Please note that the customized task ID must be unique within a single user account.

200

Copy

Collapse
{
  "code": 0, //Error codes; specific definitions see Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system, for tracking and troubleshooting
  "data": {
    "task_id": "string", //Task ID, generated by the system
    "task_info": { //Task creation parameters
      "external_task_id": "string" //Customer-defined task ID
    },
    "task_status": "string", //Task status: submitted, processing, succeed, failed
    "created_at": 1722769557708, //Task creation time, Unix timestamp, ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, ms
  }
}
Invocation examples
Create Multi-Image Elements
curl --location 'https://xxx/v1/general/advanced-custom-elements/' \
--header 'Authorization: Bearer xxx' \
--header 'Content-Type: application/json\' \
--data '{
    "element_name": "xxx",
    "element_description": "xxx",
    "reference_type": "image_refer",
    "element_image_list": {
      "frontal_image": "xxx",
      "refer_images": [
        {"image_url": "xxx"},
        {"image_url": "xxx"}
      ]
    },
    "element_voice_id": string,
    "callback_url": "xxx",
    "external_task_id": "",
     "tag_list": [
        {
            "tag_id": "xxx"
        }
    ]
  }'
Create Video Character Elements
curl --location 'https://xxx/v1/general/advanced-custom-elements/' \
--header 'Authorization: Bearer xxx' \
--header 'Content-Type: application/json\' \
--data '{
    "element_name": "xxx",
    "element_description": "xxx",
    "reference_type": "video_refer",
    "element_video_list": {
        "refer_videos": [
            {
                "video_url": "xxx"
            }
        ]
    },
    "element_voice_id": string,
    "callback_url": "xxx",
    "external_task_id": "",
    "tag_list": [
        {
            "tag_id": "xxx"
        }
    ]
}'
Query Custom Element (Single)
GET
/v1/general/advanced-custom-elements/{id}
💡
The service related to creating entities has been upgraded to a brand new version. If you need to browse the old version, please proceed to:Kling AI (OLD VERSION) ELEMENTS API Specification

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
Required
The task ID of the element creation task. Request path parameter, directly fill the value in the request path.

external_task_id
string
Optional
Customized Task ID for audio generation

The external_task_id filled in when creating the task. You can choose to query by external_task_id or task_id
When creating a task, you can choose to query by external_task_id or task_id.
200

Copy

Collapse
{
  "code": 0, //Error codes; specific definitions see Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system
  "data": {
    "task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status: submitted, processing, succeed, failed
    "task_status_msg": "string", //Task status message, failure reason when failed
    "task_info": { //Task creation parameters
      "external_task_id": "string" //Customer-defined task ID
    },
    "task_result": {
      "elements": [
        {
          "element_id": 0,
          "element_name": "string",
          "element_description": "string",
          "reference_type": "video_refer",
          "element_image_list": {},
          "element_video_list": {},
          "element_voice_info": {
            "voice_id": "string", //Custom voice ID; globally unique
            "voice_name": "string", //Custom voice name
            "trial_url": "string", //Trial audio download URL
            "owned_by": "kling" //Voice source, kling is official, number is creator ID
          },
          "tag_list": [],
          "owned_by": "kling", //Element source, kling is official element library
          "status": "succeed" //Element status: succeed when normal, deleted when removed
        }
      ]
    },
    "final_unit_deduction": "string", //Final unit deduction for the task
    "created_at": 1722769557708, //Task creation time, Unix timestamp, ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, ms
  }
}
Query Custom Element (List)
GET
/v1/general/advanced-custom-elements
💡
The service related to creating entities has been upgraded to a brand new version. If you need to browse the old version, please proceed to:Kling AI (OLD VERSION) ELEMENTS API Specification

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

200

Copy

Collapse
{
  "code": 0, //Error codes; specific definitions see Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system
  "data": [
    {
      "task_id": "string", //Task ID, generated by the system
      "task_status": "string", //Task status: submitted, processing, succeed, failed
      "task_status_msg": "string", //Task status message
      "task_info": { "external_task_id": "string" }, //Task creation parameters
      "task_result": {
        "elements": [
          {
            "element_id": 0,
            "element_name": "string",
            "element_description": "string",
            "reference_type": "video_refer",
            "element_image_list": {},
            "element_video_list": {},
            "element_voice_info": {},
            "tag_list": [],
            "owned_by": "kling", //Element source
            "status": "succeed" //Element status: succeed, deleted
          }
        ]
      },
      "final_unit_deduction": "string", //Final unit deduction
      "created_at": 1722769557708, //Task creation time, Unix timestamp, ms
      "updated_at": 1722769557708 //Task update time, Unix timestamp, ms
    }
  ]
}
Query Presets Element (List)
GET
/v1/general/advanced-presets-elements
💡
The service related to creating entities has been upgraded to a brand new version. If you need to browse the old version, please proceed to:Kling AI (OLD VERSION) ELEMENTS API Specification

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

200

Copy

Collapse
{
  "code": 0, //Error codes; specific definitions see Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system
  "data": [
    {
      "task_id": "string", //Task ID, generated by the system
      "task_status": "string", //Task status: submitted, processing, succeed, failed
      "task_status_msg": "string", //Task status message
      "task_info": { "external_task_id": "string" }, //Task creation parameters
      "task_result": {
        "elements": [
          {
            "element_id": 0,
            "element_name": "string",
            "element_description": "string",
            "reference_type": "video_refer",
            "element_image_list": {},
            "element_video_list": {},
            "element_voice_info": {},
            "tag_list": [],
            "owned_by": "kling", //Element source
            "status": "succeed" //Element status: succeed, deleted
          }
        ]
      },
      "final_unit_deduction": "string", //Final unit deduction
      "created_at": 1722769557708, //Task creation time, Unix timestamp, ms
      "updated_at": 1722769557708 //Task update time, Unix timestamp, ms
    }
  ]
}
Delete Custom Element
POST
/v1/general/delete-elements
💡
The services related to the delete custom element have been directly upgraded, eliminating the need to browse other documents

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
element_id
string
Required
The ID of the element to be deleted; only supports deleting custom elements.

200

Copy

Collapse
{
  "code": 0, //Error codes; specific definitions see Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system
  "data": {
    "task_id": "string", //Task ID, generated by the system
    "task_status": "string" //Task status: submitted, processing, succeed, failed
  }
}


Account Information Inquiry
Query Resource Package List and Remaining Quantity under the Account
GET
/account/costs
Note: This API is free to call and allows you to query the list and balance of resource packages under your account. Please note to control the request rate (QPS<=1)

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
start_time
int
Required
Query start time, Unix timestamp, unit: ms

end_time
int
Required
Query end time, Unix timestamp, unit: ms

resource_pack_name
string
Optional
Resource package name, used to precisely specify a resource package to query

cURL
Python

Copy

Collapse
curl --request GET \
  --url 'https://api-singapore.klingai.com/account/costs?start_time=1726124664368&end_time=1727366400000' \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json'
200

Copy

Collapse
{
  "code": 0, // Error codes; specific definitions see Error codes
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, for tracking and troubleshooting
  "data": {
    "code": 0, // Error codes; specific definitions see Error codes
    "msg": "string", // Error information
    "resource_pack_subscribe_infos": [ // Resource package list
      {
        "resource_pack_name": "Video Generation - 10,000 entries", // Resource package name
        "resource_pack_id": "509f3fd3d4ab4a3f9eec5db27aa44f27", // Resource package ID
        "resource_pack_type": "decreasing_total", // Resource package type; "decreasing_total" = decreasing total, "constant_period" = constant periodicity
        "total_quantity": 200.0, // Total quantity
        "remaining_quantity": 118.0, // Remaining quantity (Please note: remaining quantity statistics have a 12h delay)
        "purchase_time": 1726124664368, // Purchase time, Unix timestamp in ms
        "effective_time": 1726124664368, // Effective time, Unix timestamp in ms
        "invalid_time": 1727366400000, // Expiration time, Unix timestamp in ms
        "status": "expired" // Resource package status: "toBeOnline" = Pending effectiveness, "online" = In effect, "expired" = Expired, "runOut" = Used up
      }
    ]
  }
}


