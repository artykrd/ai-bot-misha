<br />

<br />

# Gemini API

The fastest path from prompt to production with Gemini, Veo, Nano Banana, and more.  

### Python

    from google import genai

    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Explain how AI works in a few words",
    )

    print(response.text)

### JavaScript

    import { GoogleGenAI } from "@google/genai";

    const ai = new GoogleGenAI({});

    async function main() {
      const response = await ai.models.generateContent({
        model: "gemini-2.5-flash",
        contents: "Explain how AI works in a few words",
      });
      console.log(response.text);
    }

    await main();

### Go

    package main

    import (
        "context"
        "fmt"
        "log"
        "google.golang.org/genai"
    )

    func main() {
        ctx := context.Background()
        client, err := genai.NewClient(ctx, nil)
        if err != nil {
            log.Fatal(err)
        }

        result, err := client.Models.GenerateContent(
            ctx,
            "gemini-2.5-flash",
            genai.Text("Explain how AI works in a few words"),
            nil,
        )
        if err != nil {
            log.Fatal(err)
        }
        fmt.Println(result.Text())
    }

### Java

    package com.example;

    import com.google.genai.Client;
    import com.google.genai.types.GenerateContentResponse;

    public class GenerateTextFromTextInput {
      public static void main(String[] args) {
        Client client = new Client();

        GenerateContentResponse response =
            client.models.generateContent(
                "gemini-2.5-flash",
                "Explain how AI works in a few words",
                null);

        System.out.println(response.text());
      }
    }

### C#

    using System.Threading.Tasks;
    using Google.GenAI;
    using Google.GenAI.Types;

    public class GenerateContentSimpleText {
      public static async Task main() {
        var client = new Client();
        var response = await client.Models.GenerateContentAsync(
          model: "gemini-2.5-flash", contents: "Explain how AI works in a few words"
        );
        Console.WriteLine(response.Candidates[0].Content.Parts[0].Text);
      }
    }

### REST

    curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
      -H "x-goog-api-key: $GEMINI_API_KEY" \
      -H 'Content-Type: application/json' \
      -X POST \
      -d '{
        "contents": [
          {
            "parts": [
              {
                "text": "Explain how AI works in a few words"
              }
            ]
          }
        ]
      }'

