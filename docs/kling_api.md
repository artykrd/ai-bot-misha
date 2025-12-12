Overview
What is Kling AI?

Kling AI, the new generation of AI creative productivity tools, is based on the image generation @Kolors and video generation @Kling technology independently developed by Kuaishou’s Large Model Algorithm Team, providing a wealth of AI images, AI videos, and related controllable editing capabilities.

    For creators (individuals/enterprises), it provides an online creation platform and tools on the web and mobile devices.
    For developers (individuals/enterprises), it offers API solutions.

Get access to 「Kling AI」

[1] For Users (Individuals/ Enterprises)

    Web: Kling AI｜Next-generation AI Creative Studio
    App：Coming soon…

[2] For Developers (Individuals/ Enterprises)

    App：Coming soon…

User Guide

[1] Prompt Guide：Kling AI Best Practices


General Information
API Domain

1
https://api-singapore.klingai.com

API Authentication

    Step-1：Obtain AccessKey + SecretKey
    Step-2：Every time you request the API, you need to generate an API Token according to the Fixed Encryption Method, Authorization = Bearer <API Token> in Requset Header
        Encryption Method：Follow JWT（Json Web Token, RFC 7519）standard
        JWT consists of three parts：Header、Payload、Signature

python
java
Copy
Collapse

1
2
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
16
17
18
19
20
21
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
        "nbf": int(time.time()) - 5 # The time when it starts to take effect, in this example, represents the current time minus 5s
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
200	0	Request	-	-
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

1
2
3
4
5
{
	"code": 1303,
	"message": "parallel task over resource pack limit",
	"request_id": "9984d27b-a408-4073-ae28-17ca6a13622d" //uuid
}

Recommended Approach

Since this error is triggered by system load (not by parameter issues), it is recommended to:

    Backoff Retry Strategy: Use an exponential backoff algorithm to delay retries (recommended initial delay ≥ 1 second).
    Queue Management: Control the submission rate through a task queue and dynamically adapt to available concurrency.


Video Generation
Model	kling-v1	kling-v1-5	kling-v1-6 Image2Video	kling-v1-6 Text2Video	kling-v2 Master
Mode	STD	PRO	STD	PRO	STD	PRO	STD	PRO	-
Resolution	720p	720p	720p	1080p	720p	1080p	720p	1080p	720p
Frame Rate	30fps	30fps	30fps	30fps	30fps	30fps	24fps	24fps	24fps


Model	kling-v2-1 Image2Video	kling-v2-1 Master	kling-v2-5 Image to Video	kling-v2-5 Text to Video
Mode	STD	PRO	-	PRO	PRO
Resolution	720p	1080p	1080p	1080p	1080p
Frame Rate	24fps	24fps	24fps	24fps	24fps


kling-v1	std 5s	std 10s	pro 5s	pro 10s
text to video	video generation	✅	✅	✅	✅
camera control	✅	-	-	-
image to video	video generation	✅	✅	✅	✅
start/end frame	✅	-	✅	-
motion brush	✅	-	✅	-
others	-	-	-	-
video extension
(Not supported negative_prompt and cfg_scale)	✅	✅	✅	✅
video effects
Dual-character: Hug, Kiss, heart_gesture	✅	✅	✅	✅
others	-	-	-	-


kling-v1-5	std 5s	std 10s	pro 5s	pro 10s
text to video	all	-	-	-	-
image to video	video generation	✅	✅	✅	✅
start/end frame	-	-	✅	✅
end frame	-	-	✅	✅
motion brush	-	-	✅	-
camera control
（simple only）	-	-	✅	-
others	-	-	-	-
video extension	✅	✅	✅	✅
video effects
Dual-character: Hug, Kiss, heart_gesture	✅	✅	✅	✅
others	-	-	-	-


kling-v1-6	std 5s	std 10s	pro 5s	pro 10s
text to video	video generation	✅	✅	✅	✅
others	-	-	-	-
image to video	video generation	✅	✅	✅	✅
start/end frame	-	-	✅	✅
end frame	-	-	✅	✅
others	-	-	-	-
multi-image2video	✅	✅	✅	✅
multi-elements	✅	✅	✅	✅
video extension	✅	✅	✅	✅
video effects
Dual-character: Hug, Kiss, heart_gesture	✅	✅	✅	✅


kling-v2-master	5s	10s
text to video	video generation	✅	✅
others	-	-
image to video	video generation	✅	✅
others	-	-
others	-	-


kling-v2-1	std 5s	std 10s	pro 5s	pro10s
text to video	all	-	-	-	-
image to video	video generation	✅	✅	✅	✅
start/end frame	-	-	✅	✅
others	-	-	-	-
other	-	-	-	-


kling-v2-1-master	5s	10s
text to video	video generation	✅	✅
others	-	-
image to video	video generation	✅	✅
others	-	-
other	-	-


kling-v2-5-turbo	std 5s	std 10s	pro 5s	pro 10s
text to video	video generation	✅	✅	✅	✅
others	-	-	-	-
image to video	video generation	✅	✅	✅	✅
start/end frame	-	-	✅	✅
others	-	-	-	-
others	-	-	-	-


no related of model	support or not	description
lip sync	✅	Can be combined with text or audio to drive the mouth shape of characters in the video
video to audio	✅	Supports adding audio to all videos generated by Kling models and user-uploaded videos
text to audio	-	Supports generating audio by text prompts
others	-	-
Image Generation
kling-v1	1:1	16:9	4:3	3:2	2:3	3:4	9:16	21:9
text to image	✅	✅	✅	✅	✅	✅	✅	-
image to image	entire image	✅	✅	✅	✅	✅	✅	✅	-
others	-	-	-	-	-	-	-	-


kling-v1-5	1:1	16:9	4:3	3:2	2:3	3:4	9:16	21:9
text to image	✅	✅	✅	✅	✅	✅	✅	✅
image to image	subject	✅	✅	✅	✅	✅	✅	✅	✅
face	✅	✅	✅	✅	✅	✅	✅	✅
others	-	-	-	-	-	-	-	-


kling-v2	1:1	16:9	4:3	3:2	2:3	3:4	9:16	21:9
text to image	✅	✅	✅	✅	✅	✅	✅	✅
image to image	multi-image to image	✅	✅	✅	✅	✅	✅	✅	✅
restyle	✅ (The resolution of the generated image is the same as that of the input image, and it does not support setting the resolution separately)
others	-	-	-	-	-	-	-	-


kling-v2-new	1:1	16:9	4:3	3:2	2:3	3:4	9:16	21:9
text to image	-	-	-	-	-	-	-	-
image to image	restyle	✅(The resolution of the generated image is the same as that of the input image, and it does not support setting the resolution separately)
others	-	-	-	-	-	-	-	-


kling-v2-1	1:1	16:9	4:3	3:2	2:3	3:4	9:16	21:9
text to image	✅	✅	✅	✅	✅	✅	✅	✅
image to image	multi-image to image	✅	✅	✅	✅	✅	✅	✅	✅
others	-	-	-	-	-	-	-	-


no related of model	support or not	description
image expansion	✅	Supports expand content based on existing images
others	-	


Model	kling-v1	kling-v1-5	kling-2
Feature	Text to Image	Image to Image	Text to Image	Image to Image	Text to Image	Image to Image
Resolution	1K	1K	1K	1K	1K/2K	1K


Video Generation - Text to Video
Create Task
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/text2video	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
💡

Please note that in order to maintain naming consistency, the original model field has been changed to model_name, so in the future, please use this field to specify the version of the model that needs to be called.

    At the same time, we keep the behavior forward-compatible, if you continue to use the original model field, it will not have any impact on the interface call, there will not be any exception, which is equivalent to the default behavior when model_name is empty (i.e., call the V1 model).


Field	Type	Required Field	Default	Description
model_name	string	Optional	kling-v1	Model Name
Enum values：kling-v1, kling-v1-6, kling-v2-master, kling-v2-1-master, kling-v2-5-turbo
prompt	string	Required	None	

Positive text prompt

    Cannot exceed 2500 characters

negative_prompt	string	Optional	Null	

Negative text prompt

    Cannot exceed 2500 characters

cfg_scale	float	Optional	0.5	

Flexibility in video generation; The higher the value, the lower the model’s degree of flexibility, and the stronger the relevance to the user’s prompt.

    Value range: [0, 1]

Kling-v2.x model does not support the this parameters
mode	string	Optional	std	

Video generation mode

    Enum values: std, pro
    std: Standard Mode, which is cost-effective
    pro: Professional Mode, generates videos use longer duration but higher quality video output

camera_control	object	Optional	Null	

Terms of controlling camera movement ( If not specified, the model will intelligently match based on the input text/images)
The support range for different model versions and video modes varies. For more details, please refer to the current document's "3-0 Capability Map"

camera_control

    type

	string	Optional	None	

Predefined camera movements type

    Enum values: “simple”, “down_back”, “forward_up”, “right_turn_forward”, “left_turn_forward”
    simple: Camera movement，Under this Type, you can choose one out of six options for camera movement in the “config”.
    down_back: Camera descends and moves backward ➡️ Pan down and zoom out, Under this Type, the config parameter must be set to “None”.
    forward_up: Camera moves forward and tilts up ➡️ Zoom in and pan up, the config parameter must be set to “None”.
    right_turn_forward: Rotate right and move forward ➡️ Rotate right and advance, the config parameter must be set to “None”.
    left_turn_forward: Rotate left and move forward ➡️ Rotate left and advance, the config parameter must be set to “None”.

camera_control

    config

	object	Optional	None	

Contains 6 Fields, used to specify the camera’s movement or change in different directions

    When the camera movement Type is set to simple, the Required Field must be filled out; when other Types are specified, it should be left blank.
    Choose one out of the following six parameters, meaning only one parameter should be non-zero, while the rest should be zero.

config

    horizontal

	float	Optional	None	Horizontal, controls the camera’s movement along the horizontal axis (translation along the x-axis).
Value range：[-10, 10], a negative Value indicates a translation to the left, while a positive Value indicates a translation to the right.

config

    vertical

	float	Optional	None	Vertical, controls the camera’s movement along the vertical axis (translation along the y-axis).
Value range：[-10, 10], a negative Value indicates a downward translation, while a positive Value indicates an upward translation.

config

    pan

	float	Optional	None	Pan, controls the camera’s rotation in the vertical plane (rotation around the x-axis).
Value range：[-10, 10]，a negative Value indicates a downward rotation around the x-axis, while a positive Value indicates an upward rotation around the x-axis.

config

    tilt

	float	Optional	None	Tilt, controls the camera’s rotation in the horizontal plane (rotation around the y-axis).
Value range：[-10, 10]，a negative Value indicates a rotation to the left around the y-axis, while a positive Value indicates a rotation to the right around the y-axis.

config

    roll

	float	Optional	None	Roll, controls the camera’s rolling amount (rotation around the z-axis).
Value range：[-10, 10]，a negative Value indicates a counterclockwise rotation around the z-axis, while a positive Value indicates a clockwise rotation around the z-axis.

config

    zoom

	float	Optional	None	Zoom, controls the change in the camera’s focal length, affecting the proximity of the field of view.
Value range：[-10, 10], A negative Value indicates an increase in focal length, resulting in a narrower field of view, while a positive Value indicates a decrease in focal length, resulting in a wider field of view.
aspect_ratio	string	Optional	16:9	The aspect ratio of the generated video frame (width:height)
Enum values：16:9, 9:16, 1:1
duration	string	Optional	5	Video Length, unit: s (seconds)
Enum values: 5，10
callback_url	string	Optional	None	The callback notification address for the result of this task. If configured, the server will actively notify when the task status changes
The specific message schema of the notification can be found in “Callback Protocol”
external_task_id	string	Optional	None	

Customized Task ID

    Users can provide a customized task ID, which will not overwrite the system-generated task ID but can be used for task queries.
    Please note that the customized task ID must be unique within a single user account.

Response Body
JSON
Copy
Collapse

{
  "code": 0, //Error codes；Specific definitions can be found in "Error Code"
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "task_info":{ //Task creation parameters
    	"external_task_id": "string" //Customer-defined task ID
    },
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, unit ms
  }
}

Query Task (Single)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/text2video/{id}	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Path Parameters
Field	Type	Required Field	Default	Description
task_id	string	Optional	None	Task ID for Text to Video
Request Path Parameters，directly fill the Value in the request path
When creating a task, you can choose to query by external_task_id or task_id.
external_task_id	string	Optional	None	Customized Task ID for Text-to-Video
Request Path Parameters，directly fill the Value in the request path
When creating a task, you can choose to query by external_task_id or task_id.
Request Body

None
Response Body
JSON
Copy
Collapse

{
  "code": 0, //Error codes；Specific definitions can be found in "Error Code"
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by thTask ID, generated by the system is used to track requests and troubleshoot problems
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
    "task_info":{ //Task creation parameters
    	"external_task_id": "string" //Customer-defined task ID
    },
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708, //Task update time, Unix timestamp, unit: ms
    "task_result":{
      "videos":[
        {
        	"id": "string", //Generated video ID; globally unique
      		"url": "string", //URL for generating videos，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.mp4(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
      		"duration": "string" //Total video duration, unit: s (seconds)
        }
      ]
    }
  }
}

Query Task (List)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/text2video	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Query Parameters

/v1/videos/text2video?pageNum=1&pageSize=30
Field	Type	Required Field	Default	Description
pageNum	int	Optional	1	Page number
Value range：[1,1000]
pageSize	int	Optional	30	Data volume per page
Value range：[1,500]
Request Body

None
Response Body
JSON
Copy
Collapse

