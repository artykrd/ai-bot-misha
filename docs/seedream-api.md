ModelArk APIs fall into two categories: model invocation (data-plane APIs) and control-plane APIs for managing inference endpoints and other control and management tasks They use different authentication methods. The sections below describe authentication for ModelArk APIs
<span id="28e0db57"></span>
# Concepts

* **Data-plane APIs**: interfaces that directly handle **business data transfer, real-time interaction, and user request handling**, focusing on the flow and processing of actual business data, and delivering the system’s core external service capabilities Both the Chat API and Responses API for invoking model services are data-plane APIs
* **Control-plane AP**I: interfaces for **system resource management, configuration control, and status Monitoring**, focusing on managing and scheduling the data plane and system resources, and serving as the control center that ensures stable system operations ModelArk’s management API Key and foundation model management are control-plane APIs
* **Base URL**: the base template for constructing full API request URLs. It includes **the scheme (for example, http/https), host (domain name or IP), port (optional), and base path (optional)**, and serves as the common prefix for all specific API paths You can compose a full API URL by appending the API path, version, and other parameters to the Base URL. Typical structure: `[scheme]://[host]/[base path (optional)]`

<span id="b77a3928"></span>
# Base URL
Base URLs for each API type

* Data plane API:https://ark.ap-southeast.bytepluses.com/api/v3

