Sora 2 Image To Video Stable


API Endpoints
Get Started
Things You Should Know
Authentication
All APIs require authentication via Bearer Token.

Authorization: Bearer YOUR_API_KEY

Get API Key:

API Key Management
🔒 Keep your API Key secure

🚫 Do not share it with others

⚡ Reset immediately if compromised

POST
/api/v1/jobs/createTask
Create Task
Create a new generation task

Request Parameters
The API accepts a JSON payload with the following structure:

Request Body Structure
{
  "model": "string",
  "callBackUrl": "string (optional)",
  "input": {
    // Input parameters based on form configuration
  }
}
Root Level Parameters
model
Required
string
The model name to use for generation

Example:

"sora-2-image-to-video-stable"
callBackUrl
Optional
string
Callback URL for task completion notifications. Optional parameter. If provided, the system will send POST requests to this URL when the task completes (success or failure). If not provided, no callback notifications will be sent.

Example:

"https://your-domain.com/api/callback"
Input Object Parameters
The input object contains the following parameters based on the form configuration:

input.prompt
Required
string
The text prompt describing the desired video motion

Max length: 10000 characters
Example:

"A claymation conductor passionately leads a claymation orchestra, while the entire group joyfully sings in chorus the phrase: “Sora 2 is now available on Kie AI."
input.image_urls
Required
array(URL)
URL of the image to use as the first frame. Must be publicly accessible

Please provide the URL of the uploaded file; Accepted types: image/jpeg, image/png, image/webp; Max size: 10.0MB
Example:

["https://file.aiquickdraw.com/custom-page/akr/section-images/17594315607644506ltpf.jpg"]
input.aspect_ratio
Optional
string
This parameter defines the aspect ratio of the image.

Available options:

portrait
-
Portrait
landscape
-
Landscape
Example:

"landscape"
input.n_frames
Optional
string
The number of frames to be generated.

Available options:

10
-
10s
15
-
15s
Example:

"10"
input.upload_method
Optional
string
Upload destination. Defaults to s3; choose oss for Aliyun storage (better access within China).

Available options:

s3
-
s3
oss
-
oss
Example:

"s3"
Request Example

cURL

JavaScript

Python
curl -X POST "https://api.kie.ai/api/v1/jobs/createTask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "sora-2-image-to-video-stable",
    "callBackUrl": "https://your-domain.com/api/callback",
    "input": {
      "prompt": "A claymation conductor passionately leads a claymation orchestra, while the entire group joyfully sings in chorus the phrase: “Sora 2 is now available on Kie AI.",
      "image_urls": [
        "https://file.aiquickdraw.com/custom-page/akr/section-images/17594315607644506ltpf.jpg"
      ],
      "aspect_ratio": "landscape",
      "n_frames": "10",
      "upload_method": "s3"
    }
}'
Response Example
{
  "code": 200,
  "message": "success",
  "data": {
    "taskId": "task_12345678"
  }
}
Response Fields
code
Status code, 200 for success, others for failure
message
Response message, error description when failed
data.taskId
Task ID for querying task status
Callback Notifications
When you provide the callBackUrl parameter when creating a task, the system will send POST requests to the specified URL upon task completion (success or failure).