{
  "code": 0, //Error codes；Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system,Task ID, generated by the systemgenerated by the systemto track requests and troubleshoot problems
  "data":[
    {
      "task_id": "string", //Task ID, generated by the system
      "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
      "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
      "task_info":{ //Task creation parameters
        "external_task_id": "string" //Customer-defined task ID
      },
      "created_at": 1722769557708, //Task creation time, Unix timestamp, unit: ms
      "updated_at": 1722769557708, //Task update time, Unix timestamp, unit: ms
      "task_result":{
        "videos":[
          {
            "id": "string", //Generated video ID; globally unique
            "url": "string", //URL for generating videos，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.mp4(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
            "duration": "string" //Total video duration, unit: s (seconds)
          }
        ]
      }
    }
  ]
}



Video Generation - Image to Video
Create Task
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/image2video	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
💡

Please note that in order to maintain naming consistency, the original model field has been changed to model_name, so in the future, please use this field to specify the version of the model that needs to be called.

    At the same time, we keep the behavior forward-compatible, if you continue to use the original model field, it will not have any impact on the interface call, there will not be any exception, which is equivalent to the default behavior when model_name is empty (i.e., call the V1 model).

Bash
Copy
Collapse
curl --location --request POST 'https://api-singapore.klingai.com/v1/videos/image2video' \
--header 'Authorization: Bearer xxx' \
--header 'Content-Type: application/json' \
--data-raw '{
    "model_name": "kling-v1",
    "mode": "pro",
    "duration": "5",
    "image": "https://h2.inkwai.com/bs2/upload-ylab-stunt/se/ai_portal_queue_mmu_image_upscale_aiweb/3214b798-e1b4-4b00-b7af-72b5b0417420_raw_image_0.jpg",
    "prompt": "The astronaut stood up and walked away",
    "cfg_scale": 0.5,
    "static_mask": "https://h2.inkwai.com/bs2/upload-ylab-stunt/ai_portal/1732888177/cOLNrShrSO/static_mask.png",
    "dynamic_masks": [
      {
        "mask": "https://h2.inkwai.com/bs2/upload-ylab-stunt/ai_portal/1732888130/WU8spl23dA/dynamic_mask_1.png",
        "trajectories": [
          {"x":279,"y":219},{"x":417,"y":65}
        ]
      }
    ]
}'

Field	Type	Required Field	Default	Description
model_name	string	Optional	kling-v1	

Model Name

    Enum values：kling-v1, kling-v1-5, kling-v1-6, kling-v2-master, kling-v2-1, kling-v2-1-master, kling-v2-5-turbo

image	string	Required	Null	

Reference Image

    Support inputting image Base64 encoding or image URL (ensure accessibility)

Please note, if you use the Base64 method, make sure all image data parameters you pass are in Base64 encoding format. When submitting data, do not add any prefixes to the Base64-encoded string, such as data:image/png;base64. The correct parameter format should be the Base64-encoded string itself.
Example: Correct Base64 encoded parameter:

1
iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Incorrect Base64 encoded parameter (includes the data: prefix):

1
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Please provide only the Base64-encoded string portion so that the system can correctly process and parse your data.

    Supported image formats include.jpg / .jpeg / .png
    The image file size cannot exceed 10MB, and the width and height dimensions of the image shall not be less than 300px, and the aspect ratio of the image should be between 1:2.5 ~ 2.5:1
    At least one parameter should be filled in between parameter image and parameter image_tail; cannot both be empty at the same time
    image+image_tail, dynamic_masks/static_mask, and camera_control. These three parameters cannot be used at the same time

The support range for different model versions and video modes varies. For more details, please refer to the current document's "3-0 Capability Map"
image_tail	string	Optional	Null	

Reference Image - End frame control

    Support inputting image Base64 encoding or image URL (ensure accessibility)

Please note, if you use the Base64 method, make sure all image data parameters you pass are in Base64 encoding format. When submitting data, do not add any prefixes to the Base64-encoded string, such as data:image/png;base64. The correct parameter format should be the Base64-encoded string itself.
Example: Correct Base64 encoded parameter:

1
iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Incorrect Base64 encoded parameter (includes the data: prefix):

1
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Please provide only the Base64-encoded string portion so that the system can correctly process and parse your data.

    Supported image formats include.jpg / .jpeg / .png
    The image file size cannot exceed 10MB, and the width and height dimensions of the image shall not be less than 300px
    At least one parameter should be filled in between parameter image and parameter image_tail; cannot both be empty at the same time
    image+image_tail, dynamic_masks/static_mask, and camera_control. These three parameters cannot be used at the same time

The support range for different model versions and video modes varies. For more details, please refer to the current document's "3-0 Capability Map"
prompt	string	Optional	None	

Positive text prompt

    Cannot exceed 2500 characters

negative_prompt	string	Optional	Null	

Negative text prompt

    Cannot exceed 2500 characters

cfg_scale	float	Optional	0.5	

Flexibility in video generation; The higher the value, the lower the model’s degree of flexibility, and the stronger the relevance to the user’s prompt.

    Value range: [0, 1]

Kling-v2.x model does not support the this parameters
mode	string	Optional	std	

Video generation mode

    Enum values: std, pro
    std: Standard Mode, which is cost-effective
    pro: Professional Mode, generates videos use longer duration but higher quality video output

The support range for different model versions and video modes varies. For more details, please refer to the current document's "3-0 Capability Map"
static_mask	string	Optional	null	

Static Brush Application Area (Mask image created by users using the motion brush)
The "Motion Brush" feature includes two types of brushes: Dynamic Brush (dynamic_masks) and Static Brush (static_mask).

    Support inputting image Base64 encoding or image URL (ensure the URL is accessible and follows the same format requirements as the image field).
    Supported image formats include.jpg / .jpeg / .png
    The aspect ratio of the mask image must match the input image (image field); otherwise, the task will fail (failed).
    The resolutions of the static_mask image and the dynamic_masks.mask image must be identical; otherwise, the task will fail (failed).

The support range for different model versions and video modes varies. For more details, please refer to the current document's "3-0 Capability Map"
Please refer to the code block above for a specific example.
dynamic_masks	array	Optional	null	

Dynamic Brush Configuration List
Multiple configurations can be set up (up to 6 groups). Each group includes a "mask area" (mask) and a sequence of "motion trajectories" (trajectories).\nUntil 20241129: The Dynamic Brush feature only supports the kling-v1 model in Standard Mode (std 5s) and Professional Mode (pro 5s).\nPlease refer to the code block above for a specific example.

dynamic_masks

    mask

	string	Optional	null	

Dynamic Brush Application Area (Mask image created by users using the motion brush)

    Support inputting image Base64 encoding or image URL (ensure the URL is accessible and follows the same format requirements as the image field).
    Supported image formats include.jpg / .jpeg / .png
    The aspect ratio of the mask image must match the input image (image field); otherwise, the task will fail (failed).
    The resolutions of the static_mask image and the dynamic_masks.mask image must be identical; otherwise, the task will fail (failed).

dynamic_masks

    trajectories

	array	Optional	null	

Motion Trajectory Coordinate Sequence

    To generate a 5-second video, the trajectory length must not exceed 77 coordinates, with the number of coordinates ranging from [2, 77].
    The coordinate system is based on the bottom-left corner of the image as the origin point.

Note-1: The more coordinates provided, the more precise the trajectory will be. For example, if only two trajectory points are provided, the motion will form a straight line connecting these two points.
Note-2: The trajectory direction follows the input order. The first coordinate serves as the starting point, and subsequent coordinates are connected sequentially to form the motion trajectory.

dynamic_masks

    trajectories
        x

	int	Optional	null	The horizontal coordinate (X-coordinate) of each trajectory point is defined within a 2D pixel coordinate system, where the bottom-left corner of the input image (image) serves as the origin point (0, 0).

dynamic_masks

    trajectories
        y

	int	Optional	null	The vertical coordinate (Y-coordinate) of each trajectory point is defined within a 2D pixel coordinate system, where the bottom-left corner of the input image (image) serves as the origin point (0, 0).
camera_control	object	Optional	Null	

Terms of controlling camera movement ( If not specified, the model will intelligently match based on the input text/images)
The support range for different model versions and video modes varies. For more details, please refer to the current document's "3-0 Capability Map"

camera_control

    type

	string	Optional	None	

Predefined camera movements type

    Enum values: “simple”, “down_back”, “forward_up”, “right_turn_forward”, “left_turn_forward”
    simple: Camera movement，Under this Type, you can choose one out of six options for camera movement in the “config”.
    down_back: Camera descends and moves backward ➡️ Pan down and zoom out, Under this Type, the config parameter must be set to “None”.
    forward_up: Camera moves forward and tilts up ➡️ Zoom in and pan up, the config parameter must be set to “None”.
    right_turn_forward: Rotate right and move forward ➡️ Rotate right and advance, the config parameter must be set to “None”.
    left_turn_forward: Rotate left and move forward ➡️ Rotate left and advance, the config parameter must be set to “None”.

camera_control

    config

	object	Optional	None	

Contains 6 Fields, used to specify the camera’s movement or change in different directions

    When the camera movement Type is set to simple, the Required Field must be filled out; when other Types are specified, it should be left blank.
    Choose one out of the following six parameters, meaning only one parameter should be non-zero, while the rest should be zero.

config

    horizontal

	float	Optional	None	

Horizontal, controls the camera’s movement along the horizontal axis (translation along the x-axis).

    Value range：[-10, 10], a negative Value indicates a translation to the left, while a positive Value indicates a translation to the right.

config

    vertical

	float	Optional	None	

Vertical, controls the camera’s movement along the vertical axis (translation along the y-axis).

    Value range：[-10, 10], a negative Value indicates a downward translation, while a positive Value indicates an upward translation.

config

    pan

	float	Optional	None	

Pan, controls the camera’s rotation in the vertical plane (rotation around the x-axis).

    Value range：[-10, 10]，a negative Value indicates a downward rotation around the x-axis, while a positive Value indicates an upward rotation around the x-axis.

config

    tilt

	float	Optional	None	

Tilt, controls the camera’s rotation in the horizontal plane (rotation around the y-axis).

    Value range：[-10, 10]，a negative Value indicates a rotation to the left around the y-axis, while a positive Value indicates a rotation to the right around the y-axis.

config

    roll

	float	Optional	None	

Roll, controls the camera’s rolling amount (rotation around the z-axis).

    Value range：[-10, 10]，a negative Value indicates a counterclockwise rotation around the z-axis, while a positive Value indicates a clockwise rotation around the z-axis.

config

    zoom

	float	Optional	None	

Zoom, controls the change in the camera’s focal length, affecting the proximity of the field of view.

    Value range：[-10, 10], A negative Value indicates an increase in focal length, resulting in a narrower field of view, while a positive Value indicates a decrease in focal length, resulting in a wider field of view.

duration	string	Optional	5	

Video Length, unit: s (seconds)

    Enum values：5，10

callback_url	string	Optional	None	

The callback notification address for the result of this task. If configured, the server will actively notify when the task status changes

    The specific message schema of the notification can be found in "Callback Protocol

external_task_id	string	Optional	None	

Customized Task ID

    Users can provide a customized task ID, which will not overwrite the system-generated task ID but can be used for task queries.
    Please note that the customized task ID must be unique within a single user account.

Response Body
JSON
Copy
Collapse
{
  "code": 0, //Error codes；Specific definitions can be found in "Error Code"
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "task_info":{ //Task creation parameters
    	"external_task_id": "string" //Customer-defined task ID
    },
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, unit ms
  }
}

Query Task (Single)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/image2video/{id}	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Path Parameters
Field	Type	Required Field	Default	Description
task_id	string	Optional	None	Task ID for Image to Video
Request Path Parameters，directly fill the Value in the request path
When creating a task, you can choose to query by external_task_id or task_id.
external_task_id	string	Optional	None	Customized Task ID for Image-to-Video
Request Path Parameters，directly fill the Value in the request path
When creating a task, you can choose to query by external_task_id or task_id.
Request Body

None
Response Body
JSON
Copy
Collapse
{
  "code": 0, //Error codes；Specific definitions can be found in "Error Code"
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by thTask ID, generated by the system is used to track requests and troubleshoot problems
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
    "task_info":{ //Task creation parameters
    	"external_task_id": "string" //Customer-defined task ID
    },
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708, //Task update time, Unix timestamp, unit: ms
    "task_result":{
      "videos":[
        {
        	"id": "string", //Generated video ID; globally unique
      		"url": "string", //URL for generating videos，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.mp4(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
      		"duration": "string" //Total video duration, unit: s (seconds)
        }
      ]
    }
  }
}

Query Task (List)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/image2video	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Query Parameters

/v1/videos/image2video?pageNum=1&pageSize=30
Field	Type	Required Field	Default	Description
pageNum	int	Optional	1	Page number
Value range：[1,1000]
pageSize	int	Optional	30	Data volume per page
Value range：[1,500]
Request Body

None
Response Body
JSON
Copy
Collapse
{
  "code": 0, //Error codes；Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system,Task ID, generated by the systemgenerated by the systemto track requests and troubleshoot problems
  "data":[
    {
      "task_id": "string", //Task ID, generated by the system
      "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
      "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
      "task_info":{ //Task creation parameters
    		"external_task_id": "string" //Customer-defined task ID
    	},
    	"created_at": 1722769557708, //Task creation time, Unix timestamp, unit: ms
    	"updated_at": 1722769557708, //Task update time, Unix timestamp, unit: ms
      "task_result":{
        "videos":[
          {
            "id": "string", //Generated video ID; globally unique
            "url": "string", //URL for generating videos，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.mp4(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
            "duration": "string" //Total video duration, unit: s (seconds)
          }
        ]
    	}
    }
  ]
}



(Elements) Multi-Image to Video
Create Task
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/multi-image2video	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
Field	Field	Field	Field	Field
model_name	string	Optional	kling-v1-6	

