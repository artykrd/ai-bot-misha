Your First API Call

The DeepSeek API uses an API format compatible with OpenAI. By modifying the configuration, you can use the OpenAI SDK or softwares compatible with the OpenAI API to access the DeepSeek API.
PARAM	VALUE
base_url *       	https://api.deepseek.com
api_key	apply for an API key

* To be compatible with OpenAI, you can also use https://api.deepseek.com/v1 as the base_url. But note that the v1 here has NO relationship with the model's version.

* deepseek-chat and deepseek-reasoner are upgraded to DeepSeek-V3.2 now. deepseek-chat is the non-thinking mode of DeepSeek-V3.2 and deepseek-reasoner is the thinking mode of DeepSeek-V3.2.
Invoke The Chat API

Once you have obtained an API key, you can access the DeepSeek API using the following example scripts. This is a non-stream example, you can set the stream parameter to true to get stream response.

    curl
    python
    nodejs

# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)

print(response.choices[0].message.content)


Models & Pricing

The prices listed below are in units of per 1M tokens. A token, the smallest unit of text that the model recognizes, can be a word, a number, or even a punctuation mark. We will bill based on the total number of input and output tokens by the model.
Model Details
MODEL	deepseek-chat	deepseek-reasoner	deepseek-reasoner(1)
BASE URL	https://api.deepseek.com	https://api.deepseek.com/
v3.2_speciale_expires_on_20251215
MODEL VERSION	DeepSeek-V3.2
(Non-thinking Mode)	DeepSeek-V3.2
(Thinking Mode)	DeepSeek-V3.2-Speciale
（Thinking Mode Only）
CONTEXT LENGTH	128K
MAX OUTPUT	DEFAULT: 4K
MAXIMUM: 8K	DEFAULT: 32K
MAXIMUM: 64K	DEFAULT: 128K
MAXIMUM: 128K
FEATURES	Json Output	✓	✓	✗
Tool Calls	✓	✓	✗
Chat Prefix Completion（Beta）	✓	✓	✗
FIM Completion（Beta）	✓	✗	✗
PRICING	1M INPUT TOKENS (CACHE HIT)	$0.028
1M INPUT TOKENS (CACHE MISS)	$0.28
1M OUTPUT TOKENS	$0.42

    (1) Users can access the DeepSeek-V3.2-Speciale model by setting base_url="https://api.deepseek.com/v3.2_speciale_expires_on_20251215". This model only supports thinking mode and will be available until December 15, 2025, 15:59 UTC.

Deduction Rules

The expense = number of tokens × price. The corresponding fees will be directly deducted from your topped-up balance or granted balance, with a preference for using the granted balance first when both balances are available.

Product prices may vary and DeepSeek reserves the right to adjust them. We recommend topping up based on your actual usage and regularly checking this page for the most recent pricing information.


The Temperature Parameter

The default value of temperature is 1.0.

    We recommend users to set the temperature according to their use case listed in below.

USE CASE	TEMPERATURE
Coding / Math   	0.0
Data Cleaning / Data Analysis	1.0
General Conversation	1.3
Translation	1.3
Creative Writing / Poetry	1.5


Token & Token Usage

Tokens are the basic units used by models to represent natural language text, and also the units we use for billing. They can be intuitively understood as 'characters' or 'words'. Typically, a Chinese word, an English word, a number, or a symbol is counted as a token.

Generally, the conversion ratio between tokens in the model and the number of characters is approximately as following:

    1 English character ≈ 0.3 token.
    1 Chinese character ≈ 0.6 token.

However, due to the different tokenization methods used by different models, the conversion ratios can vary. The actual number of tokens processed each time is based on the model's return, which you can view from the usage results.
Calculate token usage offline
You can run the demo tokenizer code in the following zip package to calculate the token usage for your intput/output.


Rate Limit

DeepSeek API does NOT constrain user's rate limit. We will try out best to serve every request.

However, please note that when our servers are under high traffic pressure, your requests may take some time to receive a response from the server. During this period, your HTTP request will remain connected, and you may continuously receive contents in the following formats:

    Non-streaming requests: Continuously return empty lines
    Streaming requests: Continuously return SSE keep-alive comments (: keep-alive)

These contents do not affect the parsing of the JSON body by the OpenAI SDK. If you are parsing the HTTP responses yourself, please ensure to handle these empty lines or comments appropriately.

If the request is still not completed after 30 minutes, the server will close the connection.


Error Codes

When calling DeepSeek API, you may encounter errors. Here list the causes and solutions.
                    CODE                    	DESCRIPTION
400 - Invalid Format	Cause: Invalid request body format.
Solution: Please modify your request body according to the hints in the error message. For more API format details, please refer to DeepSeek API Docs.
401 - Authentication Fails	Cause: Authentication fails due to the wrong API key.
Solution: Please check your API key. If you don't have one, please create an API key first.
402 - Insufficient Balance	Cause: You have run out of balance.
Solution: Please check your account's balance, and go to the Top up page to add funds.
422 - Invalid Parameters	Cause: Your request contains invalid parameters.
Solution: Please modify your request parameters according to the hints in the error message. For more API format details, please refer to DeepSeek API Docs.
429 - Rate Limit Reached	Cause: You are sending requests too quickly.
Solution: Please pace your requests reasonably. We also advise users to temporarily switch to the APIs of alternative LLM service providers, like OpenAI.
500 - Server Error	Cause: Our server encounters an issue.
Solution: Please retry your request after a brief wait and contact us if the issue persists.
503 - Server Overloaded	Cause: The server is overloaded due to high traffic.
Solution: Please retry your request after a brief wait.