Success Callback Example
{
    "code": 200,
    "data": {
        "completeTime": 1755599644000,
        "costTime": 8,
        "createTime": 1755599634000,
        "model": "sora-2-image-to-video-stable",
        "param": "{\"callBackUrl\":\"https://your-domain.com/api/callback\",\"model\":\"sora-2-image-to-video-stable\",\"input\":{\"prompt\":\"A claymation conductor passionately leads a claymation orchestra, while the entire group joyfully sings in chorus the phrase: “Sora 2 is now available on Kie AI.\",\"image_urls\":[\"https://file.aiquickdraw.com/custom-page/akr/section-images/17594315607644506ltpf.jpg\"],\"aspect_ratio\":\"landscape\",\"n_frames\":\"10\",\"upload_method\":\"s3\"}}",
        "resultJson": "{\"resultUrls\":[\"https://example.com/generated-image.jpg\"]}",
        "state": "success",
        "taskId": "e989621f54392584b05867f87b160672",
        "failCode": null,
        "failMsg": null,
    },
    "msg": "Playground task completed successfully."
}
Failure Callback Example
{
    "code": 501,
    "data": {
        "completeTime": 1755597081000,
        "costTime": 0,
        "createTime": 1755596341000,
        "failCode": "500",
        "failMsg": "Internal server error",
        "model": "sora-2-image-to-video-stable",
        "param": "{\"callBackUrl\":\"https://your-domain.com/api/callback\",\"model\":\"sora-2-image-to-video-stable\",\"input\":{\"prompt\":\"A claymation conductor passionately leads a claymation orchestra, while the entire group joyfully sings in chorus the phrase: “Sora 2 is now available on Kie AI.\",\"image_urls\":[\"https://file.aiquickdraw.com/custom-page/akr/section-images/17594315607644506ltpf.jpg\"],\"aspect_ratio\":\"landscape\",\"n_frames\":\"10\",\"upload_method\":\"s3\"}}",
        "state": "fail",
        "taskId": "bd3a37c523149e4adf45a3ddb5faf1a8",
        "resultJson": null,
    },
    "msg": "Playground task failed."
}
Important Notes
The callback content structure is identical to the Query Task API response
The param field contains the complete Create Task request parameters, not just the input section
If callBackUrl is not provided, no callback notifications will be sent


Sora 2 Text To Video Stable
POST
/api/v1/jobs/createTask
Create Task
Create a new generation task

Request Parameters
The API accepts a JSON payload with the following structure:

Request Body Structure
{
  "model": "string",
  "callBackUrl": "string (optional)",
  "input": {
    // Input parameters based on form configuration
  }
}
Root Level Parameters
model
Required
string
The model name to use for generation

Example:

"sora-2-text-to-video-stable"
callBackUrl
Optional
string
Callback URL for task completion notifications. Optional parameter. If provided, the system will send POST requests to this URL when the task completes (success or failure). If not provided, no callback notifications will be sent.

Example:

"https://your-domain.com/api/callback"
Input Object Parameters
The input object contains the following parameters based on the form configuration:

input.prompt
Required
string
The text prompt describing the desired video motion

Max length: 10000 characters
Example:

"A professor stands at the front of a lively classroom, enthusiastically giving a lecture. On the blackboard behind him are colorful chalk diagrams. With an animated gesture, he declares to the students: “Sora 2 is now available on Kie AI, making it easier than ever to create stunning videos.” The students listen attentively, some smiling and taking notes."
input.aspect_ratio
Optional
string
This parameter defines the aspect ratio of the image.

Available options:

portrait
-
Portrait
landscape
-
Landscape
Example:

"landscape"
input.n_frames
Optional
string
The number of frames to be generated.

Available options:

10
-
10s
15
-
15s
Example:

"10"
input.upload_method
Optional
string
Upload destination. Defaults to s3; choose oss for Aliyun storage (better access within China).

Available options:

s3
-
s3
oss
-
oss
Example:

"s3"
Request Example

cURL

JavaScript

Python
curl -X POST "https://api.kie.ai/api/v1/jobs/createTask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "sora-2-text-to-video-stable",
    "callBackUrl": "https://your-domain.com/api/callback",
    "input": {
      "prompt": "A professor stands at the front of a lively classroom, enthusiastically giving a lecture. On the blackboard behind him are colorful chalk diagrams. With an animated gesture, he declares to the students: “Sora 2 is now available on Kie AI, making it easier than ever to create stunning videos.” The students listen attentively, some smiling and taking notes.",
      "aspect_ratio": "landscape",
      "n_frames": "10",
      "upload_method": "s3"
    }
}'
Response Example
{
  "code": 200,
  "message": "success",
  "data": {
    "taskId": "task_12345678"
  }
}
Response Fields
code
Status code, 200 for success, others for failure
message
Response message, error description when failed
data.taskId
Task ID for querying task status
Callback Notifications
When you provide the callBackUrl parameter when creating a task, the system will send POST requests to the specified URL upon task completion (success or failure).