Model Name

    Enum values：kling-v1-6

image_list	array	Required	Null	

Reference Image List

    Support up to 4 images, load with key:value, details as follows:

"image_list":[
	{
  	"image":"image_url"
  },
	{
  	"image":"image_url"
  },
	{
  	"image":"image_url"
  },
	{
  	"image":"image_url"
  }
]

    Please directly upload the image with selected subject since there is no cropping logic on the API side.
    Support inputting image Base64 encoding or image URL (ensure accessibility)

Please note, if you use the Base64 method, make sure all image data parameters you pass are in Base64 encoding format. When submitting data, do not add any prefixes to the Base64-encoded string, such as data:image/png;base64. The correct parameter format should be the Base64-encoded string itself.
Example:
Correct Base64 encoded parameter:

1
iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Incorrect Base64 encoded parameter (includes the data: prefix):

1
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Please provide only the Base64-encoded string portion so that the system can correctly process and parse your data.

    Supported image formats include.jpg / .jpeg / .png
    The image file size cannot exceed 10MB, and the image resolution should not be less than 300*300px, and the aspect ratio of the image should be between 1:2.5 ~ 2.5:1

prompt	string	Required	None	

Positive text prompt

    Cannot exceed 2500 characters

negative_prompt	string	Optional	Null	

Negative text prompt

    Cannot exceed 2500 characters

mode	string	Optional	std	

Video generation mode

    Enum values: std, pro
    std: Standard Mode, which is cost-effective
    pro: Professional Mode, generates videos use longer duration but higher quality video output

The support range for different model versions and video modes varies. For more details, please refer to the current document's "3-0 Capability Map"
duration	string	Optional	5	

Video Length, unit: s (seconds)

    Enum values：5，10

Please note, requests that include the end frame (image_tail) and motion brush (dynamic_masks & static_mask) currently only support the generation of videos up to 5 seconds long.
aspect_ratio	string	Optional	16:9	

The aspect ratio of the generated video frame (width:height)

    Enum values：16:9, 9:16, 1:1

callback_url	string	Optional	null	

The callback notification address for the result of this task. If configured, the server will actively notify when the task status changes

    The specific message schema of the notification can be found in “Callback Protocol”

external_task_id	string	Optional	None	

Customized Task ID

    Users can provide a customized task ID, which will not overwrite the system-generated task ID but can be used for task queries.
    Please note that the customized task ID must be unique within a single user account.

Query Task (Single)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/multi-image2video/{id}	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Path Parameters
Field	Type	Required Field	Default	Description
task_id	string	Optional	None	Task ID for Multi-Image to Video
Request Path Parameters，directly fill the Value in the request path
When creating a task, you can choose to query by external_task_id or task_id.
external_task_id	string	Optional	None	Customized Task ID for Multi-Image-to-Video
Request Path Parameters，directly fill the Value in the request path
When creating a task, you can choose to query by external_task_id or task_id.
Request Body

None
Response Body
JSON
Copy
Collapse
{
  "code": 0, //Error codes；Specific definitions can be found in "Error Code"
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by thTask ID, generated by the system is used to track requests and troubleshoot problems
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
    "task_info":{ //Task creation parameters
    	"external_task_id": "string" //Customer-defined task ID
    },
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708, //Task update time, Unix timestamp, unit: ms
    "task_result":{
      "videos":[
        {
        	"id": "string", //Generated video ID; globally unique
      		"url": "string", //URL for generating videos，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.mp4(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
      		"duration": "string" //Total video duration, unit: s (seconds)
        }
      ]
    }
  }
}

Query Task (List)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/multi-image2video	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Query Parameters

/v1/videos/multi-image2video?pageNum=1&pageSize=30
Field	Type	Required Field	Default	Description
pageNum	int	Optional	1	Page number
Value range：[1,1000]
pageSize	int	Optional	30	Data volume per page
Value range：[1,500]
Request Body

None
Response Body
JSON
Copy
Collapse

{
  "code": 0, //Error codes；Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system,Task ID, generated by the systemgenerated by the systemto track requests and troubleshoot problems
  "data":[
    {
      "task_id": "string", //Task ID, generated by the system
      "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
      "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
      "task_info":{ //Task creation parameters
        "external_task_id": "string" //Customer-defined task ID
      },
      "created_at": 1722769557708, //Task creation time, Unix timestamp, unit: ms
      "updated_at": 1722769557708, //Task update time, Unix timestamp, unit: ms
      "task_result":{
        "videos":[
          {
            "id": "string", //Generated video ID; globally unique
            "url": "string", //URL for generating videos，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.mp4(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
            "duration": "string" //Total video duration, unit: s (seconds)
          }
        ]
      }
    }
  ]
}



Multi-Elements
Initialize Video for Editing
💡

Operation Guide: When using the Multi-elements feature, the original video must first be initialized. In particular, when replacing or removing elements within the existing video, the relevant elements need to be marked in the video beforehand.
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/multi-elements/init-selection	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
Field	Type	Required Field	Default	Description
video_id	string	Optional	Null	

The ID of the video generated by the Kling AI.

    Only videos generated within the last 30 days are supported.
    Only supports videos with a duration of ≥ 2 seconds and ≤ 5 seconds, or ≥ 7 seconds and ≤ 10 seconds.
    Related to the video_url parameter: both video_id and video_url cannot be empty at the same time, and cannot both have values at the same time.

video_url	string	Optional	Null	

Get link for uploaded video.

    Only .mp4/.mov formats are supported.
    Only supports videos with a duration of ≥ 2 seconds and ≤ 5 seconds, or ≥ 7 seconds and ≤ 10 seconds.
    Video resolution must be between 720px and 2160px (inclusive) in both width and height.
    Only supports videos with frame rates of 24, 30, or 60 fps.
    Related to the video_id parameter: both video_id and video_url cannot be empty at the same time, and cannot both have values at the same time.

响应体
JSON
Copy
Collapse
{
  "code": 0, // Error code; see error code definitions for details
  "message": "string", // Error message
  "request_id": "string", // Request ID, generated by the system for tracking and debugging
  "data": {
    "status": 0, // Recognition status code; non-zero indicates recognition failure
    "session_id": "id", // Session ID, generated during video initialization and remains unchanged during editing operations; valid for 24 hours

    // Response data for the video initialization stage
    "fps": 30.0, // Frames per second after video parsing; must be included when requesting preview for selection
    "original_duration": 1000, // Parsed video duration (in milliseconds); must be included when creating tasks
    "width": 720, // Parsed video width; currently not used
    "height": 1280, // Parsed video height; currently not used
    "total_frame": 300, // Total number of frames in the parsed video; must be included when creating tasks
    "normalized_video": "url" // URL of the initialized video
  }
}

Add Video Selection Area
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/multi-elements/add-selection	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
Field	Type	Required Field	Default	Description
session_id	string	Required	None	Session ID, Generated during the video initialization task. It remains unchanged during the selection/editing process.
frame_index	int	Required	None	

Frame Number

    A maximum of 10 frames can be marked. That is, up to 10 frames can be used to define selection areas in the video.
    Only supports marking 1 frame at a time.

points	object[]	Required	None	

Click Coordinates, represented by x and y

    Value range: [0, 1], expressed as percentages; [0, 1] represents the top-left corner of the frame.
    Multiple points can be marked at once; up to 10 points can be marked on a single frame.

Response Body
JSON
Copy
Collapse

{
  "code": 0, // Error code; refer to the error code documentation for details
  "message": "string", // Error message
  "request_id": "string", // Request ID, system-generated for tracking and debugging
  "data": {
    "status": 0, // Recognition status code; non-zero indicates failure
    "session_id": "id", // Session ID, generated during video initialization; remains unchanged throughout selection/editing, valid for 24 hours

    "res": {
      // Segmentation results for three operations: add selection, reduce selection, and remove all selections
      "frame_index": 0,
      "rle_mask_list": [{
        "object_id": 0,
        "rle_mask": {
          "size": [
            720,
            1280
          ],
          "counts": "string"
        },
        "png_mask": {
          "size": [
            720,
            1280
          ],
          "base64": "string"
        }
      }]
  	}
	}
}

Sample Code

Decoding Image Segmentation Result
TypeScript
Copy
Collapse

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
      M[y * R.w + x] = v === false ? 0 : 1 // 注意此处是 y * width + x，即横着排列
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
TypeScript
Copy
Collapse

// height 为视频的高度 width 为视频的宽度
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
        // 设置像素点颜色：红色，绿色，蓝色，透明度
        imageData.data[imageIndex] = 116 // 红色
        imageData.data[imageIndex + 1] = 255 // 绿色
        imageData.data[imageIndex + 2] = 82 // 蓝色
        imageData.data[imageIndex + 3] = 163 // 透明度
      }
    }
  }
  ctx.putImageData(imageData, 0, 0)
}

Delete Video Selection Area
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/multi-elements/delete-selection	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
Field	Type	Required Field	Default	Description
session_id	string	Required	None	Session ID, Generated during the video initialization task and remains unchanged throughout the selection/editing process.
frame_index	int	Required	None	Frame Number
points	object[]	Required	None	

Click Coordinates, represented by x and y

    Value range: [0, 1], expressed as percentages; [0, 1] represents the top-left corner of the frame.
    Multiple points can be provided at once.
    Coordinates must exactly match those used when adding the video selection area.

Response Body
JSON
Copy
Collapse

{
  "code": 0, // Error code; see error code definitions for details
  "message": "string", // Error message
  "request_id": "string", // Request ID, system-generated for tracking and debugging
  "data": {
    "status": 0, // Recognition status code; non-zero indicates failure
    "session_id": "id", // Session ID, generated during video initialization; remains unchanged during editing, valid for 24 hours

    "res": {
      // Segmentation result returned during the three phases: add selection, reduce selection, and remove all selections
      "frame_index": 0,
      "rle_mask_list": [{
        "object_id": 0,
        "rle_mask": {
          "size": [
            720,
            1280
          ],
          "counts": "string"
        },
        "png_mask": {
          "size": [
            720,
            1280
          ],
          "base64": "string"
        }
      }]
    }
  }
}

Clear Video Selection
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/multi-elements/clear-selection	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
Field	Type	Required Field	Default	Description
session_id	string	Required	None	Session ID, Generated during the video initialization task and remains unchanged throughout the selection/editing process.
Response Body
JSON
Copy
Collapse

{
  "code": 0, // Error code; refer to the error code documentation for details
  "message": "string", // Error message
  "request_id": "string", // Request ID, system-generated for tracking and troubleshooting
  "data": {
    "status": 0, // Recognition status code; non-zero indicates recognition failure
    "session_id": "id", // Session ID, generated during the video initialization task; remains unchanged during editing operations, valid for 24 hours
  }
}

Preview Video with Selected Areas
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/multi-elements/preview-selection	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
Field	Type	Required Field	Default	Description
session_id	string	必须	无	Session ID, Generated during the video initialization task and remains unchanged throughout the selection/editing process.
Response Body
JSON
Copy
Collapse
{
  "code": 0, // Error code; see error code definitions for details
  "message": "string", // Error message
  "request_id": "string", // Request ID, system-generated for tracking and troubleshooting
  "data": {
    "status": 0, // Recognition status code; non-zero indicates failure
    "session_id": "id", // Session ID, generated during video initialization; remains unchanged during editing, valid for 24 hours

    "res": {
      // Response data for the video preview display stage
      "video": "url", // Video containing the mask
      "video_cover": "url", // Cover image of the video containing the mask
      "tracking_output": "url" // Per-frame mask results in the segmentation output
    }
  }
}

Create Task
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/multi-elements/	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
Field	Type	Required Field	Default	Description
model_name	string	Optional	kling-v1-6	

Model Name

    Enum value: kling-v1-6

session_id	string	Required	None	

Session ID

    Generated during the video initialization task and remains unchanged during editing operations.

edit_mode	string	Required	None	

Operation Type

    Enum values: addition, swap, removal, where:
        addition: Add an element
        swap: Replace an element
        removal: Remove an element

image_list	array	Optional	Null	

Cropped Reference Images

    For adding video elements: This parameter is required; upload 1–2 images
    For editing (swapping) video elements: This parameter is required; upload 1 image only
    For deleting video elements: This parameter is not required
    Use key:value format as follows:

"image_list":[
	{
  	"image":"image_url"
  },
	{
  	"image":"image_url"
  }
]

    The API does not perform cropping, please upload images with subjects already cropped
    Supports image input as either Base64-encoded string or URL (ensure the URL is publicly accessible)

Note: If you choose to use Base64 for image input, please ensure that all image data parameters are strictly in Base64-encoded format. Do not include any prefix such as data:image/png;base64, in the submitted string. The correct format should be the raw Base64-encoded string only.
Examples:
Correct Base64-encoded parameter:

1
iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Wrong Base64-encoded parameter (includes data: prefix):

1
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Please provide only the Base64-encoded string itself to ensure the system can correctly process and parse your data.

    Supported image formats: .jpg / .jpeg / .png
    Image file size must not exceed 10MB. Image dimensions must be at least 300px in width and height

prompt	string	Required	None	

Positive Prompt

    Use the format <<<xxx>>> to explicitly refer to a specific video or image, such as <<<video_1>>> or <<<image_1>>>
    To ensure optimal results, the prompt must include references to the video and image(s) required for the editing, as shown in the “Recommended Prompt Templates” below
    Must not exceed 2,500 characters

💡

Recommended Prompt Templates Adding Elements ● Using the context of <<<video_1>>>, seamlessly add [x] from <<<image_1>>> Replacing Elements ● Swap [x] from <<<image_1>>> for [x] from <<<video_1>>> Removing Elements ● Delete [x] from <<<video_1>>> Note: The [x] represents placeholders where the user should fill in specific content.
negative_prompt	string	Optional	Null	