Thinking Mode

The DeepSeek model supports the thinking mode: before outputting the final answer, the model will first output a chain-of-thought reasoning to improve the accuracy of the final response. You can enable thinking mode using any of the following methods:

    Set the model parameter: "model": "deepseek-reasoner"

    Set the thinking parameter: "thinking": {"type": "enabled"}

If you are using the OpenAI SDK, when setting thinking parameter, you need to pass the thinking parameter within extra_body:

response = client.chat.completions.create(
  model="deepseek-chat",
  # ...
  extra_body={"thinking": {"type": "enabled"}}
)

API Parameters

    Input：
        max_tokens：The maximum output length (including the COT part). Default to 32K, maximum to 64K.

    Output：
        reasoning_content：The content of the CoT，which is at the same level as content in the output structure. See API Example for details.
        content: The content of the final answer.
        tool_calls: The tool calls.

    Supported Features：Json Output、Tool Calls、Chat Completion、Chat Prefix Completion (Beta)

    Not Supported Features：FIM (Beta)

    Not Supported Parameters：temperature、top_p、presence_penalty、frequency_penalty、logprobs、top_logprobs. Please note that to ensure compatibility with existing software, setting temperature、top_p、presence_penalty、frequency_penalty will not trigger an error but will also have no effect. Setting logprobs、top_logprobs will trigger an error.

Multi-turn Conversation

In each turn of the conversation, the model outputs the CoT (reasoning_content) and the final answer (content). In the next turn of the conversation, the CoT from previous turns is not concatenated into the context, as illustrated in the following diagram:
API Example

The following code, using Python as an example, demonstrates how to access the CoT and the final answer, as well as how to conduct multi-turn conversations. Note that in the code for the new turn of conversation, only the content from the previous turn's output is passed, while the reasoning_content is ignored.

    NoStreaming
    Streaming

from openai import OpenAI
client = OpenAI(api_key="<DeepSeek API Key>", base_url="https://api.deepseek.com")

# Turn 1
messages = [{"role": "user", "content": "9.11 and 9.8, which is greater?"}]
response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=messages
)

reasoning_content = response.choices[0].message.reasoning_content
content = response.choices[0].message.content

# Turn 2
messages.append({'role': 'assistant', 'content': content})
messages.append({'role': 'user', 'content': "How many Rs are there in the word 'strawberry'?"})
response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=messages
)
# ...

Tool Calls

DeepSeek model's thinking mode now supports tool calls. Before outputting the final answer, the model can engage in multiple turns of reasoning and tool calls to improve the quality of the response. The calling pattern is illustrated below:

    During the process of answering question 1 (Turn 1.1 - 1.3), the model performed multiple turns of thinking + tool calls before providing the answer. During this process, the user needs to send the reasoning content (reasoning_content) back to the API to allow the model to continue reasoning.

    When the next user question begins (Turn 2.1), the previous reasoning_content should be removed, while keeping other elements to send to the API. If reasoning_content is retained and sent to the API, the API will ignore it.

Compatibility Notice

Since the tool invocation process in thinking mode requires users to pass back reasoning_content to the API, if your code does not correctly pass back reasoning_content, the API will return a 400 error. Please refer to the sample code below for the correct way.
Sample Code

Below is a simple sample code for tool calls in thinking mode:

import os
import json
from openai import OpenAI

# The definition of the tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_date",
            "description": "Get the current date",
            "parameters": { "type": "object", "properties": {} },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of a location, the user should supply the location and date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": { "type": "string", "description": "The city name" },
                    "date": { "type": "string", "description": "The date in format YYYY-mm-dd" },
                },
                "required": ["location", "date"]
            },
        }
    },
]

# The mocked version of the tool calls
def get_date_mock():
    return "2025-12-01"

def get_weather_mock(location, date):
    return "Cloudy 7~13°C"

TOOL_CALL_MAP = {
    "get_date": get_date_mock,
    "get_weather": get_weather_mock
}

def clear_reasoning_content(messages):
    for message in messages:
        if hasattr(message, 'reasoning_content'):
            message.reasoning_content = None

def run_turn(turn, messages):
    sub_turn = 1
    while True:
        response = client.chat.completions.create(
            model='deepseek-chat',
            messages=messages,
            tools=tools,
            extra_body={ "thinking": { "type": "enabled" } }
        )
        messages.append(response.choices[0].message)
        reasoning_content = response.choices[0].message.reasoning_content
        content = response.choices[0].message.content
        tool_calls = response.choices[0].message.tool_calls
        print(f"Turn {turn}.{sub_turn}\n{reasoning_content=}\n{content=}\n{tool_calls=}")
        # If there is no tool calls, then the model should get a final answer and we need to stop the loop
        if tool_calls is None:
            break
        for tool in tool_calls:
            tool_function = TOOL_CALL_MAP[tool.function.name]
            tool_result = tool_function(**json.loads(tool.function.arguments))
            print(f"tool result for {tool.function.name}: {tool_result}\n")
            messages.append({
                "role": "tool",
                "tool_call_id": tool.id,
                "content": tool_result,
            })
        sub_turn += 1

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url=os.environ.get('DEEPSEEK_BASE_URL'),
)

# The user starts a question
turn = 1
messages = [{
    "role": "user",
    "content": "How's the weather in Hangzhou Tomorrow"
}]
run_turn(turn, messages)