Success Callback Example
{
    "code": 200,
    "data": {
        "completeTime": 1755599644000,
        "costTime": 8,
        "createTime": 1755599634000,
        "model": "sora-2-text-to-video-stable",
        "param": "{\"callBackUrl\":\"https://your-domain.com/api/callback\",\"model\":\"sora-2-text-to-video-stable\",\"input\":{\"prompt\":\"A professor stands at the front of a lively classroom, enthusiastically giving a lecture. On the blackboard behind him are colorful chalk diagrams. With an animated gesture, he declares to the students: “Sora 2 is now available on Kie AI, making it easier than ever to create stunning videos.” The students listen attentively, some smiling and taking notes.\",\"aspect_ratio\":\"landscape\",\"n_frames\":\"10\",\"upload_method\":\"s3\"}}",
        "resultJson": "{\"resultUrls\":[\"https://example.com/generated-image.jpg\"]}",
        "state": "success",
        "taskId": "e989621f54392584b05867f87b160672",
        "failCode": null,
        "failMsg": null,
    },
    "msg": "Playground task completed successfully."
}
Failure Callback Example
{
    "code": 501,
    "data": {
        "completeTime": 1755597081000,
        "costTime": 0,
        "createTime": 1755596341000,
        "failCode": "500",
        "failMsg": "Internal server error",
        "model": "sora-2-text-to-video-stable",
        "param": "{\"callBackUrl\":\"https://your-domain.com/api/callback\",\"model\":\"sora-2-text-to-video-stable\",\"input\":{\"prompt\":\"A professor stands at the front of a lively classroom, enthusiastically giving a lecture. On the blackboard behind him are colorful chalk diagrams. With an animated gesture, he declares to the students: “Sora 2 is now available on Kie AI, making it easier than ever to create stunning videos.” The students listen attentively, some smiling and taking notes.\",\"aspect_ratio\":\"landscape\",\"n_frames\":\"10\",\"upload_method\":\"s3\"}}",
        "state": "fail",
        "taskId": "bd3a37c523149e4adf45a3ddb5faf1a8",
        "resultJson": null,
    },
    "msg": "Playground task failed."
}
Important Notes
The callback content structure is identical to the Query Task API response
The param field contains the complete Create Task request parameters, not just the input section
If callBackUrl is not provided, no callback notifications will be sent


Sora 2 Image To Video
POST
/api/v1/jobs/createTask
Create Task
Create a new generation task

Request Parameters
The API accepts a JSON payload with the following structure:

Request Body Structure
{
  "model": "string",
  "callBackUrl": "string (optional)",
  "input": {
    // Input parameters based on form configuration
  }
}
Root Level Parameters
model
Required
string
The model name to use for generation

Example:

"sora-2-text-to-video-stable"
callBackUrl
Optional
string
Callback URL for task completion notifications. Optional parameter. If provided, the system will send POST requests to this URL when the task completes (success or failure). If not provided, no callback notifications will be sent.

Example:

"https://your-domain.com/api/callback"
Input Object Parameters
The input object contains the following parameters based on the form configuration:

input.prompt
Required
string
The text prompt describing the desired video motion

Max length: 10000 characters
Example:

"A professor stands at the front of a lively classroom, enthusiastically giving a lecture. On the blackboard behind him are colorful chalk diagrams. With an animated gesture, he declares to the students: “Sora 2 is now available on Kie AI, making it easier than ever to create stunning videos.” The students listen attentively, some smiling and taking notes."
input.aspect_ratio
Optional
string
This parameter defines the aspect ratio of the image.

Available options:

portrait
-
Portrait
landscape
-
Landscape
Example:

"landscape"
input.n_frames
Optional
string
The number of frames to be generated.

Available options:

10
-
10s
15
-
15s
Example:

"10"
input.upload_method
Optional
string
Upload destination. Defaults to s3; choose oss for Aliyun storage (better access within China).

Available options:

s3
-
s3
oss
-
oss
Example:

"s3"
Request Example

cURL

JavaScript