[Start building](https://ai.google.dev/gemini-api/docs/quickstart)  
Follow our Quickstart guide to get an API key and make your first API call in minutes.

*** ** * ** ***

## Meet the models

[auto_awesomeGemini 3 Pro
Our most intelligent model, the best in the world for multimodal understanding, all built on state-of-the-art reasoning.](https://ai.google.dev/gemini-api/docs/models#gemini-3-pro)[video_libraryVeo 3.1
Our state-of-the-art video generation model, with native audio.](https://ai.google.dev/gemini-api/docs/video)[🍌Nano Banana and Nano Banana Pro
State-of-the-art image generation and editing models.](https://ai.google.dev/gemini-api/docs/image-generation)[sparkGemini 2.5 Pro
Our powerful reasoning model, which excels at coding and complex reasonings tasks.](https://ai.google.dev/gemini-api/docs/models#gemini-2.5-pro)[sparkGemini 2.5 Flash
Our most balanced model, with a 1 million token context window and more.](https://ai.google.dev/gemini-api/docs/models/gemini#gemini-2.5-flash)[sparkGemini 2.5 Flash-Lite
Our fastest and most cost-efficient multimodal model with great performance for high-frequency tasks.](https://ai.google.dev/gemini-api/docs/models/gemini#gemini-2.5-flash-lite)

## Explore Capabilities

[imagesmode
Native Image Generation (Nano Banana)
Generate and edit highly contextual images natively with Gemini 2.5 Flash Image.](https://ai.google.dev/gemini-api/docs/image-generation)[article
Long Context
Input millions of tokens to Gemini models and derive understanding from unstructured images, videos, and documents.](https://ai.google.dev/gemini-api/docs/long-context)[code
Structured Outputs
Constrain Gemini to respond with JSON, a structured data format suitable for automated processing.](https://ai.google.dev/gemini-api/docs/structured-output)[functions
Function Calling
Build agentic workflows by connecting Gemini to external APIs and tools.](https://ai.google.dev/gemini-api/docs/function-calling)[videocam
Video Generation with Veo 3.1
Create high-quality video content from text or image prompts with our state-of-the-art model.](https://ai.google.dev/gemini-api/docs/video)[android_recorder
Voice Agents with Live API
Build real-time voice applications and agents with the Live API.](https://ai.google.dev/gemini-api/docs/live)[build
Tools
Connect Gemini to the world through built-in tools like Google Search, URL Context, Google Maps, Code Execution and Computer Use.](https://ai.google.dev/gemini-api/docs/tools)[stacks
Document Understanding
Process up to 1000 pages of PDF files with full multimodal understanding or other text-based file types.](https://ai.google.dev/gemini-api/docs/document-processing)[cognition_2
Thinking
Explore how thinking capabilities improve reasoning for complex tasks and agents.](https://ai.google.dev/gemini-api/docs/thinking)

## Resources

[Google AI Studio
Test prompts, manage your API keys, monitor usage, and build prototypes in platform for AI builders.
Open Google AI Studio](https://aistudio.google.com)[groupDeveloper Community
Ask questions and find solutions from other developers and Google engineers.
Join the community](https://discuss.ai.google.dev/c/gemini-api/4)[menu_bookAPI Reference
Find detailed information about the Gemini API in the official reference documentation.
Read the API reference](https://ai.google.dev/api)


<br />

This quickstart shows you how to install our[libraries](https://ai.google.dev/gemini-api/docs/libraries)and make your first Gemini API request.

## Before you begin

You need a Gemini API key. If you don't already have one, you can[get it for free in Google AI Studio](https://aistudio.google.com/app/apikey).

## Install the Google GenAI SDK

### Python

Using[Python 3.9+](https://www.python.org/downloads/), install the[`google-genai`package](https://pypi.org/project/google-genai/)using the following[pip command](https://packaging.python.org/en/latest/tutorials/installing-packages/):  

    pip install -q -U google-genai

### JavaScript

Using[Node.js v18+](https://nodejs.org/en/download/package-manager), install the[Google Gen AI SDK for TypeScript and JavaScript](https://www.npmjs.com/package/@google/genai)using the following[npm command](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm):  

    npm install @google/genai

### Go

Install[google.golang.org/genai](https://pkg.go.dev/google.golang.org/genai)in your module directory using the[go get command](https://go.dev/doc/code):  

    go get google.golang.org/genai

### Java

If you're using Maven, you can install[google-genai](https://github.com/googleapis/java-genai)by adding the following to your dependencies:  

    <dependencies>
      <dependency>
        <groupId>com.google.genai</groupId>
        <artifactId>google-genai</artifactId>
        <version>1.0.0</version>
      </dependency>
    </dependencies>

### C#

Install[googleapis/go-genai](https://googleapis.github.io/dotnet-genai/)in your module directory using the[dotnet add command](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-package-add)  

    dotnet add package Google.GenAI

### Apps Script

1. To create a new Apps Script project, go to[script.new](https://script.google.com/u/0/home/projects/create).
2. Click**Untitled project**.
3. Rename the Apps Script project**AI Studio** and click**Rename**.
4. Set your[API key](https://developers.google.com/apps-script/guides/properties#manage_script_properties_manually)
   1. At the left, click**Project Settings** ![The icon for project settings](https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/settings/default/24px.svg).
   2. Under**Script Properties** click**Add script property**.
   3. For**Property** , enter the key name:`GEMINI_API_KEY`.
   4. For**Value**, enter the value for the API key.
   5. Click**Save script properties**.
5. Replace the`Code.gs`file contents with the following code:

## Make your first request

Here is an example that uses the[`generateContent`](https://ai.google.dev/api/generate-content#method:-models.generatecontent)method to send a request to the Gemini API using the Gemini 2.5 Flash model.

If you[set your API key](https://ai.google.dev/gemini-api/docs/api-key#set-api-env-var)as the environment variable`GEMINI_API_KEY`, it will be picked up automatically by the client when using the[Gemini API libraries](https://ai.google.dev/gemini-api/docs/libraries). Otherwise you will need to[pass your API key](https://ai.google.dev/gemini-api/docs/api-key#provide-api-key-explicitly)as an argument when initializing the client.

Note that all code samples in the Gemini API docs assume that you have set the environment variable`GEMINI_API_KEY`.  

### Python

    from google import genai

    # The client gets the API key from the environment variable `GEMINI_API_KEY`.
    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents="Explain how AI works in a few words"
    )
    print(response.text)

### JavaScript

    import { GoogleGenAI } from "@google/genai";

    // The client gets the API key from the environment variable `GEMINI_API_KEY`.
    const ai = new GoogleGenAI({});

    async function main() {
      const response = await ai.models.generateContent({
        model: "gemini-2.5-flash",
        contents: "Explain how AI works in a few words",
      });
      console.log(response.text);
    }

    main();

### Go

    package main

    import (
        "context"
        "fmt"
        "log"
        "google.golang.org/genai"
    )

    func main() {
        ctx := context.Background()
        // The client gets the API key from the environment variable `GEMINI_API_KEY`.
        client, err := genai.NewClient(ctx, nil)
        if err != nil {
            log.Fatal(err)
        }

        result, err := client.Models.GenerateContent(
            ctx,
            "gemini-2.5-flash",
            genai.Text("Explain how AI works in a few words"),
            nil,
        )
        if err != nil {
            log.Fatal(err)
        }
        fmt.Println(result.Text())
    }

### Java

    package com.example;

    import com.google.genai.Client;
    import com.google.genai.types.GenerateContentResponse;

    public class GenerateTextFromTextInput {
      public static void main(String[] args) {
        // The client gets the API key from the environment variable `GEMINI_API_KEY`.
        Client client = new Client();

        GenerateContentResponse response =
            client.models.generateContent(
                "gemini-2.5-flash",
                "Explain how AI works in a few words",
                null);

        System.out.println(response.text());
      }
    }

### C#

    using System.Threading.Tasks;
    using Google.GenAI;
    using Google.GenAI.Types;

    public class GenerateContentSimpleText {
      public static async Task main() {
        // The client gets the API key from the environment variable `GEMINI_API_KEY`.
        var client = new Client();
        var response = await client.Models.GenerateContentAsync(
          model: "gemini-2.5-flash", contents: "Explain how AI works in a few words"
        );
        Console.WriteLine(response.Candidates[0].Content.Parts[0].Text);
      }
    }

### Apps Script

    // See https://developers.google.com/apps-script/guides/properties
    // for instructions on how to set the API key.
    const apiKey = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');
    function main() {
      const payload = {
        contents: [
          {
            parts: [
              { text: 'Explain how AI works in a few words' },
            ],
          },
        ],
      };

      const url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent';
      const options = {
        method: 'POST',
        contentType: 'application/json',
        headers: {
          'x-goog-api-key': apiKey,
        },
        payload: JSON.stringify(payload)
      };

      const response = UrlFetchApp.fetch(url, options);
      const data = JSON.parse(response);
      const content = data['candidates'][0]['content']['parts'][0]['text'];
      console.log(content);
    }

### REST

    curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
      -H "x-goog-api-key: $GEMINI_API_KEY" \
      -H 'Content-Type: application/json' \
      -X POST \
      -d '{
        "contents": [
          {
            "parts": [
              {
                "text": "Explain how AI works in a few words"
              }
            ]
          }
        ]
      }'

## What's next

Now that you made your first API request, you might want to explore the following guides that show Gemini in action:

- [Text generation](https://ai.google.dev/gemini-api/docs/text-generation)
- [Image generation](https://ai.google.dev/gemini-api/docs/image-generation)
- [Image understanding](https://ai.google.dev/gemini-api/docs/image-understanding)
- [Thinking](https://ai.google.dev/gemini-api/docs/thinking)
- [Function calling](https://ai.google.dev/gemini-api/docs/function-calling)
- [Long context](https://ai.google.dev/gemini-api/docs/long-context)
- [Embeddings](https://ai.google.dev/gemini-api/docs/embeddings)


<br />

To use the Gemini API, you need an API key. This page outlines how to create and manage your keys in Google AI Studio as well as how to set up your environment to use them in your code.

## API Keys

An[API key](https://cloud.google.com/api-keys/docs/overview)is an encrypted string that you can use when calling Google Cloud APIs. You can create and manage all your Gemini API Keys from the[Google AI Studio](https://aistudio.google.com/app/apikey)**API Keys**page.

Once you have an API key, you have the following options to connect to the Gemini API:

- [Setting your API key as an environment variable](https://ai.google.dev/gemini-api/docs/api-key#set-api-env-var)
- [Providing your API key explicitly](https://ai.google.dev/gemini-api/docs/api-key#provide-api-key-explicitly)

For initial testing, you can hard code an API key, but this should only be temporary since it's not secure. You can find examples for hard coding the API key in[Providing API key explicitly](https://ai.google.dev/gemini-api/docs/api-key#provide-api-key-explicitly)section.

## Google Cloud projects

[Google Cloud projects](https://cloud.google.com/resource-manager/docs/creating-managing-projects)are fundamental to using Google Cloud services (such as the Gemini API), managing billing, and controlling collaborators and permissions. Google AI Studio provides a lightweight interface to your Google Cloud projects.

If you don't have any projects created yet, you must either create a new project or import one from Google Cloud into Google AI Studio. The**Projects** page in Google AI Studio will display all keys that have sufficient permission to use the Gemini API. Refer to the[import projects](https://ai.google.dev/gemini-api/docs/api-key#import-projects)section for instructions.

### Default project

For new users, after accepting Terms of Service, Google AI Studio creates a default Google Cloud Project and API Key, for ease of use. You can rename this project in Google AI Studio by navigating to**Projects** view in the**Dashboard** , clicking the 3 dots settings button next to a project and choosing**Rename project**. Existing users, or users who already have Google Cloud Accounts won't have a default project created.

## Import projects

Each Gemini API key is associated with a Google Cloud project. By default, Google AI Studio does not show all of your Cloud Projects. You must import the projects you want by searching for the name or project ID in the**Import Projects**dialog. To view a complete list of projects you have access to, visit the Cloud Console.

If you don't have any projects imported yet, follow these steps to import a Google Cloud project and create a key:

1. Go to[Google AI Studio](https://aistudio.google.com).
2. Open the**Dashboard**from the left side panel.
3. Select**Projects**.
4. Select the**Import projects** button in the**Projects**page.
5. Search for and select the Google Cloud project you want to import and select the**Import**button.

Once a project is imported, go to the**API Keys** page from the**Dashboard**menu and create an API key in the project you just imported.
| **Note:** For existing users, the keys are pre-populated in the imports pane based on the last 30-days of activity in AI Studio.

## Limitations

The following are limitations of managing API keys and Google Cloud projects in Google AI Studio.

- You can create a maximum of 10 project at a time from the Google AI Studio**Projects**page.
- You can name and rename projects and keys.
- The**API keys** and**Projects**pages display a maximum of 100 keys and 50 projects.
- Only API keys that have no restrictions, or are restricted to the Generative Language API are displayed.

For additional management access to your projects, visit the Google Cloud Console.

## Setting the API key as an environment variable

If you set the environment variable`GEMINI_API_KEY`or`GOOGLE_API_KEY`, the API key will automatically be picked up by the client when using one of the[Gemini API libraries](https://ai.google.dev/gemini-api/docs/libraries). It's recommended that you set only one of those variables, but if both are set,`GOOGLE_API_KEY`takes precedence.

If you're using the REST API, or JavaScript on the browser, you will need to provide the API key explicitly.

Here is how you can set your API key locally as the environment variable`GEMINI_API_KEY`with different operating systems.  

### Linux/macOS - Bash

Bash is a common Linux and macOS terminal configuration. You can check if you have a configuration file for it by running the following command:  

    ~/.bashrc

If the response is "No such file or directory", you will need to create this file and open it by running the following commands, or use`zsh`:  

    touch ~/.bashrc
    open ~/.bashrc

Next, you need to set your API key by adding the following export command:  

    export GEMINI_API_KEY=<YOUR_API_KEY_HERE>

After saving the file, apply the changes by running:  

    source ~/.bashrc

### macOS - Zsh

Zsh is a common Linux and macOS terminal configuration. You can check if you have a configuration file for it by running the following command:  

    ~/.zshrc

If the response is "No such file or directory", you will need to create this file and open it by running the following commands, or use`bash`:  

    touch ~/.zshrc
    open ~/.zshrc

Next, you need to set your API key by adding the following export command:  

    export GEMINI_API_KEY=<YOUR_API_KEY_HERE>

After saving the file, apply the changes by running:  

    source ~/.zshrc

### Windows

1. Search for "Environment Variables" in the search bar.
2. Choose to modify**System Settings**. You may have to confirm you want to do this.
3. In the system settings dialog, click the button labeled**Environment Variables**.
4. Under either**User variables** (for the current user) or**System variables** (applies to all users who use the machine), click**New...**
5. Specify the variable name as`GEMINI_API_KEY`. Specify your Gemini API Key as the variable value.
6. Click**OK**to apply the changes.
7. Open a new terminal session (cmd or Powershell) to get the new variable.

## Providing the API key explicitly

In some cases, you may want to explicitly provide an API key. For example:

- You're doing a simple API call and prefer hard coding the API key.
- You want explicit control without having to rely on automatic discovery of environment variables by the Gemini API libraries
- You're using an environment where environment variables are not supported (e.g web) or you are making REST calls.

Below are examples for how you can provide an API key explicitly:  

### Python

    from google import genai

    client = genai.Client(api_key="<var translate="no">YOUR_API_KEY</var>")

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents="Explain how AI works in a few words"
    )
    print(response.text)

### JavaScript

    import { GoogleGenAI } from "@google/genai";

    const ai = new GoogleGenAI({ apiKey: "<var translate="no">YOUR_API_KEY</var>" });

    async function main() {
      const response = await ai.models.generateContent({
        model: "gemini-2.5-flash",
        contents: "Explain how AI works in a few words",
      });
      console.log(response.text);
    }

    main();

### Go

    package main

    import (
        "context"
        "fmt"
        "log"
        "google.golang.org/genai"
    )

    func main() {
        ctx := context.Background()
        client, err := genai.NewClient(ctx, &genai.ClientConfig{
            APIKey:  "<var translate="no">YOUR_API_KEY</var>",
            Backend: genai.BackendGeminiAPI,
        })
        if err != nil {
            log.Fatal(err)
        }

        result, err := client.Models.GenerateContent(
            ctx,
            "gemini-2.5-flash",
            genai.Text("Explain how AI works in a few words"),
            nil,
        )
        if err != nil {
            log.Fatal(err)
        }
        fmt.Println(result.Text())
    }

### Java

    package com.example;

    import com.google.genai.Client;
    import com.google.genai.types.GenerateContentResponse;

    public class GenerateTextFromTextInput {
      public static void main(String[] args) {
        Client client = Client.builder().apiKey("<var translate="no">YOUR_API_KEY</var>").build();

        GenerateContentResponse response =
            client.models.generateContent(
                "gemini-2.5-flash",
                "Explain how AI works in a few words",
                null);

        System.out.println(response.text());
      }
    }

### REST

    curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
      -H 'Content-Type: application/json' \
      -H "x-goog-api-key: <var translate="no">YOUR_API_KEY</var>" \
      -X POST \
      -d '{
        "contents": [
          {
            "parts": [
              {
                "text": "Explain how AI works in a few words"
              }
            ]
          }
        ]
      }'

## Keep your API key secure

Treat your Gemini API key like a password. If compromised, others can use your project's quota, incur charges (if billing is enabled), and access your private data, such as files.

### Critical security rules

- **Never commit API keys to source control.**Do not check your API key into version control systems like Git.

- **Never expose API keys on the client-side.**Do not use your API key directly in web or mobile apps in production. Keys in client-side code (including our JavaScript/TypeScript libraries and REST calls) can be extracted.

### Best practices

- **Use server-side calls with API keys**The most secure way to use your API key is to call the Gemini API from a server-side application where the key can be kept confidential.

- **Use ephemeral tokens for client-side access (Live API only):** For direct client-side access to the Live API, you can use ephemeral tokens. They come with lower security risks and can be suitable for production use. Review[ephemeral tokens](https://ai.google.dev/gemini-api/docs/ephemeral-tokens)guide for more information.

- **Consider adding restrictions to your key:** You can limit a key's permissions by adding[API key restrictions](https://cloud.google.com/api-keys/docs/add-restrictions-api-keys#add-api-restrictions). This minimizes the potential damage if the key is ever leaked.

For some general best practices, you can also review this[support article](https://support.google.com/googleapi/answer/6310037).


<br />

<br />

When building with the Gemini API, we recommend using the**Google GenAI SDK** . These are the official, production-ready libraries that we develop and maintain for the most popular languages. They are in[General Availability](https://ai.google.dev/gemini-api/docs/libraries#new-libraries)and used in all our official documentation and examples.
| **Note:** If you're using one of our legacy libraries, we strongly recommend you[migrate](https://ai.google.dev/gemini-api/docs/migrate)to the Google GenAI SDK. Review the[legacy libraries](https://ai.google.dev/gemini-api/docs/libraries#previous-sdks)section for more information.

If you're new to the Gemini API, follow our[quickstart guide](https://ai.google.dev/gemini-api/docs/quickstart)to get started.

## Language support and installation

The Google GenAI SDK is available for the Python, JavaScript/TypeScript, Go and Java languages. You can install each language's library using package managers, or visit their GitHub repos for further engagement:  

### Python

- Library:[`google-genai`](https://pypi.org/project/google-genai)

- GitHub Repository:[googleapis/python-genai](https://github.com/googleapis/python-genai)

- Installation:`pip install google-genai`

### JavaScript

- Library:[`@google/genai`](https://www.npmjs.com/package/@google/genai)

- GitHub Repository:[googleapis/js-genai](https://github.com/googleapis/js-genai)

- Installation:`npm install @google/genai`

### Go

- Library:[`google.golang.org/genai`](https://pkg.go.dev/google.golang.org/genai)

- GitHub Repository:[googleapis/go-genai](https://github.com/googleapis/go-genai)

- Installation:`go get google.golang.org/genai`

### Java

- Library:`google-genai`

- GitHub Repository:[googleapis/java-genai](https://github.com/googleapis/java-genai)

- Installation: If you're using Maven, add the following to your dependencies:

    <dependencies>
      <dependency>
        <groupId>com.google.genai</groupId>
        <artifactId>google-genai</artifactId>
        <version>1.0.0</version>
      </dependency>
    </dependencies>

### C#

- Library:`Google.GenAI`

- GitHub Repository:[googleapis/go-genai](https://googleapis.github.io/dotnet-genai/)

- Installation:`dotnet add package Google.GenAI`

## General availability

We started rolling out Google GenAI SDK, a new set of libraries to access Gemini API, in late 2024 when we launched Gemini 2.0.

As of May 2025, they reached General Availability (GA) across all supported platforms and are the recommended libraries to access the Gemini API. They are stable, fully supported for production use, and are actively maintained. They provide access to the latest features, and offer the best performance working with Gemini.

If you're using one of our legacy libraries, we strongly recommend you migrate so that you can access the latest features and get the best performance working with Gemini. Review the[legacy libraries](https://ai.google.dev/gemini-api/docs/libraries#previous-sdks)section for more information.

## Legacy libraries and migration

If you are using one of our legacy libraries, we recommend that you[migrate to the new libraries](https://ai.google.dev/gemini-api/docs/migrate).

The legacy libraries don't provide access to recent features (such as[Live API](https://ai.google.dev/gemini-api/docs/live)and[Veo](https://ai.google.dev/gemini-api/docs/video)) and are on a deprecation path. They will stop receiving updates on November 30th, 2025, the feature gaps will grow and potential bugs may no longer get fixed.

Each legacy library's support status varies, detailed in the following table:

|         Language          |                                     Legacy library                                      |                         Support status                         |                                                        Recommended library                                                        |
|---------------------------|-----------------------------------------------------------------------------------------|----------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| **Python**                | [google-generativeai](https://github.com/google-gemini/deprecated-generative-ai-python) | All support, including bug fixes, ends on November 30th, 2025. | [google-genai](https://github.com/googleapis/python-genai)                                                                        |
| **JavaScript/TypeScript** | [@google/generativeai](https://github.com/google-gemini/generative-ai-js)               | All support, including bug fixes, ends on November 30th, 2025. | [@google/genai](https://github.com/googleapis/js-genai)                                                                           |
| **Go**                    | [google.golang.org/generative-ai](https://github.com/google/generative-ai-go)           | All support, including bug fixes, ends on November 30th, 2025. | [google.golang.org/genai](https://github.com/googleapis/go-genai)                                                                 |
| **Dart and Flutter**      | [google_generative_ai](https://pub.dev/packages/google_generative_ai/install)           | Not actively maintained                                        | Use trusted community or third party libraries, like[firebase_ai](https://pub.dev/packages/firebase_ai), or access using REST API |
| **Swift**                 | [generative-ai-swift](https://github.com/google/generative-ai-swift)                    | Not actively maintained                                        | Use[Firebase AI Logic](https://firebase.google.com/products/firebase-ai-logic)                                                    |
| **Android**               | [generative-ai-android](https://github.com/google-gemini/generative-ai-android)         | Not actively maintained                                        | Use[Firebase AI Logic](https://firebase.google.com/products/firebase-ai-logic)                                                    |

**Note for Java developers:** There was no legacy Google-provided Java SDK for the Gemini API, so no migration from a previous Google library is required. You can start directly with the new library in the[Language support and installation](https://ai.google.dev/gemini-api/docs/libraries#install)section.

## Prompt templates for code generation

Generative models (e.g., Gemini, Claude) and AI-powered IDEs (e.g., Cursor) may produce code for the Gemini API using outdated or deprecated libraries due to their training data cutoff. For the generated code to use the latest, recommended libraries, provide version and usage guidance directly in your prompts. You can use the templates below to provide the necessary context:

- [Python](https://github.com/googleapis/python-genai/blob/main/codegen_instructions.md)

- [JavaScript/TypeScript](https://github.com/googleapis/js-genai/blob/main/codegen_instructions.md)


<br />

<br />

Gemini models are accessible using the OpenAI libraries (Python and TypeScript / Javascript) along with the REST API, by updating three lines of code and using your[Gemini API key](https://aistudio.google.com/apikey). If you aren't already using the OpenAI libraries, we recommend that you call the[Gemini API directly](https://ai.google.dev/gemini-api/docs/quickstart).  

### Python

    from openai import OpenAI

    client = OpenAI(
        api_key="GEMINI_API_KEY",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "Explain to me how AI works"
            }
        ]
    )

    print(response.choices[0].message)

### JavaScript

    import OpenAI from "openai";

    const openai = new OpenAI({
        apiKey: "GEMINI_API_KEY",
        baseURL: "https://generativelanguage.googleapis.com/v1beta/openai/"
    });

    const response = await openai.chat.completions.create({
        model: "gemini-2.0-flash",
        messages: [
            { role: "system", content: "You are a helpful assistant." },
            {
                role: "user",
                content: "Explain to me how AI works",
            },
        ],
    });

    console.log(response.choices[0].message);

### REST

    curl "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer GEMINI_API_KEY" \
    -d '{
        "model": "gemini-2.0-flash",
        "messages": [
            {"role": "user", "content": "Explain to me how AI works"}
        ]
        }'

What changed? Just three lines!

- **`api_key="GEMINI_API_KEY"`** : Replace "`GEMINI_API_KEY`" with your actual Gemini API key, which you can get in[Google AI Studio](https://aistudio.google.com).

- **`base_url="https://generativelanguage.googleapis.com/v1beta/openai/"`:**This tells the OpenAI library to send requests to the Gemini API endpoint instead of the default URL.

- **`model="gemini-2.5-flash"`**: Choose a compatible Gemini model

## Thinking

Gemini 3 and 2.5 models are trained to think through complex problems, leading to significantly improved reasoning. The Gemini API comes with[thinking parameters](https://ai.google.dev/gemini-api/docs/thinking#levels-budgets)which give fine grain control over how much the model will think.

Gemini 3 uses`"low"`and`"high"`thinking levels, and Gemini 2.5 models use exact thinking budgets. These map to OpenAI's reasoning efforts as follows:

| `reasoning_effort`(OpenAI) | `thinking_level`(Gemini 3) | `thinking_budget`(Gemini 2.5) |
|----------------------------|----------------------------|-------------------------------|
| `minimal`                  | `low`                      | `1,024`                       |
| `low`                      | `low`                      | `1,024`                       |
| `medium`                   | `high`                     | `8,192`                       |
| `high`                     | `high`                     | `24,576`                      |

If no`reasoning_effort`is specified, Gemini uses the model's default[level](https://ai.google.dev/gemini-api/docs/thinking#levels)or[budget](https://ai.google.dev/gemini-api/docs/thinking#set-budget).

If you want to disable thinking, you can set`reasoning_effort`to`"none"`for 2.5 models. Reasoning cannot be turned off for Gemini 2.5 Pro or 3 models.  

### Python

    from openai import OpenAI

    client = OpenAI(
        api_key="GEMINI_API_KEY",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        reasoning_effort="low",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "Explain to me how AI works"
            }
        ]
    )

    print(response.choices[0].message)

### JavaScript

    import OpenAI from "openai";

    const openai = new OpenAI({
        apiKey: "GEMINI_API_KEY",
        baseURL: "https://generativelanguage.googleapis.com/v1beta/openai/"
    });

    const response = await openai.chat.completions.create({
        model: "gemini-2.5-flash",
        reasoning_effort: "low",
        messages: [
            { role: "system", content: "You are a helpful assistant." },
            {
                role: "user",
                content: "Explain to me how AI works",
            },
        ],
    });

    console.log(response.choices[0].message);

### REST

    curl "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer GEMINI_API_KEY" \
    -d '{
        "model": "gemini-2.5-flash",
        "reasoning_effort": "low",
        "messages": [
            {"role": "user", "content": "Explain to me how AI works"}
          ]
        }'

Gemini thinking models also produce[thought summaries](https://ai.google.dev/gemini-api/docs/thinking#summaries). You can use the[`extra_body`](https://ai.google.dev/gemini-api/docs/openai#extra-body)field to include Gemini fields in your request.

Note that`reasoning_effort`and`thinking_level`/`thinking_budget`overlap functionality, so they can't be used at the same time.  

### Python

    from openai import OpenAI

    client = OpenAI(
        api_key="GEMINI_API_KEY",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[{"role": "user", "content": "Explain to me how AI works"}],
        extra_body={
          'extra_body': {
            "google": {
              "thinking_config": {
                "thinking_budget": "low",
                "include_thoughts": True
              }
            }
          }
        }
    )

    print(response.choices[0].message)

### JavaScript

    import OpenAI from "openai";

    const openai = new OpenAI({
        apiKey: "GEMINI_API_KEY",
        baseURL: "https://generativelanguage.googleapis.com/v1beta/openai/"
    });

    const response = await openai.chat.completions.create({
        model: "gemini-2.5-flash",
        messages: [{role: "user", content: "Explain to me how AI works",}],
        extra_body: {
          "google": {
            "thinking_config": {
              "thinking_budget": "low",
              "include_thoughts": true
            }
          }
        }
    });

    console.log(response.choices[0].message);

### REST

    curl "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer GEMINI_API_KEY" \
    -d '{
        "model": "gemini-2.5-flash",
          "messages": [{"role": "user", "content": "Explain to me how AI works"}],
          "extra_body": {
            "google": {
               "thinking_config": {
                 "include_thoughts": true
               }
            }
          }
        }'

Gemini 3 supports OpenAI compatibility for thought signatures in chat completion APIs. You can find the full example on the[thought signatures](https://ai.google.dev/gemini-api/docs/thought-signatures#openai)page.

## Streaming

The Gemini API supports[streaming responses](https://ai.google.dev/gemini-api/docs/text-generation?lang=python#generate-a-text-stream).  

### Python

    from openai import OpenAI

    client = OpenAI(
        api_key="GEMINI_API_KEY",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    response = client.chat.completions.create(
      model="gemini-2.0-flash",
      messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
      ],
      stream=True
    )

    for chunk in response:
        print(chunk.choices[0].delta)

### JavaScript

    import OpenAI from "openai";

    const openai = new OpenAI({
        apiKey: "GEMINI_API_KEY",
        baseURL: "https://generativelanguage.googleapis.com/v1beta/openai/"
    });

    async function main() {
      const completion = await openai.chat.completions.create({
        model: "gemini-2.0-flash",
        messages: [
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": "Hello!"}
        ],
        stream: true,
      });

      for await (const chunk of completion) {
        console.log(chunk.choices[0].delta.content);
      }
    }

    main();

### REST

    curl "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer GEMINI_API_KEY" \
    -d '{
        "model": "gemini-2.0-flash",
        "messages": [
            {"role": "user", "content": "Explain to me how AI works"}
        ],
        "stream": true
      }'

## Function calling

Function calling makes it easier for you to get structured data outputs from generative models and is[supported in the Gemini API](https://ai.google.dev/gemini-api/docs/function-calling/tutorial).  

### Python

    from openai import OpenAI

    client = OpenAI(
        api_key="GEMINI_API_KEY",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    tools = [
      {
        "type": "function",
        "function": {
          "name": "get_weather",
          "description": "Get the weather in a given location",
          "parameters": {
            "type": "object",
            "properties": {
              "location": {
                "type": "string",
                "description": "The city and state, e.g. Chicago, IL",
              },
              "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location"],
          },
        }
      }
    ]

    messages = [{"role": "user", "content": "What's the weather like in Chicago today?"}]
    response = client.chat.completions.create(
      model="gemini-2.0-flash",
      messages=messages,
      tools=tools,
      tool_choice="auto"
    )

    print(response)

### JavaScript

    import OpenAI from "openai";

    const openai = new OpenAI({
        apiKey: "GEMINI_API_KEY",
        baseURL: "https://generativelanguage.googleapis.com/v1beta/openai/"
    });

    async function main() {
      const messages = [{"role": "user", "content": "What's the weather like in Chicago today?"}];
      const tools = [
          {
            "type": "function",
            "function": {
              "name": "get_weather",
              "description": "Get the weather in a given location",
              "parameters": {
                "type": "object",
                "properties": {
                  "location": {
                    "type": "string",
                    "description": "The city and state, e.g. Chicago, IL",
                  },
                  "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
              },
            }
          }
      ];

      const response = await openai.chat.completions.create({
        model: "gemini-2.0-flash",
        messages: messages,
        tools: tools,
        tool_choice: "auto",
      });

      console.log(response);
    }

    main();

### REST

    curl "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer GEMINI_API_KEY" \
    -d '{
      "model": "gemini-2.0-flash",
      "messages": [
        {
          "role": "user",
          "content": "What'\''s the weather like in Chicago today?"
        }
      ],
      "tools": [
        {
          "type": "function",
          "function": {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
              "type": "object",
              "properties": {
                "location": {
                  "type": "string",
                  "description": "The city and state, e.g. Chicago, IL"
                },
                "unit": {
                  "type": "string",
                  "enum": ["celsius", "fahrenheit"]
                }
              },
              "required": ["location"]
            }
          }
        }
      ],
      "tool_choice": "auto"
    }'

## Image understanding

Gemini models are natively multimodal and provide best in class performance on[many common vision tasks](https://ai.google.dev/gemini-api/docs/vision).  

### Python

    import base64
    from openai import OpenAI

    client = OpenAI(
        api_key="GEMINI_API_KEY",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    # Function to encode the image
    def encode_image(image_path):
      with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

    # Getting the base64 string
    base64_image = encode_image("Path/to/agi/image.jpeg")

    response = client.chat.completions.create(
      model="gemini-2.0-flash",
      messages=[
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": "What is in this image?",
            },
            {
              "type": "image_url",
              "image_url": {
                "url":  f"data:image/jpeg;base64,{base64_image}"
              },
            },
          ],
        }
      ],
    )

    print(response.choices[0])

### JavaScript

    import OpenAI from "openai";
    import fs from 'fs/promises';

    const openai = new OpenAI({
      apiKey: "GEMINI_API_KEY",
      baseURL: "https://generativelanguage.googleapis.com/v1beta/openai/"
    });

    async function encodeImage(imagePath) {
      try {
        const imageBuffer = await fs.readFile(imagePath);
        return imageBuffer.toString('base64');
      } catch (error) {
        console.error("Error encoding image:", error);
        return null;
      }
    }

    async function main() {
      const imagePath = "Path/to/agi/image.jpeg";
      const base64Image = await encodeImage(imagePath);

      const messages = [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": "What is in this image?",
            },
            {
              "type": "image_url",
              "image_url": {
                "url": `data:image/jpeg;base64,${base64Image}`
              },
            },
          ],
        }
      ];

      try {
        const response = await openai.chat.completions.create({
          model: "gemini-2.0-flash",
          messages: messages,
        });

        console.log(response.choices[0]);
      } catch (error) {
        console.error("Error calling Gemini API:", error);
      }
    }

    main();

### REST

    bash -c '
      base64_image=$(base64 -i "Path/to/agi/image.jpeg");
      curl "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer GEMINI_API_KEY" \
        -d "{
          \"model\": \"gemini-2.0-flash\",
          \"messages\": [
            {
              \"role\": \"user\",
              \"content\": [
                { \"type\": \"text\", \"text\": \"What is in this image?\" },
                {
                  \"type\": \"image_url\",
                  \"image_url\": { \"url\": \"data:image/jpeg;base64,${base64_image}\" }
                }
              ]
            }
          ]
        }"
    '

## Generate an image

| **Note:** Image generation is only available in the paid tier.

Generate an image:  

### Python

    import base64
    from openai import OpenAI
    from PIL import Image
    from io import BytesIO

    client = OpenAI(
        api_key="GEMINI_API_KEY",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    response = client.images.generate(
        model="imagen-3.0-generate-002",
        prompt="a portrait of a sheepadoodle wearing a cape",
        response_format='b64_json',
        n=1,
    )

    for image_data in response.data:
      image = Image.open(BytesIO(base64.b64decode(image_data.b64_json)))
      image.show()

### JavaScript

    import OpenAI from "openai";

    const openai = new OpenAI({
      apiKey: "GEMINI_API_KEY",
      baseURL: "https://generativelanguage.googleapis.com/v1beta/openai/",
    });

    async function main() {
      const image = await openai.images.generate(
        {
          model: "imagen-3.0-generate-002",
          prompt: "a portrait of a sheepadoodle wearing a cape",
          response_format: "b64_json",
          n: 1,
        }
      );

      console.log(image.data);
    }

    main();

### REST

    curl "https://generativelanguage.googleapis.com/v1beta/openai/images/generations" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer GEMINI_API_KEY" \
      -d '{
            "model": "imagen-3.0-generate-002",
            "prompt": "a portrait of a sheepadoodle wearing a cape",
            "response_format": "b64_json",
            "n": 1,
          }'

## Audio understanding

Analyze audio input:  

### Python

    import base64
    from openai import OpenAI

    client = OpenAI(
        api_key="GEMINI_API_KEY",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    with open("/path/to/your/audio/file.wav", "rb") as audio_file:
      base64_audio = base64.b64encode(audio_file.read()).decode('utf-8')

    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=[
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": "Transcribe this audio",
            },
            {
                  "type": "input_audio",
                  "input_audio": {
                    "data": base64_audio,
                    "format": "wav"
              }
            }
          ],
        }
      ],
    )

    print(response.choices[0].message.content)

### JavaScript

    import fs from "fs";
    import OpenAI from "openai";

    const client = new OpenAI({
      apiKey: "GEMINI_API_KEY",
      baseURL: "https://generativelanguage.googleapis.com/v1beta/openai/",
    });

    const audioFile = fs.readFileSync("/path/to/your/audio/file.wav");
    const base64Audio = Buffer.from(audioFile).toString("base64");

    async function main() {
      const response = await client.chat.completions.create({
        model: "gemini-2.0-flash",
        messages: [
          {
            role: "user",
            content: [
              {
                type: "text",
                text: "Transcribe this audio",
              },
              {
                type: "input_audio",
                input_audio: {
                  data: base64Audio,
                  format: "wav",
                },
              },
            ],
          },
        ],
      });

      console.log(response.choices[0].message.content);
    }

    main();

### REST

**Note:** If you get an`Argument list too long`error, the encoding of your audio file might be too long for curl.  

    bash -c '
      base64_audio=$(base64 -i "/path/to/your/audio/file.wav");
      curl "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer GEMINI_API_KEY" \
        -d "{
          \"model\": \"gemini-2.0-flash\",
          \"messages\": [
            {
              \"role\": \"user\",
              \"content\": [
                { \"type\": \"text\", \"text\": \"Transcribe this audio file.\" },
                {
                  \"type\": \"input_audio\",
                  \"input_audio\": {
                    \"data\": \"${base64_audio}\",
                    \"format\": \"wav\"
                  }
                }
              ]
            }
          ]
        }"
    '

## Structured output

Gemini models can output JSON objects in any[structure you define](https://ai.google.dev/gemini-api/docs/structured-output).  

### Python

    from pydantic import BaseModel
    from openai import OpenAI

    client = OpenAI(
        api_key="GEMINI_API_KEY",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    class CalendarEvent(BaseModel):
        name: str
        date: str
        participants: list[str]

    completion = client.beta.chat.completions.parse(
        model="gemini-2.0-flash",
        messages=[
            {"role": "system", "content": "Extract the event information."},
            {"role": "user", "content": "John and Susan are going to an AI conference on Friday."},
        ],
        response_format=CalendarEvent,
    )

    print(completion.choices[0].message.parsed)

### JavaScript

    import OpenAI from "openai";
    import { zodResponseFormat } from "openai/helpers/zod";
    import { z } from "zod";

    const openai = new OpenAI({
        apiKey: "GEMINI_API_KEY",
        baseURL: "https://generativelanguage.googleapis.com/v1beta/openai"
    });

    const CalendarEvent = z.object({
      name: z.string(),
      date: z.string(),
      participants: z.array(z.string()),
    });

    const completion = await openai.chat.completions.parse({
      model: "gemini-2.0-flash",
      messages: [
        { role: "system", content: "Extract the event information." },
        { role: "user", content: "John and Susan are going to an AI conference on Friday" },
      ],
      response_format: zodResponseFormat(CalendarEvent, "event"),
    });

    const event = completion.choices[0].message.parsed;
    console.log(event);

## Embeddings

Text embeddings measure the relatedness of text strings and can be generated using the[Gemini API](https://ai.google.dev/gemini-api/docs/embeddings).  

### Python

    from openai import OpenAI

    client = OpenAI(
        api_key="GEMINI_API_KEY",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    response = client.embeddings.create(
        input="Your text string goes here",
        model="gemini-embedding-001"
    )

    print(response.data[0].embedding)

### JavaScript

    import OpenAI from "openai";

    const openai = new OpenAI({
        apiKey: "GEMINI_API_KEY",
        baseURL: "https://generativelanguage.googleapis.com/v1beta/openai/"
    });

    async function main() {
      const embedding = await openai.embeddings.create({
        model: "gemini-embedding-001",
        input: "Your text string goes here",
      });

      console.log(embedding);
    }

    main();

### REST

    curl "https://generativelanguage.googleapis.com/v1beta/openai/embeddings" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer GEMINI_API_KEY" \
    -d '{
        "input": "Your text string goes here",
        "model": "gemini-embedding-001"
      }'

## Batch API

You can create[batch jobs](https://ai.google.dev/gemini-api/docs/batch-mode), submit them, and check their status using the OpenAI library.

You'll need to prepare the JSONL file in OpenAI input format. For example:  

    {"custom_id": "request-1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gemini-2.5-flash", "messages": [{"role": "user", "content": "Tell me a one-sentence joke."}]}}
    {"custom_id": "request-2", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gemini-2.5-flash", "messages": [{"role": "user", "content": "Why is the sky blue?"}]}}

OpenAI compatibility for Batch supports creating a batch, monitoring job status, and viewing batch results.

Compatibility for upload and download is currently not supported. Instead, the following example uses the`genai`client for uploading and downloading[files](https://ai.google.dev/gemini-api/docs/files), the same as when using the Gemini[Batch API](https://ai.google.dev/gemini-api/docs/batch-mode#input-file).  

### Python

    from openai import OpenAI

    # Regular genai client for uploads & downloads
    from google import genai
    client = genai.Client()

    openai_client = OpenAI(
        api_key="GEMINI_API_KEY",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    # Upload the JSONL file in OpenAI input format, using regular genai SDK
    uploaded_file = client.files.upload(
        file='my-batch-requests.jsonl',
        config=types.UploadFileConfig(display_name='my-batch-requests', mime_type='jsonl')
    )

    # Create batch
    batch = openai_client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )

    # Wait for batch to finish (up to 24h)
    while True:
        batch = client.batches.retrieve(batch.id)
        if batch.status in ('completed', 'failed', 'cancelled', 'expired'):
            break
        print(f"Batch not finished. Current state: {batch.status}. Waiting 30 seconds...")
        time.sleep(30)
    print(f"Batch finished: {batch}")

    # Download results in OpenAI output format, using regular genai SDK
    file_content = genai_client.files.download(file=batch.output_file_id).decode('utf-8')

    # See batch_output JSONL in OpenAI output format
    for line in file_content.splitlines():
        print(line)    

The OpenAI SDK also supports[generating embeddings with the Batch API](https://ai.google.dev/gemini-api/docs/batch-api#batch-embeddings). To do so, switch out the`create`method's`endpoint`field for an embeddings endpoint, as well as the`url`and`model`keys in the JSONL file:  

    # JSONL file using embeddings model and endpoint
    # {"custom_id": "request-1", "method": "POST", "url": "/v1/embeddings", "body": {"model": "ggemini-embedding-001", "messages": [{"role": "user", "content": "Tell me a one-sentence joke."}]}}
    # {"custom_id": "request-2", "method": "POST", "url": "/v1/embeddings", "body": {"model": "gemini-embedding-001", "messages": [{"role": "user", "content": "Why is the sky blue?"}]}}

    # ...

    # Create batch step with embeddings endpoint
    batch = openai_client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/embeddings",
        completion_window="24h"
    )

See the[Batch embedding generation](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_OpenAI_Compatibility.ipynb)section of the OpenAI compatibility cookbook for a complete example.

## `extra_body`

There are several features supported by Gemini that are not available in OpenAI models but can be enabled using the`extra_body`field.

**`extra_body`features**

|-------------------|-----------------------------------------------------------------|
| `cached_content`  | Corresponds to Gemini's`GenerateContentRequest.cached_content`. |
| `thinking_config` | Corresponds to Gemini's`ThinkingConfig`.                        |

### `cached_content`

Here's an example of using`extra_body`to set`cached_content`:  

### Python

    from openai import OpenAI

    client = OpenAI(
        api_key=MY_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/"
    )

    stream = client.chat.completions.create(
        model="gemini-2.5-pro",
        n=1,
        messages=[
            {
                "role": "user",
                "content": "Summarize the video"
            }
        ],
        stream=True,
        stream_options={'include_usage': True},
        extra_body={
            'extra_body':
            {
                'google': {
                  'cached_content': "cachedContents/0000aaaa1111bbbb2222cccc3333dddd4444eeee"
              }
            }
        }
    )

    for chunk in stream:
        print(chunk)
        print(chunk.usage.to_dict())

## List models

Get a list of available Gemini models:  

### Python

    from openai import OpenAI

    client = OpenAI(
      api_key="GEMINI_API_KEY",
      base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    models = client.models.list()
    for model in models:
      print(model.id)

### JavaScript

    import OpenAI from "openai";

    const openai = new OpenAI({
      apiKey: "GEMINI_API_KEY",
      baseURL: "https://generativelanguage.googleapis.com/v1beta/openai/",
    });

    async function main() {
      const list = await openai.models.list();

      for await (const model of list) {
        console.log(model);
      }
    }
    main();

### REST

    curl https://generativelanguage.googleapis.com/v1beta/openai/models \
    -H "Authorization: Bearer GEMINI_API_KEY"

## Retrieve a model

Retrieve a Gemini model:  

### Python

    from openai import OpenAI

    client = OpenAI(
      api_key="GEMINI_API_KEY",
      base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    model = client.models.retrieve("gemini-2.0-flash")
    print(model.id)

### JavaScript

    import OpenAI from "openai";

    const openai = new OpenAI({
      apiKey: "GEMINI_API_KEY",
      baseURL: "https://generativelanguage.googleapis.com/v1beta/openai/",
    });

    async function main() {
      const model = await openai.models.retrieve("gemini-2.0-flash");
      console.log(model.id);
    }

    main();

### REST

    curl https://generativelanguage.googleapis.com/v1beta/openai/models/gemini-2.0-flash \
    -H "Authorization: Bearer GEMINI_API_KEY"

## Current limitations

Support for the OpenAI libraries is still in beta while we extend feature support.

If you have questions about supported parameters, upcoming features, or run into any issues getting started with Gemini, join our[Developer Forum](https://discuss.ai.google.dev/c/gemini-api/4).

## What's next

Try our[OpenAI Compatibility Colab](https://colab.sandbox.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_OpenAI_Compatibility.ipynb)to work through more detailed examples.



<br />

Gemini models can process documents in PDF format, using native vision to understand entire document contexts. This goes beyond just text extraction, allowing Gemini to:

- Analyze and interpret content, including text, images, diagrams, charts, and tables, even in long documents up to 1000 pages.
- Extract information into[structured output](https://ai.google.dev/gemini-api/docs/structured-output)formats.
- Summarize and answer questions based on both the visual and textual elements in a document.
- Transcribe document content (e.g. to HTML), preserving layouts and formatting, for use in downstream applications.

You can also pass non-PDF documents in the same way but Gemini will see them as normal text which will eliminate context like charts or formatting.

## Passing PDF data inline

You can pass PDF data inline in the request to`generateContent`. This is best suited for smaller documents or temporary processing where you don't need to reference the file in subsequent requests. We recommend using the[Files API](https://ai.google.dev/gemini-api/docs/document-processing#large-pdfs)for larger documents that you need to refer to in multi-turn interactions to improve request latency and reduce bandwidth usage.

The following example shows you how to fetch a PDF from a URL and convert it to bytes for processing:  

### Python

    from google import genai
    from google.genai import types
    import httpx

    client = genai.Client()

    doc_url = "https://discovery.ucl.ac.uk/id/eprint/10089234/1/343019_3_art_0_py4t4l_convrt.pdf"

    # Retrieve and encode the PDF byte
    doc_data = httpx.get(doc_url).content

    prompt = "Summarize this document"
    response = client.models.generate_content(
      model="gemini-2.5-flash",
      contents=[
          types.Part.from_bytes(
            data=doc_data,
            mime_type='application/pdf',
          ),
          prompt])
    print(response.text)

### JavaScript

    import { GoogleGenAI } from "@google/genai";

    const ai = new GoogleGenAI({ apiKey: "GEMINI_API_KEY" });

    async function main() {
        const pdfResp = await fetch('https://discovery.ucl.ac.uk/id/eprint/10089234/1/343019_3_art_0_py4t4l_convrt.pdf')
            .then((response) => response.arrayBuffer());

        const contents = [
            { text: "Summarize this document" },
            {
                inlineData: {
                    mimeType: 'application/pdf',
                    data: Buffer.from(pdfResp).toString("base64")
                }
            }
        ];

        const response = await ai.models.generateContent({
            model: "gemini-2.5-flash",
            contents: contents
        });
        console.log(response.text);
    }

    main();

### Go

    package main

    import (
        "context"
        "fmt"
        "io"
        "net/http"
        "os"
        "google.golang.org/genai"
    )

    func main() {

        ctx := context.Background()
        client, _ := genai.NewClient(ctx, &genai.ClientConfig{
            APIKey:  os.Getenv("GEMINI_API_KEY"),
            Backend: genai.BackendGeminiAPI,
        })

        pdfResp, _ := http.Get("https://discovery.ucl.ac.uk/id/eprint/10089234/1/343019_3_art_0_py4t4l_convrt.pdf")
        var pdfBytes []byte
        if pdfResp != nil && pdfResp.Body != nil {
            pdfBytes, _ = io.ReadAll(pdfResp.Body)
            pdfResp.Body.Close()
        }

        parts := []*genai.Part{
            &genai.Part{
                InlineData: &genai.Blob{
                    MIMEType: "application/pdf",
                    Data:     pdfBytes,
                },
            },
            genai.NewPartFromText("Summarize this document"),
        }

        contents := []*genai.Content{
            genai.NewContentFromParts(parts, genai.RoleUser),
        }

        result, _ := client.Models.GenerateContent(
            ctx,
            "gemini-2.5-flash",
            contents,
            nil,
        )

        fmt.Println(result.Text())
    }

### REST

    DOC_URL="https://discovery.ucl.ac.uk/id/eprint/10089234/1/343019_3_art_0_py4t4l_convrt.pdf"
    PROMPT="Summarize this document"
    DISPLAY_NAME="base64_pdf"

    # Download the PDF
    wget -O "${DISPLAY_NAME}.pdf" "${DOC_URL}"

    # Check for FreeBSD base64 and set flags accordingly
    if [[ "$(base64 --version 2>&1)" = *"FreeBSD"* ]]; then
      B64FLAGS="--input"
    else
      B64FLAGS="-w0"
    fi

    # Base64 encode the PDF
    ENCODED_PDF=$(base64 $B64FLAGS "${DISPLAY_NAME}.pdf")

    # Generate content using the base64 encoded PDF
    curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GOOGLE_API_KEY" \
        -H 'Content-Type: application/json' \
        -X POST \
        -d '{
          "contents": [{
            "parts":[
              {"inline_data": {"mime_type": "application/pdf", "data": "'"$ENCODED_PDF"'"}},
              {"text": "'$PROMPT'"}
            ]
          }]
        }' 2> /dev/null > response.json

    cat response.json
    echo

    jq ".candidates[].content.parts[].text" response.json

    # Clean up the downloaded PDF
    rm "${DISPLAY_NAME}.pdf"

You can also read a PDF from a local file for processing:  

### Python

    from google import genai
    from google.genai import types
    import pathlib

    client = genai.Client()

    # Retrieve and encode the PDF byte
    filepath = pathlib.Path('file.pdf')

    prompt = "Summarize this document"
    response = client.models.generate_content(
      model="gemini-2.5-flash",
      contents=[
          types.Part.from_bytes(
            data=filepath.read_bytes(),
            mime_type='application/pdf',
          ),
          prompt])
    print(response.text)

### JavaScript

    import { GoogleGenAI } from "@google/genai";
    import * as fs from 'fs';

    const ai = new GoogleGenAI({ apiKey: "GEMINI_API_KEY" });

    async function main() {
        const contents = [
            { text: "Summarize this document" },
            {
                inlineData: {
                    mimeType: 'application/pdf',
                    data: Buffer.from(fs.readFileSync("content/343019_3_art_0_py4t4l_convrt.pdf")).toString("base64")
                }
            }
        ];

        const response = await ai.models.generateContent({
            model: "gemini-2.5-flash",
            contents: contents
        });
        console.log(response.text);
    }

    main();

### Go

    package main

    import (
        "context"
        "fmt"
        "os"
        "google.golang.org/genai"
    )

    func main() {

        ctx := context.Background()
        client, _ := genai.NewClient(ctx, &genai.ClientConfig{
            APIKey:  os.Getenv("GEMINI_API_KEY"),
            Backend: genai.BackendGeminiAPI,
        })

        pdfBytes, _ := os.ReadFile("path/to/your/file.pdf")

        parts := []*genai.Part{
            &genai.Part{
                InlineData: &genai.Blob{
                    MIMEType: "application/pdf",
                    Data:     pdfBytes,
                },
            },
            genai.NewPartFromText("Summarize this document"),
        }
        contents := []*genai.Content{
            genai.NewContentFromParts(parts, genai.RoleUser),
        }

        result, _ := client.Models.GenerateContent(
            ctx,
            "gemini-2.5-flash",
            contents,
            nil,
        )

        fmt.Println(result.Text())
    }

## Uploading PDFs using the Files API

We recommend you use Files API for larger files or when you intend to reuse a document across multiple requests. This improves request latency and reduces bandwidth usage by decoupling the file upload from the model requests.
| **Note:** The Files API is available at no cost in all regions where the Gemini API is available. Uploaded files are stored for 48 hours.

### Large PDFs from URLs

Use the File API to simplify uploading and processing large PDF files from URLs:  

### Python

    from google import genai
    from google.genai import types
    import io
    import httpx

    client = genai.Client()

    long_context_pdf_path = "https://www.nasa.gov/wp-content/uploads/static/history/alsj/a17/A17_FlightPlan.pdf"

    # Retrieve and upload the PDF using the File API
    doc_io = io.BytesIO(httpx.get(long_context_pdf_path).content)

    sample_doc = client.files.upload(
      # You can pass a path or a file-like object here
      file=doc_io,
      config=dict(
        mime_type='application/pdf')
    )

    prompt = "Summarize this document"

    response = client.models.generate_content(
      model="gemini-2.5-flash",
      contents=[sample_doc, prompt])
    print(response.text)

### JavaScript

    import { createPartFromUri, GoogleGenAI } from "@google/genai";

    const ai = new GoogleGenAI({ apiKey: "GEMINI_API_KEY" });

    async function main() {

        const pdfBuffer = await fetch("https://www.nasa.gov/wp-content/uploads/static/history/alsj/a17/A17_FlightPlan.pdf")
            .then((response) => response.arrayBuffer());

        const fileBlob = new Blob([pdfBuffer], { type: 'application/pdf' });

        const file = await ai.files.upload({
            file: fileBlob,
            config: {
                displayName: 'A17_FlightPlan.pdf',
            },
        });

        // Wait for the file to be processed.
        let getFile = await ai.files.get({ name: file.name });
        while (getFile.state === 'PROCESSING') {
            getFile = await ai.files.get({ name: file.name });
            console.log(`current file status: ${getFile.state}`);
            console.log('File is still processing, retrying in 5 seconds');

            await new Promise((resolve) => {
                setTimeout(resolve, 5000);
            });
        }
        if (file.state === 'FAILED') {
            throw new Error('File processing failed.');
        }

        // Add the file to the contents.
        const content = [
            'Summarize this document',
        ];

        if (file.uri && file.mimeType) {
            const fileContent = createPartFromUri(file.uri, file.mimeType);
            content.push(fileContent);
        }

        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: content,
        });

        console.log(response.text);

    }

    main();

### Go

    package main

    import (
      "context"
      "fmt"
      "io"
      "net/http"
      "os"
      "google.golang.org/genai"
    )

    func main() {

      ctx := context.Background()
      client, _ := genai.NewClient(ctx, &genai.ClientConfig{
        APIKey:  os.Getenv("GEMINI_API_KEY"),
        Backend: genai.BackendGeminiAPI,
      })

      pdfURL := "https://www.nasa.gov/wp-content/uploads/static/history/alsj/a17/A17_FlightPlan.pdf"
      localPdfPath := "A17_FlightPlan_downloaded.pdf"

      respHttp, _ := http.Get(pdfURL)
      defer respHttp.Body.Close()

      outFile, _ := os.Create(localPdfPath)
      defer outFile.Close()

      _, _ = io.Copy(outFile, respHttp.Body)

      uploadConfig := &genai.UploadFileConfig{MIMEType: "application/pdf"}
      uploadedFile, _ := client.Files.UploadFromPath(ctx, localPdfPath, uploadConfig)

      promptParts := []*genai.Part{
        genai.NewPartFromURI(uploadedFile.URI, uploadedFile.MIMEType),
        genai.NewPartFromText("Summarize this document"),
      }
      contents := []*genai.Content{
        genai.NewContentFromParts(promptParts, genai.RoleUser), // Specify role
      }

        result, _ := client.Models.GenerateContent(
            ctx,
            "gemini-2.5-flash",
            contents,
            nil,
        )

      fmt.Println(result.Text())
    }

### REST

    PDF_PATH="https://www.nasa.gov/wp-content/uploads/static/history/alsj/a17/A17_FlightPlan.pdf"
    DISPLAY_NAME="A17_FlightPlan"
    PROMPT="Summarize this document"

    # Download the PDF from the provided URL
    wget -O "${DISPLAY_NAME}.pdf" "${PDF_PATH}"

    MIME_TYPE=$(file -b --mime-type "${DISPLAY_NAME}.pdf")
    NUM_BYTES=$(wc -c < "${DISPLAY_NAME}.pdf")

    echo "MIME_TYPE: ${MIME_TYPE}"
    echo "NUM_BYTES: ${NUM_BYTES}"

    tmp_header_file=upload-header.tmp

    # Initial resumable request defining metadata.
    # The upload url is in the response headers dump them to a file.
    curl "${BASE_URL}/upload/v1beta/files?key=${GOOGLE_API_KEY}" \
      -D upload-header.tmp \
      -H "X-Goog-Upload-Protocol: resumable" \
      -H "X-Goog-Upload-Command: start" \
      -H "X-Goog-Upload-Header-Content-Length: ${NUM_BYTES}" \
      -H "X-Goog-Upload-Header-Content-Type: ${MIME_TYPE}" \
      -H "Content-Type: application/json" \
      -d "{'file': {'display_name': '${DISPLAY_NAME}'}}" 2> /dev/null

    upload_url=$(grep -i "x-goog-upload-url: " "${tmp_header_file}" | cut -d" " -f2 | tr -d "\r")
    rm "${tmp_header_file}"

    # Upload the actual bytes.
    curl "${upload_url}" \
      -H "Content-Length: ${NUM_BYTES}" \
      -H "X-Goog-Upload-Offset: 0" \
      -H "X-Goog-Upload-Command: upload, finalize" \
      --data-binary "@${DISPLAY_NAME}.pdf" 2> /dev/null > file_info.json

    file_uri=$(jq ".file.uri" file_info.json)
    echo "file_uri: ${file_uri}"

    # Now generate content using that file
    curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GOOGLE_API_KEY" \
        -H 'Content-Type: application/json' \
        -X POST \
        -d '{
          "contents": [{
            "parts":[
              {"text": "'$PROMPT'"},
              {"file_data":{"mime_type": "application/pdf", "file_uri": '$file_uri'}}]
            }]
          }' 2> /dev/null > response.json

    cat response.json
    echo

    jq ".candidates[].content.parts[].text" response.json

    # Clean up the downloaded PDF
    rm "${DISPLAY_NAME}.pdf"

### Large PDFs stored locally

### Python

    from google import genai
    from google.genai import types
    import pathlib
    import httpx

    client = genai.Client()

    # Retrieve and encode the PDF byte
    file_path = pathlib.Path('large_file.pdf')

    # Upload the PDF using the File API
    sample_file = client.files.upload(
      file=file_path,
    )

    prompt="Summarize this document"

    response = client.models.generate_content(
      model="gemini-2.5-flash",
      contents=[sample_file, "Summarize this document"])
    print(response.text)

### JavaScript

    import { createPartFromUri, GoogleGenAI } from "@google/genai";

    const ai = new GoogleGenAI({ apiKey: "GEMINI_API_KEY" });

    async function main() {
        const file = await ai.files.upload({
            file: 'path-to-localfile.pdf'
            config: {
                displayName: 'A17_FlightPlan.pdf',
            },
        });

        // Wait for the file to be processed.
        let getFile = await ai.files.get({ name: file.name });
        while (getFile.state === 'PROCESSING') {
            getFile = await ai.files.get({ name: file.name });
            console.log(`current file status: ${getFile.state}`);
            console.log('File is still processing, retrying in 5 seconds');

            await new Promise((resolve) => {
                setTimeout(resolve, 5000);
            });
        }
        if (file.state === 'FAILED') {
            throw new Error('File processing failed.');
        }

        // Add the file to the contents.
        const content = [
            'Summarize this document',
        ];

        if (file.uri && file.mimeType) {
            const fileContent = createPartFromUri(file.uri, file.mimeType);
            content.push(fileContent);
        }

        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: content,
        });

        console.log(response.text);

    }

    main();

### Go

    package main

    import (
        "context"
        "fmt"
        "os"
        "google.golang.org/genai"
    )

    func main() {

        ctx := context.Background()
        client, _ := genai.NewClient(ctx, &genai.ClientConfig{
            APIKey:  os.Getenv("GEMINI_API_KEY"),
            Backend: genai.BackendGeminiAPI,
        })
        localPdfPath := "/path/to/file.pdf"

        uploadConfig := &genai.UploadFileConfig{MIMEType: "application/pdf"}
        uploadedFile, _ := client.Files.UploadFromPath(ctx, localPdfPath, uploadConfig)

        promptParts := []*genai.Part{
            genai.NewPartFromURI(uploadedFile.URI, uploadedFile.MIMEType),
            genai.NewPartFromText("Give me a summary of this pdf file."),
        }
        contents := []*genai.Content{
            genai.NewContentFromParts(promptParts, genai.RoleUser),
        }

        result, _ := client.Models.GenerateContent(
            ctx,
            "gemini-2.5-flash",
            contents,
            nil,
        )

        fmt.Println(result.Text())
    }

### REST

    NUM_BYTES=$(wc -c < "${PDF_PATH}")
    DISPLAY_NAME=TEXT
    tmp_header_file=upload-header.tmp

    # Initial resumable request defining metadata.
    # The upload url is in the response headers dump them to a file.
    curl "${BASE_URL}/upload/v1beta/files?key=${GEMINI_API_KEY}" \
      -D upload-header.tmp \
      -H "X-Goog-Upload-Protocol: resumable" \
      -H "X-Goog-Upload-Command: start" \
      -H "X-Goog-Upload-Header-Content-Length: ${NUM_BYTES}" \
      -H "X-Goog-Upload-Header-Content-Type: application/pdf" \
      -H "Content-Type: application/json" \
      -d "{'file': {'display_name': '${DISPLAY_NAME}'}}" 2> /dev/null

    upload_url=$(grep -i "x-goog-upload-url: " "${tmp_header_file}" | cut -d" " -f2 | tr -d "\r")
    rm "${tmp_header_file}"

    # Upload the actual bytes.
    curl "${upload_url}" \
      -H "Content-Length: ${NUM_BYTES}" \
      -H "X-Goog-Upload-Offset: 0" \
      -H "X-Goog-Upload-Command: upload, finalize" \
      --data-binary "@${PDF_PATH}" 2> /dev/null > file_info.json

    file_uri=$(jq ".file.uri" file_info.json)
    echo file_uri=$file_uri

    # Now generate content using that file
    curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GOOGLE_API_KEY" \
        -H 'Content-Type: application/json' \
        -X POST \
        -d '{
          "contents": [{
            "parts":[
              {"text": "Can you add a few more lines to this poem?"},
              {"file_data":{"mime_type": "application/pdf", "file_uri": '$file_uri'}}]
            }]
          }' 2> /dev/null > response.json

    cat response.json
    echo

    jq ".candidates[].content.parts[].text" response.json

You can verify the API successfully stored the uploaded file and get its metadata by calling[`files.get`](https://ai.google.dev/api/rest/v1beta/files/get). Only the`name`(and by extension, the`uri`) are unique.  

### Python

    from google import genai
    import pathlib

    client = genai.Client()

    fpath = pathlib.Path('example.txt')
    fpath.write_text('hello')

    file = client.files.upload(file='example.txt')

    file_info = client.files.get(name=file.name)
    print(file_info.model_dump_json(indent=4))

### REST

    name=$(jq ".file.name" file_info.json)
    # Get the file of interest to check state
    curl https://generativelanguage.googleapis.com/v1beta/files/$name > file_info.json
    # Print some information about the file you got
    name=$(jq ".file.name" file_info.json)
    echo name=$name
    file_uri=$(jq ".file.uri" file_info.json)
    echo file_uri=$file_uri

## Passing multiple PDFs

The Gemini API is capable of processing multiple PDF documents (up to 1000 pages) in a single request, as long as the combined size of the documents and the text prompt stays within the model's context window.  

### Python

    from google import genai
    import io
    import httpx

    client = genai.Client()

    doc_url_1 = "https://arxiv.org/pdf/2312.11805"
    doc_url_2 = "https://arxiv.org/pdf/2403.05530"

    # Retrieve and upload both PDFs using the File API
    doc_data_1 = io.BytesIO(httpx.get(doc_url_1).content)
    doc_data_2 = io.BytesIO(httpx.get(doc_url_2).content)

    sample_pdf_1 = client.files.upload(
      file=doc_data_1,
      config=dict(mime_type='application/pdf')
    )
    sample_pdf_2 = client.files.upload(
      file=doc_data_2,
      config=dict(mime_type='application/pdf')
    )

    prompt = "What is the difference between each of the main benchmarks between these two papers? Output these in a table."

    response = client.models.generate_content(
      model="gemini-2.5-flash",
      contents=[sample_pdf_1, sample_pdf_2, prompt])
    print(response.text)

### JavaScript

    import { createPartFromUri, GoogleGenAI } from "@google/genai";

    const ai = new GoogleGenAI({ apiKey: "GEMINI_API_KEY" });

    async function uploadRemotePDF(url, displayName) {
        const pdfBuffer = await fetch(url)
            .then((response) => response.arrayBuffer());

        const fileBlob = new Blob([pdfBuffer], { type: 'application/pdf' });

        const file = await ai.files.upload({
            file: fileBlob,
            config: {
                displayName: displayName,
            },
        });

        // Wait for the file to be processed.
        let getFile = await ai.files.get({ name: file.name });
        while (getFile.state === 'PROCESSING') {
            getFile = await ai.files.get({ name: file.name });
            console.log(`current file status: ${getFile.state}`);
            console.log('File is still processing, retrying in 5 seconds');

            await new Promise((resolve) => {
                setTimeout(resolve, 5000);
            });
        }
        if (file.state === 'FAILED') {
            throw new Error('File processing failed.');
        }

        return file;
    }

    async function main() {
        const content = [
            'What is the difference between each of the main benchmarks between these two papers? Output these in a table.',
        ];

        let file1 = await uploadRemotePDF("https://arxiv.org/pdf/2312.11805", "PDF 1")
        if (file1.uri && file1.mimeType) {
            const fileContent = createPartFromUri(file1.uri, file1.mimeType);
            content.push(fileContent);
        }
        let file2 = await uploadRemotePDF("https://arxiv.org/pdf/2403.05530", "PDF 2")
        if (file2.uri && file2.mimeType) {
            const fileContent = createPartFromUri(file2.uri, file2.mimeType);
            content.push(fileContent);
        }

        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: content,
        });

        console.log(response.text);
    }

    main();

### Go

    package main

    import (
        "context"
        "fmt"
        "io"
        "net/http"
        "os"
        "google.golang.org/genai"
    )

    func main() {

        ctx := context.Background()
        client, _ := genai.NewClient(ctx, &genai.ClientConfig{
            APIKey:  os.Getenv("GEMINI_API_KEY"),
            Backend: genai.BackendGeminiAPI,
        })

        docUrl1 := "https://arxiv.org/pdf/2312.11805"
        docUrl2 := "https://arxiv.org/pdf/2403.05530"
        localPath1 := "doc1_downloaded.pdf"
        localPath2 := "doc2_downloaded.pdf"

        respHttp1, _ := http.Get(docUrl1)
        defer respHttp1.Body.Close()

        outFile1, _ := os.Create(localPath1)
        _, _ = io.Copy(outFile1, respHttp1.Body)
        outFile1.Close()

        respHttp2, _ := http.Get(docUrl2)
        defer respHttp2.Body.Close()

        outFile2, _ := os.Create(localPath2)
        _, _ = io.Copy(outFile2, respHttp2.Body)
        outFile2.Close()

        uploadConfig1 := &genai.UploadFileConfig{MIMEType: "application/pdf"}
        uploadedFile1, _ := client.Files.UploadFromPath(ctx, localPath1, uploadConfig1)

        uploadConfig2 := &genai.UploadFileConfig{MIMEType: "application/pdf"}
        uploadedFile2, _ := client.Files.UploadFromPath(ctx, localPath2, uploadConfig2)

        promptParts := []*genai.Part{
            genai.NewPartFromURI(uploadedFile1.URI, uploadedFile1.MIMEType),
            genai.NewPartFromURI(uploadedFile2.URI, uploadedFile2.MIMEType),
            genai.NewPartFromText("What is the difference between each of the " +
                                  "main benchmarks between these two papers? " +
                                  "Output these in a table."),
        }
        contents := []*genai.Content{
            genai.NewContentFromParts(promptParts, genai.RoleUser),
        }

        modelName := "gemini-2.5-flash"
        result, _ := client.Models.GenerateContent(
            ctx,
            modelName,
            contents,
            nil,
        )

        fmt.Println(result.Text())
    }

### REST

    DOC_URL_1="https://arxiv.org/pdf/2312.11805"
    DOC_URL_2="https://arxiv.org/pdf/2403.05530"
    DISPLAY_NAME_1="Gemini_paper"
    DISPLAY_NAME_2="Gemini_1.5_paper"
    PROMPT="What is the difference between each of the main benchmarks between these two papers? Output these in a table."

    # Function to download and upload a PDF
    upload_pdf() {
      local doc_url="$1"
      local display_name="$2"

      # Download the PDF
      wget -O "${display_name}.pdf" "${doc_url}"

      local MIME_TYPE=$(file -b --mime-type "${display_name}.pdf")
      local NUM_BYTES=$(wc -c < "${display_name}.pdf")

      echo "MIME_TYPE: ${MIME_TYPE}"
      echo "NUM_BYTES: ${NUM_BYTES}"

      local tmp_header_file=upload-header.tmp

      # Initial resumable request
      curl "${BASE_URL}/upload/v1beta/files?key=${GOOGLE_API_KEY}" \
        -D "${tmp_header_file}" \
        -H "X-Goog-Upload-Protocol: resumable" \
        -H "X-Goog-Upload-Command: start" \
        -H "X-Goog-Upload-Header-Content-Length: ${NUM_BYTES}" \
        -H "X-Goog-Upload-Header-Content-Type: ${MIME_TYPE}" \
        -H "Content-Type: application/json" \
        -d "{'file': {'display_name': '${display_name}'}}" 2> /dev/null

      local upload_url=$(grep -i "x-goog-upload-url: " "${tmp_header_file}" | cut -d" " -f2 | tr -d "\r")
      rm "${tmp_header_file}"

      # Upload the PDF
      curl "${upload_url}" \
        -H "Content-Length: ${NUM_BYTES}" \
        -H "X-Goog-Upload-Offset: 0" \
        -H "X-Goog-Upload-Command: upload, finalize" \
        --data-binary "@${display_name}.pdf" 2> /dev/null > "file_info_${display_name}.json"

      local file_uri=$(jq ".file.uri" "file_info_${display_name}.json")
      echo "file_uri for ${display_name}: ${file_uri}"

      # Clean up the downloaded PDF
      rm "${display_name}.pdf"

      echo "${file_uri}"
    }

    # Upload the first PDF
    file_uri_1=$(upload_pdf "${DOC_URL_1}" "${DISPLAY_NAME_1}")

    # Upload the second PDF
    file_uri_2=$(upload_pdf "${DOC_URL_2}" "${DISPLAY_NAME_2}")

    # Now generate content using both files
    curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GOOGLE_API_KEY" \
        -H 'Content-Type: application/json' \
        -X POST \
        -d '{
          "contents": [{
            "parts":[
              {"file_data": {"mime_type": "application/pdf", "file_uri": '$file_uri_1'}},
              {"file_data": {"mime_type": "application/pdf", "file_uri": '$file_uri_2'}},
              {"text": "'$PROMPT'"}
            ]
          }]
        }' 2> /dev/null > response.json

    cat response.json
    echo

    jq ".candidates[].content.parts[].text" response.json

## Technical details

Gemini supports PDF files up to 50MB or 1000 pages. This limit applies to both inline data and Files API uploads. Each document page is equivalent to 258 tokens.

While there are no specific limits to the number of pixels in a document besides the model's[context window](https://ai.google.dev/gemini-api/docs/long-context), larger pages are scaled down to a maximum resolution of 3072 x 3072 while preserving their original aspect ratio, while smaller pages are scaled up to 768 x 768 pixels. There is no cost reduction for pages at lower sizes, other than bandwidth, or performance improvement for pages at higher resolution.

### Gemini 3 models

Gemini 3 introduces granular control over multimodal vision processing with the`media_resolution`parameter. You can now set the resolution to low, medium, or high per individual media part. With this addition, the processing of PDF documents has been updated:

1. **Native text inclusion:**Text natively embedded in the PDF is extracted and provided to the model.
2. **Billing \& token reporting:**
   - You are**not charged** for tokens originating from the extracted**native text**in PDFs.
   - In the`usage_metadata`section of the API response, tokens generated from processing PDF pages (as images) are now counted under the`IMAGE`modality, not a separate`DOCUMENT`modality as in some earlier versions.

For more details about the media resolution parameter, see the[Media resolution](https://ai.google.dev/gemini-api/docs/media-resolution)guide.

### Document types

Technically, you can pass other MIME types for document understanding, like TXT, Markdown, HTML, XML, etc. However, document vision***only meaningfully understands PDFs***. Other types will be extracted as pure text, and the model won't be able to interpret what we see in the rendering of those files. Any file-type specifics like charts, diagrams, HTML tags, Markdown formatting, etc., will be lost.

### Best practices

For best results:

- Rotate pages to the correct orientation before uploading.
- Avoid blurry pages.
- If using a single page, place the text prompt after the page.

## What's next

To learn more, see the following resources:

- [File prompting strategies](https://ai.google.dev/gemini-api/docs/files#prompt-guide): The Gemini API supports prompting with text, image, audio, and video data, also known as multimodal prompting.
- [System instructions](https://ai.google.dev/gemini-api/docs/text-generation#system-instructions): System instructions let you steer the behavior of the model based on your specific needs and use cases.


Many Gemini models come with large context windows of 1 million or more tokens.
Historically, large language models (LLMs) were significantly limited by
the amount of text (or tokens) that could be passed to the model at one time.
The Gemini long context window unlocks many new use cases and developer
paradigms.

The code you already use for cases like [text
generation](https://ai.google.dev/gemini-api/docs/text-generation) or [multimodal
inputs](https://ai.google.dev/gemini-api/docs/vision) will work without any changes with long context.

This document gives you an overview of what you can achieve using models with
context windows of 1M and more tokens. The page gives a brief overview of
a context window, and explores how developers should think about long context,
various real world use cases for long context, and ways to optimize the usage
of long context.

For the context window sizes of specific models, see the
[Models](https://ai.google.dev/gemini-api/docs/models) page.

## What is a context window?

The basic way you use the Gemini models is by passing information (context)
to the model, which will subsequently generate a response. An analogy for the
context window is short term memory. There is a limited amount of information
that can be stored in someone's short term memory, and the same is true for
generative models.

You can read more about how models work under the hood in our [generative models
guide](https://ai.google.dev/gemini-api/docs/prompting-strategies#under-the-hood).

## Getting started with long context

Earlier versions of generative models were only able to process 8,000
tokens at a time. Newer models pushed this further by accepting 32,000 or even
128,000 tokens. Gemini is the first model capable of accepting 1 million tokens.

In practice, 1 million tokens would look like:

- 50,000 lines of code (with the standard 80 characters per line)
- All the text messages you have sent in the last 5 years
- 8 average length English novels
- Transcripts of over 200 average length podcast episodes

The more limited context windows common in many other models often require
strategies like arbitrarily dropping old messages, summarizing content, using
RAG with vector databases, or filtering prompts to save tokens.

While these techniques remain valuable in specific scenarios, Gemini's extensive
context window invites a more direct approach: providing all relevant
information upfront. Because Gemini models were purpose-built with massive
context capabilities, they demonstrate powerful in-context learning. For
example, using only in-context instructional materials (a 500-page reference
grammar, a dictionary, and ≈400 parallel sentences), Gemini
[learned to translate](https://storage.googleapis.com/deepmind-media/gemini/gemini_v1_5_report.pdf)
from English to Kalamang---a Papuan language with
fewer than 200 speakers---with quality similar to a human learner using the same
materials. This illustrates the paradigm shift enabled by Gemini's long context,
empowering new possibilities through robust in-context learning.

## Long context use cases

While the standard use case for most generative models is still text input, the
Gemini model family enables a new paradigm of multimodal use cases. These
models can natively understand text, video, audio, and images. They are
accompanied by the [Gemini API that takes in multimodal file
types](https://ai.google.dev/gemini-api/docs/prompting_with_media) for
convenience.

### Long form text

Text has proved to be the layer of intelligence underpinning much of the
momentum around LLMs. As mentioned earlier, much of the practical limitation of
LLMs was because of not having a large enough context window to do certain
tasks. This led to the rapid adoption of retrieval augmented generation (RAG)
and other techniques which dynamically provide the model with relevant
contextual information. Now, with larger and larger context windows, there are
new techniques becoming available which unlock new use cases.

Some emerging and standard use cases for text based long context include:

- Summarizing large corpuses of text
  - Previous summarization options with smaller context models would require a sliding window or another technique to keep state of previous sections as new tokens are passed to the model
- Question and answering
  - Historically this was only possible with RAG given the limited amount of context and models' factual recall being low
- Agentic workflows
  - Text is the underpinning of how agents keep state of what they have done and what they need to do; not having enough information about the world and the agent's goal is a limitation on the reliability of agents

[Many-shot in-context learning](https://arxiv.org/pdf/2404.11018) is one of the
most unique capabilities unlocked by long context models. Research has shown
that taking the common "single shot" or "multi-shot" example paradigm, where the
model is presented with one or a few examples of a task, and scaling that up to
hundreds, thousands, or even hundreds of thousands of examples, can lead to
novel model capabilities. This many-shot approach has also been shown to perform
similarly to models which were fine-tuned for a specific task. For use cases
where a Gemini model's performance is not yet sufficient for a production
rollout, you can try the many-shot approach. As you might explore later in the
long context optimization section, context caching makes this type of high input
token workload much more economically feasible and even lower latency in some
cases.

### Long form video

Video content's utility has long been constrained by the lack of accessibility
of the medium itself. It was hard to skim the content, transcripts often failed
to capture the nuance of a video, and most tools don't process image, text, and
audio together. With Gemini, the long-context text capabilities translate to
the ability to reason and answer questions about multimodal inputs with
sustained performance.

Some emerging and standard use cases for video long context include:

- Video question and answering
- Video memory, as shown with [Google's Project Astra](https://deepmind.google/technologies/gemini/project-astra/)
- Video captioning
- Video recommendation systems, by enriching existing metadata with new multimodal understanding
- Video customization, by looking at a corpus of data and associated video metadata and then removing parts of videos that are not relevant to the viewer
- Video content moderation
- Real-time video processing

When working with videos, it is important to consider how the [videos are
processed into tokens](https://ai.google.dev/gemini-api/docs/tokens#media-token), which affects
billing and usage limits. You can learn more about prompting with video files in
the [Prompting
guide](https://ai.google.dev/gemini-api/docs/prompting_with_media?lang=python#prompting-with-videos).

### Long form audio

The Gemini models were the first natively multimodal large language models
that could understand audio. Historically, the typical developer workflow would
involve stringing together multiple domain specific models, like a
speech-to-text model and a text-to-text model, in order to process audio. This
led to additional latency required by performing multiple round-trip requests
and decreased performance usually attributed to disconnected architectures of
the multiple model setup.

Some emerging and standard use cases for audio context include:

- Real-time transcription and translation
- Podcast / video question and answering
- Meeting transcription and summarization
- Voice assistants

You can learn more about prompting with audio files in the [Prompting
guide](https://ai.google.dev/gemini-api/docs/prompting_with_media?lang=python#prompting-with-videos).

## Long context optimizations

The primary optimization when working with long context and the Gemini
models is to use [context
caching](https://ai.google.dev/gemini-api/docs/caching). Beyond the previous
impossibility of processing lots of tokens in a single request, the other main
constraint was the cost. If you have a "chat with your data" app where a user
uploads 10 PDFs, a video, and some work documents, you would historically have
to work with a more complex retrieval augmented generation (RAG) tool /
framework in order to process these requests and pay a significant amount for
tokens moved into the context window. Now, you can cache the files the user
uploads and pay to store them on a per hour basis. The input / output cost per
request with Gemini Flash for example is \~4x less than the standard
input / output cost, so if
the user chats with their data enough, it becomes a huge cost saving for you as
the developer.

## Long context limitations

In various sections of this guide, we talked about how Gemini models achieve
high performance across various needle-in-a-haystack retrieval evals. These
tests consider the most basic setup, where you have a single needle you are
looking for. In cases where you might have multiple "needles" or specific pieces
of information you are looking for, the model does not perform with the same
accuracy. Performance can vary to a wide degree depending on the context. This
is important to consider as there is an inherent tradeoff between getting the
right information retrieved and cost. You can get \~99% on a single query, but
you have to pay the input token cost every time you send that query. So for 100
pieces of information to be retrieved, if you needed 99% performance, you would
likely need to send 100 requests. This is a good example of where context
caching can significantly reduce the cost associated with using Gemini models
while keeping the performance high.

## FAQs

### Where is the best place to put my query in the context window?

In most cases, especially if the total context is long, the model's
performance will be better if you put your query / question at the end of the
prompt (after all the other context).

### Do I lose model performance when I add more tokens to a query?

Generally, if you don't need tokens to be passed to the model, it is best to
avoid passing them. However, if you have a large chunk of tokens with some
information and want to ask questions about that information, the model is
highly capable of extracting that information (up to 99% accuracy in many
cases).

### How can I lower my cost with long-context queries?

If you have a similar set of tokens / context that you want to re-use many
times, [context caching](https://ai.google.dev/gemini-api/docs/caching) can help reduce the costs
associated with asking questions about that information.

### Does the context length affect the model latency?

There is some fixed amount of latency in any given request, regardless of the
size, but generally longer queries will have higher latency (time to first
token).