# The user starts a new question
turn = 2
messages.append({
    "role": "user",
    "content": "How's the weather in Hangzhou Tomorrow"
})
# We recommended to clear the reasoning_content in history messages so as to save network bandwidth
clear_reasoning_content(messages)
run_turn(turn, messages)

In each sub-request of Turn 1, the reasoning_content generated during that turn is sent to the API, allowing the model to continue its previous reasoning. response.choices[0].message contains all necessary fields for the assistant message, including content, reasoning_content, and tool_calls. For simplicity, you can directly append the message to the end of the messages list using the following code:

messages.append(response.choices[0].message)

This line of code is equivalent to:

messages.append({
    'role': 'assistant',
    'content': response.choices[0].message.content,
    'reasoning_content': response.choices[0].message.reasoning_content,
    'tool_calls': response.choices[0].message.tool_calls,
})

At the beginning of Turn 2, we recommend discarding the reasoning_content from previous turns to save network bandwidth:

clear_reasoning_content(messages)

The sample output of this code is as follows:

Turn 1.1
reasoning_content="The user is asking about the weather in Hangzhou tomorrow. I need to get the current date first, then calculate tomorrow's date, and then call the weather API. Let me start by getting the current date."
content=''
tool_calls=[ChatCompletionMessageToolCall(id='call_00_Tcek83ZQ4fFb1RfPQnsPEE5w', function=Function(arguments='{}', name='get_date'), type='function', index=0)]
tool_result(get_date): 2025-12-01

Turn 1.2
reasoning_content='Today is December 1, 2025. Tomorrow is December 2, 2025. I need to format the date as YYYY-mm-dd: "2025-12-02". Now I can call get_weather with location Hangzhou and date 2025-12-02.'
content=''
tool_calls=[ChatCompletionMessageToolCall(id='call_00_V0Uwt4i63m5QnWRS1q1AO1tP', function=Function(arguments='{"location": "Hangzhou", "date": "2025-12-02"}', name='get_weather'), type='function', index=0)]
tool_result(get_weather): Cloudy 7~13°C

Turn 1.3
reasoning_content="I have the weather information: Cloudy with temperatures between 7 and 13°C. I should respond in a friendly, helpful manner. I'll mention that it's for tomorrow (December 2, 2025) and give the details. I can also ask if they need any other information. Let's craft the response."
content="Tomorrow (Tuesday, December 2, 2025) in Hangzhou will be **cloudy** with temperatures ranging from **7°C to 13°C**.  \n\nIt might be a good idea to bring a light jacket if you're heading out. Is there anything else you'd like to know about the weather?"
tool_calls=None

Turn 2.1
reasoning_content="The user wants clothing advice for tomorrow based on the weather in Hangzhou. I know tomorrow's weather: cloudy, 7-13°C. That's cool but not freezing. I should suggest layered clothing, maybe a jacket, long pants, etc. I can also mention that since it's cloudy, an umbrella might not be needed unless there's rain chance, but the forecast didn't mention rain. I should be helpful and give specific suggestions. I can also ask if they have any specific activities planned to tailor the advice. Let me respond."
content="Based on tomorrow's forecast of **cloudy weather with temperatures between 7°C and 13°C** in Hangzhou, here are some clothing suggestions:\n\n**Recommended outfit:**\n- **Upper body:** A long-sleeve shirt or sweater, plus a light to medium jacket (like a fleece, windbreaker, or light coat)\n- **Lower body:** Long pants or jeans\n- **Footwear:** Closed-toe shoes or sneakers\n- **Optional:** A scarf or light hat for extra warmth, especially in the morning and evening\n\n**Why this works:**\n- The temperature range is cool but not freezing, so layering is key\n- Since it's cloudy but no rain mentioned, you likely won't need an umbrella\n- The jacket will help with the morning chill (7°C) and can be removed if you warm up during the day\n\n**If you have specific plans:**\n- For outdoor activities: Consider adding an extra layer\n- For indoor/office settings: The layered approach allows you to adjust comfortably\n\nWould you like more specific advice based on your planned activities?"
tool_calls=None



Multi-round Conversation

This guide will introduce how to use the DeepSeek /chat/completions API for multi-turn conversations.

The DeepSeek /chat/completions API is a "stateless" API, meaning the server does not record the context of the user's requests. Therefore, the user must concatenate all previous conversation history and pass it to the chat API with each request.

The following code in Python demonstrates how to concatenate context to achieve multi-turn conversations.

from openai import OpenAI
client = OpenAI(api_key="<DeepSeek API Key>", base_url="https://api.deepseek.com")

# Round 1
messages = [{"role": "user", "content": "What's the highest mountain in the world?"}]
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages
)

messages.append(response.choices[0].message)
print(f"Messages Round 1: {messages}")

# Round 2
messages.append({"role": "user", "content": "What is the second?"})
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages
)

messages.append(response.choices[0].message)
print(f"Messages Round 2: {messages}")

In the first round of the request, the messages passed to the API are:

[
    {"role": "user", "content": "What's the highest mountain in the world?"}
]

In the second round of the request:

    Add the model's output from the first round to the end of the messages.
    Add the new question to the end of the messages.

The messages ultimately passed to the API are:

[
    {"role": "user", "content": "What's the highest mountain in the world?"},
    {"role": "assistant", "content": "The highest mountain in the world is Mount Everest."},
    {"role": "user", "content": "What is the second?"}
]



Chat Prefix Completion (Beta)