Python
curl -X POST "https://api.kie.ai/api/v1/jobs/createTask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "sora-2-text-to-video-stable",
    "callBackUrl": "https://your-domain.com/api/callback",
    "input": {
      "prompt": "A professor stands at the front of a lively classroom, enthusiastically giving a lecture. On the blackboard behind him are colorful chalk diagrams. With an animated gesture, he declares to the students: “Sora 2 is now available on Kie AI, making it easier than ever to create stunning videos.” The students listen attentively, some smiling and taking notes.",
      "aspect_ratio": "landscape",
      "n_frames": "10",
      "upload_method": "s3"
    }
}'
Response Example
{
  "code": 200,
  "message": "success",
  "data": {
    "taskId": "task_12345678"
  }
}
Response Fields
code
Status code, 200 for success, others for failure
message
Response message, error description when failed
data.taskId
Task ID for querying task status
Callback Notifications
When you provide the callBackUrl parameter when creating a task, the system will send POST requests to the specified URL upon task completion (success or failure).

Success Callback Example
{
    "code": 200,
    "data": {
        "completeTime": 1755599644000,
        "costTime": 8,
        "createTime": 1755599634000,
        "model": "sora-2-text-to-video-stable",
        "param": "{\"callBackUrl\":\"https://your-domain.com/api/callback\",\"model\":\"sora-2-text-to-video-stable\",\"input\":{\"prompt\":\"A professor stands at the front of a lively classroom, enthusiastically giving a lecture. On the blackboard behind him are colorful chalk diagrams. With an animated gesture, he declares to the students: “Sora 2 is now available on Kie AI, making it easier than ever to create stunning videos.” The students listen attentively, some smiling and taking notes.\",\"aspect_ratio\":\"landscape\",\"n_frames\":\"10\",\"upload_method\":\"s3\"}}",
        "resultJson": "{\"resultUrls\":[\"https://example.com/generated-image.jpg\"]}",
        "state": "success",
        "taskId": "e989621f54392584b05867f87b160672",
        "failCode": null,
        "failMsg": null,
    },
    "msg": "Playground task completed successfully."
}
Failure Callback Example
{
    "code": 501,
    "data": {
        "completeTime": 1755597081000,
        "costTime": 0,
        "createTime": 1755596341000,
        "failCode": "500",
        "failMsg": "Internal server error",
        "model": "sora-2-text-to-video-stable",
        "param": "{\"callBackUrl\":\"https://your-domain.com/api/callback\",\"model\":\"sora-2-text-to-video-stable\",\"input\":{\"prompt\":\"A professor stands at the front of a lively classroom, enthusiastically giving a lecture. On the blackboard behind him are colorful chalk diagrams. With an animated gesture, he declares to the students: “Sora 2 is now available on Kie AI, making it easier than ever to create stunning videos.” The students listen attentively, some smiling and taking notes.\",\"aspect_ratio\":\"landscape\",\"n_frames\":\"10\",\"upload_method\":\"s3\"}}",
        "state": "fail",
        "taskId": "bd3a37c523149e4adf45a3ddb5faf1a8",
        "resultJson": null,
    },
    "msg": "Playground task failed."
}


POST
/api/v1/jobs/createTask
Create Task
Create a new generation task

Request Parameters
The API accepts a JSON payload with the following structure:

Request Body Structure
{
  "model": "string",
  "callBackUrl": "string (optional)",
  "progressCallBackUrl": "string (optional)",
  "input": {
    // Input parameters based on form configuration
  }
}
Root Level Parameters
model
Required
string
The model name to use for generation

Example:

"sora-2-text-to-video"
callBackUrl
Optional
string
Callback URL for task completion notifications. Optional parameter. If provided, the system will send POST requests to this URL when the task completes (success or failure). If not provided, no callback notifications will be sent.

Example:

"https://your-domain.com/api/callback"
progressCallBackUrl
Optional
string
Callback URL for task progress updates. Optional. If provided, the system will send POST requests to this URL during generation to report progress. Only supported for Sora video models (sora-2-text-to-video, sora-2-image-to-video, sora-2-pro-text-to-video, sora-2-pro-image-to-video).

Example:

"https://your-domain.com/api/v1/jobs/progressCallBackUrl"
Input Object Parameters
The input object contains the following parameters based on the form configuration:

input.prompt
Required
string
The text prompt describing the desired video motion

Max length: 10000 characters
Example:

"A professor stands at the front of a lively classroom, enthusiastically giving a lecture. On the blackboard behind him are colorful chalk diagrams. With an animated gesture, he declares to the students: “Sora 2 is now available on Kie AI, making it easier than ever to create stunning videos.” The students listen attentively, some smiling and taking notes."
input.aspect_ratio
Optional
string
This parameter defines the aspect ratio of the image.

Available options:

portrait
-
Portrait
landscape
-
Landscape
Example:

"landscape"
input.n_frames
Optional
string
The number of frames to be generated.

Available options:

10
-
10s
15
-
15s
Example:

"10"
input.remove_watermark
Optional
boolean
When enabled, removes watermarks from the generated video.

Boolean value (true/false)
Example:

true
input.upload_method
Optional
string
Upload destination. Defaults to s3; choose oss for Aliyun storage (better access within China).

Available options:

s3
-
s3
oss
-
oss
Example:

"s3"
Request Example

cURL

JavaScript

Python
curl -X POST "https://api.kie.ai/api/v1/jobs/createTask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "sora-2-text-to-video",
    "callBackUrl": "https://your-domain.com/api/callback",
    "progressCallBackUrl": "https://your-domain.com/api/v1/jobs/progressCallBackUrl",
    "input": {
      "prompt": "A professor stands at the front of a lively classroom, enthusiastically giving a lecture. On the blackboard behind him are colorful chalk diagrams. With an animated gesture, he declares to the students: “Sora 2 is now available on Kie AI, making it easier than ever to create stunning videos.” The students listen attentively, some smiling and taking notes.",
      "aspect_ratio": "landscape",
      "n_frames": "10",
      "remove_watermark": true,
      "upload_method": "s3"
    }
}'
Response Example
{
  "code": 200,
  "message": "success",
  "data": {
    "taskId": "task_12345678"
  }
}
Response Fields
code
Status code, 200 for success, others for failure
message
Response message, error description when failed
data.taskId
Task ID for querying task status
Callback Notifications
When you provide the callBackUrl parameter when creating a task, the system will send POST requests to the specified URL upon task completion (success or failure).

Success Callback Example
{
    "code": 200,
    "data": {
        "completeTime": 1755599644000,
        "costTime": 8,
        "createTime": 1755599634000,
        "model": "sora-2-text-to-video",
        "param": "{\"callBackUrl\":\"https://your-domain.com/api/callback\",\"progressCallBackUrl\":\"https://your-domain.com/api/v1/jobs/progressCallBackUrl\",\"model\":\"sora-2-text-to-video\",\"input\":{\"prompt\":\"A professor stands at the front of a lively classroom, enthusiastically giving a lecture. On the blackboard behind him are colorful chalk diagrams. With an animated gesture, he declares to the students: “Sora 2 is now available on Kie AI, making it easier than ever to create stunning videos.” The students listen attentively, some smiling and taking notes.\",\"aspect_ratio\":\"landscape\",\"n_frames\":\"10\",\"remove_watermark\":true,\"upload_method\":\"s3\"}}",
        "resultJson": "{\"resultUrls\":[\"https://example.com/generated-image.jpg\"],\"resultWaterMarkUrls\":[\"https://example.com/generated-watermark-image.jpg\"]}",
        "state": "success",
        "taskId": "e989621f54392584b05867f87b160672",
        "failCode": null,
        "failMsg": null,
    },
    "msg": "Playground task completed successfully."
}
Failure Callback Example
{
    "code": 501,
    "data": {
        "completeTime": 1755597081000,
        "costTime": 0,
        "createTime": 1755596341000,
        "failCode": "500",
        "failMsg": "Internal server error",
        "model": "sora-2-text-to-video",
        "param": "{\"callBackUrl\":\"https://your-domain.com/api/callback\",\"progressCallBackUrl\":\"https://your-domain.com/api/v1/jobs/progressCallBackUrl\",\"model\":\"sora-2-text-to-video\",\"input\":{\"prompt\":\"A professor stands at the front of a lively classroom, enthusiastically giving a lecture. On the blackboard behind him are colorful chalk diagrams. With an animated gesture, he declares to the students: “Sora 2 is now available on Kie AI, making it easier than ever to create stunning videos.” The students listen attentively, some smiling and taking notes.\",\"aspect_ratio\":\"landscape\",\"n_frames\":\"10\",\"remove_watermark\":true,\"upload_method\":\"s3\"}}",
        "state": "fail",
        "taskId": "bd3a37c523149e4adf45a3ddb5faf1a8",
        "resultJson": null,
    },
    "msg": "Playground task failed."
}