<span id="0fed4817"></span>
# Data plane API authentication
Supports two authentication methods: API key authentication (simple and convenient) and Access Key authentication (traditional cloud resource permission management; managed by resource groups, cloud products, and other dimensions; suitable for fine-grained enterprise management).
<span id="60db1ed6"></span>
## API key
<span id="6011c5a5"></span>
### Prerequisites
* [Obtain an API key](https://console.byteplus.com/ark/apiKey)
* [Enable the model service](https://console.byteplus.com/ark/openManagement)
* In [Model List](/docs/ModelArk/1330310) obtain the required Model ID

<span id="d44d13a6"></span>
### Signature construction
Add the `Authorization` header to the HTTP request header as follows:
```Shell
Authorization: Bearer $ARK_API_KEY
```

<span id="e8bd2618"></span>
### Sample API call
```Shell
curl https://ark.ap-southeast.bytepluses.com/api/v3/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "seed-1-6-250915",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Hello!"
        }
    ]
  }'
```


* Replace the Model ID as needed. To query the Model ID, see [Model List](/docs/ModelArk/1330310).

<span id="21bff83b"></span>
## Access key
<span id="3ad1c414"></span>
### Prerequisites
You have obtained the Access Key. To create or view an Access Key, see [API Access Key Management](https://console.byteplus.com/iam/keymanage).
> Because the primary account's Access Key has elevated permissions, create an IAM user, grant permissions such as ModelArk, then use the IAM user's Access Key to perform operations. For details, see [Access Control Using IAM](/docs/ModelArk/1263493) .

<span id="d03b2bb1"></span>
### Usage example
See [Use Access Key for authentication](/docs/undefined/6906ced5922904054fca577c#fa44b913).
> When using Access Key authentication, set the model field to the Endpoint ID.

<span id="bdd329d5"></span>
# Control plane API authentication
Other APIs include control plane APIs for API key management, inference endpoint management, and more.
<span id="50f355e8"></span>
## Access key
You have obtained the Access Key. To create or view an Access Key, see [API access key management](https://console.byteplus.com/iam/keymanage).
<span id="c04e9b57"></span>
### Method: use samples/documentation (simple, recommended)
See [OpenAPI Center](https://api.byteplus.com/api-explorer?action=GetApiKey&groupName=Manage%20API%20Key&serviceCode=ark&tab=3&tab_sdk=GO&version=2024-01-01).



ModelArk offers SDKs for Python, Go, and Java, enabling you to quickly integrate ModelArk’s model services into your existing tech stack.
<span id="2708d57e"></span>
# Python SDK
<span id="f2baa8aa"></span>
## Prerequisites
Python is installed locally, version 3.7 or later.
> You can verify the Python version in the terminal. If installation is needed, refer to the [Python installation guide](https://wiki.python.org/moin/BeginnersGuide/Download) and choose version 3.7 or later.

```Bash
python -V
```

<span id="bb014324"></span>
## Install the Python SDK
Run the following command in the terminal to install the Python SDK.
```Bash
pip install byteplus-python-sdk-v2 
```

:::tip
* If local installation errors occur, try the following:
   * Run `pip install byteplus-python-sdk[ark]`
* If source code installation is needed, download and unzip the corresponding version of the SDK package, enter the directory and run: `python setup.py install --user`
:::
<span id="d6b883b8"></span>
## Upgrade the Python SDK
To access ModelArk's latest capabilities, upgrade the SDK to the latest version.
```Bash
pip install byteplus-python-sdk-v2  -U
```

<span id="f116fb9f"></span>
# Go SDK
<span id="0fa8c2bc"></span>
## Prerequisites
Check the version of Go; it must be 1.18 or later.
```Bash
go version
```

If Go isn’t installed or the version is too old, visit the [official Go website](https://golang.google.cn/dl/) to download and install version 1.18 or later.
<span id="ae8b42ab"></span>
## Install the Go SDK

1. The Go SDK is managed via go mod; run the following command to initialize go mod. Replace `<your-project-name>` with the actual project name.

```Bash
go mod init <your-project-name>
```


2. After initializing go mod locally, run the following command to install the latest SDK version.

```Bash
go get -u github.com/byteplus-sdk/byteplus-go-sdk-v2 
```

:::tip
If you need to install a specific SDK version, use the following command:
`go get -u github.com/byteplus-sdk/byteplus-go-sdk-v2@<VERSION>`
Replace `<VERSION>` with the actual version number. View available SDK versions at: https://github.com/byteplus-sdk/byteplus-go-sdk-v2/releases
:::

3. Import the SDK into your code.

```Go
import "github.com/byteplus-sdk/byteplus-go-sdk-v2/service/arkruntime"
```


4. After updating dependencies, use the following command to clean up unnecessary dependencies and organize the `go.mod` and `go.sum` files.

```Bash
go mod tidy
```

<span id="f0739bb0"></span>
## Upgrade the Go SDK
Refer to Step 1 and 2 in the **Install the Go SDK** section to upgrade to the latest/specified SDK version.

* Upgrade to the latest version

```Bash
go get -u github.com/byteplus-sdk/byteplus-go-sdk-v2
```


* Upgrade to a specific version

```Bash
go get -u github.com/byteplus-sdk/byteplus-go-sdk-v2@<VERSION>
```

<span id="e7ae2925"></span>
# Java SDK
<span id="41f31f3c"></span>
## Applicability
This SDK supports Java server-side development only and does not currently support Android platforms. For Android, you need to implement your own integration.
<span id="e3518e9f"></span>
## Prerequisites

1. Check the Java version; it must be 1.8 or later.

```Bash
java -version
```

If Java isn’t installed or the version is too old, visit the [official Oracle website](https://www.java.com/en/download/help/index_installing.html) to download and install version 1.8 or later.
<span id="ae8db863"></span>
## Install the Java SDK
The ModelArk Java SDK can be installed using either Maven or Gradle.
<span id="db12484d"></span>
### Install via Maven
In `pom.xml`, add the following configuration. For the full setup, see [Maven Central](https://central.sonatype.com/artifact/com.byteplus/byteplus-java-sdk-v2-ark-runtime):
```XML
...
<dependency>
  <groupId>com.byteplus</groupId>
  <artifactId>byteplus-java-sdk-v2-ark-runtime</artifactId>
  <version>LATEST</version>
</dependency>
...
```

<span id="4858e8c3"></span>
### Install via Gradle
In `build.gradle`, add the following configuration. Add the dependency to the `dependencies` section.
```Plain Text
implementation 'com.byteplus:byteplus-java-sdk-v2-ark-runtime:LATEST'
```

<span id="4ab4182d"></span>
## Upgrade the Java SDK
:::tip
Get the SDK version information, replace 'LATEST' with a specific/latest version number. Version information can be found at: https://github.com/byteplus-sdk/byteplus-java-sdk-v2/releases
:::
Use the same methods described in the **Install the Java SDK** section to upgrade, replace 'LATEST' with a specific/latest version number.
<span id="6f32c555"></span>
# Third-party SDKs
ModelArk's model invocation APIs are compatible with the OpenAI API protocol. You can use OpenAI-compatible multi-language community SDK to call ModelArk's models or applications. It's easy to migrate your services to the ModelArk platform and the Seed model family. For details, see [Compatible with OpenAI API](/docs/ModelArk/1330626).
<span id="4b8511f6"></span>
# See also
[Common SDK usage examples](/docs/ModelArk/1544136)




 ` POST https://ark.ap-southeast.bytepluses.com/api/v3/chat/completions` [Try](https://api.byteplus.com/api-explorer/?action=ChatCompletions&groupName=Chat%20API&serviceCode=ark&version=2024-01-01)
This topic describes the request and response parameters of the API for calling text generation and visual understanding models. You can refer to this topic for the meaning of a field when using the API.

```mixin-react
return (<Tabs>
<Tabs.TabPane title="Try" key="sqgXNE7u"><RenderMd content={`<APILink link="https://api.byteplus.com/api-explorer/?action=ChatCompletions&groupName=Chat%20API&serviceCode=ark&version=2024-01-01" description="API Explorer 您可以通过 API Explorer 在线发起调用，无需关注签名生成过程，快速获取调用结果。"></APILink>
`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Quickstart" key="ns6cERWb"><RenderMd content={` [ ](#)[Experience center](https://console.byteplus.com/ark/region:ark+ap-southeast-1/experience/chat)<span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_2abecd05ca2779567c6d32f0ddc7874d.png =20x) </span>[Model list](https://docs.byteplus.com/en/docs/ModelArk/1330310)<span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_a5fdd3028d35cc512a10bd71b982b6eb.png =20x) </span>[Billing](https://docs.byteplus.com/en/docs/ModelArk/1099320)<span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_afbcf38bdec05c05089d5de5c3fd8fc8.png =20x) </span>[API Key](https://console.byteplus.com/ark/region:ark+ap-southeast-1/apiKey)
 <span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_bef4bc3de3535ee19d0c5d6c37b0ffdd.png =20x) </span>[Model activation](https://console.byteplus.com/ark/region:ark+ap-southeast-1/openManagement)<span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_57d0bca8e0d122ab1191b40101b5df75.png =20x) </span>[Text generation guide](https://docs.byteplus.com/en/docs/ModelArk/1399009) <span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_57d0bca8e0d122ab1191b40101b5df75.png =20x) </span>[Visual understanding guide](https://docs.byteplus.com/en/docs/ModelArk/1362931) <span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_f45b5cd5863d1eed3bc3c81b9af54407.png =20x) </span>[API document](https://docs.byteplus.com/en/docs/ModelArk/Chat)
`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Authentication" key="luFI3H0KOr"><RenderMd content={`This API supports API key authentication. For more information, refer to [Authentication methods](https://docs.byteplus.com/en/docs/ModelArk/1298459).
> If you want to use access key authentication, we recommend that you use the SDK. For more information, refer to [SDK overview](https://docs.byteplus.com/en/docs/ModelArk/1302007).
`}></RenderMd></Tabs.TabPane></Tabs>);
```


---


<span id="lYMB9msn"></span>
## Request parameters
> Jump to [Response parameters](#CKb7vjIa)

<span id="pHVIfgol"></span>
### Request body

---


**model** `string` `required`
The ID of the model that you want to call. You can [activate a model service](https://console.byteplus.com/ark/region:ark+ap-southeast-1/openManagement) and [query the model ID](https://docs.byteplus.com/en/docs/ModelArk/model_id).
You can also use an endpoint ID to call a model, querying its rate limits, billing method (prepaid or postpaid), and runtime status, and using its advanced capabilities such as monitoring and security. For more information, refer to [Obtain an endpoint ID](https://docs.byteplus.com/en/docs/ModelArk/1099522).

---


**messages**  `object[]` `required`
The list of messages in the chat so far. Different models support different message types, such as text, image, and video (work orders required).

Message types

---


system message `object`
The instructions provided by developers for models to follow, such as what role a model is to play or what goal a model is to achieve.

Attributes

---


messages.**role** `string` `required`
The role that sends the message. In this case, it is `system`.

---


messages.**content** `string / object[]` `required`
The content of the system message.

Attributes

---


plain text message content `string`
The content of the plain text message. This type is supported by large language models (LLMs).

---


multimodal message content `object[]` 
Types such as text, image, and video are supported. This field is supported by multimodal models, such as visual understanding models, and some LLMs.

Message of each modality

---


text content `object`
The text content in the multimodal message. This message type is supported by [visual understanding models](https://docs.byteplus.com/en/docs/ModelArk/1330310#visual-understanding) and some LLMs.

Attributes

---


messages.content.**text ** `string` `required`
The text message content.

---


messages.content.**type ** `string` `required`
The text message type. In this case, it is `text`.


---


image content `object`
The image content in the multimodal message. This message type is supported by [visual understanding models](https://docs.byteplus.com/en/docs/ModelArk/1330310#visual-understanding).

Attributes

---


messages.content.**image_url ** `object` `required`
The image message content.

Attributes

---


messages.content.image_url.**url ** `string` `required`
You can pass in an image URL or the Base64\-encoded content of the image. Image sizes supported by models slightly differ. For details, refer to [Usage instructions](https://docs.byteplus.com/en/docs/ModelArk/1362931#token-usage-description).

* Image URL: Make sure that the image URL is accessible. We recommend that you use TOS to store the image and generate an image URL.
* Base64\-encoded content: The format must be `data:image/<image format>;base64,<Base64-encoded content>`. For details, refer to [this example](https://docs.byteplus.com/en/docs/ModelArk/1362931#base64-encoding-input).


---


messages.content.image_url.**detail ** `string`  `default value:  auto`
You can manually set the image quality. Valid values: `high`, `low`, and `auto`.

* `high`: The high\-detail mode, which is suitable for scenarios requiring an understanding of image details, such as extracting multiple local information or features from an image or comprehending complex and rich image details. This mode enables a more comprehensive understanding.
* `low`: The low\-detail mode, which is suitable for scenarios requiring simple image classification/recognition or overall content comprehension/description. This mode enables a faster understanding.
* `auto`: The default mode, which varies depending on the model. For details, refer to [Controlling the Precision of Image Understanding](https://docs.byteplus.com/en/docs/ModelArk/1362931#controlling-the-precision-of-image-understanding).


---


messages.content.**type ** `string` `required`
The image message type. In this case, it is `image_url`.


---


Video content `object`
> For the video understanding model, please refer to [Video Understanding Model](https://docs.byteplus.com/en/docs/ModelArk/1330310#visual-understanding). 

In multimodal messages, the video content section.

Attributes

---


messages.content.**type** `string` `required`
The type of video message, which should be video_url here.

---


messages.content.**video_url** `object` `required`
The content part of the video message.

Attributes

---


messages.content.video_url.**url** `string` `required`
Supports passing in video links or Base64 encoding of videos. For specific usage, please refer to [the document](https://docs.byteplus.com/en/docs/ModelArk/1362931#base64-encoding-entered).

---


messages.content.video_url.**fps** `float/ null` `default value: 1`
Value range: [0.2, 5].
Specifies the number of images to extract from the video per second. A higher value results in a more detailed understanding of frame changes in the video; a lower value reduces the perception of frame changes in the video but consumes fewer tokens and operates faster. For detailed explanations, see [Usage Instructions](https://docs.byteplus.com/en/docs/ModelArk/1362931#usage-instructions).






---


user message `object` 
The messages sent by users, including prompts and additional contextual information. Different models support different field types. A model can support up to three message types, including text, image, and video (work orders required).

Attributes

---


messages **.role ** `string` `required`
The role of sending information should be `user` here

---


messages **.content ** `string / object[]` **  ** `required`
User Information Content

Content Catalog

---


plain text message content `string`
The content of the plain text message. This type is supported by large language models (LLMs).

---


multimodal message content `object[]` 
Types such as text, image, and video are supported. This field is supported by multimodal models, such as visual understanding models, and some LLMs.

Message of each modality

---


text content `object`
The text content in the multimodal message. This message type is supported by [visual understanding models](https://docs.byteplus.com/en/docs/ModelArk/1330310#visual-understanding) and some LLMs.

Attributes

---


messages.content.**text ** `string` `required`
The text message content.

---


messages.content.**type ** `string` `required`
The text message type. In this case, it is `text`.


---


Image content `object`
The image content in the multimodal message. This message type is supported by [visual understanding models](https://docs.byteplus.com/en/docs/ModelArk/1330310#visual-understanding).

Attributes

---


messages.content.**type ** `string` `required`
The image message type. In this case, it is `image_url`.

---


messages.content.**image_url ** `object` `required`
The image message content.

Attributes

---


messages.content.image_url.**url ** `string` `required`
You can pass in an image URL or the Base64\-encoded content of the image. Image sizes supported by models slightly differ. For details, refer to [Usage instructions](https://docs.byteplus.com/en/docs/ModelArk/1362931#instructions).

* Image URL: Make sure that the image URL is accessible. We recommend that you use TOS to store the image and generate an image URL.
* Base64\-encoded content: The format must be `data:image/<image format>;base64,<Base64-encoded content>`. For details, refer to [this example](https://docs.byteplus.com/en/docs/ModelArk/1362931#base64-encoding-entered).


---


messages.content.image_url.**detail ** `string / null`  `default: low`
Valid values: `high`, `low`, and `auto`.
You can manually set the image quality.

* `high`: The high\-detail mode, which is suitable for scenarios requiring an understanding of image details, such as extracting multiple local information or features from an image or comprehending complex and rich image details. This mode enables a more comprehensive understanding. In this case, **min_pixels ** is set to `3136`, and **max_pixels ** is set to `4014080`.
* `low`: The low\-detail mode, which is suitable for scenarios requiring simple image classification/recognition or overall content comprehension/description. This mode enables a faster understanding. In this case, **min_pixels ** is set to `3136`, and **max_pixels ** is set to `1048576`.
* `auto`: The default mode, which varies depending on the model. For details, refer to [Control over the depth of image understanding](https://docs.byteplus.com/en/docs/ModelArk/1362931#understanding-the-depth-control-of-images).


---


messages.content.image_url.**image_pixel_limit  ** `object / null` `default: null`
You can set the image pixel limits. If an image falls outside the specified range, it is proportionally resized to be within the range.
Priority: If you set both the **detail** and **image_pixel_limit** fields, **image_pixel_limit** takes precedence over **detail.** 
If you do not set **min_pixels** or **max_pixels** for this field, the **min_pixels** or **max_pixels** value set for the **detail** field is used.
Value limits for the sub\-fields: `3136` ≤ **min_pixels ** ≤ **max_pixels ** ≤ `4014080`

---


messages.content.image_url.image_pixel_limit.**max_pixels ** `integer`
Value range: (**min_pixels**, `4014080`].
The maximum image pixels. Images with more pixels are proportionally scaled down to stay below the **max_pixels** value.
If you do not set it, the **max_pixels** value set for the **detail** field is used.

---


messages.content.image_url.image_pixel_limit.**min_pixels**
Value range: [`3136`, **max_pixels**).
The minimum image pixels. Images with fewer pixels are proportionally scaled up to stay above the **min_pixels** value.
If you do not set it, the **min_pixels** value set for the **detail** field, that is, `3136`, is used.



---


Video content `object`
> For the video understanding model, please refer to [Video Understanding Model](https://docs.byteplus.com/en/docs/ModelArk/1330310#visual-understanding). 

In multimodal messages, the video content section.

Attributes

---


messages.content.**type** `string` `required`
The type of video message, which should be video_url here.

---


messages.content.**video_url** `object` `required`
The content part of the video message.

Attributes

---


messages.content.video_url.**url** `string` `required`
Supports passing in video links or Base64 encoding of videos. For specific usage, please refer to [the document](https://docs.byteplus.com/en/docs/ModelArk/1362931#base64-encoding-entered).

---


messages.content.video_url.**fps** `float/ null` `default value: 1`
Value range: [0.2, 5].
Specifies the number of images to extract from the video per second. A higher value results in a more detailed understanding of frame changes in the video; a lower value reduces the perception of frame changes in the video but consumes fewer tokens and operates faster. For detailed explanations, see [Usage Instructions](https://docs.byteplus.com/en/docs/ModelArk/1362931#usage-instructions).






---


model message `object`
The messages replied by the model in the chat history. They are typically used during the passing in of multi\-turn chat history and during [response prefilling](https://docs.byteplus.com/en/docs/ModelArk/1359497) to enable the model to continue to respond based on the preset content.

Attributes
:::tip tip
For the messages.**content** ** ** and messages.**tool_calls** fields, ** ** you must specify at least one of them.

:::
---


messages.**role** `string` `required`
The role that sends the message. In this case, it is `assistant`.

---


messages.**content** `string / array`  
The messages replied by the model.

---


messages.**reasoning_content** `string`
Chain\-of\-thought content in model messages.
> Only `seed-1-8-251215` and `deepseek-v3-2-251201` support this field.


---


messages.**tool_calls** `object[]`
The tool call messages replied by the model in the chat history.

Attributes

---


messages.tool_calls **.function ** `object` `required`
The information about the tool function called by the model.

Display sub\-fields

---


messages.tool_calls **.** function.**name ** `string` `required`
The name of the function called by the model.

---


messages.tool_calls **.** function.**arguments ** `string` `required`
The parameters in the JSON format generated by the model to call a function.
:::tip tip
The models may generate some invalid parameters and construct some parameters that are not defined in the function parameter specifications. Before calling a function, verify whether the generated parameters are valid in your code.

:::

---


messages.tool_calls **.id ** `string` `required`
The ID of the called tool.

---


messages.tool_calls **.type ** `string` `required`
The type of the tool. Currently, only `function` is supported.



---


tool message `object`
The messages of a model calling tools in the chat history. They are typically used during the passing in of multi\-turn chat history.

Attributes

---


messages.**role** `string` `required`
The role that sends the message. In this case, it is `tool`.

---


messages.**content** `string / array`  `required`
The messages returned by the tool.

---


messages.**tool_call_id ** `string` `required`
The ID of the tool called by the model.


&nbsp;

---


**thinking** `object` `default: {"type":"enabled"}`
Controls whether the model enables deep thinking mode. 
> The default value of different models are different. For models that support this field and usage examples, please refer to [the documentation](https://docs.byteplus.com/en/docs/ModelArk/1449737#disable-enable-deep-thinking).


Attributes

---


thinking.**type ** `string`  `required`
Valid values：`enabled`， `disabled`。

* `enabled`: Enable thinking mode. The model will always think before answering.
* `disabled`: Disable thinking mode. The model will answer questions directly without prior thinking.


---


**reasoning_effort** `string / null` `default: medium`
> Currently, no models support this parameter.

Valid values: `minimal`,`low` ,`medium`, `high`。
Limits the workload of in\-depth reasoning. Reducing the workload of in\-depth reasoning can result in faster response speeds and lower token consumption for in\-depth reasoning.

---


**stream** `boolean / null` `default: false`
Specifies whether to return the response content in streaming mode.

* `false`: All content generated by the model is returned at a time.
* `true`: The content generated by the model is returned by block according to the SSE protocol and ends with the message of `data: [DONE]`. 
   If **stream** is set to `true`, you can set the **stream_options** field to get token consumption details.


---


**stream_options** `object / null` `default: null`
The options for streaming responses. If **stream** is set to `true`, you can set the **stream_options** field.

Attributes

---


stream_options.**include_usage ** `boolean / null` `default: false`
Specifies whether to return token usage for this request.

* `false`: No token usage is returned.
* `true`: An extra block before the `data: [DONE]` message is returned. In this block, the **usage** field indicates the token usage of the entire request, and the **choices** field is an empty array. All other blocks also contain the **usage** field, but the value is `null`.


---


**max_tokens** `integer / null` `default: 4096`
Value range: Varies by model, refer to [Model list](https://docs.byteplus.com/en/docs/ModelArk/1330310).
The maximum length of the model's response (in tokens).
:::tip tip
The model's response does not include chain\-of\-thought content. Model response = Model output \- Model COT (if any).
The total length of the output tokens is also limited by the model's context length.

:::
---


**max_completion_tokens** `integer / null`
Models supporting this field and associated usage guidelines are available in [the documentation](https://docs.byteplus.com/en/docs/ModelArk/1399009#set-the-maximum-output-length-of-the-model).
Controls the maximum length of the model's output (including both the model's response and its chain\-of\-thought content, measured in tokens).
When this parameter is configured, the model can generate extra\-long content. In such cases, **max_tokens** (defaulting to 4k) and the maximum length of the chain of thought are overridden; the model will generate content as needed until reaching the value set in **max_completion_tokens**.
This field cannot be set alongside max_tokens; doing so will result in an immediate error.

---


**service_tier** `string / null` `default: auto`
Specifies whether to use TPM guarantee packages. It takes effect on inference endpoints with purchased guarantee packages. Valid values:

* `auto`: TPM guarantee packages are preferentially used. If the inference endpoint has a TPM guarantee package quota, the TPM guarantee package is used for this request for higher rate limits and faster responses. Otherwise, the default rate limits and standard response speed are used.
* `default`: No TPM guarantee package is used for this request. The default rate limits and standard response speed are used, even if the requested inference endpoint has a TPM guarantee package quota.


---


**stop** `string / string[] / null` `default: null`
If the model encounters a string specified by the stop field, it stops content generation. The specified strings are not output. Up to four strings are supported.
`["Hello", "Weather"]`

---


**response_format** `object`  `default: {"type": "text"}`
The format in which the model outputs content.

Formats

---


**text** `object`
By default, model responses are in the format of text.

Attributes

---


response_format.**type** `string` `required`
In this case, it is `text`.


---


**JSON Mode** `object`
Model response content is organized as a JSON object. 
> See [documentation](https://docs.byteplus.com/en/docs/ModelArk/1568221#supported-models) for models supporting this field.


Attributes

---


response_format.**type ** `string` `required`
In this case, it is `json_object`.


---


**JSON Schema** `object`  `beta`
Model response content is structured as a JSON object, following the defined JSON structure in the schema field.
> See [documentation](https://docs.byteplus.com/en/docs/ModelArk/1568221#supported-models) for models supporting this field.
> This capability is still in the beta phase; use with caution in production environments.


Attributes

---


response_format.**type ** `string` `required`
In this case, it is `json_schema`。

---


response_format.**json_schema** `object` `required`
Definition of the JSON structure.

Attributes

---


response_format.json_schema.**name** `string` `required`
User\-defined name of the JSON structure.

---


response_format.json_schema.**description** `string / null` 
Description of the response purpose. The model will determine how to respond in this format based on this description.

---


response_format.json_schema.**schema** `object` `required`
JSON format definition of the response format, described as a JSON Schema object.

---


response_format.json_schema.**strict** `boolean / null` `default: false`
Whether to enable strict adherence to the schema when generating output.

* `ture`: The model will always strictly follow the format defined in the **Schema** field.
* `false`: The model will try to follow the structure defined in the **schema** field as much as possible.




---


**frequency_penalty** `float / null` `default: 0`
Value range: [\-2.0, 2.0].
The frequency penalty. If the value is positive, the penalty is applied based on the frequency of the new token, thus reducing the likelihood of repetitions.

---


**presence_penalty** `float / null` `default: 0`
Value range: [\-2.0, 2.0].
The presence penalty. If the value is positive, the penalty is applied based on the presence of the new token, thus increasing the likelihood that the model talks about new topics.

---


**temperature** `float / null` `default: 1`
Valid values: [0, 2].
The sampling temperature, which controls the variability and randomness of generated text. If the value is 0, the model considers only the token with the highest logprob.
A higher value (for example, 0.8) makes the output more random, while a lower value (for example, 0.2) makes the output more deterministic.
We recommend that you adjust either the temperature or top_p parameter.

---


**top_p** `float / null` `default: 0.7`
Value range: [0, 1].
The nucleus sampling probability threshold. The model considers possibilities that equal or exceed the value of top_p. If the value is 0, the model considers only the token with the highest logprob.
For example, 0.1 indicates that only the top 10% of probable tokens are considered. The larger the value, the greater the randomness. The lower the value, the greater the certainty. We recommend that you adjust either the temperature or top_p parameter.

---


**logprobs** `boolean / null` `default: false`
> The model with deep thinking ability does not support this field. For the deep thinking ability model, please refer to the [documentation](https://docs.byteplus.com/en/docs/ModelArk/1330310#deep-thinking).

Specifies whether to return the logprobs of tokens.

* `false`: No logprob is returned.
* `true`: The logprob for each token in the message is returned.


---


**top_logprobs** `integer / null` `default: 0`
> The model with deep thinking ability does not support this field. For the deep thinking ability model, please refer to the [documentation](https://docs.byteplus.com/en/docs/ModelArk/1330310#deep-thinking).

Value range: [0, 20].
The number of tokens most likely to return at each token position, each with an associated logprob. Only if **logprobs** is set to `true` can you set the **top_logprobs** parameter.

---


**logit_bias** `map / null` `default: null`
> The model with deep thinking ability does not support this field. For the deep thinking ability model, please refer to the [documentation](https://docs.byteplus.com/en/docs/ModelArk/1330310#deep-thinking).

The likelihood of specified tokens appearing in a model\-generated output, which makes the content more consistent with specific preferences. **logit_bias** accepts a map where each key is a token ID in the vocabulary obtained through the tokenization API and each value is a bias value in the range of [\-100, 100].
If the value is \-1, the model is less encouraged to use the token. If the value is 1, the model is more encouraged to do so. If the value is \-100, the model must not use the token. If the value is 100, the model can only use the token. The actual effect of this parameter may vary by model.
&nbsp;

---


**tools** `object[] / null` `default: null`
The list of tools that a model can call. This structure is required for a model to call tools. For models supporting this field, refer to [Documentation](https://docs.byteplus.com/en/docs/ModelArk/1262342).

Attributes

---


tools.**type ** `string` `required`
The type of the tool. Currently, only `function` is supported.

---


tools.**function ** `object` `required`
The list of tools whose type is `function` that the model can call.

Attributes

---


tools.function.**name ** `string` `required`
The name of the called function.

---


tools.function.**description ** `string` 
The description of the called function. It helps the LLM to determine whether to call the function.

---


tools.function.**parameters ** `object` 
Function request parameters in JSON Schema format. For more information about the format, refer to [JSON Schema](https://json-schema.org/understanding-json-schema). Here is an example:
```JSON
{
  "type": "object",
  "properties": {
    "Parameter Name": {
      "type": "string | number | boolean | object | array",
      "description": "Parameter description"
    }
  },
  "required": ["Required Parameter"]
}
```

Note:

* All field names are case\-sensitive.
* **Parameters** must be a valid JSON Schema object.
* We recommend that you name fields in English and put Chinese characters (if any) in the **description** field.


&nbsp;
<span id="CKb7vjIa"></span>
## Response parameters
> Jump to [Request parameters](#lYMB9msn)

<span id="woS9silO"></span>
### 
<span id="dSeXigg7"></span>
### Non\-streaming call
> Jump to [Streaming call](#xW8kgzY1)


---


**id** `string`
The unique identifier of the request.

---


**model** `string`
The name and version of the model used in the request.

---


**service_tier** `string`
Indicates whether TPM guarantee packages are used for the request.

* `scale`: The TPM guarantee package quota is used for the request.
* `default`: No TPM guarantee package quota is used for the request.


---


**created** `integer`
The Unix timestamp in seconds of the creation time of the request.

---


**object** `string`
It is fixed to `chat.completion`.

---


**choices** `object[]`
The model output for the request.

Attributes

---


choices.**index ** `integer`
The index of the element in the **choices** list.

---


choices.**finish_reason ** `string`
The reason why the model stopped generating tokens. Valid values:

* `stop`: Model output ends or is truncated because the field specified in the stop request parameter is hit.
* `length`: Model output is truncated because one of the following limits is reached:
   * The length of the response reaches the limit specified by the `max_token` field.
   * The length of the chain\-of\-thought and the response reaches the limit specified by the `max_completion_tokens` field.
   * The length of the input, the chain\-of\-thought, and the response reaches the limit specified by the `context_window` field.
* `content_filter`: Model output is intercepted by content moderation.
* `tool_calls`: A tool is called by the model.


---


choices.**message ** `object`
The content output by the model.

Attributes

---


choices.message.**role ** `string`
The role that outputs the content. In this case, it is `assistant`.

---


choices.message.**content ** `string`
The content of the message generated by the model.

---


choices.message.**reasoning_content ** `string / null`
The content of the chain\-of\-thought of the model during problem\-solving.
This field is supported only by advanced reasoning models. For more information, refer to [Model List](https://docs.byteplus.com/en/docs/ModelArk/1330310#15e7367e).

---


choices.message.**tool_calls ** `object[] / null`
The tool calls generated by the model.

Attributes

---


choices.message.tool_calls.**id ** `string`
The ID of the called tool.

---


choices.message.tool_calls.**type ** `string`
The type of the tool. Currently, only `function` is supported.

---


choices.message.tool_calls.**function ** `object`
The function called by the model.

Attributes

---


choices.message.tool_calls.function.**name ** `string`
The name of the function called by the model.

---


choices.message.tool_calls.function.**arguments ** `string`
The parameters in the JSON format generated by the model to call a function.
The models may generate some invalid parameters and construct some parameters that are not defined in the function parameter specifications. Before calling a function, verify whether the generated parameters are valid in your code.




---


choices.**logprobs ** `object / null`
The logprob of the current content.

Attributes

---


choices.logprobs.**content ** `object[] / null`
The logprob of the token in each content element in the message list.

Attributes

---


choices.logprobs.content.**token ** `string`
The current token.

---


choices.logprobs.content.**bytes ** `integer[] / null`
The UTF\-8 value of the current token, in the format of a list of integers. It can be used for encoding and decoding characters consisting of multiple tokens, such as emojis or special characters. If the token does not have a UTF\-8 value, the list is empty.

---


choices.logprobs.content.**logprob ** `float`
The logprob of the current token.

---


choices.logprobs.content.**top_logprobs ** `object[]`
The list of most probable tokens in the current position and their logprobs. In some cases, the number returned may be less than the number specified in the top_logprobs request parameter.

**Attributes**

---


choices.logprobs.content.top_logprobs.**token ** `string`
The current token.

---


choices.logprobs.content.top_logprobs.**bytes ** `integer[] / null`
The UTF\-8 value of the current token, in the format of a list of integers. It can be used for encoding and decoding characters consisting of multiple tokens, such as emojis or special characters. If the token does not have a UTF\-8 value, the list is empty.

---


choices.logprobs.content.top_logprobs.**logprob ** `float`
The logprob of the current token.




---


choices.**moderation_hit_type ** `string` `/ null`
If the text output by the model contains sensitive information, a matching risk classification tag is returned for the text.
Return values and their meanings:

* `severe_violation`: The text output by the model involves severe violations.
* `violence`: The text output by the model involves radical behaviors.

Note: Currently, only [visual understanding models](https://docs.byteplus.com/en/docs/ModelArk/1362931) support returning this field. To return risk classification tags, you must also set ModerationStrategy to Basic on the Endpoint settings page of the ModelArk console or in the [CreateEndpoint](https://docs.byteplus.com/en/docs/ModelArk/1262823) API.


---


**usage** `object`
The token usage for the request.

Attributes

---


usage.**prompt_tokens ** `integer`
The number of prompt tokens input.

---


usage.**completion_tokens ** `integer`
The number of tokens generated by the model.

---


usage.**total_tokens ** `integer`
The total number of input and output tokens consumed by this request.

---


usage.**prompt_tokens_details ** `object`
Currently, the API does not support this field.
The details of the tokens that hit the context cache.

Attributes

---


usage.prompt_tokens_details.**cached_tokens** `integer`
Currently, the API does not support this field. In this case, it is  `0`.


---


usage.**completion_tokens_details ** `object`
The details of the tokens consumed for the request.

Attributes

---


usage.completion_tokens_details.**reasoning_tokens ** `integer`
The number of tokens consumed to output the chain\-of\-thought content.
For models supporting the output of chain\-of\-thought content, refer to [Documentation](https://docs.byteplus.com/en/docs/ModelArk/1449737).



---


&nbsp;
<span id="xW8kgzY1"></span>
### Streaming call
> Jump to [Non-streaming call](#dSeXigg7)


---


**id** `string`
The unique identifier of the request.

---


**model** `string`
The name and version of the model used in the request.

---


**service_tier** `string`
Indicates whether TPM guarantee packages are used for the request.

* `scale`: The TPM guarantee package quota is used for the request.
* `default`: No TPM guarantee package quota is used for the request.


---


**created** `integer`
The Unix timestamp in seconds of the creation time of the request.

---


**object** `string`
It is fixed to `chat.completion.chunk`.

---


**choices** `object[]`
The model output for the request.

Attributes

---


choices.**index ** `integer`
The index of the element in the **choices** list.

---


choices.**finish_reason ** `string`
The reason why the model stopped generating tokens. Valid values:

* `stop`: Model output ends or is truncated because the field specified in the stop request parameter is hit.
* `length`: Model output is truncated because one of the following limits is reached:
   * The length of the response reaches the limit specified by the `max_token` field.
   * The length of the chain\-of\-thought and the response reaches the limit specified by the `max_completion_tokens` field.
   * The length of the input, the chain\-of\-thought, and the response reaches the limit specified by the `context_window` field.
* `content_filter`: Model output is intercepted by content moderation.
* `tool_calls`: A tool is called by the model.


---


choices.**delta ** `object`
The incremental content output by the model.

Attributes

---


choices.delta.**role ** `string`
The role that outputs the content. In this case, it is `assistant`.

---


choices.delta.**content ** `string`
The content of the message generated by the model.

---


choices.delta.**reasoning_content ** `string / null`
The content of the chain\-of\-thought of the model during problem\-solving.
This field is supported only by advanced reasoning models. For more information, refer to [Models supporting advanced reasoning](https://docs.byteplus.com/en/docs/ModelArk/1449737).

---


choices.delta.**tool_calls ** `string / null`
The tool calls generated by the model.

Attributes

---


choices.delta.tool_calls.**id ** `string`
The ID of the called tool.

---


choices.delta.tool_calls.**type ** `string`
The type of the tool. Currently, only `function` is supported.

---


choices.delta.tool_calls.**function ** `object`
The function called by the model.

Attributes

---


choices.delta.tool_calls.function.**name ** `string`
The name of the function called by the model.

---


choices.delta.tool_calls.function.**arguments ** `string`
The parameters in the JSON format generated by the model to call a function.
The models may generate some invalid parameters and construct some parameters that are not defined in the function parameter specifications. Before calling a function, verify whether the generated parameters are valid in your code.




---


choices.**logprobs ** `object / null`
The logprob of the current content.

Attributes

---


choices.logprobs.**content ** `object[] / null`
The logprob of the token in each content element in the message list.

Attributes

---


choices.logprobs.content.**token ** `string`
The current token.

---


choices.logprobs.content.**bytes ** `integer[] / null`
The UTF\-8 value of the current token, in the format of a list of integers. It can be used for encoding and decoding characters consisting of multiple tokens, such as emojis or special characters. If the token does not have a UTF\-8 value, the list is empty.

---


choices.logprobs.content.**logprob ** `float`
The logprob of the current token.

---


choices.logprobs.content.**top_logprobs ** `object[]`
The list of most probable tokens in the current position and their logprobs. In some cases, the number returned may be less than the number specified in the top_logprobs request parameter.

Attributes

---


choices.logprobs.content.top_logprobs.**token ** `string`
The current token.

---


choices.logprobs.content.top_logprobs.**bytes ** `integer[] / null`
The UTF\-8 value of the current token, in the format of a list of integers. It can be used for encoding and decoding characters consisting of multiple tokens, such as emojis or special characters. If the token does not have a UTF\-8 value, the list is empty.

---


choices.logprobs.content.top_logprobs.**logprob ** `float`
The logprob of the current token.




---


choices.**moderation_hit_type ** `string` `/ null`
If the text output by the model contains sensitive information, a matching risk classification tag is returned for the text.
Return values and their meanings:

* `severe_violation`: The text output by the model involves severe violations.
* `violence`: The text output by the model involves radical behaviors.

Note: Currently, only [visual understanding models](https://docs.byteplus.com/en/docs/ModelArk/1330310#visual-understanding) support returning this field. To return risk classification tags, you must also set ModerationStrategy to Basic on the [Endpoint settings](https://console.byteplus.com/ark/region:ark+ap-southeast-1/endpoint/create?customModelId=) page of the ModelArk console or in the [CreateEndpoint](https://docs.byteplus.com/en/docs/ModelArk/CreateEndpoint) API.


---


**usage** `object`
The token usage for the request.
For a streaming call, token usage is not calculated by default, and the return value is `null`.
To calculate token usage, set **stream_options.include_usage** to `true`.

Attributes

---


usage.**prompt_tokens ** `integer`
The number of prompt tokens input.

---


usage.**completion_tokens ** `integer`
The number of tokens generated by the model.

---


usage.**total_tokens ** `integer`
The total number of input and output tokens consumed by this request.

---


usage.**prompt_tokens_details ** `object`
Currently, the API does not support this field.
The details of the tokens that hit the context cache.

Attributes

---


usage.prompt_tokens_details.**cached_tokens ** `integer`
Currently, the API does not support this field. In this case, it is  `0`.


---


usage.**completion_tokens_details ** `object`
The details of the tokens consumed for the request.

Attributes

---


usage.completion_tokens_details.**reasoning_tokens ** `integer`
The number of tokens consumed to output the chain\-of\-thought content.
For models supporting the output of chain\-of\-thought content, refer to [Documentation](https://docs.byteplus.com/en/docs/ModelArk/1449737).




import os
from byteplussdkarkruntime import Ark

client = Ark(api_key=os.environ.get("ARK_API_KEY"))

completion = client.chat.completions.create(
    model="skylark-pro-250415",
    messages=[
        {"role": "user", "content": "You are a helpful assistant."}
    ]
)
print(completion.choices[0].message.content)


{
	"choices": [{
		"finish_reason": "stop",
		"index": 0,
		"logprobs": null,
		"message": {
			"content": "Hello! How are you? Is there anything I can help you with, like answering questions, writing content, brainstorming ideas? I’m here and ready to chat.  ",
			"role": "assistant"
		}
	}],
	"created": 1749110144,
	"id": "0217491101427332b0b8a623b95f3e6209666650b67ac353d7ad2",
	"model": "skylark-pro-250415",
	"service_tier": "default",
	"object": "chat.completion",
	"usage": {
		"completion_tokens": 35,
		"prompt_tokens": 20,
		"total_tokens": 55,
		"prompt_tokens_details": {
			"cached_tokens": 0
		},
		"completion_tokens_details": {
			"reasoning_tokens": 0
		}
	}
} 


{
	"choices": [{
		"finish_reason": "stop",
		"index": 0,
		"logprobs": null,
		"message": {
			"content": "Hello! How are you? Is there anything I can help you with, like answering questions, writing content, brainstorming ideas? I’m here and ready to chat.  ",
			"role": "assistant"
		}
	}],
	"created": 1749110144,
	"id": "0217491101427332b0b8a623b95f3e6209666650b67ac353d7ad2",
	"model": "skylark-pro-250415",
	"service_tier": "default",
	"object": "chat.completion",
	"usage": {
		"completion_tokens": 35,
		"prompt_tokens": 20,
		"total_tokens": 55,
		"prompt_tokens_details": {
			"cached_tokens": 0
		},
		"completion_tokens_details": {
			"reasoning_tokens": 0
		}
	}
} 



import os
from byteplussdkarkruntime import Ark

# Get your API KEY from environment variables, configuration method see: https://docs.byteplus.com/en/docs/ModelArk/1399008
api_key = os.getenv('ARK_API_KEY')

client = Ark(
    base_url='https://ark.ap-southeast.bytepluses.com/api/v3',
    api_key=api_key,
)

# Create a dialogue request
response = client.responses.create(
    # Replace with the model's Model ID
    model="seed-1-6-250615",
    input="Hello."
)

print(response)



{
    "created_at": 1761651397,
    "id": "resp_021761651397473f77831a0a17adee8e985c3ef7c2c9d7c2e039a",
    "max_output_tokens": 32768,
    "model": "seed-1-6-250615",
    "object": "response",
    "output": [
        {
            "id": "rs_02176165139780300000000000000000000ffffc0a89854b2f7db",
            "type": "reasoning",
            "summary": [
                {
                    "type": "summary_text",
                    "text": "\nGot it, the user said \"Hello.\" so I should respond in a friendly and welcoming way. Let me keep it simple and warm. Maybe \"Hi there! How can I assist you today?\" That sounds good. It's friendly and invites them to share what they need help with."
                }
            ],
            "status": "completed"
        },
        {
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "output_text",
                    "text": "Hi there! How can I assist you today? 😊"
                }
            ],
            "status": "completed",
            "id": "msg_02176165139860400000000000000000000ffffc0a89854ee0eba"
        }
    ],
    "service_tier": "default",
    "status": "completed",
    "usage": {
        "input_tokens": 85,
        "output_tokens": 72,
        "total_tokens": 157,
        "input_tokens_details": {
            "cached_tokens": 0
        },
        "output_tokens_details": {
            "reasoning_tokens": 60
        }
    },
    "caching": {
        "type": "disabled"
    },
    "store": true,
    "expire_at": 1761910597
}

import os
from byteplussdkarkruntime import Ark

# Get your API KEY from environment variables, configuration method: https://docs.byteplus.com/en/docs/ModelArk/1399008
api_key = os.getenv('ARK_API_KEY')

client = Ark(
    base_url='https://ark.ap-southeast.bytepluses.com/api/v3',
    api_key=api_key,
)

response = client.responses.create(
    model="seed-1-6-250615",
    input=[
            {
             "role": "system", 
             "content": "You are a Three-Character Classic expert. Every time the user inputs, you can only respond with three Chinese characters. If the user input is three characters, respond by matching them like a couplet; if not, summarize the meaning of the user input into three characters. At any time, the reply is strictly limited to three characters."
            },
            {
            "role": "user",
            "content":"The beginning of man"
            }
          ],
    caching={"type": "enabled"},
    thinking={"type": "disabled"},
)
print(response)

second_response = client.responses.create(
    model="seed-1-6-250615",
    previous_response_id=response.id,
    input=[{"role": "user", "content": "next sentence"}],
    caching={"type": "enabled"},
    thinking={"type": "disabled"},
)
print(second_response)

third_response = client.responses.create(
    model="seed-1-6-250615",
    previous_response_id=second_response.id,
    input=[{"role": "user", "content": "next sentence"}],
    caching={"type": "enabled"},
    thinking={"type": "disabled"},
)
print(third_response)


[
    {
        "created_at": 1761652282,
        "id": "resp_0217616522826532b0b8a623b95f3e6209666650b67ac35d5e593",
        "max_output_tokens": 32768,
        "model": "seed-1-6-250615",
        "object": "response",
        "output": [
            {
                "type": "message",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "text": "人之初\nThe user input is \"The beginning of man\", which translates to \"人之始\" in Chinese. Following the Three-Character Classic, the corresponding line is \"人之初\" (rén zhī chū), meaning \"At the beginning of man\". This is a direct and accurate three-character response that aligns with the classic text and the requirement to summarize or couplet. "
                    }
                ],
                "status": "completed",
                "id": "msg_02176165228281300000000000000000000ffffc0a89028ec41c4"
            }
        ],
        "thinking": {
            "type": "disabled"
        },
        "service_tier": "default",
        "status": "completed",
        "usage": {
            "input_tokens": 85,
            "output_tokens": 81,
            "total_tokens": 166,
            "input_tokens_details": {
                "cached_tokens": 0
            },
            "output_tokens_details": {
                "reasoning_tokens": 0
            }
        },
        "caching": {
            "type": "enabled"
        },
        "store": true,
        "expire_at": 1761911482
    },
    {
        "created_at": 1761652441,
        "id": "resp_021761652441240f77831a0a17adee8e985c3ef7c2c9d7c23dff7",
        "max_output_tokens": 32768,
        "model": "seed-1-6-250615",
        "object": "response",
        "output": [
            {
                "type": "message",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "text": "性本善\nThe user asked for the \"next sentence\" after \"人之初\" from the Three-Character Classic. The original text follows with \"性本善\" (xìng běn shàn), meaning \"Nature is inherently good\". This is the exact next line, fitting the three-character requirement. "
                    }
                ],
                "status": "completed",
                "id": "msg_02176165244144300000000000000000000ffffc0a8b0278c24e3"
            }
        ],
        "previous_response_id": "resp_0217616522826532b0b8a623b95f3e6209666650b67ac35d5e593",
        "thinking": {
            "type": "disabled"
        },
        "service_tier": "default",
        "status": "completed",
        "usage": {
            "input_tokens": 178,
            "output_tokens": 66,
            "total_tokens": 244,
            "input_tokens_details": {
                "cached_tokens": 166
            },
            "output_tokens_details": {
                "reasoning_tokens": 0
            }
        },
        "caching": {
            "type": "enabled"
        },
        "store": true,
        "expire_at": 1761911641
    },
    {
        "created_at": 1761652574,
        "id": "resp_0217616525739048dc171a3be6ae4e53778426833a8a879ba8cf9",
        "max_output_tokens": 32768,
        "model": "seed-1-6-250615",
        "object": "response",
        "output": [
            {
                "type": "message",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "text": "性相近\nThe user continues to ask for the next sentence in the Three-Character Classic. After \"性本善\", the next line is \"性相近\" (xìng xiāng jìn), which means \"Natures are similar\". This strictly adheres to the three-character format and the classic text. "
                    }
                ],
                "status": "completed",
                "id": "msg_02176165257412500000000000000000000ffffc0a89043cde0f2"
            }
        ],
        "previous_response_id": "resp_021761652441240f77831a0a17adee8e985c3ef7c2c9d7c23dff7",
        "thinking": {
            "type": "disabled"
        },
        "service_tier": "default",
        "status": "completed",
        "usage": {
            "input_tokens": 256,
            "output_tokens": 67,
            "total_tokens": 323,
            "input_tokens_details": {
                "cached_tokens": 244
            },
            "output_tokens_details": {
                "reasoning_tokens": 0
            }
        },
        "caching": {
            "type": "enabled"
        },
        "store": true,
        "expire_at": 1761911774
    }
]


import os
from byteplussdkarkruntime import Ark

# Get your API KEY from environment variables, configuration method: https://docs.byteplus.com/en/docs/ModelArk/1399008
api_key = os.getenv('ARK_API_KEY')

client = Ark(
    base_url='https://ark.ap-southeast.bytepluses.com/api/v3',
    api_key=api_key,
)

tools = [{
    "type": "function",
    "name": "Get Weather Information",
    "description": "Obtain weather information based on the provided location",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name, e.g.: Beijing"
            }
        },
        "required": [
            "location"
        ]
    }
}]

# Create a conversation request
response = client.responses.create(
    model="seed-1-6-250615",
    input=[{"role": "user", "content": "What's the weather like in Beijing?"}],
    tools=tools,
)

print(response)


{
    "created_at": 1761652695,
    "id": "resp_021761652695533e26ea4ff982ac6e590cb805428c1b8b83800c3",
    "max_output_tokens": 32768,
    "model": "seed-1-6-250615",
    "object": "response",
    "output": [
        {
            "id": "rs_02176165269576500000000000000000000ffffc0a89028689dd7",
            "type": "reasoning",
            "summary": [
                {
                    "type": "summary_text",
                    "text": "\n我现在需要处理用户的查询：“Query today weather in Beijing”。首先，我要确定用户的需求是什么。用户想知道北京今天的天气，所以需要获取天气信息。\n\n接下来，查看可用的工具。这里只有一个工具get_weather_info，它的功能是根据提供的位置获取天气信息，参数是location，需要城市名称。用户已经明确提到了北京，所以参数应该是北京。\n\n然后，检查是否需要调用工具。用户的问题无法直接回答，必须通过工具获取数据，因此需要调用get_weather_info。\n\n再考虑是否需要并行调用。这里只需要一个工具，所以单工具调用即可。参数正确，没有缺失，不需要追问用户。\n\n最后，按照格式要求生成调用。使用<|FunctionCallBegin|>和<|FunctionCallEnd|>包裹，确保JSON格式正确。因此，正确的调用应该是：\n\n<|FunctionCallBegin|>[{\"name\":\"get_weather_info\",\"parameters\":{\"location\":\"Beijing\"}}]<|FunctionCallEnd|>"
                }
            ],
            "status": "completed"
        },
        {
            "arguments": "{\"location\":\"Beijing\"}",
            "call_id": "call_wv4yxfx4ph132occfjx1ynek",
            "name": "get_weather_info",
            "type": "function_call",
            "id": "fc_02176165269876700000000000000000000ffffc0a8902867413a",
            "status": "completed"
        }
    ],
    "service_tier": "default",
    "status": "completed",
    "tools": [
        {
            "name": "get_weather_info",
            "type": "function",
            "description": "Obtain weather information based on the provided location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g.: Beijing"
                    }
                },
                "required": [
                    "location"
                ]
            }
        }
    ],
    "usage": {
        "input_tokens": 457,
        "output_tokens": 286,
        "total_tokens": 743,
        "input_tokens_details": {
            "cached_tokens": 0
        },
        "output_tokens_details": {
            "reasoning_tokens": 221
        }
    },
    "caching": {
        "type": "disabled"
    },
    "store": true,
    "expire_at": 1761911895
}


`POST https://ark.ap-southeast.bytepluses.com/api/v3/files`
Uploads files.

```mixin-react
return (<Tabs>
<Tabs.TabPane title="Quick start" key="QxSECyHp"><RenderMd content={`<span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_2abecd05ca2779567c6d32f0ddc7874d.png =20x) </span>[Model List](https://docs.byteplus.com/en/docs/ModelArk/1330310)<span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_a5fdd3028d35cc512a10bd71b982b6eb.png =20x) </span>[Model Billing](https://docs.byteplus.com/en/docs/ModelArk/1099320)<span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_57d0bca8e0d122ab1191b40101b5df75.png =20x) </span>[Files API Tutorial](https://docs.byteplus.com/en/docs/ModelArk/1885708)<span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_afbcf38bdec05c05089d5de5c3fd8fc8.png =20x) </span>[API Key](https://console.byteplus.com/ark/region:ark+ap-southeast-1/apiKey)
`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Authentication" key="UBNZCunX"><RenderMd content={`This API supports API key and access key authentication. For more information, see [Authentication methods](https://docs.byteplus.com/en/docs/ModelArk/1298459).
`}></RenderMd></Tabs.TabPane></Tabs>);
```


---


<span id="KrXsbnTl"></span>
## Request parameters
<span id="kDVgPfMB"></span>
### Request body
**file** `file` %%require%%
The file to be uploaded; must be a binary file. See [Files API Tutorial](https://docs.byteplus.com/en/docs/ModelArk/1885708) for more details on restrictions.

---


**purpose** `string` `Default: user_data` %%require%%
Purpose of the uploaded file.
`user_data`: A file that can be used flexibly for any purpose.

---


**preprocess_configs ** `object / null`
Preprocessing rules for different file types.

Attributes

---


preprocess_configs.video.**fps** `float / null ` `Default: 1`
Value range: `[0.2, 5]`.
The number of images to be extracted from the video per second. 

* The higher the value, the more detailed the understanding of changes in the video frames. 
* The lower the value, the less sensitive the model is to changes in the video frames, but fewer tokens are used and the speed is faster. 

The token usage range for a single video is [10k, 80k]. For details, see [Video Understanding](https://docs.byteplus.com/en/docs/ModelArk/1895586).

---


preprocess_configs.video.**model** `string` 
The video understanding Model ID or Endpoint ID to be used when performing inference on this file.
:::tip Note
The model ID specified in the Files API is not tightly coupled with the model used for inference. It only affects the frame sampling strategy applied during video preprocessing when the file is uploaded.
For details about frame sampling strategies, see [Frame sampling](https://docs.byteplus.com/en/docs/ModelArk/1895586#frame-sampling-strategy).

:::
* Model ID: Different model IDs apply different frame sampling strategies.
* Endpoint ID：Frame sampling follows the strategy associated with the model mapped to the specified endpoint ID at upload time. In the response, the **model** field reflects the actual model ID used for inference.
* Parameter not provided: The default frame sampling strategy corresponding to models prior to `seed-1.8` is applied.

:::warning Note
The `seed-1-8-251228` model supports enhanced long\-video understanding. Its maximum sampled frame count has been increased from 640 frames to 1280 frames.
If you intend to use `seed-1-8-251228` for video understanding but do not specify this model ID when uploading the file via the Files API, the system will still apply the pre–seed\-1.8 frame sampling strategy. As a result, the number of frames actually understood by the model will be reduced.

:::

---


**expire_at ** `integer Default: current time +604800`
Value range: `[current time +86400, current time +2592000]` \- i.e., file is retained for at least 1 day and at most 30 days.
Set the storage validity period. Enter the UTC Unix timestamp in seconds.
<span id="uGrbcAto"></span>
## Response parameters
The model will return the corresponding [file object](https://docs.byteplus.com/en/docs/ModelArk/1873424).


curl https://ark.ap-southeast.bytepluses.com/api/v3/files \
-H "Authorization: Bearer $ARK_API_KEY" \
-F 'purpose=user_data' \
-F 'file=@/Users/doc/demo.mp4' \
-F 'preprocess_configs[video][fps]=0.3'


{
    "object": "file",
    "id": "file-20251018114827-6zgrb",
    "purpose": "user_data",
    "filename": "demo.mp4",
    "bytes": 695110,
    "mime_type": "video/mp4",
    "created_at": 1760759307,
    "expire_at": 1761364107,
    "status": "processing",
    "preprocess_configs": {
        "video": {
            "fps": 0.3
        }
    }
}


`GET https://ark.ap-southeast.bytepluses.com/api/v3/files/{id}`
Retrieves file information using the file ID.

```mixin-react
return (<Tabs>
<Tabs.TabPane title="Quick start" key="0vnptpsU"><RenderMd content={`<span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_2abecd05ca2779567c6d32f0ddc7874d.png =20x) </span>[Model List](https://docs.byteplus.com/en/docs/ModelArk/1330310)<span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_a5fdd3028d35cc512a10bd71b982b6eb.png =20x) </span>[Model Billing](https://docs.byteplus.com/en/docs/ModelArk/1099320)<span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_57d0bca8e0d122ab1191b40101b5df75.png =20x) </span>[Files API Tutorial](https://docs.byteplus.com/en/docs/ModelArk/1885708)<span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_afbcf38bdec05c05089d5de5c3fd8fc8.png =20x) </span>[API Key](https://console.byteplus.com/ark/region:ark+ap-southeast-1/apiKey)
`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Authentication" key="AVJwaEeA"><RenderMd content={`This API supports API key and access key authentication. For more information, see [Authentication methods](https://docs.byteplus.com/en/docs/ModelArk/1298459).
`}></RenderMd></Tabs.TabPane></Tabs>);
```

&nbsp;
<span id="YP6bDFZC"></span>
## Request parameters
<span id="wcna9TMz"></span>
### Path parameters

---


id  `string` %%require%%
The ID of the file to retrieve.
<span id="5PiUp3nH"></span>
## Response parameters
The model returns the corresponding[ object](https://docs.byteplus.com/en/docs/ModelArk/1873424).

curl https://ark.ap-southeast.bytepluses.com/api/v3/files/file-20251119**** \
-H "Authorization: Bearer $ARK_API_KEY"


{
    "object": "file",
    "id": "file-20251119****",
    "purpose": "user_data",
    "filename": "demo.mp4",
    "bytes": 18773126,
    "mime_type": "video/mp4",
    "created_at": 1763552708,
    "expire_at": 1764157507,
    "status": "active"
}




`POST https://ark.ap-southeast.bytepluses.com/api/v3/images/generations` [Try](https://api.byteplus.com/api-explorer/?action=ImageGenerations&groupName=Image%20Generation%20API&serviceCode=ark&version=2024-01-01)
This document describes the input and output parameters for the image generation API.

**Image** ** generation capabilities by model**

* **seedream\-4.5==^new^==** **、seedream\-4.0**
   * Generate multiple image in sequence \- i.e., a batch of related images generated based on your input; set **sequential_image_generation** to `auto`
      * Generate a batch of related images based on your input of **++multiple reference images (2\-14) +++ **  ++ text prompt++ (the total number of input and output images ≤ 15).
      * Generate a batch of related images (up to 14) from a ++single reference image + text prompt++.
      * Generate a batch of related images (up to 15) from text ++prompt++.
   * Generate a single image (set **sequential_image_generation** to `disabled` **)** .
      * Generate a single image from **++multiple reference images (2\-14) ++ **  +++ text prompt++.
      * Generate a single image from ++a single reference image + text prompt++.
      * Generate a single image from ++text prompt++.
* **seedream\-3.0\-t2i**
   * Generate a single image from ++a text prompt++.
* **seededit\-3.0\-i2i**
   * Generate a single image from ++a single reference image+text prompt++.


```mixin-react
return (<Tabs>
<Tabs.TabPane title="Quick start" key="oOTdY3Sn"><RenderMd content={` [ ](#)[Experience Center](https://console.byteplus.com/ark/region:ark+ap-southeast-1/experience/vision?type=GenImage) <span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_2abecd05ca2779567c6d32f0ddc7874d.png =20x) </span>[Model List](https://docs.byteplus.com/en/docs/ModelArk/1330310#image-generation) <span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_a5fdd3028d35cc512a10bd71b982b6eb.png =20x) </span>[Model Billing](https://docs.byteplus.com/en/docs/ModelArk/1099320#image-generation) <span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_afbcf38bdec05c05089d5de5c3fd8fc8.png =20x) </span>[API Key](https://console.byteplus.com/ark/region:ark+ap-southeast-1/apiKey?apikey=%7B%7D)
 <span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_57d0bca8e0d122ab1191b40101b5df75.png =20x) </span>[API Call Guide](https://docs.byteplus.com/en/docs/ModelArk/1824690) <span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_f45b5cd5863d1eed3bc3c81b9af54407.png =20x) </span>[API Reference](https://docs.byteplus.com/en/docs/ModelArk/1666945) <span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_1609c71a747f84df24be1e6421ce58f0.png =20x) </span>[FAQs](https://docs.byteplus.com/en/docs/ModelArk/1359411) <span>![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_bef4bc3de3535ee19d0c5d6c37b0ffdd.png =20x) </span>[Model Activation](https://console.byteplus.com/ark/region:ark+ap-southeast-1/openManagement?LLM=%7B%7D&OpenTokenDrawer=false)
`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Authentication" key="bCgTrLVs"><RenderMd content={`This API only supports API Key authentication. Obtain a long\\-term API Key on the [ API Key management](https://console.byteplus.com/ark/region:ark+ap-southeast-1/apiKey?apikey=%7B%7D) page.
`}></RenderMd></Tabs.TabPane></Tabs>);
```


---


<span id="7thx2dVa"></span>
## Request parameters
<span id="BFVUvDi6"></span>
### Request body

---


**model** `string` %%require%%
The model ID used for image generation: [Model ID](https://docs.byteplus.com/en/docs/ModelArk/1330310#image-generation) or [inference endpoint](https://docs.byteplus.com/en/docs/ModelArk/1099522) (Endpoint ID).

---


**prompt ** `string` %%require%%
The text prompt used for image generation. (Prompt guide: [Seedream 4.0-4.5](https://docs.byteplus.com/en/docs/ModelArk/1829186), [Seedream 3.0](https://docs.byteplus.com/en/docs/ModelArk/1795150))
We recommend keeping the prompt under **600 English words**. Excessively long prompts may scatter information, causing the model to overlook details and focus only on major elements, which can result in missing details in the generated image.

---


**image** `string/array` 
> Seededit\-3.0\-t2i does not support this parameter.

Provide the image to edit as a Base64 string or an accessible URL. **Seedream\-4.5 and ** **seedream\-4.0** support inputting a single image or multiple images ([see the multi-image blending example](https://docs.byteplus.com/en/docs/ModelArk/1824121#multi-image-blending-multi-image-input-single-image-output)), while **seededit\-3.0\-i2i** only supports single\-image input.

* Image URL: Ensure that the image URL is accessible.
* Base64 encoding: The format must be `data:image/<image format>;base64,<Base64 encoding>`. Note that `<image format>` must be in lowercase, e.g., `data:image/png;base64,<base64_image>`.

:::tip Description

* Input Images must meet the following requirements:
   * Image format: JPEG, PNG (The seedream\-4.5 and seedream\-4.0 model also support WEBP、BMP、TIFF and GIF formats**==^new^==**)
   * Aspect ratio (width/height): 
      * Between [1/16, 16] (for seedream\-4.5 and seedream\-4.0)
      * Between [1/3, 3] (for seededit\-3.0\-i2i and seededit\-3.0\-t2i)
   * Width and height (px): \> 14
   * Size: Up to 10 MB
   * Total pixels: No more than `6000x6000=36000000` (The total pixel limit applies to the **product of the single image’s width and height**, rather than to either dimension individually.)
* Seedream\-4.5 and seedream\-4.0 support uploading a maximum of 14 reference images.


:::
---


**size** `String`  

```mixin-react
return (<Tabs>
<Tabs.TabPane title="seedream-4.5" key="BMB6AP1M"><RenderMd content={`Specify the output image dimensions. Two methods are available, but they cannot be used at the same time.

* Method 1 | Specify the resolution of the generated image, and describe its aspect ratio, shape, or purpose in the prompt using natural language. You let the model determine the width and height.
   * Optional values: \`2K\`, \`4K\`
* Method 2 | Specify the width and height of the generated image in pixels:
   * Default value: \`2048x2048\`
   * Total pixels range: [\`2560x1440=3,686,400\`, \`4096x4096=16,777,216\`] 
   * Aspect ratio range: [1/16, 16]

:::tip Description
When using Method 2, both the total pixel range and the aspect ratio range must be satisfied simultaneously. The total pixel limit applies to the **product of the single image’s width and height**, rather than to either dimension individually.

* **Valid example: ** \`3750x1250\`

Total pixel count: 3750x1250=4,687,500, which is within the acceptable range of [3,686,400, 16,777,216]. Aspect ratio: 3750/1250=3, which is within the acceptable range of [1/16, 16].

* **Invalid example: ** \`1500x1500\`

Total pixel count: 1500x1500 = 2,250,000, which does not meet the minimum requirement of 3,686,400. Aspect ratio: 1500/1500 = 1, which meets the range of [1/16, 16]. But it's invalid as it only meets one of the two requirements.
:::
Recommended width and height:

|Aspect ratio |Width and Height Pixel Values |
|---|---|
|1:1 |\`2048x2048\` |
|4:3 |\`2304x1728\` |
|3:4 |\`1728x2304\` |
|16:9 |\`2560x1440\` |
|9:16 |\`1440x2560\` |
|3:2 |\`2496x1664\` |
|2:3 |\`1664x2496\` |
|21:9 |\`3024x1296\` |

`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="seedream-4.0" key="kghENadO"><RenderMd content={`Specify the output image dimensions. Two methods are available, but they cannot be used at the same time.

* Method 1 | Specify the resolution of the generated image, and describe its aspect ratio, shape, or purpose in the prompt using natural language. You let the model determine the width and height.
   * Optional values: \`1K\`, \`2K\`, \`4K\`
* Method 2 | Specify the width and height of the generated image in pixels:
   * Default value: \`2048x2048\`
   * Total pixels range: [\`1280x720=921,600\`, \`4096x4096=16,777,216\`] 
   * Aspect ratio range: [1/16, 16]

:::tip Description
When using Method 2, both the total pixel range and the aspect ratio range must be satisfied simultaneously. The total pixel limit applies to the **product of the single image’s width and height**, rather than to either dimension individually.

* **Valid example: ** \`1600x600\`

Total pixel count: 1600x600 = 960,000, which is within the acceptable range of [921,600, 16,777,216]. Aspect ratio: 1600/600 = 8/3, which is within the acceptable range of [1/16, 16].

* **Invalid example: ** \`800x800\`

Total pixel count: 800x800 = 640,000, which does not meet the minimum requirement of 921,600. Aspect ratio: 800/800 = 1, which meets the range of [1/16, 16]. But it's invalid as it only meets one of the two requirements.
:::
Recommended width and height:

|Aspect ratio |Width and Height Pixel Values |
|---|---|
|1:1 |\`2048x2048\` |
|4:3 |\`2304x1728\` |
|3:4 |\`1728x2304\` |
|16:9 |\`2560x1440\` |
|9:16 |\`1440x2560\` |
|3:2 |\`2496x1664\` |
|2:3 |\`1664x2496\` |
|21:9 |\`3024x1296\` |

`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="seedream-3.0-t2i" key="MKsftGMr"><RenderMd content={`Set the width and height of the generated image in pixels.

* Default value: \`1024x1024\`
* The value range of total pixels:  [\`512x512\`, \`2048x2048\`]

Recommended width and height:

|Aspect ratio |Width and height in pixels Value |
|---|---|
|1:1 |\`1024x1024\` |
|4:3 |\`1152x864\` |
|3:4 |\`864x1152\` |
|16:9 |\`1280x720\` |
|9:16 |\`720x1280\` |
|3:2 |\`1248x832\` |
|2:3 |\`832x1248\` |
|21:9 |\`1512x648\` |

`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="seededit-3.0-i2i" key="icUtzktnqP"><RenderMd content={`Specify the width and height of the generated image in pixels. **Only support adaptive for now.** 

* adaptive: Compare your input image's dimensions with those in the table below and select the closest match for the output image. Specifically, the system selects the **first** available aspect ratio with the **smallest difference** from that of the original image.
* Preset width and height in pixels


|Width/Height |Width |High |
|---|---|---|
|0.33 |512 |1536 |
|0.35 |544 |1536 |
|0.38 |576 |1536 |
|0.4 |608 |1536 |
|0.42 |640 |1536 |
|0.47 |640 |1376 |
|0.51 |672 |1312 |
|0.55 |704 |1280 |
|0.56 |736 |1312 |
|0.6 |768 |1280 |
|0.63 |768 |1216 |
|0.66 |800 |1216 |
|0.67 |832 |1248 |
|0.7 |832 |1184 |
|0.72 |832 |1152 |
|0.75 |864 |1152 |
|0.78 |896 |1152 |
|0.82 |896 |1088 |
|0.85 |928 |1088 |
|0.88 |960 |1088 |
|0.91 |992 |1088 |
|0.94 |1024 |1088 |
|0.97 |1024 |1056 |
|1 |1024 |1024 |
|1.06 |1056 |992 |
|1.1 |1088 |992 |
|1.17 |1120 |960 |
|1.24 |1152 |928 |
|1.29 |1152 |896 |
|1.33 |1152 |864 |
|1.42 |1184 |832 |
|1.46 |1216 |832 |
|1.5 |1248 |832 |
|1.56 |1248 |800 |
|1.62 |1248 |768 |
|1.67 |1280 |768 |
|1.74 |1280 |736 |
|1.82 |1280 |704 |
|1.78 |1312 |736 |
|1.86 |1312 |704 |
|1.95 |1312 |672 |
|2 |1344 |672 |
|2.05 |1376 |672 |
|2.1 |1408 |672 |
|2.2 |1408 |640 |
|2.25 |1440 |640 |
|2.3 |1472 |640 |
|2.35 |1504 |640 |
|2.4 |1536 |640 |
|2.53 |1536 |608 |
|2.67 |1536 |576 |
|2.82 |1536 |544 |
|3 |1536 |512 |

`}></RenderMd></Tabs.TabPane></Tabs>);
```


---


**seed** `integer` `Default: -1`
> Only seedream\-3.0\-t2i and seededit\-3.0\-i2i support this parameter.

A random seed that controls the randomness of the generated content. The value range is [\-1, 2147483647].
Warning

* For the same request, the model will produce different results when using different seed values. For example, leaving the seed unspecified, setting it to \-1 (meaning use a random number), or manually changing the seed will all lead to different outputs.
* When the same seed is used for the same request, the model will generate similar results, but exact duplication is not guaranteed.


---


**sequential_image_generation** `string`  `Default: disabled`
> This parameter is only supported on seedream\-4.5 and seedream\-4.0 | See[ batch image output](https://docs.byteplus.com/en/docs/ModelArk/1824121#batch-image-output) for an example.

Whether to disable the batch generation feature.
:::tip Description
Batch image generation: a batch of thematically related images generated based on your input content.
:::
Valid values:

* `auto`: The model automatically determines whether to return multiple images and the number of returned images based on the user's prompt.
* `disabled`: Only one image is generated.


---


**sequential_image_generation_options ** `object` 
> Only seedream\-4.5 and seedream\-4.0 support this parameter.

Configuration for the batch image generation feature; Only effective when **sequential_image_generation** is set to `auto`.

Attributes

---


sequential_image_generation_options.**max_images** ** ** `integer` `Default: 15`
Specifies the maximum number of images to generate in this request.

* Value range: [1, 15]

:::tip Description
The actual number of generated images is determined jointly by **max_images ** and the number of input reference images. **Number of input reference images + Number of generated images ≤ 15**.

:::

---


**stream**  `boolean` `Default: false`
> Only seedream\-4.5 and seedream\-4.0 support this parameter | See [Streaming Output ](https://docs.byteplus.com/en/docs/ModelArk/1824121#streaming-output)for an example.

Whether to enable streaming output mode.

* `false`: All output images are returned at once.
* `true`: Each output image is returned immediately after generated. Applicable for both single and batch image generation.


---


**guidance_scale** `float`
> Default value for seedream\-3.0\-t2i: 2.5
> Default value for seededit\-3.0\-i2i: 5.5
> Seedream\-4.5 and seedream\-4.0 are not supported.

This parameter controls how closely the generated image follows the prompt, affecting the model’s degree of creative freedom. A higher value reduces freedom and increases adherence to the prompt.
Valid values: [`1`, `10`] 

---


**response_format** `string` `Default: url`
Specifies how the generated images are returned.
The generated image is in JPEG and can be returned in the following two ways:

* `url`: Returns a download link for the image. **The link is valid for 24 hours after the image is generated.** 
* `b64_json`: Returns the image data in JSON as a Base64\-encoded string.


---


**watermark**  `boolean` `Default: true`
Adds a watermark to the generated image.

* `false`: No watermark.
* `true`: Adds a "AI generated" watermark on the bottom\-right corner of the image.


---


**optimize_prompt_options==^new^==** ** ** `object` 
> Only seedream\-4.5 (only supports `standard` mode) and seedream\-4.0 support this parameter.

Configuration for prompt optimization feature.

optimize_prompt_options.**mode ** `string` `Default: standard`
Set the mode for the prompt optimization feature. 

* `standard`：Higher quality, longer generation time.
* `fast`：Faster but at a more average quality.


---


&nbsp;
<span id="7P96iLnc"></span>
## Response parameters
<span id="Hrya4y9k"></span>
### Streaming response parameters
See [Streaming Response](https://docs.byteplus.com/en/docs/ModelArk/1824137).
&nbsp;
<span id="1AxnwQZN"></span>
### Non\-streaming response parameters

---


**model** `String`
The model ID used for image generation (`model name-version`).

---


**created** `integer`
The Unix timestamp in seconds of the creation time of the request.

---


**data** `array`
Information of the output images.
:::tip Description
When generating a batch of images with the seedream\-4.5 and seedream\-4.0 model, if an image fails to generate：

* If the failure is due to the rejection by content filter: The next generation task will still be requested, other image generation tasks in the same request will not be affected.
* If the failure is due to an internal service error (500): The next picture generation task will not be requested.


:::
Possible type
Image information `object`
Successfully generated information.

Attributes
data.**url ** `string`
The URL of the image, returned when **response_format** is specified as `url`. This link will expire **within 24 hours** of generation. Be sure to save the image before expiration.

---


data.**b64_json** `string`
The Base64 information of the image; returned when **response_format** is specified as `b64_json`.

---


data.**size** `string`
> Only seedream\-4.5 and seedream\-4.0 support this parameter.

The width and height of the image in pixels, in the format `<width>x<height>`, such as `2048×2048`.


---


Error message `object`
Error message for a failed image generation.

Attributes
data.**error** `Object`
Error message structure.

Attributes

---


data.error.**code**
The error code for a failed image generation. See [Error Codes](https://docs.byteplus.com/en/docs/ModelArk/1299023).

---


data.error.**message**
Error message for a failed image generation.




---


**usage** `Object`
Usage information for the current request.

Attributes

---


usage.**generated_images ** `integer`
The number of images successfully generated by the model, excluding failed generations.
**Note**: Billing is based on the number of successfully generated images.

---


usage.**output_tokens** `integer`
The number of tokens consumed for the images generated by the model.
The calculation logic is to calculate `sum(image width*image height)/256` and then round the result to an integer.

---


usage.**total_tokens** `integer`
The total number of tokens consumed by this request.
This value is the same as **output_tokens ** as input tokens are currently not calculated.

**error**  `object`
The error message for this request, if any.

Attributes

---


error.**code** `String` 
See [Error Codes](https://docs.byteplus.com/en/docs/ModelArk/1299023).

---


error.**message** `String`
Error message

&nbsp;


import os
# Install SDK:pip install byteplus-python-sdk-v2  .
from byteplussdkarkruntime import Ark 

client = Ark(
    #The base URL for model invocation
    base_url="https://ark.ap-southeast.bytepluses.com/api/v3", 
    # Get API Key：https://console.byteplus.com/ark/region:ark+ap-southeast-1/apikey
    api_key=os.getenv('ARK_API_KEY'), 
)
 
imagesResponse = client.images.generate( 
    #Replace with Model ID
    model="seedream-4-5-251128",
    prompt="Vibrant close-up editorial portrait, model with piercing gaze, wearing a sculptural hat, rich color blocking, sharp focus on eyes, shallow depth of field, Vogue magazine cover aesthetic, shot on medium format, dramatic studio lighting.",
    size="2K",
    response_format="url",
    watermark=False
) 
 
print(imagesResponse.data[0].url)


{
    "model": "seedream-4-5-251128",
    "created": 1757323224,
    "data": [
        {
            "url": "https://...",
            "size": "1760x2368"
        }
    ],
    "usage": {
        "generated_images": 1,
        "output_tokens": 16280,
        "total_tokens": 16280
    }
}


import os
# Install SDK:pip install byteplus-python-sdk-v2 
from byteplussdkarkruntime import Ark 

client = Ark(
    #The base URL for model invocation
    base_url="https://ark.ap-southeast.bytepluses.com/api/v3", 
    # Get API Key：https://console.byteplus.com/ark/region:ark+ap-southeast-1/apikey
    api_key=os.getenv('ARK_API_KEY'), 
)
 
imagesResponse = client.images.generate( 
    #Replace with Model ID
    model="seedream-4-5-251128", 
    prompt="Keep the model's pose and the flowing shape of the liquid dress unchanged. Change the clothing material from silver metal to completely transparent clear water (or glass). Through the liquid water, the model's skin details are visible. Lighting changes from reflection to refraction.",
    image="https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_image/seedream4_5_imageToimage.png",
    size="2K",
    response_format="url",
    watermark=False
) 
 
print(imagesResponse.data[0].url)


{
    "model": "seedream-4-5-251128",
    "created": 1757323224,
    "data": [
        {
            "url": "https://...",
            "size": "1760x2368"
        }
    ],
    "usage": {
        "generated_images": 1,
        "output_tokens": 16280,
        "total_tokens": 16280
    }
}


import os
# Install SDK:pip install byteplus-python-sdk-v2 
from byteplussdkarkruntime import Ark 

client = Ark(
    #The base URL for model invocation
    base_url="https://ark.ap-southeast.bytepluses.com/api/v3", 
    # Get API Key：https://console.byteplus.com/ark/region:ark+ap-southeast-1/apikey
    api_key=os.getenv('ARK_API_KEY'), 
) 
imagesResponse = client.images.generate( 
    #Replace with Model ID
    model="seedream-4-5-251128",
    prompt="Replace the clothing in image 1 with the outfit from image 2.",
    image=["https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_image/seedream4_imagesToimage_1.png", "https://ark-project.tos-cn-beijing.volces.com/doc_image/seedream4_5_imagesToimage_2.png"],
    size="2K",
    sequential_image_generation="disabled",
    response_format="url",
    watermark=False
) 
 
print(imagesResponse.data[0].url)


{
    "model": "seedream-4-5-251128",
    "created": 1757323224,
    "data": [
        {
            "url": "https://...",
            "size": "1760x2368"
        }
    ],
    "usage": {
        "generated_images": 1,
        "output_tokens": 16280,
        "total_tokens": 16280
    }
}


import os
# Install SDK:pip install byteplus-python-sdk-v2  .
from byteplussdkarkruntime import Ark 
from byteplussdkarkruntime.types.images.images import SequentialImageGenerationOptions

client = Ark(
    #The base URL for model invocation
    base_url="https://ark.ap-southeast.bytepluses.com/api/v3", 
    # Get API Key：https://console.byteplus.com/ark/region:ark+ap-southeast-1/apikey
    api_key=os.getenv('ARK_API_KEY'), 
) 
 
imagesResponse = client.images.generate( 
    #Replace with Model ID
    model="seedream-4-5-251128",
    prompt="Generate 3 images of a girl and a cow plushie happily riding a roller coaster in an amusement park, depicting morning, noon, and night.",
    image=["https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_image/seedream4_imagesToimages_1.png", "https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_image/seedream4_imagesToimages_2.png"],
    size="2K",
    sequential_image_generation="auto",
    sequential_image_generation_options=SequentialImageGenerationOptions(max_images=3),
    response_format="url",
    watermark=False
) 
 
# Iterate through all image data
for image in imagesResponse.data:
    # Output the current image's URL and size
    print(f"URL: {image.url}, Size: {image.size}")

{
  "model": "seedream-4-5-251128",
  "created": 1757388756,
  "data": [
    {
      "url": "https://...",
      "size": "2720x1536"
    },
    {
      "url": "https://...",
      "size": "2720x1536"
    },
    {
      "url": "https://...",
      "size": "2720x1536"
    }
  ],
  "usage": {
    "generated_images": 3,
    "output_tokens": 48960,
    "total_tokens": 48960
  }
}


import os
# Install SDK:pip install byteplus-python-sdk-v2 
from byteplussdkarkruntime import Ark 
from byteplussdkarkruntime.types.images.images import SequentialImageGenerationOptions

client = Ark(
    #The base URL for model invocation
    base_url="https://ark.ap-southeast.bytepluses.com/api/v3", 
    # Get API Key：https://console.byteplus.com/ark/region:ark+ap-southeast-1/apikey
    api_key=os.getenv('ARK_API_KEY'), 
) 

if __name__ == "__main__":
    stream = client.images.generate(
        #Replace with Model ID
        model="seedream-4-5-251128",
        prompt="Referring to Figure 1, generate four images with characters wearing sunglasses, riding motorcycles, wearing hats, and holding lollipops",
        image="https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_image/seedream4_imageToimages_1.png",
        size="2K",
        sequential_image_generation="auto",
        sequential_image_generation_options=SequentialImageGenerationOptions(max_images=4),
        response_format="url",
        stream=True,
        watermark=False
    )
    for event in stream:
        if event is None:
            continue
        if event.type == "image_generation.partial_failed":
            print(f"Stream generate images error: {event.error}")
            if event.error is not None and event.error.code.equal("InternalServiceError"):
                break
        elif event.type == "image_generation.partial_succeeded":
            if event.error is None and event.url:
                print(f"recv.Size: {event.size}, recv.Url: {event.url}")
        elif event.type == "image_generation.completed":
            if event.error is None:
                print("Final completed event:")
                print("recv.Usage:", event.usage)
        elif event.type == "image_generation.partial_image":
            print(f"Partial image index={event.partial_image_index}, size={len(event.b64_json)}")


event: image_generation.partial_succeeded
data: {
  "type": "image_generation.partial_succeeded",
  "model": "seedream-4-5-251128",
  "created": 1757396757,
  "image_index": 0,
  "url": "https://...",
  "size": "2496x1664"
}

event: image_generation.partial_succeeded
data: {
  "type": "image_generation.partial_succeeded",
  "model": "seedream-4-5-251128",
  "created": 1757396785,
  "image_index": 1,
  "url": "https://...",
  "size": "2496x1664"
}

event: image_generation.partial_succeeded
data: {
  "type": "image_generation.partial_succeeded",
  "model": "seedream-4-5-251128",
  "created": 1757396825,
  "image_index": 2,
  "url": "https://...",
  "size": "2496x1664"
}

event: image_generation.completed
data: {
  "type": "image_generation.completed",
  "model": "seedream-4-5-251128",
  "created": 1757396825,
  "usage": {
    "generated_images": 3,
    "output_tokens": 48672,
    "total_tokens": 48672
  }
}

data: [DONE]


You can upload, retrieve, list, and delete files using the Files API.
In multimodal understanding scenarios, the Files API is used in combination with the Responses API, offering the following advantages:

* Large file support: Supports uploading files up to 512 MB, meeting the needs for large file processing.
* File reuse: Supports reusing files across multiple requests via File ID, eliminating the need for repeated uploads and saving on public network download latency.
* Reduced inference time: Decouples data preprocessing from model inference, preventing the need to re-upload content with each request and reducing latency caused by preprocessing.

<span id="62e9d75a"></span>
## Prerequisites
[Obtain API Key](https://console.byteplus.com/ark/apiKey)
<span id="c4765823"></span>
## API documentation
[Files API reference](https://docs.byteplus.com/en/docs/ModelArk/1870405)
<span id="821e2a5c"></span>
## Usage examples
<span id="963e0807"></span>
### Upload files
The Files API allows uploading various file types. After a successful upload, a File ID is returned. The File ID can be reused in multiple requests without needing to re-upload the content, reducing public network download latency. 
To upload files larger than 50 MB, or to reuse a file across multiple requests, use the Files API to upload the file, then use the File ID in the Responses API to initiate a request.

```mixin-react
return (<Tabs>
<Tabs.TabPane title="Curl" key="G6QRlu9jzn"><RenderMd content={`\`\`\`Bash
curl https://ark.ap-southeast.bytepluses.com/api/v3/files \\
-H "Authorization: Bearer $ARK_API_KEY" \\
-F 'purpose=user_data' \\
-F 'file=@/Users/doc/demo.mp4' \\
-F 'preprocess_configs[video][fps]=0.3'
\`\`\`

The response parameters are as follows:
\`\`\`Bash
{
    "object": "file",
    "id": "file-20251018114827-6zgrb",
    "purpose": "user_data",
    "filename": "demo.mp4",
    "bytes": 695110,
    "mime_type": "video/mp4",
    "created_at": 1760759307,
    "expire_at": 1761364107,
    "status": "processing",
    "preprocess_configs": {
        "video": {
            "fps": 0.3
        }
    }
}
\`\`\`

`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Python SDK" key="TBr8qFIJMK"><RenderMd content={`\`\`\`Python
import os
from byteplussdkarkruntime import Ark

client = Ark(
    base_url='https://ark.ap-southeast.bytepluses.com/api/v3',
    api_key=os.getenv('ARK_API_KEY')
)

file = client.files.create(
    # replace with your local video path
    file=open("/Users/doc/demo.mp4", "rb"),
    purpose="user_data",
    preprocess_configs={
        "video": {
            "fps": 0.3,  # define the sampling fps of the video, default is 1.0
        }
    }
)
print(file)
\`\`\`

`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Go SDK" key="a43wfekM1h"><RenderMd content={`\`\`\`Go
package main

import (
    "context"
    "fmt"
    "os"

    "github.com/byteplus-sdk/byteplus-go-sdk-v2/service/arkruntime"
    "github.com/byteplus-sdk/byteplus-go-sdk-v2/service/arkruntime/model/file"
    "github.com/byteplus-sdk/byteplus-go-sdk-v2/byteplus"
)

func main() {
    client := arkruntime.NewClientWithApiKey(
        os.Getenv("ARK_API_KEY"),
        arkruntime.WithBaseUrl("https://ark.ap-southeast.bytepluses.com/api/v3"),
    )
    ctx := context.Background()

    data, err := os.Open("/Users/doc/demo.mp4")
    if err != nil {
        fmt.Printf("read file error: %v\\n", err)
        return
    }
    fileInfo, err := client.UploadFile(ctx, &file.UploadFileRequest{
        File:    data,
        Purpose: file.PurposeUserData,
        PreprocessConfigs: &file.PreprocessConfigs{
            Video: &file.Video{
                Fps: byteplus.Float64(0.3),
            },
        },
    })

    if err != nil {
        fmt.Printf("upload file error: %v", err)
        return
    }
    fmt.Printf("file info: %v\\n", fileInfo)

}
\`\`\`


`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Java SDK" key="u8zZgGSNQl"><RenderMd content={`\`\`\`Java
package com.ark.sample;

import com.byteplus.ark.runtime.model.files.FileMeta;
import com.byteplus.ark.runtime.model.files.PreprocessConfigs;
import com.byteplus.ark.runtime.model.files.UploadFileRequest;
import com.byteplus.ark.runtime.model.files.Video;
import com.byteplus.ark.runtime.service.ArkService;
import java.io.File;

public class demo {

    public static void main(String[] args) {
        String apiKey = System.getenv("ARK_API_KEY");
        ArkService service = ArkService.builder().apiKey(apiKey).baseUrl("https://ark.ap-southeast.bytepluses.com/api/v3").build();

        System.out.println("===== Upload File Example=====");
        FileMeta fileMeta;
        fileMeta = service.uploadFile(
                UploadFileRequest.builder().
                        file(new File("/Users/doc/demo.mp4")) // replace with your image file path
                        .purpose("user_data")
                        .preprocessConfigs(PreprocessConfigs.builder().video(new Video(0.3)).build())
                        .build());
        System.out.println("Uploaded file Meta: " + fileMeta);

        service.shutdownExecutor();
    }
}
\`\`\`


`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Compatible with OpenAI SDK" key="i8j4CX1Moe"><RenderMd content={`\`\`\`Python
import os
from openai import OpenAI

client = OpenAI(
    base_url='https://ark.ap-southeast.bytepluses.com/api/v3',
    api_key=os.getenv('ARK_API_KEY')
)

file = client.files.create(
    # replace with your local video path
    file=open("/Users/doc/demo.mp4", "rb"),
    purpose="user_data",
    extra_body={
        "preprocess_configs":{
            "video": {
                "fps": 0.3
            }
        }
    }
)
print(file)
\`\`\`

`}></RenderMd></Tabs.TabPane></Tabs>);
 ```

<span id="d75377d6"></span>
#### File storage limitations

* Single file size: 512 MB.
* Total storage capacity: 20 GB.
* File storage duration: By default, files are stored for 7 days. You can customize the storage validity period using the **expire_at**  parameter, with a value range of 1 – 30 days.

<span id="fd98059d"></span>
#### File preprocessing
When uploading files using the Files API, the interface will preprocess the files based on their type.

* Video files: By default, segments are extracted at a rate of 1 frame per second (FPS). You can set a custom frame rate using **preprocess_configs.video.fps**
   * For long videos with minimal scene changes, a lower FPS value can be set;
   * For precise capture of scene changes, a higher FPS value can be set. 
   After file preprocessing, using the File ID in the Responses API can shorten inference duration.
* PDF files: Pages are processed into multiple images. During preprocessing, the split images are not scaled in resolution, ensuring that the original information in the PDF file is retained completely and clearly.

<span id="34ad0fff"></span>
#### Preprocessing timeout limit
When using the Files API for file preprocessing, the timeout limit is 5 minutes. Timeouts are typically affected by factors such as video duration, number of PDF pages, pixel count per page, and pixel count per frame.

* **Timeout mitigation:** Check for excessive pixel resolution first. Frame extraction from 1080p videos is especially prone to timeouts. It is recommended to compress videos to 720p or lower.
   **Note**: Higher original resolution does not improve final results. The model automatically compresses resolution during the inference stage, so increasing the original pixel resolution provides no benefit to output quality.
* **Video compression tools and commands:** Below is an example command to compress a video to 720p. To download FFmpeg, see [Download FFmpeg](http://ffmpeg.org/download.html).

```Bash
ffmpeg -i input.mp4 \
  -vf "scale=1280:720" \
  -c:v libx264 -crf 23 \
  -c:a aac -b:a 128k \
  output_720p.mp4
```

<span id="81920512"></span>
#### File types
The Files API supports various file types, as detailed below.

| | | | \
|File type |File format |MIME type |
|---|---|---|
| | | | \
|Picture |.jpg、.jpeg、.png、.gif、.webp、.bmp、.tiff、.ico、.icns、.sgi、.jp2、.heic、.heif |`image/jpeg`、`image/png`、`image/gif`、`image/webp`、`image/bmp`、`image/tiff`、`image/x-icon`、`image/icns`、`image/sgi`、`image/jp2`、`image/heic`、`image/heif` |
| | | | \
|Video |.mp4、.avi、.mov |`video/mp4`、`video/avi`、`video/mov` |
| | | | \
|PDF |.pdf |`application/pdf` |

<span id="91473606"></span>
### Retrieve a file
Retrieve file information using the File ID, such as file size, expiration time, MIME type, and file processing status.
> Only when the file processing status is **active** can it be used as model input in the Responses API.


```mixin-react
return (<Tabs>
<Tabs.TabPane title="Curl" key="QxZ6NyTRlp"><RenderMd content={`\`\`\`Bash
curl https://ark.ap-southeast.bytepluses.com/api/v3/files/file-20251014**** \\
-H "Authorization: Bearer $ARK_API_KEY"
\`\`\`

`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Python SDK" key="gFbISBM1dB"><RenderMd content={`\`\`\`Python
import os
from byteplussdkarkruntime import Ark

# Get API Key：https://console.byteplus.com/ark/region:ark+ap-southeast-1/apikey
api_key = os.getenv('ARK_API_KEY')

client = Ark(
    base_url='https://ark.ap-southeast.bytepluses.com/api/v3',
    api_key=api_key,
)

# Retrieve file
response = client.files.retrieve(
    file_id="file-2025******"
)

print(response)
\`\`\`


`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Go SDK" key="xVX0QAbRE6"><RenderMd content={`\`\`\`Go
package main

import (
    "context"
    "fmt"
    "os"

    "github.com/byteplus-sdk/byteplus-go-sdk-v2/service/arkruntime"
)

func main() {
    client := arkruntime.NewClientWithApiKey(os.Getenv("ARK_API_KEY"),arkruntime.WithBaseUrl("https://ark.ap-southeast.bytepluses.com/api/v3"))
    ctx := context.Background()

    fileInfo, err := client.RetrieveFile(ctx, "file-20251114****") // update file info
    if err != nil {
        fmt.Printf("get file status error: %v", err)
        return
    }
    fmt.Printf("file info: %v", fileInfo)

}
\`\`\`


`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Java SDK" key="xA0TVkmXXj"><RenderMd content={`\`\`\`Java
package com.ark.sample;

import com.byteplus.ark.runtime.model.files.FileMeta;
import com.byteplus.ark.runtime.service.ArkService;

public class demo {
    public static void main(String[] args) {
        String apiKey = System.getenv("ARK_API_KEY");
        ArkService service = ArkService.builder().apiKey(apiKey).baseUrl("https://ark.ap-southeast.bytepluses.com/api/v3").build();

        // Retrieve file
        FileMeta fileMeta = service.retrieveFile("file-20251117****");
        System.out.println("Retrieve File:" + fileMeta);

        service.shutdownExecutor();
    }
}
\`\`\`


`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Compatible with OpenAI SDK" key="lVa411RPj5"><RenderMd content={`\`\`\`Python
import os
from openai import OpenAI

api_key = os.getenv('ARK_API_KEY')

client = OpenAI(
    base_url='https://ark.ap-southeast.bytepluses.com/api/v3',
    api_key=api_key,
)

response = client.files.retrieve(
    file_id="file-20251117****"
)

print(response)
\`\`\`


`}></RenderMd></Tabs.TabPane></Tabs>);
 ```

<span id="34f747b5"></span>
### List files
Query the list of uploaded files via the Files API.

```mixin-react
return (<Tabs>
<Tabs.TabPane title="Curl" key="fEjJTE4GAy"><RenderMd content={`\`\`\`Bash
curl https://ark.ap-southeast.bytepluses.com/api/v3/files \\
-H "Authorization: Bearer $ARK_API_KEY"
\`\`\`

`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Python SDK" key="xarONpMa4Y"><RenderMd content={`\`\`\`Python
import os
from byteplussdkarkruntime import Ark

api_key = os.getenv('ARK_API_KEY')

client = Ark(
    base_url='https://ark.ap-southeast.bytepluses.com/api/v3',
    api_key=api_key,
)

response = client.files.list()

print(response)
\`\`\`


`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Go SDK" key="LX5Jq00GZM"><RenderMd content={`\`\`\`Go
package main

import (
    "context"
    "fmt"
    "os"

    "github.com/byteplus-sdk/byteplus-go-sdk-v2/service/arkruntime"
    "github.com/byteplus-sdk/byteplus-go-sdk-v2/service/arkruntime/model/file"
)

func main() {
    client := arkruntime.NewClientWithApiKey(os.Getenv("ARK_API_KEY"),arkruntime.WithBaseUrl("https://ark.ap-southeast.bytepluses.com/api/v3"),)
    ctx := context.Background()

    fileInfo, err := client.ListFiles(ctx, &file.ListFilesRequest{}) 
    if err != nil {
        fmt.Printf("get file List error: %v", err)
        return
    }
    fmt.Printf("file List: %v", fileInfo)
}
\`\`\`


`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Java SDK" key="bGyFkKuDif"><RenderMd content={`\`\`\`Java
package com.ark.sample;

import com.byteplus.ark.runtime.model.files.ListFilesResponse;
import com.byteplus.ark.runtime.model.files.ListFilesRequest;
import com.byteplus.ark.runtime.service.ArkService;

public class demo {
    public static void main(String[] args) {
        String apiKey = System.getenv("ARK_API_KEY");
        ArkService service = ArkService.builder().apiKey(apiKey).baseUrl("https://ark.ap-southeast.bytepluses.com/api/v3").build();

        ListFilesRequest request = new ListFilesRequest();
        ListFilesResponse ListFiles = service.listFiles(request);
        System.out.println("List Files:" + ListFiles);

        service.shutdownExecutor();
    }
}
\`\`\`


`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Compatible with OpenAI SDK" key="XSDQMDZyZM"><RenderMd content={`\`\`\`Python
import os
from openai import OpenAI

api_key = os.getenv('ARK_API_KEY')

client = OpenAI(
    base_url='https://ark.ap-southeast.bytepluses.com/api/v3',
    api_key=api_key,
)

response = client.files.list()

print(response)
\`\`\`


`}></RenderMd></Tabs.TabPane></Tabs>);
 ```

<span id="9eb4f3d2"></span>
### Delete a file
Uploaded files are stored for 7 days by default. You can customize the storage validity period using the **expire_at**  parameter, with a range of 1 to 30 days. Files will be automatically deleted after exceeding the storage validity period.
It is also supported to delete uploaded files via the Files API. The usage example is as follows:

```mixin-react
return (<Tabs>
<Tabs.TabPane title="Curl" key="nhJdnSPvnM"><RenderMd content={`\`\`\`Bash
curl https://ark.ap-southeast.bytepluses.com/api/v3/files/file-20251014**** \\
-X DELETE \\
-H "Authorization: Bearer $ARK_API_KEY"
\`\`\`

`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Python SDK" key="BU9WZmzmpH"><RenderMd content={`\`\`\`Python
import os
from byteplussdkarkruntime import Ark

api_key = os.getenv('ARK_API_KEY')

client = Ark(
    base_url='https://ark.ap-southeast.bytepluses.com/api/v3',
    api_key=api_key,
)

if __name__ == "__main__":
    try:
        client.files.delete(
            file_id="file-20251014****"
        )
    except Exception as e:
        print(f"failed to delete response: {e}")
\`\`\`


`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Go SDK" key="LvQs3GNvYs"><RenderMd content={`\`\`\`Go
package main

import (
    "context"
    "fmt"
    "os"

    "github.com/byteplus-sdk/byteplus-go-sdk-v2/service/arkruntime"
)

func main() {
    client := arkruntime.NewClientWithApiKey(os.Getenv("ARK_API_KEY"),arkruntime.WithBaseUrl("https://ark.ap-southeast.bytepluses.com/api/v3"),)
    ctx := context.Background()

    fileInfo, err := client.DeleteFile(ctx, "file-20251114****") 
    if err != nil {
        fmt.Printf("delete file error: %v", err)
        return
    }
    fmt.Printf(" delete file: %v", fileInfo)
}
\`\`\`


`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Java SDK" key="YIJ48qyhHM"><RenderMd content={`\`\`\`Java
package com.ark.sample;

import com.byteplus.ark.runtime.model.files.DeleteFileResponse;
import com.byteplus.ark.runtime.service.ArkService;

public class demo {
    public static void main(String[] args) {
        String apiKey = System.getenv("ARK_API_KEY");
        ArkService service = ArkService.builder().apiKey(apiKey).baseUrl("https://ark.ap-southeast.bytepluses.com/api/v3").build();

        // delete file
        DeleteFileResponse deleteFile = service.deleteFile("file-20251117****");
        System.out.println("Delete File:" + deleteFile);

        service.shutdownExecutor();
    }
}
\`\`\`


`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Compatible with OpenAI SDK" key="s5rqGJutWX"><RenderMd content={`\`\`\`Python
import os
from openai import OpenAI

api_key = os.getenv('ARK_API_KEY')

client = OpenAI(
    base_url='https://ark.ap-southeast.bytepluses.com/api/v3',
    api_key=api_key,
)

if __name__ == "__main__":
    try:
        response = client.files.delete(
            file_id="file-20251119****"
        )
        print(response)
    except Exception as e:
        print(f"failed to delete response: {e}")
\`\`\`


`}></RenderMd></Tabs.TabPane></Tabs>);
 ```

<span id="8a45d4bd"></span>
## Use File ID for multimodal understanding
For scenarios where files are large or need to be reused across multiple requests, it is recommended to upload files via the Files API and then use the File ID in the Responses API to achieve multimodal understanding. 
For specific examples, see [Video Understanding](/docs/ModelArk/1895586), [Image Understanding](/docs/ModelArk/1362931), and [Document Understanding](/docs/ModelArk/1902647).
After uploading a file, you need to wait until file processing is complete (i.e., when **status** is active) before using the corresponding File ID for analysis in the Responses API. The following is sample code for video understanding.

```mixin-react
return (<Tabs>
<Tabs.TabPane title="Curl" key="j9eY0YiN0b"><RenderMd content={`1. Upload video file to obtain File ID.
   \`\`\`Bash
   curl https://ark.ap-southeast.bytepluses.com/api/v3/files \\
   -H "Authorization: Bearer $ARK_API_KEY" \\
   -F 'purpose=user_data' \\
   -F 'file=@/Users/doc/demo.mp4' \\
   -F 'preprocess_configs[video][fps]=0.3'
   \`\`\`

2. Reference File ID in Responses API.
   \`\`\`Bash
   curl https://ark.ap-southeast.bytepluses.com/api/v3/responses \\
   -H "Authorization: Bearer $ARK_API_KEY" \\
   -H 'Content-Type: application/json' \\
   -d '{
       "model": "seed-1-6-250915",
       "input": [
           {
               "role": "user",
               "content": [
                   {
                       "type": "input_file",
                       "file_id": "file-20251018****"
                   },
                   {
                       "type": "input_text",
                        "text": "Describe the sequence of actions performed by the person in the video and output the results in JSON format. Include start_time, end_time, event, and danger (boolean), and express timestamps in HH:mm:ss format."
                   }
               ]
           }
       ]
   }'
   \`\`\`

`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Python SDK" key="RT64gWFGRa"><RenderMd content={`\`\`\`Python
import asyncio
import os
from byteplussdkarkruntime import AsyncArk 
from byteplussdkarkruntime.types.responses.response_completed_event import ResponseCompletedEvent
from byteplussdkarkruntime.types.responses.response_reasoning_summary_text_delta_event import ResponseReasoningSummaryTextDeltaEvent
from byteplussdkarkruntime.types.responses.response_output_item_added_event import ResponseOutputItemAddedEvent
from byteplussdkarkruntime.types.responses.response_text_delta_event import ResponseTextDeltaEvent
from byteplussdkarkruntime.types.responses.response_text_done_event import ResponseTextDoneEvent

client = AsyncArk(
    base_url='https://ark.ap-southeast.bytepluses.com/api/v3',
    api_key=os.getenv('ARK_API_KEY')
)

async def main():
    # upload video file
    print("Upload video file")
    file = await client.files.create(
        # replace with your local video path
        file=open("/Users/doc/demo.mp4", "rb"),
        purpose="user_data",
        preprocess_configs={
            "video": {
                "fps": 0.3,  # define the sampling fps of the video, default is 1.0
            }
        }
    )
    print(f"File uploaded: {file.id}")

    # Wait for the file to finish processing
    await client.files.wait_for_processing(file.id)
    print(f"File processed: {file.id}")

    stream = await client.responses.create(
        model="seed-1-6-250915",
        input=[
            {"role": "user", "content": [
                {
                    "type": "input_video",
                    "file_id": file.id  # ref video file id
                },
                {
                    "type": "input_text",
                    "text": "Describe the sequence of actions performed by the person in the video and output the results in JSON format. Include start_time, end_time, event, and danger (boolean), and express timestamps in HH:mm:ss format."      
                }
            ]},
        ],
        caching={
            "type": "enabled",
        },
        store=True,
        stream=True
    )
    
    async for event in stream:
        if isinstance(event, ResponseReasoningSummaryTextDeltaEvent):
            print(event.delta, end="")
        if isinstance(event, ResponseOutputItemAddedEvent):
            print("\\noutPutItem " + event.type + " start:")
        if isinstance(event, ResponseTextDeltaEvent):
            print(event.delta,end="")
        if isinstance(event, ResponseTextDoneEvent):
            print("\\noutPutTextDone.")
        if isinstance(event, ResponseCompletedEvent):
            print("Response Completed. Usage = " + event.response.usage.model_dump_json())

if __name__ == "__main__":
    asyncio.run(main())
\`\`\`


`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Go SDK" key="xteQaSxmvJ"><RenderMd content={`\`\`\`Go
package main

import (
    "context"
    "fmt"
    "io"
    "os"
    "time"

    "github.com/byteplus-sdk/byteplus-go-sdk-v2/service/arkruntime"
    "github.com/byteplus-sdk/byteplus-go-sdk-v2/service/arkruntime/model/file"
    "github.com/byteplus-sdk/byteplus-go-sdk-v2/service/arkruntime/model/responses"
    "github.com/byteplus-sdk/byteplus-go-sdk-v2/byteplus"
)

func main() {
    client := arkruntime.NewClientWithApiKey(
        // Get API Key：https://console.byteplus.com/ark/region:ark+ap-southeast-1/apikey
        os.Getenv("ARK_API_KEY"),
        arkruntime.WithBaseUrl("https://ark.ap-southeast.bytepluses.com/api/v3"),
    )
    ctx := context.Background()

    fmt.Println("----- upload video data -----")
    data, err := os.Open("/Users/doc/demo.mp4")
    if err != nil {
        fmt.Printf("read file error: %v\\n", err)
        return
    }
    fileInfo, err := client.UploadFile(ctx, &file.UploadFileRequest{
        File:    data,
        Purpose: file.PurposeUserData,
        PreprocessConfigs: &file.PreprocessConfigs{
            Video: &file.Video{
                Fps: byteplus.Float64(0.3),
            },
        },
    })

    if err != nil {
        fmt.Printf("upload file error: %v", err)
        return
    }

    // Wait for the file to finish processing
    for fileInfo.Status == file.StatusProcessing {
        fmt.Println("Waiting for video to be processed...")
        time.Sleep(2 * time.Second)
        fileInfo, err = client.RetrieveFile(ctx, fileInfo.ID) // update file info
        if err != nil {
            fmt.Printf("get file status error: %v", err)
            return
        }
    }
    fmt.Printf("Video processing completed: %s, status: %s\\n", fileInfo.ID, fileInfo.Status)
    inputMessage := &responses.ItemInputMessage{
        Role: responses.MessageRole_user,
        Content: []*responses.ContentItem{
            {
                Union: &responses.ContentItem_Video{
                    Video: &responses.ContentItemVideo{
                        Type:   responses.ContentItemType_input_video,
                        FileId: byteplus.String(fileInfo.ID),
                    },
                },
            },
            {
                Union: &responses.ContentItem_Text{
                    Text: &responses.ContentItemText{
                        Type: responses.ContentItemType_input_text,
                        Text: "Describe the sequence of actions performed by the person in the video and output the results in JSON format. Include start_time, end_time, event, and danger (boolean), and express timestamps in HH:mm:ss format."
                    },
                },
            },
        },
    }
    createResponsesReq := &responses.ResponsesRequest{
        Model: "seed-1-6-250915",
        Input: &responses.ResponsesInput{
            Union: &responses.ResponsesInput_ListValue{
                ListValue: &responses.InputItemList{ListValue: []*responses.InputItem{{
                    Union: &responses.InputItem_InputMessage{
                        InputMessage: inputMessage,
                    },
                }}},
            },
        },
        Caching: &responses.ResponsesCaching{Type: responses.CacheType_enabled.Enum()},
    }

    resp, err := client.CreateResponsesStream(ctx, createResponsesReq)
    if err != nil {
        fmt.Printf("stream error: %v\\n", err)
        return
    }
    var responseId string
    for {
        event, err := resp.Recv()
        if err == io.EOF {
            break
        }
        if err != nil {
            fmt.Printf("stream error: %v\\n", err)
            return
        }
        handleEvent(event)
        if responseEvent := event.GetResponse(); responseEvent != nil {
            responseId = responseEvent.GetResponse().GetId()
            fmt.Printf("Response ID: %s", responseId)
        }
    }
}

func handleEvent(event *responses.Event) {
    switch event.GetEventType() {
    case responses.EventType_response_reasoning_summary_text_delta.String():
        print(event.GetReasoningText().GetDelta())
    case responses.EventType_response_reasoning_summary_text_done.String(): // aggregated reasoning text
        fmt.Printf("\\nAggregated reasoning text: %s\\n", event.GetReasoningText().GetText())
    case responses.EventType_response_output_text_delta.String():
        print(event.GetText().GetDelta())
    case responses.EventType_response_output_text_done.String(): // aggregated output text
        fmt.Printf("\\nAggregated output text: %s\\n", event.GetTextDone().GetText())
    default:
        return
    }
}
\`\`\`


`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Java SDK" key="EqamavLqf4"><RenderMd content={`\`\`\`Java
package com.ark.sample;

import com.byteplus.ark.runtime.model.files.FileMeta;
import com.byteplus.ark.runtime.model.files.PreprocessConfigs;
import com.byteplus.ark.runtime.model.files.UploadFileRequest;
import com.byteplus.ark.runtime.model.files.Video;
import com.byteplus.ark.runtime.service.ArkService;
import com.byteplus.ark.runtime.model.responses.request.*;
import com.byteplus.ark.runtime.model.responses.item.ItemEasyMessage;
import com.byteplus.ark.runtime.model.responses.constant.ResponsesConstants;
import com.byteplus.ark.runtime.model.responses.item.MessageContent;
import com.byteplus.ark.runtime.model.responses.content.InputContentItemVideo;
import com.byteplus.ark.runtime.model.responses.content.InputContentItemText;

import com.byteplus.ark.runtime.model.responses.event.functioncall.FunctionCallArgumentsDoneEvent;
import com.byteplus.ark.runtime.model.responses.event.outputitem.OutputItemAddedEvent;
import com.byteplus.ark.runtime.model.responses.event.outputitem.OutputItemDoneEvent;
import com.byteplus.ark.runtime.model.responses.event.outputtext.OutputTextDeltaEvent;
import com.byteplus.ark.runtime.model.responses.event.outputtext.OutputTextDoneEvent;
import com.byteplus.ark.runtime.model.responses.event.reasoningsummary.ReasoningSummaryTextDeltaEvent;
import com.byteplus.ark.runtime.model.responses.event.response.ResponseCompletedEvent;
import java.io.File;
import java.util.concurrent.TimeUnit;

public class demo {
    public static void main(String[] args) {
        String apiKey = System.getenv("ARK_API_KEY");
        ArkService service = ArkService.builder().apiKey(apiKey).baseUrl("https://ark.ap-southeast.bytepluses.com/api/v3").build();

        System.out.println("===== Upload File Example=====");
        // upload a video for responses
        FileMeta fileMeta;
        fileMeta = service.uploadFile(
                UploadFileRequest.builder().
                        file(new File("/Users/doc/demo.mp4")) // replace with your image file path
                        .purpose("user_data")
                        .preprocessConfigs(PreprocessConfigs.builder().video(new Video(0.3)).build())
                        .build());
        System.out.println("Uploaded file Meta: " + fileMeta);
        System.out.println("status:" + fileMeta.getStatus());

        try {
            while (fileMeta.getStatus().equals("processing")) {
                System.out.println("Waiting for video to be processed...");
                TimeUnit.SECONDS.sleep(2);
                fileMeta = service.retrieveFile(fileMeta.getId());
            }
        } catch (Exception e) {
            System.err.println("get file status error：" + e.getMessage());
        }
        System.out.println("Uploaded file Meta: " + fileMeta);

        CreateResponsesRequest request = CreateResponsesRequest.builder()
                .model("seed-1-6-250915")
                .stream(true)
                .input(ResponsesInput.builder().addListItem(
                        ItemEasyMessage.builder().role(ResponsesConstants.MESSAGE_ROLE_USER).content(
                                MessageContent.builder()
                                        .addListItem(InputContentItemVideo.builder().fileId(fileMeta.getId()).build())
                                        .addListItem(InputContentItemText.builder().text("Describe the sequence of actions performed by the person in the video and output the results in JSON format. Include start_time, end_time, event, and danger (boolean), and express timestamps in HH:mm:ss format.").build())
                                        .build()
                        ).build()
                ).build())
                .build();

        service.streamResponse(request)
                .doOnError(Throwable::printStackTrace)
                .blockingForEach(event -> {
                    if (event instanceof ReasoningSummaryTextDeltaEvent) {
                        System.out.print(((ReasoningSummaryTextDeltaEvent) event).getDelta());
                    }
                    if (event instanceof OutputItemAddedEvent) {
                        System.out.println("\\nOutputItem " + (((OutputItemAddedEvent) event).getItem().getType()) + " Start: ");
                    }
                    if (event instanceof OutputTextDeltaEvent) {
                        System.out.print(((OutputTextDeltaEvent) event).getDelta());
                    }
                    if (event instanceof OutputTextDoneEvent) {
                        System.out.println("\\nOutputText End.");
                    }
                    if (event instanceof OutputItemDoneEvent) {
                        System.out.println("\\nOutputItem " + ((OutputItemDoneEvent) event).getItem().getType() + " End.");
                    }
                    if (event instanceof FunctionCallArgumentsDoneEvent) {
                        System.out.println("\\nFunctionCall Arguments: " + ((FunctionCallArgumentsDoneEvent) event).getArguments());
                    }
                    if (event instanceof ResponseCompletedEvent) {
                        System.out.println("\\nResponse Completed. Usage = " + ((ResponseCompletedEvent) event).getResponse().getUsage());
                    }
                });


        service.shutdownExecutor();
    }
}
\`\`\`


`}></RenderMd></Tabs.TabPane>
<Tabs.TabPane title="Compatible with OpenAI SDK" key="xQZ1K6LyqJ"><RenderMd content={`\`\`\`Python
import os
import time
from openai import OpenAI

api_key = os.getenv('ARK_API_KEY')

client = OpenAI(
    base_url='https://ark.ap-southeast.bytepluses.com/api/v3',
    api_key=api_key,
)

file = client.files.create(
    file=open("/Users/doc/demo.mp4", "rb"),
    purpose="user_data"
)
# Wait for the file to finish processing
while (file.status == "processing"):
    time.sleep(2)
    file = client.files.retrieve(file.id)
print(f"File processed: {file}")
    
response = client.responses.create(
    model="seed-1-6-250915",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_video",
                    "file_id": file.id,
                },
                {
                    "type": "input_text",
                    "text": "Describe the sequence of actions performed by the person in the video and output the results in JSON format. Include start_time, end_time, event, and danger (boolean), and express timestamps in HH:mm:ss format.",
                },
            ]
        }
    ],
    stream=True
)


for event in response:
    if event.type == "response.reasoning_summary_text.delta":
        print(event.delta, end="")
    if event.type == "response.output_item.added":
        print("\\noutPutItem " + event.type + " start:")
    if event.type == "response.output_text.delta":
        print(event.delta,end="")
    if event.type == "response.output_item.done":
        print("\\noutPutTextDone.")
    if event.type == "response.completed":
        print("\\nResponse Completed. Usage = " + event.response.usage.model_dump_json())
\`\`\`


`}></RenderMd></Tabs.TabPane></Tabs>);
 ```

<span id="5a0c8d52"></span>
## Storage limitation
Each account has 20 GB of free storage. After exceeding this limit, files cannot be uploaded. Deleting files to free up storage space allows continued file uploads.
<span id="b2c2dfe3"></span>
## Limit rates and error codes

* Files API QPS rate limits and bandwidth restrictions are as follows. To increase the rate limit, please submit a support ticket.
   * Upload file: 20 QPS, 100 Mbps bandwidth
   * Retrieve file: 20 QPS
   * Query file list: 20 QPS
   * Delete file: 20 QPS
* Error codes: See [Error Code](/docs/ModelArk/1299023) for detailed information.