The chat prefix completion follows the Chat Completion API, where users provide an assistant's prefix message for the model to complete the rest of the message.
Notice

    When using chat prefix completion, users must ensure that the role of the last message in the messages list is assistant and set the prefix parameter of the last message to True.
    The user needs to set base_url="https://api.deepseek.com/beta" to enable the Beta feature.

Sample Code

Below is a complete Python code example for chat prefix completion. In this example, we set the prefix message of the assistant to "```python\n" to force the model to output Python code, and set the stop parameter to ['```'] to prevent additional explanations from the model.

from openai import OpenAI

client = OpenAI(
    api_key="<your api key>",
    base_url="https://api.deepseek.com/beta",
)

messages = [
    {"role": "user", "content": "Please write quick sort code"},
    {"role": "assistant", "content": "```python\n", "prefix": True}
]
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    stop=["```"],
)
print(response.choices[0].message.content)


FIM Completion (Beta)

In FIM (Fill In the Middle) completion, users can provide a prefix and a suffix (optional), and the model will complete the content in between. FIM is commonly used for content completion、code completion.
Notice

    The max tokens of FIM completion is 4K.
    The user needs to set base_url=https://api.deepseek.com/beta to enable the Beta feature.

Sample Code

Below is a complete Python code example for FIM completion. In this example, we provide the beginning and the end of a function to calculate the Fibonacci sequence, allowing the model to complete the content in the middle.

from openai import OpenAI

client = OpenAI(
    api_key="<your api key>",
    base_url="https://api.deepseek.com/beta",
)

response = client.completions.create(
    model="deepseek-chat",
    prompt="def fib(a):",
    suffix="    return fib(a-1) + fib(a-2)",
    max_tokens=128
)
print(response.choices[0].text)

Integration With Continue
Continue is a VSCode plugin that supports code completion. You can refer to this document to configure Continue for using the code completion feature.


JSON Output

In many scenarios, users need the model to output in strict JSON format to achieve structured output, facilitating subsequent parsing.

DeepSeek provides JSON Output to ensure the model outputs valid JSON strings.
Notice

To enable JSON Output, users should:

    Set the response_format parameter to {'type': 'json_object'}.
    Include the word "json" in the system or user prompt, and provide an example of the desired JSON format to guide the model in outputting valid JSON.
    Set the max_tokens parameter reasonably to prevent the JSON string from being truncated midway.
    When using the JSON Output feature, the API may occasionally return empty content. We are actively working on optimizing this issue. You can try modifying the prompt to mitigate such problems.

Sample Code

Here is the complete Python code demonstrating the use of JSON Output:

import json
from openai import OpenAI

client = OpenAI(
    api_key="<your api key>",
    base_url="https://api.deepseek.com",
)

system_prompt = """
The user will provide some exam text. Please parse the "question" and "answer" and output them in JSON format. 

EXAMPLE INPUT: 
Which is the highest mountain in the world? Mount Everest.

EXAMPLE JSON OUTPUT:
{
    "question": "Which is the highest mountain in the world?",
    "answer": "Mount Everest"
}
"""

user_prompt = "Which is the longest river in the world? The Nile River."

messages = [{"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}]

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    response_format={
        'type': 'json_object'
    }
)

print(json.loads(response.choices[0].message.content))

The model will output:

{
    "question": "Which is the longest river in the world?",
    "answer": "The Nile River"
}


Tool Calls

Tool Calls allows the model to call external tools to enhance its capabilities.
Non-thinking Mode
Sample Code

Here is an example of using Tool Calls to get the current weather information of the user's location, demonstrated with complete Python code.

For the specific API format of Tool Calls, please refer to the Chat Completion documentation.

from openai import OpenAI

def send_messages(messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools
    )
    return response.choices[0].message

client = OpenAI(
    api_key="<your api key>",
    base_url="https://api.deepseek.com",
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of a location, the user should supply a location first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"]
            },
        }
    },
]

messages = [{"role": "user", "content": "How's the weather in Hangzhou, Zhejiang?"}]
message = send_messages(messages)
print(f"User>\t {messages[0]['content']}")

tool = message.tool_calls[0]
messages.append(message)

messages.append({"role": "tool", "tool_call_id": tool.id, "content": "24℃"})
message = send_messages(messages)
print(f"Model>\t {message.content}")

The execution flow of this example is as follows:

    User: Asks about the current weather in Hangzhou
    Model: Returns the function get_weather({location: 'Hangzhou'})
    User: Calls the function get_weather({location: 'Hangzhou'}) and provides the result to the model
    Model: Returns in natural language, "The current temperature in Hangzhou is 24°C."

Note: In the above code, the functionality of the get_weather function needs to be provided by the user. The model itself does not execute specific functions.
Thinking Mode

From DeepSeek-V3.2, the API supports tool use in the thinking mode. For more details, please refer to Thinking Mode
strict Mode (Beta)

In strict mode, the model strictly adheres to the format requirements of the Function's JSON schema when outputting a tool call, ensuring that the model's output complies with the user's definition. It is supported by both thinking and non-thinking mode.

To use strict mode, you need to:：

    Use base_url="https://api.deepseek.com/beta" to enable Beta features
    In the tools parameter，all function need to set the strict property to true
    The server will validate the JSON Schema of the Function provided by the user. If the schema does not conform to the specifications or contains JSON schema types that are not supported by the server, an error message will be returned

The following is an example of a tool definition in the strict mode:

{
    "type": "function",
    "function": {
        "name": "get_weather",
        "strict": true,
        "description": "Get weather of a location, the user should supply a location first.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                }
            },
            "required": ["location"],
            "additionalProperties": false
        }
    }
}

Support Json Schema Types In strict Mode

    object
    string
    number
    integer
    boolean
    array
    enum
    anyOf

object

The object defines a nested structure containing key-value pairs, where properties specifies the schema for each key (or property) within the object. All properties of every object must be set as required, and the additionalProperties attribute of the object must be set to false.

Example：

{
    "type": "object",
    "properties": {
        "name": { "type": "string" },
        "age": { "type": "integer" }
    },
    "required": ["name", "age"],
    "additionalProperties": false
}

string

    Supported parameters:
        pattern: Uses regular expressions to constrain the format of the string
        format: Validates the string against predefined common formats. Currently supported formats:
            email: Email address
            hostname: Hostname
            ipv4: IPv4 address
            ipv6: IPv6 address
            uuid: UUID

    Unsupported parameters:
        minLength
        maxLength

Example:

{
    "type": "object",
    "properties": {
        "user_email": {
            "type": "string",
            "description": "The user's email address",
            "format": "email" 
        },
        "zip_code": {
            "type": "string",
            "description": "Six digit postal code",
            "pattern": "^\\d{6}$"
        }
    }
}

number/integer

    Supported parameters:
        const: Specifies a constant numeric value
        default: Defines the default value of the number
        minimum: Specifies the minimum value
        maximum: Specifies the maximum value
        exclusiveMinimum: Defines a value that the number must be greater than
        exclusiveMaximum: Defines a value that the number must be less than
        multipleOf: Ensures that the number is a multiple of the specified value

Example:

{
    "type": "object",
    "properties": {
        "score": {
            "type": "integer",
            "description": "A number from 1-5, which represents your rating, the higher, the better",
            "minimum": 1,
            "maximum": 5
        }
    },
    "required": ["score"],
    "additionalProperties": false
}

array

    Unsupported parameters:
        minItems
        maxItems

Example：

{
    "type": "object",
    "properties": {
        "keywords": {
            "type": "array",
            "description": "Five keywords of the article, sorted by importance",
            "items": {
                "type": "string",
                "description": "A concise and accurate keyword or phrase."
            }
        }
    },
    "required": ["keywords"],
    "additionalProperties": false
}

enum

The enum ensures that the output is one of the predefined options. For example, in the case of order status, it can only be one of a limited set of specified states.

Example：

{
    "type": "object",
    "properties": {
        "order_status": {
            "type": "string",
            "description": "Ordering status",
            "enum": ["pending", "processing", "shipped", "cancelled"]
        }
    }
}

anyOf

Matches any one of the provided schemas, allowing fields to accommodate multiple valid formats. For example, a user's account could be either an email address or a phone number:

{
    "type": "object",
    "properties": {
    "account": {
        "anyOf": [
            { "type": "string", "format": "email", "description": "可以是电子邮件地址" },
            { "type": "string", "pattern": "^\\d{11}$", "description": "或11位手机号码" }
        ]
    }
  }
}

$ref and $def

You can use $def to define reusable modules and then use $ref to reference them, reducing schema repetition and enabling modularization. Additionally, $ref can be used independently to define recursive structures.

{
    "type": "object",
    "properties": {
        "report_date": {
            "type": "string",
            "description": "The date when the report was published"
        },
        "authors": {
            "type": "array",
            "description": "The authors of the report",
            "items": {
                "$ref": "#/$def/author"
            }
        }
    },
    "required": ["report_date", "authors"],
    "additionalProperties": false,
    "$def": {
        "authors": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "author's name"
                },
                "institution": {
                    "type": "string",
                    "description": "author's institution"
                },
                "email": {
                    "type": "string",
                    "format": "email",
                    "description": "author's email"
                }
            },
            "additionalProperties": false,
            "required": ["name", "institution", "email"]
        }
    }
}


Context Caching

The DeepSeek API Context Caching on Disk Technology is enabled by default for all users, allowing them to benefit without needing to modify their code.

Each user request will trigger the construction of a hard disk cache. If subsequent requests have overlapping prefixes with previous requests, the overlapping part will only be fetched from the cache, which counts as a "cache hit."

Note: Between two requests, only the repeated prefix part can trigger a "cache hit." Please refer to the example below for more details.
Example 1: Long Text Q&A

First Request

messages: [
    {"role": "system", "content": "You are an experienced financial report analyst..."}
    {"role": "user", "content": "<financial report content>\n\nPlease summarize the key information of this financial report."}
]

Second Request

messages: [
    {"role": "system", "content": "You are an experienced financial report analyst..."}
    {"role": "user", "content": "<financial report content>\n\nPlease analyze the profitability of this financial report."}
]

In the above example, both requests have the same prefix, which is the system message + <financial report content> in the user message. During the second request, this prefix part will count as a "cache hit."
Example 2: Multi-round Conversation

First Request

messages: [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "What is the capital of China?"}
]

Second Request

messages: [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "What is the capital of China?"},
    {"role": "assistant", "content": "The capital of China is Beijing."},
    {"role": "user", "content": "What is the capital of the United States?"}
]

In this example, the second request can reuse the initial system message and user message from the first request, which will count as a "cache hit."
Example 3: Using Few-shot Learning

In practical applications, users can enhance the model's output performance through few-shot learning. Few-shot learning involves providing a few examples in the request to allow the model to learn a specific pattern. Since few-shot generally provides the same context prefix, the cost of few-shot is significantly reduced with the support of context caching.