Negative Prompt

    Must not exceed 2,500 characters

mode	string	Optional	std	

Video Generation Mode

    Enum values: std, pro
        std: Standard mode, basic rendering, cost-effective
        pro: Professional mode, high-quality, enhanced rendering, better video output quality

duration	string	Optional	5	

Video Duration (in seconds)

    Enum values: 5，10

💡

Only 5-second and 10-second videos are supported. The duration of the input video must meet the following requirements based on the target output duration:

    To generate a 5-second video, the input video must be ≥ 2 seconds and ≤ 5 seconds
    To generate a 10-second video, the input video must be ≥ 7 seconds and ≤ 10 seconds

callback_url	string	Optional	Null	

Callback URL for Task Result Notification If configured, the server will actively send notifications when the task status changes.

    For the message schema, refer to the “Callback Protocol”

external_task_id	string	Optional	Null	

Custom Task ID

    A user-defined task ID; it will not overwrite the system-generated task ID, but can be used to query the task
    Please ensure uniqueness of the task ID within a single user account

Response Body
JSON
Copy
Collapse
{
  "code": 0, // Error code; see error code definitions for details
  "message": "string", // Error message
  "request_id": "string", // Request ID, system-generated for tracking and troubleshooting
  "data": {
    "task_id": "string", // Task ID, system-generated
    "task_status": "string", // Task status, enum values: submitted, processing, succeed, failed
    "session_id": "id", // Session ID, generated during video initialization; remains unchanged during editing
    "created_at": 1722769557708, // Task creation time, Unix timestamp in milliseconds
    "updated_at": 1722769557708 // Task update time, Unix timestamp in milliseconds
  }
}

Query Task (Single)

| Protocol | Request URL | Request Method | Request Format | Response Format | | https | /v1/videos/multi-elements/{id} | GET | application/json | application/json |
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
Field	Type	Required Field	Default	Description
task_id	string	Required	None	

Task ID for video extension

    Request Path Parameters，directly fill the Value in the request path

Request Body

None
Response Body
JSON
Copy
Collapse
{
	"code": 0, //Error codes；Specific definitions can be found in "Error Code"
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by thTask ID, generated by the system is used to track requests and troubleshoot problems
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
    "task_info":{ //Task creation parameters
    	"external_task_id": "string" //Customer-defined task ID
    },
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708, //Task update time, Unix timestamp, unit: ms
    "task_result":{
      "videos":[
        {
        	"id": "string", //Generated video ID; globally unique
          "session_id": "id", //Session ID, generated during the video initialization task; remains unchanged during editing operations, valid for 24 hours
          
      		"url": "string", //URL for generating videos，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.mp4(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
      		"duration": "string" //Total video duration, unit: s (seconds)
        }
      ]
    }
  }
}

Query Task (List)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/multi-elements/	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Path Parameters

/v1/videos/multi-image2video?pageNum=1&pageSize=30
Field	Type	Required Field	Default	Description
pageNum	int	Optional	1	

Page Number

    Value range: [1, 1000]

pageSize	int	Optional	30	

Data Quantity per Page

    Value range: [1, 500]

Request Body

None
Response Body
JSON
Copy
Collapse

{
	"code": 0, //Error codes；Specific definitions can be found in "Error Code"
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by thTask ID, generated by the system is used to track requests and troubleshoot problems
  "data":[{
  	"task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
    "task_info":{ //Task creation parameters
    	"external_task_id": "string" //Customer-defined task ID
    },
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708, //Task update time, Unix timestamp, unit: ms
    "task_result":{
      "videos":[
        {
        	"id": "string", //Generated video ID; globally unique
          "session_id": "id", //Session ID, generated during the video initialization task; remains unchanged during editing operations, valid for 24 hours
          
      		"url": "string", //URL for generating videos，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.mp4(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
      		"duration": "string" //Total video duration, unit: s (seconds)
        }
      ]
    }
  }]
}



Video Generation
Create Task

Note 1: Video extension refers to extending the duration of text-to-video/image-to-video results. Each extension can add 4 to 5 seconds, and the model and mode used cannot be selected; they must be the same as the source video.

Note 2: Videos that have been extended can be extended again, but the total video duration cannot exceed 3 minutes.
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/video-extend	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
Field	Type	Required Field	Default	Description
video_id	string	Required	None	

Video ID

    Supports video IDs generated by the text-to-video, the image-to-video and the video extension interface (it cannot exceed 3 minutes).

Please note that based on the current cleanup policy, videos will be cleared 30 days after generation, and extension will not be possible
prompt	string	Optional	None	Text Prompt
Cannot exceed 2500 characters.
negative_prompt	string	Optional	Null	Negative text prompt
Cannot exceed 2500 characters
cfg_scale	float	Optional	0.5	Flexibility in video generation; The higher the value, the lower the model’s degree of flexibility, and the stronger the relevance to the user’s prompt.
Value range: [0, 1]
callback_url	string	Optional	None	The callback notification address for the task results, if configured, will allow the server to proactively notify when the task status changes.
For specific notification message schema, please refer to the “Callback Protocol.”
Response Body
JSON
Copy
Collapse

{
  "code": 0, //Error codes; Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system,to track requests and troubleshoot problems
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, unit ms
  }
}

Query Task (Single)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/video-extend/{id}	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Path Parameters
Field	Type	Required Field	Default	Description
task_id	string	Required	None	Task ID for video extension
Request Path Parameters，directly fill the Value in the request path
Request Body

None
Response Body
JSON
Copy
Collapse
{
  "code": 0, //Error codes；Specific definitions can be found in Error codes
  "message": "string", //Error codes；Specific definitions can be found in Error codes
  "request_id": "string", //Request ID, generated by the system,to track requests and troubleshoot problems；globally unique
  "data":{
  	"task_id": "string", //Task ID, generated by the system；globally unique
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
    "task_info":{ //Parameters information when the task is created
       "parent_video": {
         	"id": "string", //Video ID before the extension；globally unique
      		"url": "string", //URL for generating images(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
      		"duration": "string" //Total duration of the video before continuation, in s
       },
    }, //Detailed information provided by the user during task creation.
    "task_result":{
      "videos":[  //The arrays are there to preserve extensibility in case they are to be supported in the future n
        {
          "id": "string", //Generated video ID; globally unique
          "url": "string", //URL for generating images
          "seed": "string", //The random seed used for this generated video
          "duration": "string" //Total video duration, unit: s (seconds)
        }
      ]
    }
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
    "updated_at": 1722769557708, //Task update time, Unix timestamp, unit ms
  }
}

Query Task (List)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/video-extend	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Path Parameters
Field	Type	Required Field	Default	Description
pageNum	int	Optional	1	Page number
Value range：[1,1000]
pageSize	int	Optional	30	Data volume per page
Value range：[1,500]
Request Body

None
Response Body
JSON
Copy
Collapse

{
  "code": 0, //Error codes；See 1.1 Error Codes for specific definitions
  "message": "string", //Error information；See 1.1 Error Codes for specific definitions
  "request_id": "string", //Request ID, generated by the system,to track requests and troubleshoot problems
  "data":[
    {
    	"task_id": "string", //Task ID, generated by the system；globally unique
      "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
      "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
      "task_info":{ //Task creation parameters
        "parent_video": {
         	"id": "string", //Generated video ID; globally unique
      		"url": "string", //URL for generating images(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
      		"duration": "string" //Total duration of the video before continuation, in s
        },
      }, //Detailed information provided by the user during task creation.
      "task_result":{
        "videos":[  //The arrays are there to preserve extensibility in case they are to be supported in the future n
          {
            "id": "string", //Generated video ID; globally unique
            "url": "string", //URL for generating images(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
            "seed": "string", //The random seed used for this generated video
            "duration": "string" //Total video duration, unit: s (seconds)
          }
        ]
    	}
      "created_at": 1722769557708, //Task creation time, Unix timestamp, in ms
      "updated_at": 1722769557708, //Task creation time, Unix timestamp, in ms
    }
  ]
}

Avatar
Create Task
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/avatar/image2video	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Body
Field	Type	Required Field	Default	Description
image	string	Required	Null	

Avatar Reference Image

    Support inputting image Base64 encoding or image URL (ensure accessibility).

Please note, if you use the Base64 method, make sure all image data parameters you pass are in Base64 encoding format. When submitting data, do not add any prefixes to the Base64-encoded string, such as data:image/png;base64. The correct parameter format should be the Base64-encoded string itself.
Example: Correct Base64 encoded parameter:

1
iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Incorrect Base64 encoded parameter (includes the data: prefix):

1
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Please provide only the Base64-encoded string portion so that the system can correctly process and parse your data.

    Supported image formats include.jpg / .jpeg / .png
    The image file size cannot exceed 10MB, and the width and height dimensions of the image shall not be less than 300px, and the aspect ratio of the image should be between 1:2.5 ~ 2.5:1.

audio_id	string	Optional	None	

Audio ID Generated via TTS API

    Only supports no less than 2-second and no more than 300-second generated within the last 30 days.
    Either audio_id or sound_file must be provided (mutually exclusive; cannot be empty or both populated).

sound_file	string	Optional	None	

Sound File

    Supports Base64-encoded audio or accessible audio URL.
    Accepted formats: .mp3/.wav/.m4a/.aac (max 5MB). Format mismatches or oversized files will return error codes.
    Only supports no less than 2-second and no more than 300-second sound.
    Either audio_id or sound_file must be provided (mutually exclusive; cannot be empty or both populated).
    The system will verify the video content and return error codes and other information if there are any problems.

prompt	string	Optional	None	

Positive text prompt

    Can be used to define avatar actions, emotions, and camera movements, etc.
    Cannot exceed 2500 characters

mode	string	Optional	std	

Video generation mode

    Enum values: std, pro
    std: Standard Mode, which is cost-effective pro: Professional Mode, generates videos use longer duration but higher quality video output

The support range for different model versions and video modes varies. For more details, please refer to the current document's "3-0 Capability Map"
callback_url	string	Optional	None	

The callback notification address for the result of this task. If configured, the server will actively notify when the task status changes

    The specific message schema of the notification can be found in “Callback Protocol”

external_task_id	string	Optional	None	

Customized Task ID

    Users can provide a customized task ID, which will not overwrite the system-generated task ID but can be used for task queries.
    Please note that the customized task ID must be unique within a single user account.

Response Body
JSON
Copy
Collapse

{
  "code": 0, //Error codes；Specific definitions can be found in "Error Code"
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "task_info":{ //Task creation parameters
    	"external_task_id": "string" //Customer-defined task ID
    },
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, unit ms
  }
}

Query Task (Single)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/avatar/image2video/{id}	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Path Parameters
Field	Type	Required Field	DefaultValue	Description
task_id	string	Required	None	

Task ID for avatar

    Request path parameters: directly fill in the value in the request path

Request Body

None
Response Body
JSON
Copy
Collapse
{
  "code": 0, //Error codes；Specific definitions can be found in "Error Code"
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by thTask ID, generated by the system is used to track requests and troubleshoot problems
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
    "task_info":{ //Task creation parameters
    	"external_task_id": "string" //Customer-defined task ID
    },
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708, //Task update time, Unix timestamp, unit: ms
    "task_result":{
      "videos":[
        {
        	"id": "string", //Generated video ID; globally unique
      		"url": "string", //URL for generating videos，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.mp4(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
      		"duration": "string" //Total video duration, unit: s (seconds)
        }
      ]
    }
  }
}

Query Task (List)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/avatar/image2video	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Query Parameters
Field	Type	Required Field	DefaultValue	Description
pageNum	int	Optional	1	Page number
Value range: [1,1000]
pageSize	int	Optional	30	Data volume per page
Value range: [1,500]
Request Body

None
Response Body
JSON
Copy
Collapse

{
  "code": 0, //Error codes；Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system,Task ID, generated by the systemgenerated by the systemto track requests and troubleshoot problems
  "data":[
    {
      "task_id": "string", //Task ID, generated by the system
      "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
      "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
      "task_info":{ //Task creation parameters
        "external_task_id": "string" //Customer-defined task ID
      },
      "created_at": 1722769557708, //Task creation time, Unix timestamp, unit: ms
      "updated_at": 1722769557708, //Task update time, Unix timestamp, unit: ms
      "task_result":{
        "videos":[
          {
            "id": "string", //Generated video ID; globally unique
            "url": "string", //URL for generating videos，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.mp4(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
            "duration": "string" //Total video duration, unit: s (seconds)
          }
        ]
      }
    }
  ]
}


Video Generation - Lip-Sync
Identify Face
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/Identify-face	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
Field	Type	Required Field	Default	Description
video_id	string	Optional	None	

The ID of the video generated by Kling AI

    Used to specify the video and determine whether it can be used for lip-sync services.
    Only supports videos generated within the last 30 days with a duration of no more than 60 seconds.
    This parameter and ‘video_url’ are mutually exclusive—only one can be filled, and neither can be left empty.

video_url	string	Optional	None	

The URL of the video

    Used to specify the video and determine whether it can be used for lip-sync services.
    Supported video formats: .mp4/.mov, file size ≤100MB, duration 2s–60s, resolution 720p or 1080p, with both width and height between 512px–2160px. If validation fails, an error code will be returned.
    The system checks video content—if issues are detected, an error code will be returned.
    This parameter and ‘video_id’ are mutually exclusive—only one can be filled, and neither can be left empty.

Response Body
JSON
Copy
Collapse

