'''
Usage:
Ark v3 sdk
pip install 'volcengine-python-sdk[ark]'
'''

from volcenginesdkarkruntime import Ark

# fetch ak&sk from environmental variables "VOLC_ACCESSKEY", "VOLC_SECRETKEY"
# or specify ak&sk by Ark(ak="${YOUR_AK}", sk="${YOUR_SK}").
# you can get ak&sk follow this document(https://www.volcengine.com/docs/6291/65568)
client = Ark()

if __name__ == "__main__":
    # Non-streaming:
    print("----- standard request -----")
    completion = client.chat.completions.create(
        model="ep-20260225012508-xzgdk",
        messages=[
            {
                "role": "user",
                "content": "Say this is a test",
            },
        ]
    )
    print(completion.choices[0].message.content)

    # Streaming:
    print("----- streaming request -----")
    stream = client.chat.completions.create(
        model="ep-20260225012508-xzgdk",
        messages=[
            {
                "role": "user",
                "content": "How do I output all files in a directory using Python?",
            },
        ],
        stream=True
    )
    for chunk in stream:
        if not chunk.choices:
            continue

        print(chunk.choices[0].delta.content, end="")
    print()
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