First Request

messages: [    
    {"role": "system", "content": "You are a history expert. The user will provide a series of questions, and your answers should be concise and start with `Answer:`"},
    {"role": "user", "content": "In what year did Qin Shi Huang unify the six states?"},
    {"role": "assistant", "content": "Answer: 221 BC"},
    {"role": "user", "content": "Who was the founder of the Han Dynasty?"},
    {"role": "assistant", "content": "Answer: Liu Bang"},
    {"role": "user", "content": "Who was the last emperor of the Tang Dynasty?"},
    {"role": "assistant", "content": "Answer: Li Zhu"},
    {"role": "user", "content": "Who was the founding emperor of the Ming Dynasty?"},
    {"role": "assistant", "content": "Answer: Zhu Yuanzhang"},
    {"role": "user", "content": "Who was the founding emperor of the Qing Dynasty?"}
]

Second Request

messages: [    
    {"role": "system", "content": "You are a history expert. The user will provide a series of questions, and your answers should be concise and start with `Answer:`"},
    {"role": "user", "content": "In what year did Qin Shi Huang unify the six states?"},
    {"role": "assistant", "content": "Answer: 221 BC"},
    {"role": "user", "content": "Who was the founder of the Han Dynasty?"},
    {"role": "assistant", "content": "Answer: Liu Bang"},
    {"role": "user", "content": "Who was the last emperor of the Tang Dynasty?"},
    {"role": "assistant", "content": "Answer: Li Zhu"},
    {"role": "user", "content": "Who was the founding emperor of the Ming Dynasty?"},
    {"role": "assistant", "content": "Answer: Zhu Yuanzhang"},
    {"role": "user", "content": "When did the Shang Dynasty fall?"},        
]

In this example, 4-shots are used. The only difference between the two requests is the last question. The second request can reuse the content of the first 4 rounds of dialogue from the first request, which will count as a "cache hit."
Checking Cache Hit Status

In the response from the DeepSeek API, we have added two fields in the usage section to reflect the cache hit status of the request:

    prompt_cache_hit_tokens: The number of tokens in the input of this request that resulted in a cache hit (0.1 yuan per million tokens).

    prompt_cache_miss_tokens: The number of tokens in the input of this request that did not result in a cache hit (1 yuan per million tokens).

Hard Disk Cache and Output Randomness

The hard disk cache only matches the prefix part of the user's input. The output is still generated through computation and inference, and it is influenced by parameters such as temperature, introducing randomness.
Additional Notes

    The cache system uses 64 tokens as a storage unit; content less than 64 tokens will not be cached.

    The cache system works on a "best-effort" basis and does not guarantee a 100% cache hit rate.

    Cache construction takes seconds. Once the cache is no longer in use, it will be automatically cleared, usually within a few hours to a few days.



Anthropic API

To meet the demand for using the Anthropic API ecosystem, our API has added support for the Anthropic API format. With simple configuration, you can integrate the capabilities of DeepSeek into the Anthropic API ecosystem.
Use DeepSeek in Claude Code

    Install Claude Code

npm install -g @anthropic-ai/claude-code

    Config Environment Variables

export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_AUTH_TOKEN=${YOUR_API_KEY}
export API_TIMEOUT_MS=600000
export ANTHROPIC_MODEL=deepseek-chat
export ANTHROPIC_SMALL_FAST_MODEL=deepseek-chat
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1

Note: The API_TIMEOUT_MS parameter is configured to prevent excessively long outputs that could cause the Claude Code client to time out. Here, we set the timeout duration to 10 minutes.

    Enter the Project Directory, and Execute Claude Code

cd my-project
claude

Invoke DeepSeek Model via Anthropic API

    Install Anthropic SDK

pip install anthropic

    Config Environment Variables

export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_API_KEY=${DEEPSEEK_API_KEY}

    Invoke the API

import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="deepseek-chat",
    max_tokens=1000,
    system="You are a helpful assistant.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Hi, how are you?"
                }
            ]
        }
    ]
)
print(message.content)

Note: When you pass an unsupported model name to DeepSeek's Anthropic API, the API backend will automatically map it to the deepseek-chat model.
Anthropic API Compatibility Details
HTTP Header
Field	Support Status
anthropic-beta	Ignored
anthropic-version	Ignored
x-api-key	Fully Supported
Simple Fields
Field	Support Status
model	Use DeepSeek Model Instead
max_tokens	Fully Supported
container	Ignored
mcp_servers	Ignored
metadata	Ignored
service_tier	Ignored
stop_sequences	Fully Supported
stream	Fully Supported
system	Fully Supported
temperature	Fully Supported (range [0.0 ~ 2.0])
thinking	Supported (budget_tokens is ignored)
top_k	Ignored
top_p	Fully Supported
Tool Fields
tools
Field	Support Status
name	Fully Supported
input_schema	Fully Supported
description	Fully Supported
cache_control	Ignored
tool_choice
Value	Support Status
none	Fully Supported
auto	Supported (disable_parallel_tool_use is ignored)
any	Supported (disable_parallel_tool_use is ignored)
tool	Supported (disable_parallel_tool_use is ignored)
Message Fields
Field	Variant	Sub-Field	Support Status
content 	string 		Fully Supported
array, type="text"	text 	Fully Supported
cache_control 	Ignored
citations 	Ignored
array, type="image" 		Not Supported
array, type = "document" 		Not Supported
array, type = "search_result" 		Not Supported
array, type = "thinking" 		Supported
array, type="redacted_thinking" 		Not Supported
array, type = "tool_use" 	id 	Fully Supported
input 	Fully Supported
name 	Fully Supported
cache_control 	Ignored
array, type = "tool_result" 	tool_use_id 	Fully Supported
content 	Fully Supported
cache_control 	Ignored
is_error 	Ignored
array, type = "server_tool_use" 		Not Supported
array, type = "web_search_tool_result" 		Not Supported
array, type = "code_execution_tool_result" 		Not Supported
array, type = "mcp_tool_use" 		Not Supported
array, type = "mcp_tool_result" 		Not Supported
array, type = "container_upload" 		Not Supported 