POST
/api/v1/jobs/createTask
Create Task
Create a new generation task

Request Parameters
The API accepts a JSON payload with the following structure:

Request Body Structure
{
  "model": "string",
  "callBackUrl": "string (optional)",
  "input": {
    // Input parameters based on form configuration
  }
}
Root Level Parameters
model
Required
string
The model name to use for generation

Example:

"sora-2-characters-pro"
callBackUrl
Optional
string
Callback URL for task completion notifications. Optional parameter. If provided, the system will send POST requests to this URL when the task completes (success or failure). If not provided, no callback notifications will be sent.

Example:

"https://your-domain.com/api/callback"
Input Object Parameters
The input object contains the following parameters based on the form configuration:

input.origin_task_id
Required
string
Taskid of a previously generated Sora video—this video will serve as the source footage for the character you’re about to create.

Max length: 100 characters
input.character_user_name
Optional
string
A globally-unique handle for your character. Reference it in later prompts by prefixing it with @ (e.g., @sky_ranger).

Max length: 40 characters
input.character_prompt
Required
string
In one short line, state stable traits (e.g., “cheerful barista, green apron, warm smile”); avoid camera directions, contradictions, or disallowed celebrity likeness.

Max length: 1000 characters
input.safety_instruction
Optional
string
Briefly list any boundaries (“no violence, politics, or alcohol; PG-13 max”); tighter wording helps the model enforce your content limits.

Max length: 1000 characters
input.timestamps
Required
string
Enter the clip's start and end times in seconds. The segment you select must be completely inside the original video and between 1 s–4 s long; that slice will be used as the character's training material.

end - start must be between 1 and 4 seconds
Example:

"3.55,5.55"
Request Example

cURL

JavaScript

Python
curl -X POST "https://api.kie.ai/api/v1/jobs/createTask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "sora-2-characters-pro",
    "callBackUrl": "https://your-domain.com/api/callback",
    "input": {
      "timestamps": "3.55,5.55"
    }
}'
Response Example
{
  "code": 200,
  "message": "success",
  "data": {
    "taskId": "task_12345678"
  }
}
Response Fields
code
Status code, 200 for success, others for failure
message
Response message, error description when failed
data.taskId
Task ID for querying task status
Callback Notifications
When you provide the callBackUrl parameter when creating a task, the system will send POST requests to the specified URL upon task completion (success or failure).

Success Callback Example
{
    "code": 200,
    "data": {
        "completeTime": 1755599644000,
        "costTime": 8,
        "createTime": 1755599634000,
        "model": "sora-2-characters-pro",
        "param": "{\"callBackUrl\":\"https://your-domain.com/api/callback\",\"model\":\"sora-2-characters-pro\",\"input\":{\"timestamps\":\"3.55,5.55\"}}",
        "resultJson": "{\"resultObject\":{  \"character_id\": \"example_123456789\",  \"character_user_name\":\"mzsdaag.ab\",\"remark\":\"insert this username directly into your prompt.(@character_user_name).\"}}",
        "state": "success",
        "taskId": "e989621f54392584b05867f87b160672",
        "failCode": null,
        "failMsg": null,
    },
    "msg": "Playground task completed successfully."
}
Failure Callback Example
{
    "code": 501,
    "data": {
        "completeTime": 1755597081000,
        "costTime": 0,
        "createTime": 1755596341000,
        "failCode": "500",
        "failMsg": "Internal server error",
        "model": "sora-2-characters-pro",
        "param": "{\"callBackUrl\":\"https://your-domain.com/api/callback\",\"model\":\"sora-2-characters-pro\",\"input\":{\"timestamps\":\"3.55,5.55\"}}",
        "state": "fail",
        "taskId": "bd3a37c523149e4adf45a3ddb5faf1a8",
        "resultJson": null,
    },
    "msg": "Playground task failed."
}