1
2
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
16
{
  "code": 0, //Error codes；Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data":{
   	"session_id": "id", //Session ID, generated during video initialization; remains unchanged throughout selection/editing, valid for 24 hours
    "face_data":[
      {
        "face_id":"string", // The face id of video；When the same person's face is separated by more than 1 second in the video, it will be considered as different IDs
        "face_image":"url", // A schematic diagram of a face captured from a video
        "start_time":0, // This face can be used as the starting time of lip-sync
        "end_time":5200	// This face can be used as the ending time of lip-sync; Note: This value has a millisecond level error and will be longer than the actual ending time
      }
    ]
  }
}

Create Task
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/advanced-lip-sync	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
Field	Type	Required Field	Default	Description
session_id	string	Required	Null	

Session ID

    Generated during the identify face API. It remains unchanged during the selection/editing process.

face_choose	string[]	Required	Null	

Specified Face for Lip-Sync

    Includes Face ID, lip movement reference data, etc.
    Currently only supports one person lip-sync.

face_choose

    face_id

	string	Required	Null	

Face ID

    Returned by the facial recognition interface.

face_choose

    audio_id

	string	Optional	None	

Sound ID Generated via TTS API

    Only supports no less than 2-second and no more than 60-second generated within the last 30 days
    Either audio_id or sound_file must be provided (mutually exclusive; cannot be empty or both populated).

face_choose

    sound_file

	string	Optional	None	

Sound File

    Supports Base64-encoded audio or accessible audio URL.
    Accepted formats: .mp3/.wav/.m4a (max 5MB). Format mismatches or oversized files will return error codes.
    Only supports no less than 2-second and no more than 60-second sound
    Either audio_id or sound_file must be provided (mutually exclusive; cannot be empty or both populated).
    The system will verify the video content and return error codes and other information if there are any problems.

face_choose

    sound_start_time

	long	Required	Null	

Time point to start cropping sound

    Based on the original sound start time, the start time is 0′0″, units: ms
    The sound before the starting point will be cropped, and the cropped sound must not be shorter than 2 seconds

face_choose

    sound_end_time

	long	Required	Null	

Time point to stop cropping sound

    Based on the original sound start time, the start time is 0′0″, units: ms
    The sound after the end point will be cropped, and the cropped sound must not be shorter than 2 seconds
    The end point time shouldn’t be later than the total duration of the original sound

face_choose

    sound_insert_time

	long	Required	Null	

The time for inserting cropped sound

    Based on the original video start time, the start time is 0′0″, units: ms
    The time range for inserting sound should overlap with the time interval for the face’s mouth shape for at least 2 seconds
    The start time for inserting sound must not be earlier than the start time of the video, and the end time for inserting sound must not be later than the end time of the video

face_choose

    sound_volume

	float	Optional	1	

Volume Controls (higher values = louder)

    Value range: [0, 2].

face_choose

    original_audio_volume

	float	Optional	1	

Original video volume: (higher values = louder)

    Value range: [0, 2] .
    No effect if source video is silent.

callback_url	string	Optional	None	

The callback notification address for the result of this task. If configured, the server will actively notify when the task status changes

    The specific message schema of the notification can be found in “Callback Protocol”.

Response Body
JSON
Copy
Collapse

{
  "code": 0, // Error codes；Specific definitions can be found in Error codes
  "message": "string", // Error information
  "request_id": "string", // Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data":{
  	"task_id": "string", // Task ID, generated by the system
    "task_status": "string", // Task status, Enum values：submitted、processing、succeed、failed
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, unit ms
  }
}

Query Task (Single)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/advanced-lip-sync/{id}	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Path Parameters
Field	Type	Required Field	Default	Description
task_id	string	Required	None	Task ID for lip-sync
Request path parameters: directly fill in the value in the request path
Request Body

None
Response Body
JSON
Copy
Collapse

{
  "code": 0, //Error codes；Specific definitions can be found in 1.1 Error codes
  "message": "string", //Error information；Specific definitions can be found in 1.1 Error codes
  "request_id": "string", //Request ID, generated by the system, is used to track requests and troubleshoot problems；Globally unique
  "data":{
      "task_id": "string", //Task ID, generated by the system；Globally unique
      "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
      "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
      "task_info":{ //Task creation parameters
        "parent_video": {
         	"id": "string", //Generated video ID; globally unique
      		"url": "string", //URL for generating videos (To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
      		"duration": "string" //Total video duration, unit: s (seconds)
        }
      }, //Detailed information provided by the user during task creation
      "task_result":{
        "videos":[  //The arrays are there to preserve extensibility in case they are to be supported in the future n
          {
            "id": "string", //Generated video ID; globally unique
            "url": "string", //URL for generating lip-sync videos (To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
            "duration": "string" //Total lip-sync video duration, unit: s (seconds)
          }
        ]
      },
      "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
      "updated_at": 1722769557708 //Task update time, Unix timestamp, unit ms
    }
}

Query Task (List)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/advanced-lip-sync	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Query Parameters
Field	Type	Required Field	Default	Description
pageNum	int	Optional	1	Page number
Value range：[1,1000]
pageSize	int	Optional	30	Data volume per page
Value range：[1,500]
Request Body

None
Response Body
JSON
Copy
Collapse

{
  "code": 0, //Error codes；Specific definitions can be found in 1.1 Error codes
  "message": "string", //Error information；Specific definitions can be found in 1.1 Error codes
  "request_id": "string", //Request ID, generated by the system, is used to track requests and troubleshoot problems；Globally unique
  "data":[
    {
      "task_id": "string", //Task ID, generated by the system；Globally unique
      "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
      "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
      "task_info":{ //Task creation parameters
        "parent_video": {
         	"id": "string", //Generated video ID; globally unique
      		"url": "string", //URL for generating videos (To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
      		"duration": "string" //Total video duration, unit: s (seconds)
        }
      }, //Detailed information provided by the user during task creation
      "task_result":{
        "videos":[  //The arrays are there to preserve extensibility in case they are to be supported in the future n
          {
            "id": "string", //Generated video ID; globally unique
            "url": "string", //URL for generating lip-sync videos (To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
            "duration": "string" //Total lip-sync video duration, unit: s (seconds)
          }
        ]
      },
      "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
      "updated_at": 1722769557708 //Task update time, Unix timestamp, unit ms
    }
  ]
}


Video Effects
Create Task
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/effects	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
General Request Body

Total of 152 video effects are available. For the detailed list and corresponding unit deductions, please refer to: Video Effects Center
Field	Type	Required Field	Default	Description
effect_scene	string	Required	None	

Scene Name

    Enum Values：firework_2026, glamour_photo_shoot, box_of_joy, first_toast_of_the_year, my_santa_pic, santa_gift, steampunk_christmas, snowglobe, christmas_photo_shoot, ornament_crash​, santa_express, instant_christmas, particle_santa_surround, coronation_of_frost, building_sweater, spark_in_the_snow, scarlet_and_snow, cozy_toon_wrap, bullet_time_lite, magic_cloak, balloon_parade, jumping_ginger_joy, bullet_time, c4d_cartoon_pro, pure_white_wings, black_wings, golden_wing, pink_pink_wings, venomous_spider, throne_of_king, luminous_elf, woodland_elf, japanese_anime_1, american_comics, guardian_spirit, swish_swish, snowboarding, witch_transform, vampire_transform, pumpkin_head_transform, demon_transform, mummy_transform, zombie_transform, cute_pumpkin_transform, cute_ghost_transform, knock_knock_halloween, halloween_escape, baseball, inner_voice, a_list_look, memory_alive, trampoline, trampoline_night, pucker_up, guess_what, feed_mooncake, rampage_ape, flyer, dishwasher, pet_chinese_opera, magic_fireball, gallery_ring, pet_moto_rider, muscle_pet, squeeze_scream, pet_delivery, running_man , disappear, mythic_style, steampunk, c4d_cartoon, 3d_cartoon_1, 3d_cartoon_2, eagle_snatch, hug_from_past, firework, media_interview, pet_lion, pet_chef, santa_gifts, santa_hug, girlfriend, boyfriend, heart_gesture_1, pet_wizard, smoke_smoke, thumbs_up, instant_kid, dollar_rain, cry_cry, building_collapse, gun_shot, mushroom, double_gun, pet_warrior, lightning_power, jesus_hug, shark_alert, long_hair, lie_flat, polar_bear_hug, brown_bear_hug , jazz_jazz, office_escape_plow, fly_fly, watermelon_bomb, pet_dance, boss_coming, wool_curly, pet_bee, marry_me, swing_swing, day_to_night, piggy_morph, wig_out, car_explosion, ski_ski, tiger_hug, siblings, construction_worker, let’s_ride, emoji, snatched, magic_broom, felt_felt, jumpdrop, celebration, splashsplash, surfsurf, fairy_wing, angel_wing, dark_wing, skateskate, plushcut, jelly_press, jelly_slice, jelly_squish, jelly_jiggle, pixelpixel, yearbook, instant_film, anime_figure, rocketrocket, bloombloom, dizzydizzy, fuzzyfuzzy, squish, expansion, hug, kiss, heart_gesture, fight

    For more parameters, please refer to Video Effects Center

input	object	Required	None	

Supports different task input structures.

    Depending on the scene, the fields passed in the structure vary, as detailed in the “Scene Request Body”.

callback_url	string	Optional	None	

The callback notification address for the result of this task. If configured, the server will actively notify when the task status changes

    The specific message schema of the notification can be found in “Callback Protocol”

external_task_id	string	Optional	None	

Customized Task ID

    Users can provide a customized task ID, which will not overwrite the system-generated task ID but can be used for task queries.
    Please note that the customized task ID must be unique within a single user account.

Scene Request Body

Single Image Effect: 148 types available, firework_2026, glamour_photo_shoot, box_of_joy, first_toast_of_the_year, my_santa_pic, santa_gift, steampunk_christmas, snowglobe, christmas_photo_shoot, ornament_crash​, santa_express, instant_christmas, particle_santa_surround, coronation_of_frost, building_sweater, spark_in_the_snow, scarlet_and_snow, cozy_toon_wrap, bullet_time_lite, magic_cloak, balloon_parade, jumping_ginger_joy, bullet_time, c4d_cartoon_pro, pure_white_wings, black_wings, golden_wing, pink_pink_wings, venomous_spider, throne_of_king, luminous_elf, woodland_elf, japanese_anime_1, american_comics, guardian_spirit, swish_swish, snowboarding, witch_transform, vampire_transform, pumpkin_head_transform, demon_transform, mummy_transform, zombie_transform, cute_pumpkin_transform, cute_ghost_transform, knock_knock_halloween, halloween_escape, baseball, inner_voice, a_list_look, memory_alive, trampoline, trampoline_night, pucker_up, guess_what, feed_mooncake, rampage_ape, flyer, dishwasher, pet_chinese_opera, magic_fireball, gallery_ring, pet_moto_rider, muscle_pet, squeeze_scream, pet_delivery, running_man, disappear, mythic_style, steampunk, c4d_cartoon, 3d_cartoon_1, 3d_cartoon_2, eagle_snatch, hug_from_past, firework, media_interview, pet_lion, pet_chef, santa_gifts, santa_hug, girlfriend, boyfriend, heart_gesture_1, pet_wizard, smoke_smoke, thumbs_up, instant_kid, dollar_rain, cry_cry, building_collapse, gun_shot, mushroom, double_gun, pet_warrior, lightning_power, jesus_hug, shark_alert, long_hair, lie_flat, polar_bear_hug, brown_bear_hug , jazz_jazz, office_escape_plow, fly_fly, watermelon_bomb, pet_dance, boss_coming, wool_curly, pet_bee, marry_me, swing_swing, day_to_night, piggy_morph, wig_out, car_explosion, ski_ski, tiger_hug, siblings, construction_worker, let’s_ride, emoji, snatched, magic_broom, felt_felt, jumpdrop, celebration, splashsplash, surfsurf, fairy_wing, angel_wing, dark_wing, skateskate, plushcut, jelly_press, jelly_slice, jelly_squish, jelly_jiggle, pixelpixel, yearbook, instant_film, anime_figure, rocketrocket, bloombloom, dizzydizzy, fuzzyfuzzy, squish, expansion
Field	Type	Required Field	Default	Description
image	string	Required	Null	

Reference Image

    Support inputting image Base64 encoding or image URL (ensure accessibility)

Please note, if you use the Base64 method, make sure all image data parameters you pass are in Base64 encoding format. When submitting data, do not add any prefixes to the Base64-encoded string, such as data:image/png;base64. The correct parameter format should be the Base64-encoded string itself.
Example: Correct Base64 encoded parameter:

1
iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Incorrect Base64 encoded parameter (includes the data: prefix):

1
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Please provide only the Base64-encoded string portion so that the system can correctly process and parse your data.

    Supported image formats include.jpg / .jpeg / .png
    The image file size cannot exceed 10MB, and the width and height dimensions of the image shall not be less than 300px, and the aspect ratio of the image should be between 1:2.5 ~ 2.5:1

duration	string	Required	Null	

Video Length, unit: s (seconds)

    Enum values：5

Single-Image Effects Request Example
JSON
Copy
Collapse
{
  "effect_scene": "pet_lion",
  "input":{
    "image":"https://p2-kling.klingai.com/bs2/upload-ylab-stunt/c54e463c95816d959602f1f2541c62b2.png?x-kcdn-pid=112452",
    "duration": "5"
  }
}

Dual-character Effects: 4 types available, hug, kiss, heart_gesture, fight
💡

Note:​​ The “fight” effect is only supported by the ​​kling-v1-6​​ model.
Field	Type	Required Field	Default	Description
model_name	string	Optional	kling-v1	

Model Name

    Enum Values：kling-v1, kling-v1-5, kling-v1-6
        fight: kling-v1-6 only
        hug, kiss, heart_gesture: supported in all available versions (kling-v1, kling-v1-5, kling-v1-6)
    model_name parameter is required only for dual-character special effects