DeepSeek API

The DeepSeek API. To use the DeepSeek API, please create an API key first.
Authentication

    HTTP: Bearer Auth

Security Scheme Type:
	

http

HTTP Authorization Scheme:
	

bearer

Contact

DeepSeek Support: api-service@deepseek.com

Terms of Service

https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html

License

MIT


Create Chat Completion

POST 
https://api.deepseek.com/chat/completions

Creates a model response for the given chat conversation.
Request

    application/json

Body

required

    messages

    object[]

    required
    model
    stringrequired

    Possible values: [deepseek-chat, deepseek-reasoner]

    ID of the model to use. You can use deepseek-chat.

    thinking

    object

    nullable
    frequency_penalty
    numbernullable

    Possible values: >= -2 and <= 2

    Default value: 0

    Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.
    max_tokens
    integernullable

    The maximum number of tokens that can be generated in the chat completion.

    The total length of input tokens and generated tokens is limited by the model's context length.

    For the value range and default value, please refer to the documentation.
    presence_penalty
    numbernullable

    Possible values: >= -2 and <= 2

    Default value: 0

    Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.

    response_format

    object

    nullable

    stop

    object

    nullable
    stream
    booleannullable

    If set, partial message deltas will be sent. Tokens will be sent as data-only server-sent events (SSE) as they become available, with the stream terminated by a data: [DONE] message.

    stream_options

    object

    nullable
    temperature
    numbernullable

    Possible values: <= 2

    Default value: 1

    What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.

    We generally recommend altering this or top_p but not both.
    top_p
    numbernullable

    Possible values: <= 1

    Default value: 1

    An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

    We generally recommend altering this or temperature but not both.

    tools

    object[]

    nullable

    tool_choice

    object

    nullable
    logprobs
    booleannullable

    Whether to return log probabilities of the output tokens or not. If true, returns the log probabilities of each output token returned in the content of message.
    top_logprobs
    integernullable

    Possible values: <= 20

    An integer between 0 and 20 specifying the number of most likely tokens to return at each token position, each with an associated log probability. logprobs must be set to true if this parameter is used.

Responses

    200 (No streaming)
    200 (Streaming)

OK, returns a chat completion object

    application/json

    Schema
    Example (from schema)
    Example

Schema

    id
    stringrequired

    A unique identifier for the chat completion.

    choices

    object[]

    required
    created
    integerrequired

    The Unix timestamp (in seconds) of when the chat completion was created.
    model
    stringrequired

    The model used for the chat completion.
    system_fingerprint
    stringrequired

    This fingerprint represents the backend configuration that the model runs with.
    object
    stringrequired

    Possible values: [chat.completion]

    The object type, which is always chat.completion.

    usage

    object

    curl
    python
    go
    nodejs
    ruby
    csharp
    php
    java
    powershell

    OpenAI SDK

from openai import OpenAI

# for backward compatibility, you can still use `https://api.deepseek.com/v1` as `base_url`.
client = OpenAI(api_key="<your API key>", base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
  ],
    max_tokens=1024,
    temperature=0.7,
    stream=False
)

print(response.choices[0].message.content)

    REQUESTS
    HTTP.CLIENT

import requests
import json

url = "https://api.deepseek.com/chat/completions"

payload = json.dumps({
  "messages": [
    {
      "content": "You are a helpful assistant",
      "role": "system"
    },
    {
      "content": "Hi",
      "role": "user"
    }
  ],
  "model": "deepseek-chat",
  "thinking": {
    "type": "disabled"
  },
  "frequency_penalty": 0,
  "max_tokens": 4096,
  "presence_penalty": 0,
  "response_format": {
    "type": "text"
  },
  "stop": None,
  "stream": False,
  "stream_options": None,
  "temperature": 1,
  "top_p": 1,
  "tools": None,
  "tool_choice": "none",
  "logprobs": False,
  "top_logprobs": None
})
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer <TOKEN>'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)

Request Collapse all
Base URL
https://api.deepseek.com
Base URL
https://api.deepseek.com
Auth
Bearer Token
Body required

{
  "messages": [
    {
      "content": "You are a helpful assistant",
      "role": "system"
    },
    {
      "content": "Hi",
      "role": "user"
    }
  ],
  "model": "deepseek-chat",
  "thinking": {
    "type": "disabled"
  },
  "frequency_penalty": 0,
  "max_tokens": 4096,
  "presence_penalty": 0,
  "response_format": {
    "type": "text"
  },
  "stop": null,
  "stream": false,
  "stream_options": null,
  "temperature": 1,
  "top_p": 1,
  "tools": null,
  "tool_choice": "none",
  "logprobs": false,
  "top_logprobs": null
}

ResponseClear

Click the Send API Request button above and see the response here!
Previous
Introduction
Next


Create FIM Completion (Beta)

POST 
https://api.deepseek.com/beta/completions