mode	string	Optional	std	

Video generation mode

    Enum values: std, prox
    std: Standard Mode, which is cost-effective
    pro: Professional Mode, generates videos use longer duration but higher quality video output

image	Array[string]	Required	Null	

Reference Image Group
The length of the array must be 2. The first image uploaded will be positioned on the left side of the composite photo, and the second image uploaded will be positioned on the right side of the composite photo.
"https://p2-kling.klingai.com/bs2/upload-ylab-stunt/c54e463c95816d959602f1f2541c62b2.png?x-kcdn-pid=112452",
"https://p2-kling.klingai.com/bs2/upload-ylab-stunt/5eef15e03a70e1fa80732808a2f50f3f.png?x-kcdn-pid=112452"
The resulting effect of the composite photo is as follows:

    Support inputting image Base64 encoding or image URL (ensure accessibility)

Please note, if you use the Base64 method, make sure all image data parameters you pass are in Base64 encoding format. When submitting data, do not add any prefixes to the Base64-encoded string, such as data:image/png;base64. The correct parameter format should be the Base64-encoded string itself.
Example: Correct Base64 encoded parameter:

1
iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Incorrect Base64 encoded parameter (includes the data: prefix):

1
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Please provide only the Base64-encoded string portion so that the system can correctly process and parse your data.

    Supported image formats include.jpg / .jpeg / .png
    The image file size cannot exceed 10MB, and the width and height dimensions of the image shall not be less than 300px

The support range for different model versions and video modes varies. For more details, please refer to the current document's "3-0 Capability Map"
duration	string	Required	Null	

Video Length, unit: s (seconds)

    Enum values：5，10

Dual-character Effects Request Example
JSON
Copy
Collapse
{
  "effect_scene": "hug",
  "input":{
  	"model_name": "kling-v1-6",
    "mode": "std",
    "images":[
    	"https://p2-kling.klingai.com/bs2/upload-ylab-stunt/c54e463c95816d959602f1f2541c62b2.png?x-kcdn-pid=112452",
        "https://p2-kling.klingai.com/bs2/upload-ylab-stunt/5eef15e03a70e1fa80732808a2f50f3f.png?x-kcdn-pid=112452"
    ],
    "duration": "5"
  }
}

Response Body
JSON
Copy
Collapse
{
  "code": 0, //Error codes；Specific definitions can be found in "Error Code"
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "task_info":{ //Task creation parameters
    	"external_task_id": "string" //Customer-defined task ID
    },
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, unit ms
  }
}

Query Task (Single)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/effects/{id}	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Path Parameters
Field	Type	Required Field	Default	Description
task_id	string	Optional	None	Task ID for Video Effects
Request Path Parameters，directly fill the Value in the request path
When creating a task, you can choose to query by external_task_id or task_id.
task_id	string	Optional	None	Customized Task ID for Video Effects
Request Path Parameters，directly fill the Value in the request path
When creating a task, you can choose to query by external_task_id or task_id.
Request Body

None
Response Body
JSON
Copy
Collapse

{
  "code": 0, //Error codes；Specific definitions can be found in "Error Code"
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by thTask ID, generated by the system is used to track requests and troubleshoot problems
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
    "task_info":{ //Task creation parameters
    	"external_task_id": "string" //Customer-defined task ID
    },
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708, //Task update time, Unix timestamp, unit: ms
    "task_result":{
      "videos":[
        {
        	"id": "string", //Generated video ID; globally unique
      		"url": "string", //URL for generating videos，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.mp4(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
      		"duration": "string" //Total video duration, unit: s (seconds)
        }
      ]
    }
  }
}

Query Task (List)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/effects	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Path Parameters

/v1/videos/image2video?pageNum=1&pageSize=30
Field	Type	Required Field	Default	Description
pageNum	int	Optional	1	Page number
Value range：[1,1000]
pageSize	int	Optional	30	Data volume per page
Value range：[1,500]
Request Body

None
响应体
JSON
Copy
Collapse

{
  "code": 0, //Error codes；Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system,Task ID, generated by the systemgenerated by the systemto track requests and troubleshoot problems
  "data":[
    {
      "task_id": "string", //Task ID, generated by the system
      "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
      "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
      "task_info":{ //Task creation parameters
    		"external_task_id": "string" //Customer-defined task ID
    	},
    	"created_at": 1722769557708, //Task creation time, Unix timestamp, unit: ms
    	"updated_at": 1722769557708, //Task update time, Unix timestamp, unit: ms
      "task_result":{
        "videos":[
          {
            "id": "string", //Generated video ID; globally unique
            "url": "string", //URL for generating videos，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.mp4(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
            "duration": "string" //Total video duration, unit: s (seconds)
          }
        ]
    	}
    }
  ]
}


Text to Audio
Create Task
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/audio/text-to-audio	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
Field	Type	Required Field	Default	Description
prompt	string	Required	None	

text prompt

    Cannot exceed 200 characters

duration	float	Required	None	

generated audio duration

    Value range：3.0s - 10.0s, supports one decimal place precision

external_task_id	string	Optional	None	

Customized Task ID

    Users can provide a customized task ID, which will not overwrite the system-generated task ID but can be used for task queries.
    Please note that the customized task ID must be unique within a single user account.

callback_url	string	Optional	None	

The callback notification address for the result of this task. If configured, the server will actively notify when the task status changes

    The specific message schema of the notification can be found in “Callback Protocol”

Response Body
JSON
Copy
Collapse
{
    "code": 0, //Error Codes; Specific definitions can be found in Error codes
    "message": "string", //Error information
    "request_id": "string", //Request ID, generated by the system
    "data":{
        "task_id": "string", //Task ID, generated by the system
        "task_info":{ //Task creation parameters
            "external_task_id": "string" //Customer-defined task ID
        }, 
        "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
        "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
        "updated_at": 1722769557708 //Task update time, Unix timestamp, unit ms
    }
}

Query Task (Single)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/audio/text-to-audio/{id}	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Path Parameters
Field	Type	Required Field	Default	Description
task_id	string	Required	None	

The task ID for audio generation

    Request Path Parameters，directly fill the Value in the request path

external_task_id	string	Optional	None	

Customized Task ID for audio generation

    The ​​external_task_id​​ is provided when creating a taskl; You can choose to query by external_task_id or task_id.

Request Body

None
Response Body
JSON
Copy
Collapse
{
    "code": 0, //Error Codes;Specific definitions can be found in Error codes
    "message": "string", //Error information
    "request_id": "string", //Request ID, generated by the system
    "data":{
        "task_id": "string", //Task ID, generated by the system
        "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
        "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
        "task_info": { //Task creation parameters
            "external_task_id": "string"//Customer-defined task ID
        },
        "task_result":{
            "audios":[
                {
                    "id": "string", //Generated audio ID; globally unique
                    "url_mp3": "string", //URL for generated audio in MP3 format (To ensure information security, generated audios will be cleared after 30 days. Please make sure to save them promptly.)
                    "url_wav": "string", //URL for generated audio in WAV format (To ensure information security, generated audios will be cleared after 30 days. Please make sure to save them promptly.)
                    "duration_mp3": "string", //Total duration of the audio in MP3 format, unit: s (seconds)
                    "duration_wav": "string" //Total duration of the audio in WAV format, unit: s (seconds)
                }
            ]
        },
        "created_at": 1722769557708, //Task creation time, Unix timestamp, unit: ms
        "updated_at": 1722769557708, //Task update time, Unix timestamp, unit: ms
    }
}

Query Task (List)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/audio/text-to-audio	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Query Parameters

/v1/audio/text-to-audio?pageNum=1&pageSize=30
Field	Type	Required Field	Default	Description
pageNum	int	Optional	1	

Page number

    Value range：[1,1000]

pageSize	int	Optional	30	

Data volume per page

    Value range：[1,500]

Request Body

None
Response Body
JSON
Copy
Collapse
{
    "code": 0, //Error Codes；Specific definitions can be found in Error codes
    "message": "string", //Error information
    "request_id": "string", //Request ID, generated by the system
    "data":[
        {
            "task_id": "string", //Task ID, generated by the system
            "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
            "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
            "task_info": { //Task creation parameters
                "external_task_id": "string"//Customer-defined task ID
            },
            "task_result":{
                "audios": [
                    {
                        "id": "string", //Generated audio ID; globally unique
                        "url_mp3": "string", //URL for generated audio in MP3 format (To ensure information security, generated audios will be cleared after 30 days. Please make sure to save them promptly.)
                        "url_wav": "string", //URL for generated audio in WAV format (To ensure information security, generated audios will be cleared after 30 days. Please make sure to save them promptly.)
                        "duration_mp3": "string", //Total duration of the audio in MP3 format, unit: s (seconds)
                        "duration_wav": "string" //Total duration of the audio in WAV format, unit: s (seconds)
                    }
                ]
            },
            "created_at": 1722769557708, //Task creation time, Unix timestamp, unit: ms
            "updated_at": 1722769557708, //Task update time, Unix timestamp, unit: ms
        }
    ]
}


Video to Audio
Create task
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/audio/video-to-audio	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
Field	Type	Required Field	Default	Description
video_id	string	Optional	None	

The ID of the video generated by the Kling AI

    Either the video_id parameter or the video_url parameter, cannot be empty or have a value at the same time.
    Only supports videos generated within 30 days and with a duration between 3.0s and 20.0s.

video_url	string	Optional	None	

Link for uploaded video

    Either the video_id parameter or the video_url parameter, cannot be empty or have a value at the same time.
    Only .mp4/.mov formats are supported.
    File size does not exceed 100MB.
    Video duration between 3.0s and 20.0s.

sound_effect_prompt	string	Optional	None	

Sound effect prompt

    Cannot exceed 200 characters

bgm_prompt	string	Optional	None	

BGM prompt

    Cannot exceed 200 characters

asmr_mode	boolean	Optional	false	

Enable ASMR mode; This mode enhances detailed sound effects and is suitable for highly immersive content scenarios

    true means turn on ASMR mode, false means turn off ASMR mode(default value)

external_task_id	string	Optional	None	

Customized Task ID

    Users can provide a customized task ID, which will not overwrite the system-generated task ID but can be used for task queries.
    Please note that the customized task ID must be unique within a single user account.

callback_url	string	Optional	None	

The callback notification address for the result of this task. If configured, the server will actively notify when the task status changes

    The specific message schema of the notification can be found in “Callback Protocol”

Response Body
JSON
Copy
Collapse
{
    "code": 0, //Error codes；Specific definitions can be found in Error codes
    "message": "string", //Error information
    "request_id": "string", //Request ID, generated by the system
    "data":{
        "task_id": "string", //Task ID, generated by the system
        "task_info":{ //Task creation parameters
            "external_task_id": "string" //Customer-defined task ID
        }, 
        "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
        "created_at": 1722769557708, //Task creation time, Unix timestamp, unit: ms
        "updated_at": 1722769557708 //Task update time, Unix timestamp, unit: ms
    }
}

Query Task (Single)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/audio/video-to-audio/{id}	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
Field	Type	Required Field	Default	Description
task_id	string	Required	None	

The task ID for audio generation

    Request Path Parameters，directly fill the Value in the request path

external_task_id	string	Optional	None	

Customized Task ID for audio generation

    The ​​external_task_id​​ is provided when creating a task; You can choose to query by external_task_id or task_id.

Request Body

None
Response Body
JSON
Copy
Collapse
{
    "code": 0, //Error codes；Specific definitions can be found in Error codes
    "message": "string", //Error information
    "request_id": "string", //Request ID, generated by the system
    "data":{
        "task_id": "string", //Task ID, generated by the system
        "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
        "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
        "task_info": { //Task creation parameters
            "external_task_id": "string",//Customer-defined task ID
            "parent_video": {
                "id": "string", //Original Video ID; globally unique
                "url": "string", //Original Video URL (To ensure information security, videos will be cleared after 30 days. Please make sure to save them promptly.)
                "duration": "string" //Original video duration, unit: s (seconds)
            }
        },
        "task_result":{
            "videos":[
                {
                    "id": "string", //Generated Video ID; globally unique
                    "url": "string", //URL of the audio-dubbed video (To ensure information security, generated videos will be cleared after 30 days. Please make sure to save them promptly.)
                    "duration": "string" //Total audio-dubbed video duration, unit: s (seconds)
                }
            ],
            "audios":[
                {
                    "id": "string", //Generated audio ID；globally unique
                    "url_mp3": "string", //URL for generated audio in MP3 format (To ensure information security, generated audios will be cleared after 30 days. Please make sure to save them promptly.)
                    "url_wav": "string", //URL for generated audio in WAV format (To ensure information security, generated audios will be cleared after 30 days. Please make sure to save them promptly.
                    "duration_mp3": "string", //Total duration of the audio in MP3 format, unit: s (seconds)
                    "duration_wav": "string" //Total duration of the audio in WAV format, unit: s (seconds)
                }
            ]
        },
        "created_at": 1722769557708, //Task creation time, Unix timestamp, unit: ms
        "updated_at": 1722769557708, //Task update time, Unix timestamp, unit: ms
    }
}

Query Task (List)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/audio/video-to-audio	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Query Parameters

/v1/audio/video-to-audio?pageNum=1&pageSize=30
Field	Type	Required Field	Default	Description
pageNum	int	Optional	1	

Page number

    Value range：[1,1000]

pageSize	int	Optional	30	

Data volume per page

    Value range：[1,500]

Request Body