The FIM (Fill-In-the-Middle) Completion API. User must set base_url="https://api.deepseek.com/beta" to use this feature.
Request

    application/json

Body

required

    model
    stringrequired

    Possible values: [deepseek-chat]

    ID of the model to use.
    prompt
    stringrequired

    Default value: Once upon a time,

    The prompt to generate completions for.
    echo
    booleannullable

    Echo back the prompt in addition to the completion
    frequency_penalty
    numbernullable

    Possible values: >= -2 and <= 2

    Default value: 0

    Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.
    logprobs
    integernullable

    Possible values: <= 20

    Include the log probabilities on the logprobs most likely output tokens, as well the chosen tokens. For example, if logprobs is 20, the API will return a list of the 20 most likely tokens. The API will always return the logprob of the sampled token, so there may be up to logprobs+1 elements in the response.

    The maximum value for logprobs is 20.
    max_tokens
    integernullable

    The maximum number of tokens that can be generated in the completion.
    presence_penalty
    numbernullable

    Possible values: >= -2 and <= 2

    Default value: 0

    Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.

    stop

    object

    nullable
    stream
    booleannullable

    Whether to stream back partial progress. If set, tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. Example Python code.

    stream_options

    object

    nullable
    suffix
    stringnullable

    The suffix that comes after a completion of inserted text.
    temperature
    numbernullable

    Possible values: <= 2

    Default value: 1

    What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.

    We generally recommend altering this or top_p but not both.
    top_p
    numbernullable

    Possible values: <= 1

    Default value: 1

    An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

    We generally recommend altering this or temperature but not both.

Responses

    200

OK

    application/json

    Schema
    Example (from schema)

Schema

    id
    stringrequired

    A unique identifier for the completion.

    choices

    object[]

    required
    created
    integerrequired

    The Unix timestamp (in seconds) of when the completion was created.
    model
    stringrequired

    The model used for completion.
    system_fingerprint
    string

    This fingerprint represents the backend configuration that the model runs with.
    object
    stringrequired

    Possible values: [text_completion]

    The object type, which is always "text_completion"

    usage

    object

    curl
    python
    go
    nodejs
    ruby
    csharp
    php
    java
    powershell

    OpenAI SDK

from openai import OpenAI

# user should set `base_url="https://api.deepseek.com/beta"` to use this feature.
client = OpenAI(
  api_key="<your API key>",
  base_url="https://api.deepseek.com/beta",
)
response = client.completions.create(
  model="deepseek-chat",
  prompt="def fib(a):",
  suffix="    return fib(a-1) + fib(a-2)",
  max_tokens=128)
print(response.choices[0].text)

    REQUESTS
    HTTP.CLIENT

import requests
import json

url = "https://api.deepseek.com/beta/completions"

payload = json.dumps({
  "model": "deepseek-chat",
  "prompt": "Once upon a time, ",
  "echo": False,
  "frequency_penalty": 0,
  "logprobs": 0,
  "max_tokens": 1024,
  "presence_penalty": 0,
  "stop": None,
  "stream": False,
  "stream_options": None,
  "suffix": None,
  "temperature": 1,
  "top_p": 1
})
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer <TOKEN>'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)

Request Collapse all
Base URL
https://api.deepseek.com/beta
Base URL
https://api.deepseek.com/beta
Auth
Bearer Token
Body required

{
  "model": "deepseek-chat",
  "prompt": "Once upon a time, ",
  "echo": false,
  "frequency_penalty": 0,
  "logprobs": 0,
  "max_tokens": 1024,
  "presence_penalty": 0,
  "stop": null,
  "stream": false,
  "stream_options": null,
  "suffix": null,
  "temperature": 1,
  "top_p": 1
}

ResponseClear

Click the Send API Request but


Lists Models

GET 
https://api.deepseek.com/models

Lists the currently available models, and provides basic information about each one such as the owner and availability. Check Models & Pricing for our currently supported models.
Responses

    200

OK, returns A list of models

    application/json

    Schema
    Example (from schema)
    Example

Schema

    object
    stringrequired

    Possible values: [list]

    data

    Model[]

    required

    curl
    python
    go
    nodejs
    ruby
    csharp
    php
    java
    powershell

    OpenAI SDK

from openai import OpenAI

# for backward compatibility, you can still use `https://api.deepseek.com/v1` as `base_url`.
client = OpenAI(api_key="<your API key>", base_url="https://api.deepseek.com")
print(client.models.list())

    REQUESTS
    HTTP.CLIENT

import requests

url = "https://api.deepseek.com/models"

payload={}
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer <TOKEN>'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

Request Collapse all
Base URL
https://api.deepseek.com
Base URL
https://api.deepseek.com
Auth
Bearer Token
ResponseClear

Click the Send API Request button above and see the response here!


Get User Balance

GET 
https://api.deepseek.com/user/balance

Get user current balance
Responses

    200

OK, returns user balance info.

    application/json

    Schema
    Example (from schema)
    Example

Schema

    is_available
    boolean

    Whether the user's balance is sufficient for API calls.

    balance_infos

    object[]

    curl
    python
    go
    nodejs
    ruby
    csharp
    php
    java
    powershell

    REQUESTS
    HTTP.CLIENT

import requests

url = "https://api.deepseek.com/user/balance"

payload={}
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer <TOKEN>'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

Request Collapse all
Base URL
https://api.deepseek.com
Base URL
https://api.deepseek.com
Auth
Bearer Token
ResponseClear

Click the Send API Request button above and see the response here!