None
Response Body
JSON
Copy
Collapse
{
    "code": 0, //Error codes；Specific definitions can be found in Error codes
    "message": "string", //Error information
    "request_id": "string", //Request ID, generated by the system
    "data":{
        "task_id": "string", //Task ID, generated by the system
        "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
        "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
        "task_info": { //Task creation parameters
            "external_task_id": "string",//Customer-defined task ID
            "parent_video": {
                "id": "string", //Original Video ID; globally unique
                "url": "string", //Original Video URL (To ensure information security, videos will be cleared after 30 days. Please make sure to save them promptly.)
                "duration": "string" //Original video duration, unit: s (seconds)
            }
        },
      "task_result":{
          "videos":[
              {
                  "id": "string", //Generated Video ID; globally unique
                  "url": "string", //URL of the audio-dubbed video (To ensure information security, generated videos will be cleared after 30 days. Please make sure to save them promptly.)
                  "duration": "string" //Total audio-dubbed video duration, unit: s (seconds)
              }
          ],
          "audios":[
              {
                  "id": "string", //Generated audio ID；globally unique
                  "url_mp3": "string", //URL for generated audio in MP3 format (To ensure information security, generated audios will be cleared after 30 days. Please make sure to save them promptly.)
                  "url_wav": "string", //URL for generated audio in WAV format (To ensure information security, generated audios will be cleared after 30 days. Please make sure to save them promptly.
                  "duration_mp3": "string", //Total duration of the audio in MP3 format, unit: s (seconds)
                  "duration_wav": "string" //Total duration of the audio in WAV format, unit: s (seconds)
              }
          ]
      },
      "created_at": 1722769557708, //Task creation time, Unix timestamp, unit: ms
      "updated_at": 1722769557708, //Task update time, Unix timestamp, unit: ms
    }
}


TTS
Create task
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/audio/tts	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
Field	Type	Required Field	Default	Description
text	string	Required	Null	

Text Content for Lip-Sync Video Generation

    The maximum length of the text content is 1000 characters; content that is too long will return an error code and other information.
    The system will validate the text content; if there are issues, it will return an error code and other information.

voice_id	string	Required	Null	

Voice ID

    When the input·mode parameter is set to be text2video, this parameter is required.
    The system offers a variety of voice options to choose from. Click here to viewthe specific voice effects, voice IDs, and the corresponding voice languages. Voice previews do not support custom scripts.
    Voice preview file naming convention: Voice Name#Voice ID#Voice Language

voice_language	string	Required	zh	

The voice language corresponds to the Voice ID, as detailed above.

    Enum values: zh，en
    When the input·mode parameter is set to be text2video, this parameter is required.
    The voice language corresponds to the Voice ID, as detailed above.

voice_speed	float	Optional	1.0	

Speech Rate

    Valid range: [0.8, 2.0], accurate to one decimal place; values outside this range will be automatically rounded.

Response Body
JSON
Copy
Collapse
{
  "code": 0, //Error codes；Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
     "task_result":{
       "audios":[
         {
           "id": "string", // Generated sound ID；globally unique, will be cleared after 30 days
           "url": "string", // URL for generating sounds，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.mp3(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
           "duration": "string" // Total video duration, unit: s (seconds)
         }
       ]
     },
    "created_at": 1722769557708, // Task creation time, Unix timestamp, unit: ms
    "updated_at": 1722769557708 // Task update time, Unix timestamp, unit: ms
	}
}
Image Generation
Create Task
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/images/generations	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
💡

Please note that in order to maintain naming consistency, the original model field has been changed to model_name, so in the future, please use this field to specify the version of the model that needs to be called.

    At the same time, we keep the behavior forward-compatible, if you continue to use the original model field, it will not have any impact on the interface call, there will not be any exception, which is equivalent to the default behavior when model_name is empty (i.e., call the V1 model).

Field	Type	Required Field	Default	Description
model_name	string	Optional	kling-v1	

Model Name

    Enum values：kling-v1, kling-v1-5, kling-v2, kling-v2-new, kling-v2-1

prompt	string	Required	None	

Positive text prompt

    Cannot exceed 2500 characters

negative_prompt	string	Optional	Null	

Negative text prompt

    Cannot exceed 2500 characters

Note: In the Image-to-Image scenario (when the "image" field is not empty), negative prompts are not supported.
image	string	Optional	Null	

Reference Image

    Support inputting image Base64 encoding or image URL (ensure accessibility)

Please note, if you use the Base64 method, make sure all image data parameters you pass are in Base64 encoding format. When submitting data, do not add any prefixes to the Base64-encoded string, such as data:image/png;base64. The correct parameter format should be the Base64-encoded string itself.
Example: Correct Base64 encoded parameter:

1
iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Incorrect Base64 encoded parameter (includes the data: prefix):

1
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Please provide only the Base64-encoded string portion so that the system can correctly process and parse your data.

    Supported image formats include.jpg / .jpeg / .png
    The image file size cannot exceed 10MB, and the width and height dimensions of the image shall not be less than 300px, and the aspect ratio of the image should be between 1:2.5 ~ 2.5:1
    the image_reference parameter is not empty, the current parameter is required

image_reference	string	Optional	Null	

Image reference type

    Enum values：subject(character feature reference), face(character appearance reference)
    When using face(character appearance reference), the uploaded image must contain only one face.
    When using kling-v1-5 and the image parameter is not empty, the current parameter is required

Only kling-v1-5 supports the current parameter
image_fidelity	float	Optional	0.5	

Face reference intensity for user-uploaded images during generation

    Value range：[0,1]，The larger the value, the stronger the reference intensity

human_fidelity	float	Optional	0.45	

Facial reference intensity, refers to the similarity of the facial features of the person in the reference image

    Only image_reference parameter is subject is available
    Value range：[0,1]，The larger the value, the stronger the reference intensity

resolution	string	Optional	1k	

Image generation resolution

    Enum values：1k, 2k
        1k：1K standard
        2k：2K high-res

The support range for different model versions. For more details, please refer to the current document's "2-0 Capability Map"
n	int	Optional	1	

Number of generated images

    Value range：[1,9]

aspect_ratio	string	Optional	16:9	

Aspect ratio of the generated images (width:height)

    Enum values：16:9, 9:16, 1:1, 4:3, 3:4, 3:2, 2:3, 21:9

Different model versions support varying ranges. For details, refer to the Capability Map
callback_url	string	Optional	None	

The callback notification address for the result of this task. If configured, the server will actively notify when the task status changes

    The specific message schema of the notification can be found in “Callback Protocol”

Response Body
JSON
Copy
Collapse
{
  "code": 0, //Error Codes；Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, unit ms
  }
}

Query Task (Single)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/images/generations/{id}	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Path Parameters
Field	Type	Required Field	Default	Description
task_id	string	Required	None	The task ID generated by images
Request Path Parameters，directly fill the Value in the request path
Request Body

None
Response Body
JSON
Copy
Collapse
{
  "code": 0, //Error codes；Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
    "updated_at": 1722769557708, //Task update time, Unix timestamp, unit ms
    "task_result":{
      "images":[
        {
          "index": int, //Image Number，0-9
          "url": "string" //URL for generating images，such as：https://h1.inkwai.com/bs2/upload-ylab-stunt/1fa0ac67d8ce6cd55b50d68b967b3a59.png(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
        }
      ]
    }
  }
}

Query Task (List)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/images/generations	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Query Parameters

/v1/images/generations?pageNum=1&pageSize=30
Field	Type	Required Field	Default	Description
pageNum	int	Optional	1	Page number
Value range：[1,1000]
pageSize	int	Optional	30	Data volume per page
Value range：[1,500]
Request Body

None
Response Body
JSON
Copy
Collapse
{
  "code": 0, //Error codes；Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data":[
    {
      "task_id": "string", //Task ID, generated by the system
      "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
      "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
      "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
      "updated_at": 1722769557708, //Task update time, Unix timestamp, unit ms
      "task_result":{
        "images":[
          {
            "index": int, //Image Number，0-9
            "url": "string" //URL for generating images，such as：https://h1.inkwai.com/bs2/upload-ylab-stunt/1fa0ac67d8ce6cd55b50d68b967b3a59.png(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
          }
      	]
      }
    }
  ]
}



Multi-Image to Image
Create task
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/images/multi-image2image	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
Field	Type	Required Field	Default	Description
model_name	string	Optional	kling-v2	

Model Name

    Enum values: kling-v2, kling-v2-1

prompt	string	Optional	Null	

Positive text prompt

    Cannot exceed 2500 characters

subject_image_list	array	Optional	Null	

Subject Reference Images

    Support up to 4 images, at least 1 image
    Use key:value format as follows:

1
2
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
"subject_image_list":[
	{
  	"subject_image":"image_url"
  },
	{
  	"subject_image":"image_url"
  },
	{
  	"subject_image":"image_url"
  },
	{
  	"subject_image":"image_url"
  }
]

    The API does not perform cropping, please upload images with subjects already cropped
    Supports image input as either Base64-encoded string or URL (ensure the URL is publicly accessible)

Note: If you choose to use Base64 for image input, please ensure that all image data parameters are strictly in Base64-encoded format. Do not include any prefix such as data:image/png;base64, in the submitted string. The correct format should be the raw Base64-encoded string only.
Examples:
Correct Base64-encoded parameter:

1
iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Wrong Base64-encoded parameter (includes data: prefix):

1
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Please provide only the Base64-encoded string itself to ensure the system can correctly process and parse your data.

    Supported image formats: .jpg / .jpeg / .png
    Image file size must not exceed 10MB. Image dimensions must be at least 300px in width and height

scene_image	string	Optional	Null	

Scene Reference Images

    Supports image input as either Base64-encoded string or URL (ensure the URL is publicly accessible)

Note: If you choose to use Base64 for image input, please ensure that all image data parameters are strictly in Base64-encoded format. Do not include any prefix such as data:image/png;base64, in the submitted string. The correct format should be the raw Base64-encoded string only.
Examples:
Correct Base64-encoded parameter:

1
iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Wrong Base64-encoded parameter (includes data: prefix):

1
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Please provide only the Base64-encoded string itself to ensure the system can correctly process and parse your data.

    Supported image formats: .jpg / .jpeg / .png
    Image file size must not exceed 10MB. Image dimensions must be at least 300px in width and height

style_image	string	Optional	Null	

Style Reference Image

    Supports image input as either Base64-encoded string or URL (ensure the URL is publicly accessible)

Note: If you choose to use Base64 for image input, please ensure that all image data parameters are strictly in Base64-encoded format. Do not include any prefix such as data:image/png;base64, in the submitted string. The correct format should be the raw Base64-encoded string only.
Examples:
Correct Base64-encoded parameter:

1
iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Wrong Base64-encoded parameter (includes data: prefix):

1
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Please provide only the Base64-encoded string itself to ensure the system can correctly process and parse your data.

    Supported image formats: .jpg / .jpeg / .png
    Image file size must not exceed 10MB. Image dimensions must be at least 300px in width and height

n	int	Optional	1	

Number of generated images

    Value range：[1,9]

aspect_ratio	string	Optional	16:9	

Aspect ratio of the generated images (width:height)

    Enum values：16:9, 9:16, 1:1, 4:3, 3:4, 3:2, 2:3, 21:9

The support range for different model versions. For more details, please refer to the current document's "2-0 Capability Map"
callback_url	string	Optional	None	

The callback notification address for the result of this task. If configured, the server will actively notify when the task status changes

    The specific message schema of the notification can be found in “Callback Protocol”

external_task_id	string	Optional	None	

Customized Task ID for Video Effects

    Request Path Parameters，directly fill the Value in the request path
    When creating a task, you can choose to query by external_task_id or task_id.

Response Body
JSON
Copy
Collapse

{
	"code": 0, //Error Codes；Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_info":{ //Task creation parameters
    	"external_task_id": "string" //Customer-defined task ID
    }, 
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, unit ms
  }
}

Query Task (Single)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/images/multi-image2image/{id}	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Path Parameters
Field	Type	Required Field	DefaultValue	Description
task_id	string	Required	None	

The task ID generated by images

    Request Path Parameters，directly fill the Value in the request path

Request Body

None
Response Body
JSON
Copy
Collapse
{
	"code": 0, //Error codes；Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
  	"task_info":{ //Task creation parameters
    	"external_task_id": "string" //Customer-defined task ID
    }, 
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
    "updated_at": 1722769557708, //Task update time, Unix timestamp, unit ms
    "task_result":{
    	"images":[
        {
        	"index": int, //Image Number，0-9
          "url": "string" //URL for generating images，such as：https://h1.inkwai.com/bs2/upload-ylab-stunt/1fa0ac67d8ce6cd55b50d68b967b3a59.png(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
        }
      ]
    }
  }
}

Query Task (List)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/images/multi-image2image	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Query Parameters

/v1/images/generations?pageNum=1&pageSize=30
Field	Type	Required Field	DefaultValue	Description
pageNum	int	Optional	1	

Page number

    Value range：[1,1000]

pageSize	int	Optional	30	

Data volume per page

    Value range：[1,500]

Request Body

None
Response Body
JSON
Copy
Collapse
{
	"code": 0, //Error codes；Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data":[
    {
      "task_id": "string", //Task ID, generated by the system
      "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
      "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
	  	"task_info":{ //Task creation parameters
    	"external_task_id": "string" //Customer-defined task ID
    	}, 
      "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
      "updated_at": 1722769557708, //Task update time, Unix timestamp, unit ms
      "task_result":{
        "images":[
          {
            "index": int, //Image Number，0-9
            "url": "string" //URL for generating images，such as：https://h1.inkwai.com/bs2/upload-ylab-stunt/1fa0ac67d8ce6cd55b50d68b967b3a59.png(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
          }
      	]
      }
    }
  ]
}


Image Expansion
Create task
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/images/editing/expand	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
Field	Type	Required Field	Default	Description
image	string	Required	Null	

Reference Image

    Supports image input as either Base64-encoded string or URL (ensure the URL is publicly accessible)

Note: If you choose to use Base64 for image input, please ensure that all image data parameters are strictly in Base64-encoded format. Do not include any prefix such as data:image/png;base64, in the submitted string. The correct format should be the raw Base64-encoded string only.
Examples:
Correct Base64-encoded parameter:

1
iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Wrong Base64-encoded parameter (includes data: prefix):

1
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Please provide only the Base64-encoded string itself to ensure the system can correctly process and parse your data.

    Supported image formats: .jpg / .jpeg / .png
    Image file size must not exceed 10MB. Image dimensions must be at least 300px in width and height

up_expansion_ratio	float	Required	0	

Expand upwards range; calculated based on multiples of the original image height.

    Value range: [0, 2]. The total area of the new image must not exceed 3 times that of the original image.
    Example: If the original image height is 20 and the current parameter value is 0.1, then:
        The distance from the top edge of the original image to the top edge of the new image is 20 × 0.1 = 2, and the expanded area within this region is entirely part of the upscaled image.

down_expansion_ratio	float	Required	0	

Expand downwards range; calculated based on multiples of the original image height.

    Value range: [0, 2]. The total area of the new image must not exceed 3 times that of the original image.
    Example: If the original image height is 20 and the current parameter value is 0.2, then:
        The distance from the bottom edge of the original image to the bottom edge of the new image is 20 × 0.2 = 4, and the expanded area within this region is entirely part of the downscaled image.

left_expansion_ratio	float	Required	0	

Expand leftwards range; calculated based on multiples of the original image width.

    Value range: [0, 2]. The total area of the new image must not exceed 3 times that of the original image.
    Example: If the original image width is 30 and the current parameter value is 0.3, then:
        The distance from the left edge of the original image to the left edge of the new image is 30 × 0.3 = 9, and the expanded area within this region is entirely part of the left-scaled image.

right_expansion_ratio	float	Required	0	

Expand rightwards range; calculated based on multiples of the original image width.

    Value range: [0, 2]. The total area of the new image must not exceed 3 times that of the original image.
    Example: If the original image width is 30 and the current parameter value is 0.4, then:
        The distance from the right edge of the original image to the right edge of the new image is 30 × 0.4 = 12, and the expanded area within this region is entirely part of the right-scaled image.

prompt	string	Optional	None	

Positive text prompt

    Cannot exceed 2500 characters

n	int	Optional	1	

Number of generated images

    Value range：[1,9]

callback_url	string	Optional	None	

The callback notification address for the result of this task. If configured, the server will actively notify when the task status changes

    The specific message schema of the notification can be found in “Callback Protocol”

external_task_id	string	Optional	None	

Customized Task ID

    Users can provide a customized task ID, which will not overwrite the system-generated task ID but can be used for task queries.
    Please note that the customized task ID must be unique within a single user account

Response Body
JSON
Copy
Collapse

{
	"code": 0, //Error Codes；Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_info":{ //Task creation parameters
    	"external_task_id": "string" //Customer-defined task ID
    }, 
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, unit ms
  }
}

Example code
Python
Copy
Collapse

import math

def calculate_expansion_ratios(width, height, area_multiplier, aspect_ratio):
    """
    Calculate top/bottom/left/right expansion ratios for image outpainting.
    
    Parameters:
    - width: Original image width
    - height: Original image height
    - area_multiplier: Multiplier for the outpainted area relative to original image
    - aspect_ratio: Width/height ratio for the outpainted area（width/height）
    
    Returns:
    - Formatted string with 4 decimal places, e.g."0.1495,0.1495,0.6547,0.6547"
    """
    # Calculate target total area
    target_area = area_multiplier * width * height
    
    # Calculate target height and width (maintaining aspect ratio)
    target_height = math.sqrt(target_area / aspect_ratio)
    target_width = target_height * aspect_ratio
    
    # Calculate expansion pixels
    expand_top = (target_height - height) / 2
    expand_bottom = expand_top
    expand_left = (target_width - width) / 2
    expand_right = expand_left
    
    # Calculate relative ratios
    top_ratio = expand_top / height
    bottom_ratio = expand_bottom / height
    left_ratio = expand_left / width
    right_ratio = expand_right / width
    
    # Format to 4 decimal places
    return f"{top_ratio:.4f},{bottom_ratio:.4f},{left_ratio:.4f},{right_ratio:.4f}"

# Example: Original 100x100, 3x area multiplier, 16:9 aspect ratio
print(calculate_expansion_ratios(100, 100, 3, 16/9))  
# Output: "0.1495,0.1495,0.6547,0.6547"

Query Task (Single)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/images/editing/expand/{id}	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Path Parameters
Field	Type	Required Field	DefaultValue	Description
task_id	string	Required	None	

The task ID generated by images

    Request Path Parameters，directly fill the Value in the request path

Request Body

None
Response Body
JSON
Copy
Collapse

{
	"code": 0, //Error codes；Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
   "task_info":{ //Task creation parameters
    	"external_task_id": "string" //Customer-defined task ID
    }, 
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
    "updated_at": 1722769557708, //Task update time, Unix timestamp, unit ms
    "task_result":{
    	"images":[
        {
        	"index": int, //Image Number，0-9
          "url": "string" //URL for generating images，such as：https://h1.inkwai.com/bs2/upload-ylab-stunt/1fa0ac67d8ce6cd55b50d68b967b3a59.png(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
        }
      ]
    }
  }
}

Query Task (List)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/images/editing/expand	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Query Parameters

/v1/images/generations?pageNum=1&pageSize=30
Field	Type	Required Field	DefaultValue	Description
pageNum	int	Optional	1	

Page number

    Value range：[1,1000]

pageSize	int	Optional	30	

Data volume per page

    Value range：[1,500]

Request Body

None
Response Body
JSON
Copy
Collapse

{
	"code": 0, //Error codes；Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
   "task_info":{ //Task creation parameters
    	"external_task_id": "string" //Customer-defined task ID
    }, 
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
    "updated_at": 1722769557708, //Task update time, Unix timestamp, unit ms
    "task_result":{
    	"images":[
        {
        	"index": int, //Image Number，0-9
          "url": "string" //URL for generating images，such as：https://h1.inkwai.com/bs2/upload-ylab-stunt/1fa0ac67d8ce6cd55b50d68b967b3a59.png(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
        }
      ]
    }
  }
}

Image Recognize
Create Task
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/videos/image-recognize	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Body
Field	Type	Required Field	Default	Description
image	string	Required	Null	

Image to be recognized

    Support inputting image Base64 encoding or image URL (ensure accessibility).

Please note, if you use the Base64 method, make sure all image data parameters you pass are in Base64 encoding format. When submitting data, do not add any prefixes to the Base64-encoded string, such as data:image/png;base64. The correct parameter format should be the Base64-encoded string itself.
Example: Correct Base64 encoded parameter:

1
iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Incorrect Base64 encoded parameter (includes the data: prefix):

1
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Please provide only the Base64-encoded string portion so that the system can correctly process and parse your data.

    Supported image formats include.jpg / .jpeg / .png
    The image file size cannot exceed 10MB, and the width and height dimensions of the image shall not be less than 300px, and the aspect ratio of the image should be between 1:2.5 ~ 2.5:1.

	
Response Body
JSON
Copy
Collapse

{
  "code": 0, //Error codes；Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data":{
    "task_result":{
      "images":[
        {
          "type": "object_seg", // Identification of subject recognition results
          "is_contain": true,  // Has the subject been identified; Boolean value
          "url": "string", // URL for generating videos，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.png（请注意，为保障信息安全，生成的图片/视频会在30天后被清理，请及时转存）
        },
        {
          "type": "head_seg", // Identification of facial recognition results for individuals with hair included
          "is_contain": true,  // Has the subject been identified; Boolean value
          "url": "string", // URL for generating videos，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.png（请注意，为保障信息安全，生成的图片/视频会在30天后被清理，请及时转存）
        },
        {
          "type": "face_seg", // Identification of facial recognition results for individuals without hair included
          "is_contain": true,  // Has the subject been identified; Boolean value
          "url": "string", // URL for generating videos，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.png（请注意，为保障信息安全，生成的图片/视频会在30天后被清理，请及时转存）
        },
        {
          "type": "cloth_seg", // Identification of clothing recognition results
          "is_contain": true,  // Has the subject been identified; Boolean value
          "url": "string", // URL for generating videos，such as https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.png（请注意，为保障信息安全，生成的图片/视频会在30天后被清理，请及时转存）
        }
      ]
    }
  }
}


Virtual Try-On
Create Task
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/images/kolors-virtual-try-on	POST	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Body
Field	Type	Required Field	Default	Description
model_name	string	Optional	kolors-virtual-try-on-v1	

Model Name

    Enum values：kolors-virtual-try-on-v1, kolors-virtual-try-on-v1-5

human_image	string	Required	Null	

Reference human Image

    Support uploading image Base64 encoding or image URL (ensure accessibility)

Please note, if you use the Base64 method, make sure all image data parameters you pass are in Base64 encoding format. When submitting data, do not add any prefixes to the Base64-encoded string, such as data:image/png;base64. The correct parameter format should be the Base64-encoded string itself.
Example: Correct Base64 encoded parameter:

1
iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Incorrect Base64 encoded parameter (includes the data: prefix):

1
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Please provide only the Base64-encoded string portion so that the system can correctly process and parse your data.

    Supported image formats include.jpg / .jpeg / .png
    The image file size cannot exceed 10MB, and the width and height dimensions of the image shall not be less than 300px

cloth_image	string	Optional	Null	

Reference clothing image

    Support uploading clothing product images or clothing image with white background; Supports single clothing (upper, lower, and dress) try-on.
    Support uploading image Base64 encoding or image URL (ensure accessibility)

Please note, if you use the Base64 method, make sure all image data parameters you pass are in Base64 encoding format. When submitting data, do not add any prefixes to the Base64-encoded string, such as data:image/png;base64. The correct parameter format should be the Base64-encoded string itself.
Example: Correct Base64 encoded parameter:

1
iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Incorrect Base64 encoded parameter (includes the data: prefix):

1
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==

Please provide only the Base64-encoded string portion so that the system can correctly process and parse your data.

    Supported image formats include.jpg / .jpeg / .png

    The image file size cannot exceed 10MB, and the width and height dimensions of the image shall not be less than 300px

    Kolors-virtual-try-on-v1-5 model not only supports single clothing input but also the “upper + lower” combination input, which means:
        Input a single clothing image (upper, lower, or dress) -> Generate a try-on image of the single item
        Input a combination clothing image (you can merge multiple items into one image with a white background)
            If the model detects “upper + lower” -> Generate a try-on image of “upper + lower”
            If the model detects “upper + upper” -> Generation fails
            If the model detects “lower + lower” -> Generation fails
            If the model detects “dress + dress” -> Generation fails
            If the model detects “upper + dress” -> Generation fails
            If the model detects “lower + dress” -> Generation fails

callback_url	string	Optional	None	

The callback notification address for the result of this task. If configured, the server will actively notify when the task status changes

    The specific message schema of the notification can be found in “Callback Protocol”

Response Body
JSON
Copy
Collapse
{
  "code": 0, //Error codes;Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Task ID, generated by the system, used for tracking requests and debug issues
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
    "updated_at": 1722769557708 //Task update time, Unix timestamp, unit ms
  }
}

Query Task (Single)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/images/kolors-virtual-try-on/{id}	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Request Path Parameters
Field	Type	Required Field	Default	Description
task_id	string	Required	None	Task ID for image generation
Request Path Parameters，directly fill the Value in the request path
Request Body

None
Response Body
JSON
Copy
Collapse

{
  "code": 0, //Error codes；Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data":{
  	"task_id": "string", //Task ID, generated by the system
    "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
    "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
    "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
    "updated_at": 1722769557708, //Task update time, Unix timestamp, unit ms
    "task_result":{
      "images":[
        {
          "index": int, //Image Number
          "url": "string" //URL for generating images, such as：https://h1.inkwai.com/bs2/upload-ylab-stunt/1fa0ac67d8ce6cd55b50d68b967b3a59.png(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
        }
      ]
    }
  }
}

Query Task (List)
Protocol	Request URL	Request Method	Request Format	Response Format
https	/v1/images/kolors-virtual-try-on	GET	application/json	application/json
Request Header
Field	Value	Description
Content-Type	application/json	Data Exchange Format
Authorization	Authentication information, refer to API authentication	Authentication information, refer to API authentication
Query Parameters

/v1/images/kolors-virtual-try-on?pageNum=1&pageSize=30
Field	Type	Required Field	Default	Description
pageNum	int	Optional	1	Page number
Value range：[1,1000]
pageSize	int	Optional	30	Data volume per page
Value range：[1,500]
Request Body

None
Response Body
JSON
Copy
Collapse

{
  "code": 0, //Error codes；Specific definitions can be found in Error codes
  "message": "string", //Error information
  "request_id": "string", //Request ID, generated by the system, is used to track requests and troubleshoot problems
  "data":[
    {
      "task_id": "string", //Task ID, generated by the system
      "task_status": "string", //Task status, Enum values：submitted、processing、succeed、failed
      "task_status_msg": "string", //Task status information, displaying the failure reason when the task fails (such as triggering the content risk control of the platform, etc.)
      "created_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
      "updated_at": 1722769557708, //Task creation time, Unix timestamp, unit ms
      "task_result":{
        "images":[
          {
            "index": int, //Image Number
            "url": "string" //URL for generating images，such as: https://h1.inkwai.com/bs2/upload-ylab-stunt/1fa0ac67d8ce6cd55b50d68b967b3a59.png(To ensure information security, generated images/videos will be cleared after 30 days. Please make sure to save them promptly.)
          }
      	]
      }
    }
  ]
}
