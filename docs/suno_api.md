# Generate Suno AI Music

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/generate
openapi: 3.0.0
info:
  title: intro
  description: API documentation for audio generation services
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://api.sunoapi.org
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: Music Generation
    description: Endpoints for creating and managing music generation tasks
  - name: Lyrics Generation
    description: Endpoints for lyrics generation and management
  - name: WAV Conversion
    description: Endpoints for converting music to WAV format
  - name: Vocal Removal
    description: Endpoints for vocal removal from music tracks
  - name: Music Video Generation
    description: Endpoints for generating MP4 videos from music tracks
  - name: Account Management
    description: Endpoints for account and credits management
paths:
  /api/v1/generate:
    post:
      summary: Generate Music
      operationId: generate-music
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - customMode
                - instrumental
                - callBackUrl
                - model
              properties:
                prompt:
                  type: string
                  description: >-
                    A description of the desired audio content.  

                    - In Custom Mode (`customMode: true`): Required if
                    `instrumental` is `false`. The prompt will be strictly used
                    as the lyrics and sung in the generated track. Character
                    limits by model:  
                      - **V4**: Maximum 3000 characters  
                      - **V4_5, V4_5PLUS, V4_5ALL & V5**: Maximum 5000 characters  
                      Example: "A calm and relaxing piano track with soft melodies"  
                    - In Non-custom Mode (`customMode: false`): Always required.
                    The prompt serves as the core idea, and lyrics will be
                    automatically generated based on it (not strictly matching
                    the input). Maximum 500 characters.  
                      Example: "A short relaxing piano tune"
                  example: A calm and relaxing piano track with soft melodies
                style:
                  type: string
                  description: >-
                    The music style or genre for the audio.  

                    - Required in Custom Mode (`customMode: true`). Examples:
                    "Jazz", "Classical", "Electronic". 
                      - For V4 model: Max length: 200 characters. 
                      - For V4_5, V4_5PLUS, V4_5ALL and V5 models: Max length: 1000 characters.  
                      Example: "Classical"  
                    - In Non-custom Mode (`customMode: false`): Leave empty.
                  example: Classical
                title:
                  type: string
                  description: >-
                    The title of the generated music track.  

                    - Required in Custom Mode (`customMode: true`). Character
                    limits by model:  
                      - **V4 & V4_5ALL**: Maximum 80 characters  
                      - **V4_5, V4_5PLUS & V5**: Maximum 100 characters  
                      Example: "Peaceful Piano Meditation"  
                    - In Non-custom Mode (`customMode: false`): Leave empty.
                  example: Peaceful Piano Meditation
                customMode:
                  type: boolean
                  description: >-
                    Enables Custom Mode for advanced audio generation
                    settings.  

                    - Set to `true` to use Custom Mode (requires `style` and
                    `title`; `prompt` required if `instrumental` is `false`).
                    The prompt will be strictly used as lyrics if `instrumental`
                    is `false`.  

                    - Set to `false` for Non-custom Mode (only `prompt` is
                    required). Lyrics will be auto-generated based on the
                    prompt.
                  example: true
                instrumental:
                  type: boolean
                  description: >-
                    Determines if the audio should be instrumental (no
                    lyrics).  

                    - In Custom Mode (`customMode: true`):  
                      - If `true`: Only `style` and `title` are required.  
                      - If `false`: `style`, `title`, and `prompt` are required (with `prompt` used as the exact lyrics).  
                    - In Non-custom Mode (`customMode: false`): No impact on
                    required fields (`prompt` only). Lyrics are auto-generated
                    if `instrumental` is `false`.
                  example: true
                personaId:
                  type: string
                  description: >-
                    Only available when Custom Mode (`customMode: true`) is
                    enabled. Persona ID to apply to the generated music.
                    Optional. Use this to apply a specific persona style to your
                    music generation. 


                    To generate a persona ID, use the [Generate
                    Persona](https://docs.sunoapi.org/suno-api/generate-persona)
                    endpoint to create a personalized music Persona based on
                    generated music.
                  example: persona_123
                model:
                  type: string
                  description: |-
                    The model version to use for audio generation.   
                    - Available options:  
                      - **`V5`**: Superior musical expression, faster generation.  
                      - **`V4_5PLUS`**: V4.5+ is richer sound, new ways to create, max 8 min.  
                      - **`V4_5ALL`**: V4.5-all is better song structure, max 8 min.  
                      - **`V4_5`**: Superior genre blending with smarter prompts and faster output, up to 8 minutes.  
                      - **`V4`**: Best audio quality with refined song structure, up to 4 minutes.
                  enum:
                    - V4
                    - V4_5
                    - V4_5PLUS
                    - V4_5ALL
                    - V5
                  example: V4_5ALL
                negativeTags:
                  type: string
                  description: >-
                    Music styles or traits to exclude from the generated
                    audio.  

                    - Optional. Use to avoid specific styles.  
                      Example: "Heavy Metal, Upbeat Drums"
                  example: Heavy Metal, Upbeat Drums
                vocalGender:
                  type: string
                  description: Preferred vocal gender for generated vocals. Optional.
                  enum:
                    - m
                    - f
                  example: m
                styleWeight:
                  type: number
                  description: Weight of the provided style guidance. Range 0.00–1.00.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  example: 0.65
                weirdnessConstraint:
                  type: number
                  description: Constraint on creative deviation/novelty. Range 0.00–1.00.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  example: 0.65
                audioWeight:
                  type: number
                  description: >-
                    Weight of the input audio influence (where applicable).
                    Range 0.00–1.00.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  example: 0.65
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive task completion notifications when music
                    generation is complete.


                    For detailed callback format and implementation guide, see
                    [Music Generation
                    Callbacks](https://docs.sunoapi.org/suno-api/generate-music-callbacks)

                    - Alternatively, you can use the get music generation
                    details endpoint to poll task status
                  example: https://api.example.com/callback
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/ApiResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: Task ID for tracking task status
                            example: 5c79****be8e
        '500':
          $ref: '#/components/responses/Error'
      callbacks:
        audioGenerated:
          '{request.body#/callBackUrl}':
            post:
              description: >-
                System will call this callback when audio generation is
                complete.


                ### Callback Example

                ```json

                {
                  "code": 200,
                  "msg": "All generated successfully.",
                  "data": {
                    "callbackType": "complete",
                    "task_id": "2fac****9f72",
                    "data": [
                      {
                        "id": "8551****662c",
                        "audio_url": "https://example.cn/****.mp3",
                        "source_audio_url": "https://example.cn/****.mp3",
                        "stream_audio_url": "https://example.cn/****",
                        "source_stream_audio_url": "https://example.cn/****",
                        "image_url": "https://example.cn/****.jpeg",
                        "source_image_url": "https://example.cn/****.jpeg",
                        "prompt": "[Verse] Night city lights shining bright",
                        "model_name": "chirp-v3-5",
                        "title": "Iron Man",
                        "tags": "electrifying, rock",
                        "createTime": "2025-01-01 00:00:00",
                        "duration": 198.44
                      },
                      {
                        "id": "bd15****1873",
                        "audio_url": "https://example.cn/****.mp3",
                        "source_audio_url": "https://example.cn/****.mp3",
                        "stream_audio_url": "https://example.cn/****",
                        "source_stream_audio_url": "https://example.cn/****",
                        "image_url": "https://example.cn/****.jpeg",
                        "source_image_url": "https://example.cn/****.jpeg",
                        "prompt": "[Verse] Night city lights shining bright",
                        "model_name": "chirp-v3-5",
                        "title": "Iron Man",
                        "tags": "electrifying, rock",
                        "createTime": "2025-01-01 00:00:00",
                        "duration": 228.28
                      }
                    ]
                  }
                }

                ```
              requestBody:
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        code:
                          type: integer
                          description: Status code
                          example: 200
                        msg:
                          type: string
                          description: Response message
                          example: All generated successfully
                        data:
                          type: object
                          properties:
                            callbackType:
                              type: string
                              description: >-
                                Callback type: text (text generation complete),
                                first (first track complete), complete (all
                                tracks complete)
                              enum:
                                - text
                                - first
                                - complete
                            task_id:
                              type: string
                              description: Task ID
                            data:
                              type: array
                              items:
                                type: object
                                properties:
                                  id:
                                    type: string
                                    description: Audio unique identifier (audioId)
                                  audio_url:
                                    type: string
                                    description: Audio file URL
                                  source_audio_url:
                                    type: string
                                    description: Original audio file URL
                                  stream_audio_url:
                                    type: string
                                    description: Streaming audio URL
                                  source_stream_audio_url:
                                    type: string
                                    description: Original streaming audio URL
                                  image_url:
                                    type: string
                                    description: Cover image URL
                                  source_image_url:
                                    type: string
                                    description: Original cover image URL
                                  prompt:
                                    type: string
                                    description: Generation prompt/lyrics
                                  model_name:
                                    type: string
                                    description: Model name used
                                  title:
                                    type: string
                                    description: Music title
                                  tags:
                                    type: string
                                    description: Music tags
                                  createTime:
                                    type: string
                                    description: Creation time
                                    format: date-time
                                  duration:
                                    type: number
                                    description: Audio duration (seconds)
              responses:
                '200':
                  description: Callback received successfully
components:
  schemas:
    ApiResponse:
      type: object
      properties:
        code:
          type: integer
          description: |-
            # Status Codes

            - ✅ 200 - Request successful
            - ⚠️ 400 - Invalid parameters
            - ⚠️ 401 - Unauthorized access
            - ⚠️ 404 - Invalid request method or path
            - ⚠️ 405 - Rate limit exceeded
            - ⚠️ 413 - Theme or prompt too long
            - ⚠️ 429 - Insufficient credits
            - ⚠️ 430 - Your call frequency is too high. Please try again later. 
            - ⚠️ 455 - System maintenance
            - ❌ 500 - Server error
          example: 200
          enum:
            - 200
            - 400
            - 401
            - 404
            - 405
            - 413
            - 429
            - 430
            - 455
            - 500
        msg:
          type: string
          description: Error message when code != 200
          example: success
  responses:
    Error:
      description: Server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        # 🔑 API Authentication


        All endpoints require authentication using Bearer Token.


        ## Get API Key


        1. Visit the [API Key Management Page](https://sunoapi.org/api-key) to
        obtain your API Key


        ## Usage


        Add to request headers:


        ```

        Authorization: Bearer YOUR_API_KEY

        ```


        > **⚠️ Note:**

        > - Keep your API Key secure and do not share it with others

        > - If you suspect your API Key has been compromised, reset it
        immediately from the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt


# Extend Music

> Extend or modify existing music tracks.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/generate/extend
openapi: 3.0.0
info:
  title: intro
  description: API documentation for audio generation services
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://api.sunoapi.org
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: Music Generation
    description: Endpoints for creating and managing music generation tasks
  - name: Lyrics Generation
    description: Endpoints for lyrics generation and management
  - name: WAV Conversion
    description: Endpoints for converting music to WAV format
  - name: Vocal Removal
    description: Endpoints for vocal removal from music tracks
  - name: Music Video Generation
    description: Endpoints for generating MP4 videos from music tracks
  - name: Account Management
    description: Endpoints for account and credits management
paths:
  /api/v1/generate/extend:
    post:
      summary: Extend Music
      operationId: extend-music
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - defaultParamFlag
                - audioId
                - callBackUrl
                - model
              properties:
                defaultParamFlag:
                  type: boolean
                  description: >-
                    Controls parameter usage mode.  

                    - `true`: Use custom parameters (requires `continueAt`,
                    `prompt`, `style`, and `title`).  

                    - `false`: Use original audio parameters (only `audioId` is
                    required).
                  example: true
                audioId:
                  type: string
                  description: >-
                    Audio ID of the track to extend. This is the source track
                    that will be continued.
                  example: e231****-****-****-****-****8cadc7dc
                prompt:
                  type: string
                  description: >-
                    Description of how the music should be extended. Required
                    when defaultParamFlag is true.
                  example: Extend the music with more relaxing notes
                style:
                  type: string
                  description: Music style, e.g., Jazz, Classical, Electronic
                  example: Classical
                title:
                  type: string
                  description: Music title
                  example: Peaceful Piano Extended
                continueAt:
                  type: number
                  description: >-
                    The time point (in seconds) from which to start extending
                    the music.  

                    - Required when `defaultParamFlag` is `true`.  

                    - Value range: greater than 0 and less than the total
                    duration of the generated audio.  

                    - Specifies the position in the original track where the
                    extension should begin.
                  example: 60
                personaId:
                  type: string
                  description: >-
                    Only available when Custom Mode (`customMode: true`) is
                    enabled. Persona ID to apply to the generated music.
                    Optional. Use this to apply a specific persona style to your
                    music generation. 


                    To generate a persona ID, use the [Generate
                    Persona](https://docs.sunoapi.org/suno-api/generate-persona)
                    endpoint to create a personalized music Persona based on
                    generated music.
                  example: persona_123
                model:
                  type: string
                  description: >-
                    Model version to use, must be consistent with the source
                    audio.  

                    - Available options:  
                      - **`V5`**: Superior musical expression, faster generation.  
                      - **`V4_5PLUS`**: V4.5+ is richer sound, new waysto create, max 8 min.  
                      - **`V4_5ALL`**: V4.5-all is better song structure, max 8 min.  
                      - **`V4_5`**: V4.5 is smarter prompts, fastergenerations, max 8 min.  
                      - **`V4`**: V4 is improved vocal quality,max 4 min.
                  enum:
                    - V4
                    - V4_5
                    - V4_5PLUS
                    - V4_5ALL
                    - V5
                  example: V4_5ALL
                negativeTags:
                  type: string
                  description: Music styles to exclude from generation
                  example: Relaxing Piano
                vocalGender:
                  type: string
                  description: Preferred vocal gender for generated vocals. Optional.
                  enum:
                    - m
                    - f
                  example: m
                styleWeight:
                  type: number
                  description: Weight of the provided style guidance. Range 0.00–1.00.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  example: 0.65
                weirdnessConstraint:
                  type: number
                  description: Constraint on creative deviation/novelty. Range 0.00–1.00.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  example: 0.65
                audioWeight:
                  type: number
                  description: >-
                    Weight of the input audio influence (where applicable).
                    Range 0.00–1.00.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  example: 0.65
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive task completion notifications when music
                    extension is complete.


                    For detailed callback format and implementation guide, see
                    [Music Extension
                    Callbacks](https://docs.sunoapi.org/suno-api/extend-music-callbacks)

                    - Alternatively, you can use the get music generation
                    details endpoint to poll task status
                  example: https://api.example.com/callback
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/ApiResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: Task ID for tracking task status
                            example: 5c79****be8e
        '500':
          $ref: '#/components/responses/Error'
      callbacks:
        audioExtend:
          '{$request.body#/callBackUrl}':
            post:
              description: >-
                System will call this callback when audio generation is
                complete.


                ### Callback Example

                ```json

                {
                  "code": 200,
                  "msg": "All generated successfully.",
                  "data": {
                    "callbackType": "complete",
                    "task_id": "2fac****9f72",
                    "data": [
                      {
                        "id": "8551****662c",
                        "audio_url": "https://example.cn/****.mp3",
                        "source_audio_url": "https://example.cn/****.mp3",
                        "stream_audio_url": "https://example.cn/****",
                        "source_stream_audio_url": "https://example.cn/****",
                        "image_url": "https://example.cn/****.jpeg",
                        "source_image_url": "https://example.cn/****.jpeg",
                        "prompt": "[Verse] Night city lights shining bright",
                        "model_name": "chirp-v3-5",
                        "title": "Iron Man",
                        "tags": "electrifying, rock",
                        "createTime": "2025-01-01 00:00:00",
                        "duration": 198.44
                      }
                    ]
                  }
                }

                ```
              requestBody:
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        code:
                          type: integer
                          description: Status code
                          example: 200
                        msg:
                          type: string
                          description: Response message
                          example: All generated successfully
                        data:
                          type: object
                          properties:
                            callbackType:
                              type: string
                              description: >-
                                Callback type: text (text generation complete),
                                first (first track complete), complete (all
                                tracks complete)
                              enum:
                                - text
                                - first
                                - complete
                            task_id:
                              type: string
                              description: Task ID
                            data:
                              type: array
                              items:
                                type: object
                                properties:
                                  id:
                                    type: string
                                    description: Audio unique identifier (audioId)
                                  audio_url:
                                    type: string
                                    description: Audio file URL
                                  source_audio_url:
                                    type: string
                                    description: Original audio file URL
                                  stream_audio_url:
                                    type: string
                                    description: Streaming audio URL
                                  source_stream_audio_url:
                                    type: string
                                    description: Original streaming audio URL
                                  image_url:
                                    type: string
                                    description: Cover image URL
                                  source_image_url:
                                    type: string
                                    description: Original cover image URL
                                  prompt:
                                    type: string
                                    description: Generation prompt/lyrics
                                  model_name:
                                    type: string
                                    description: Model name used
                                  title:
                                    type: string
                                    description: Music title
                                  tags:
                                    type: string
                                    description: Music tags
                                  createTime:
                                    type: string
                                    description: Creation time
                                    format: date-time
                                  duration:
                                    type: number
                                    description: Audio duration (seconds)
              responses:
                '200':
                  description: Callback received successfully
components:
  schemas:
    ApiResponse:
      type: object
      properties:
        code:
          type: integer
          description: |-
            # Status Codes

            - ✅ 200 - Request successful
            - ⚠️ 400 - Invalid parameters
            - ⚠️ 401 - Unauthorized access
            - ⚠️ 404 - Invalid request method or path
            - ⚠️ 405 - Rate limit exceeded
            - ⚠️ 413 - Theme or prompt too long
            - ⚠️ 429 - Insufficient credits
            - ⚠️ 430 - Your call frequency is too high. Please try again later. 
            - ⚠️ 455 - System maintenance
            - ❌ 500 - Server error
          example: 200
          enum:
            - 200
            - 400
            - 401
            - 404
            - 405
            - 413
            - 429
            - 430
            - 455
            - 500
        msg:
          type: string
          description: Error message when code != 200
          example: success
  responses:
    Error:
      description: Server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        # 🔑 API Authentication


        All endpoints require authentication using Bearer Token.


        ## Get API Key


        1. Visit the [API Key Management Page](https://sunoapi.org/api-key) to
        obtain your API Key


        ## Usage


        Add to request headers:


        ```

        Authorization: Bearer YOUR_API_KEY

        ```


        > **⚠️ Note:**

        > - Keep your API Key secure and do not share it with others

        > - If you suspect your API Key has been compromised, reset it
        immediately from the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt


# Upload And Cover Audio

> This API covers an audio track by transforming it into a new style while retaining its core melody. It incorporates Suno's upload capability, enabling users to upload an audio file for processing. The expected result is a refreshed audio track with a new style, keeping the original melody intact.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/generate/upload-cover
openapi: 3.0.0
info:
  title: intro
  description: API documentation for audio generation services
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://api.sunoapi.org
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: Music Generation
    description: Endpoints for creating and managing music generation tasks
  - name: Lyrics Generation
    description: Endpoints for lyrics generation and management
  - name: WAV Conversion
    description: Endpoints for converting music to WAV format
  - name: Vocal Removal
    description: Endpoints for vocal removal from music tracks
  - name: Music Video Generation
    description: Endpoints for generating MP4 videos from music tracks
  - name: Account Management
    description: Endpoints for account and credits management
paths:
  /api/v1/generate/upload-cover:
    post:
      summary: Upload And Cover Audio
      operationId: upload-and-cover-audio
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - uploadUrl
                - customMode
                - instrumental
                - callBackUrl
                - model
              properties:
                uploadUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL for uploading audio files, required regardless of
                    whether customMode and instrumental are true or false.
                    Ensure the uploaded audio does not exceed 8 minutes in
                    length. **Note**: When using the V4_5ALL model, the uploaded
                    audio file must not exceed **1 minute** in length.
                  example: https://storage.example.com/upload
                prompt:
                  type: string
                  description: >-
                    A description of the desired audio content.  

                    - In Custom Mode (`customMode: true`): Required if
                    `instrumental` is `false`. The prompt will be strictly used
                    as the lyrics and sung in the generated track. Character
                    limits by model:  
                      - **V4**: Maximum 3000 characters  
                      - **V4_5, V4_5PLUS, V4_5ALL & V5**: Maximum 5000 characters  
                      Example: "A calm and relaxing piano track with soft melodies"  
                    - In Non-custom Mode (`customMode: false`): Always required.
                    The prompt serves as the core idea, and lyrics will be
                    automatically generated based on it (not strictly matching
                    the input). Maximum 500 characters.  
                      Example: "A short relaxing piano tune" 
                  example: A calm and relaxing piano track with soft melodies
                style:
                  type: string
                  description: >-
                    The music style or genre for the audio.  

                    - Required in Custom Mode (`customMode: true`). Examples:
                    "Jazz", "Classical", "Electronic". Character limits by
                    model:  
                      - **V4**: Maximum 200 characters  
                      - **V4_5, V4_5PLUS, V4_5ALL & V5**: Maximum 1000 characters  
                      Example: "Classical"  
                    - In Non-custom Mode (`customMode: false`): Leave empty.
                  example: Classical
                title:
                  type: string
                  description: >-
                    The title of the generated music track.  

                    - Required in Custom Mode (`customMode: true`). Character
                    limits by model:  
                      - **V4 & V4_5ALL**: Maximum 80 characters  
                      - **V4_5, V4_5PLUS & V5**: Maximum 100 characters  
                      Example: "Peaceful Piano Meditation"  
                    - In Non-custom Mode (`customMode: false`): Leave empty.
                  example: Peaceful Piano Meditation
                customMode:
                  type: boolean
                  description: >-
                    Enables Custom Mode for advanced audio generation
                    settings.  

                    - Set to `true` to use Custom Mode (requires `style` and
                    `title`; `prompt` required if `instrumental` is `false`).
                    The prompt will be strictly used as lyrics if `instrumental`
                    is `false`.  

                    - Set to `false` for Non-custom Mode (only `prompt` is
                    required). Lyrics will be auto-generated based on the
                    prompt.
                  example: true
                instrumental:
                  type: boolean
                  description: >-
                    Determines if the audio should be instrumental (no
                    lyrics).  

                    - In Custom Mode (`customMode: true`):  
                      - If `true`: Only `style` and `title` are required.  
                      - If `false`: `style`, `title`, and `prompt` are required (with `prompt` used as the exact lyrics).  
                    - In Non-custom Mode (`customMode: false`): No impact on
                    required fields (`prompt` only). Lyrics are auto-generated
                    if `instrumental` is `false`.
                  example: true
                personaId:
                  type: string
                  description: >-
                    Only available when Custom Mode (`customMode: true`) is
                    enabled. Persona ID to apply to the generated music.
                    Optional. Use this to apply a specific persona style to your
                    music generation. 


                    To generate a persona ID, use the [Generate
                    Persona](https://docs.sunoapi.org/suno-api/generate-persona)
                    endpoint to create a personalized music Persona based on
                    generated music.
                  example: persona_123
                model:
                  type: string
                  description: >-
                    The model version to use for audio generation.  

                    - Choose between: `V4`, `V4_5`, `V4_5PLUS`, `V4_5ALL`, or
                    `V5`. **Note:** Ensure correct formatting (e.g., use "V4" or
                    "V4_5ALL", not "V4.5" or other variations).
                  enum:
                    - V4
                    - V4_5
                    - V4_5PLUS
                    - V4_5ALL
                    - V5
                  example: V4_5ALL
                negativeTags:
                  type: string
                  description: >-
                    Music styles or traits to exclude from the generated
                    audio.  

                    - Optional. Use to avoid specific styles.  
                      Example: "Heavy Metal, Upbeat Drums"
                  example: Heavy Metal, Upbeat Drums
                vocalGender:
                  type: string
                  description: Preferred vocal gender for generated vocals. Optional.
                  enum:
                    - m
                    - f
                  example: m
                styleWeight:
                  type: number
                  description: Weight of the provided style guidance. Range 0.00–1.00.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  example: 0.65
                weirdnessConstraint:
                  type: number
                  description: Constraint on creative deviation/novelty. Range 0.00–1.00.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  example: 0.65
                audioWeight:
                  type: number
                  description: >-
                    Weight of the input audio influence (where applicable).
                    Range 0.00–1.00.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  example: 0.65
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive task completion notifications when audio
                    covering is complete.


                    For detailed callback format and implementation guide, see
                    [Upload and Cover Audio
                    Callbacks](https://docs.sunoapi.org/suno-api/upload-and-cover-audio-callbacks)

                    - Alternatively, you can use the get music generation
                    details endpoint to poll task status
                  example: https://api.example.com/callback
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/ApiResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: Task ID for tracking task status
                            example: 5c79****be8e
        '500':
          $ref: '#/components/responses/Error'
      callbacks:
        audioGenerated:
          '{request.body#/callBackUrl}':
            post:
              description: >-
                System will call this callback when audio generation is
                complete.


                ### Callback Example

                ```json

                {
                  "code": 200,
                  "msg": "All generated successfully.",
                  "data": {
                    "callbackType": "complete",
                    "task_id": "2fac****9f72",
                    "data": [
                      {
                        "id": "8551****662c",
                        "audio_url": "https://example.cn/****.mp3",
                        "source_audio_url": "https://example.cn/****.mp3",
                        "stream_audio_url": "https://example.cn/****",
                        "source_stream_audio_url": "https://example.cn/****",
                        "image_url": "https://example.cn/****.jpeg",
                        "source_image_url": "https://example.cn/****.jpeg",
                        "prompt": "[Verse] Night city lights shining bright",
                        "model_name": "chirp-v3-5",
                        "title": "Iron Man",
                        "tags": "electrifying, rock",
                        "createTime": "2025-01-01 00:00:00",
                        "duration": 198.44
                      },
                      {
                        "id": "bd15****1873",
                        "audio_url": "https://example.cn/****.mp3",
                        "source_audio_url": "https://example.cn/****.mp3",
                        "stream_audio_url": "https://example.cn/****",
                        "source_stream_audio_url": "https://example.cn/****",
                        "image_url": "https://example.cn/****.jpeg",
                        "source_image_url": "https://example.cn/****.jpeg",
                        "prompt": "[Verse] Night city lights shining bright",
                        "model_name": "chirp-v3-5",
                        "title": "Iron Man",
                        "tags": "electrifying, rock",
                        "createTime": "2025-01-01 00:00:00",
                        "duration": 228.28
                      }
                    ]
                  }
                }

                ```
              requestBody:
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        code:
                          type: integer
                          description: Status code
                          example: 200
                        msg:
                          type: string
                          description: Response message
                          example: All generated successfully
                        data:
                          type: object
                          properties:
                            callbackType:
                              type: string
                              description: >-
                                Callback type: text (text generation complete),
                                first (first track complete), complete (all
                                tracks complete)
                              enum:
                                - text
                                - first
                                - complete
                            task_id:
                              type: string
                              description: Task ID
                            data:
                              type: array
                              items:
                                type: object
                                properties:
                                  id:
                                    type: string
                                    description: Audio unique identifier (audioId)
                                  audio_url:
                                    type: string
                                    description: Audio file URL
                                  source_audio_url:
                                    type: string
                                    description: Original audio file URL
                                  stream_audio_url:
                                    type: string
                                    description: Streaming audio URL
                                  source_stream_audio_url:
                                    type: string
                                    description: Original streaming audio URL
                                  image_url:
                                    type: string
                                    description: Cover image URL
                                  source_image_url:
                                    type: string
                                    description: Original cover image URL
                                  prompt:
                                    type: string
                                    description: Generation prompt/lyrics
                                  model_name:
                                    type: string
                                    description: Model name used
                                  title:
                                    type: string
                                    description: Music title
                                  tags:
                                    type: string
                                    description: Music tags
                                  createTime:
                                    type: string
                                    description: Creation time
                                    format: date-time
                                  duration:
                                    type: number
                                    description: Audio duration (seconds)
              responses:
                '200':
                  description: Callback received successfully
components:
  schemas:
    ApiResponse:
      type: object
      properties:
        code:
          type: integer
          description: |-
            # Status Codes

            - ✅ 200 - Request successful
            - ⚠️ 400 - Invalid parameters
            - ⚠️ 401 - Unauthorized access
            - ⚠️ 404 - Invalid request method or path
            - ⚠️ 405 - Rate limit exceeded
            - ⚠️ 413 - Theme or prompt too long
            - ⚠️ 429 - Insufficient credits
            - ⚠️ 430 - Your call frequency is too high. Please try again later. 
            - ⚠️ 455 - System maintenance
            - ❌ 500 - Server error
          example: 200
          enum:
            - 200
            - 400
            - 401
            - 404
            - 405
            - 413
            - 429
            - 430
            - 455
            - 500
        msg:
          type: string
          description: Error message when code != 200
          example: success
  responses:
    Error:
      description: Server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        # 🔑 API Authentication


        All endpoints require authentication using Bearer Token.


        ## Get API Key


        1. Visit the [API Key Management Page](https://sunoapi.org/api-key) to
        obtain your API Key


        ## Usage


        Add to request headers:


        ```

        Authorization: Bearer YOUR_API_KEY

        ```


        > **⚠️ Note:**

        > - Keep your API Key secure and do not share it with others

        > - If you suspect your API Key has been compromised, reset it
        immediately from the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt


# Upload And Extend Audio

> This API extends audio tracks while preserving the original style of the audio track. It includes Suno's upload functionality, allowing users to upload audio files for processing. The expected result is a longer track that seamlessly continues the input style.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/generate/upload-extend
openapi: 3.0.0
info:
  title: intro
  description: API documentation for audio generation services
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://api.sunoapi.org
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: Music Generation
    description: Endpoints for creating and managing music generation tasks
  - name: Lyrics Generation
    description: Endpoints for lyrics generation and management
  - name: WAV Conversion
    description: Endpoints for converting music to WAV format
  - name: Vocal Removal
    description: Endpoints for vocal removal from music tracks
  - name: Music Video Generation
    description: Endpoints for generating MP4 videos from music tracks
  - name: Account Management
    description: Endpoints for account and credits management
paths:
  /api/v1/generate/upload-extend:
    post:
      summary: Upload And Extend Audio
      operationId: upload-and-extend-audio
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - uploadUrl
                - defaultParamFlag
                - callBackUrl
                - model
              properties:
                uploadUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL for uploading audio files, required regardless of
                    whether defaultParamFlag is true or false. Ensure the
                    uploaded audio does not exceed 8 minutes in length.
                    **Note**: When using the V4_5ALL model, the uploaded audio
                    file must not exceed **1 minute** in length.
                  example: https://storage.example.com/upload
                defaultParamFlag:
                  type: boolean
                  description: >-
                    Enable custom mode for advanced audio generation settings.  

                    - Set to `true` to use custom parameter mode (requires
                    `style`, `title`, and `uploadUrl`; if `instrumental` is
                    `false`, `uploadUrl` and `prompt` are required). If
                    `instrumental` is `false`, the prompt will be strictly used
                    as lyrics.  

                    - Set to `false` to use non-custom mode (only `uploadUrl`
                    required). Lyrics will be automatically generated based on
                    the prompt.
                  example: true
                instrumental:
                  type: boolean
                  description: >-
                    Determines whether the audio is instrumental (without
                    lyrics).  

                    - In custom parameter mode (`defaultParamFlag: true`):  
                      - If `true`: only `style`, `title`, and `uploadUrl` are required.  
                      - If `false`: `style`, `title`, `prompt` (`prompt` will be used as exact lyrics), and `uploadUrl` are required.  
                    - In non-custom parameter mode (`defaultParamFlag: false`):
                    does not affect required fields (only `uploadUrl` needed).
                    If `false`, lyrics will be automatically generated.
                  example: true
                prompt:
                  type: string
                  description: >-
                    Description of how the music should be extended. Required
                    when defaultParamFlag is true. Character limits by model:  
                      - **V4**: Maximum 3000 characters  
                      - **V4_5, V4_5PLUS, V4_5ALL & V5**: Maximum 5000 characters
                  example: Extend the music with more relaxing notes
                style:
                  type: string
                  description: >-
                    Music style, e.g., Jazz, Classical, Electronic. Character
                    limits by model:  
                      - **V4**: Maximum 200 characters  
                      - **V4_5, V4_5PLUS, V4_5ALL & V5**: Maximum 1000 characters
                  example: Classical
                title:
                  type: string
                  description: |-
                    Music title. Character limits by model:  
                      - **V4 & V4_5ALL**: Maximum 80 characters  
                      - **V4_5, V4_5PLUS & V5**: Maximum 100 characters
                  example: Peaceful Piano Extended
                continueAt:
                  type: number
                  description: >-
                    The time point (in seconds) from which to start extending
                    the music.  

                    - Required when `defaultParamFlag` is `true`.  

                    - Value range: greater than 0 and less than the total
                    duration of the uploaded audio.  

                    - Specifies the position in the original track where the
                    extension should begin.
                  example: 60
                personaId:
                  type: string
                  description: >-
                    Only available when Custom Mode (`customMode: true`) is
                    enabled. Persona ID to apply to the generated music.
                    Optional. Use this to apply a specific persona style to your
                    music generation. 


                    To generate a persona ID, use the [Generate
                    Persona](https://docs.sunoapi.org/suno-api/generate-persona)
                    endpoint to create a personalized music Persona based on
                    generated music.
                  example: persona_123
                model:
                  type: string
                  description: >-
                    Model version to use, must be consistent with the source
                    audio
                  enum:
                    - V4
                    - V4_5
                    - V4_5PLUS
                    - V4_5ALL
                    - V5
                  example: V4_5ALL
                negativeTags:
                  type: string
                  description: Music styles to exclude from generation
                  example: Relaxing Piano
                vocalGender:
                  type: string
                  description: Preferred vocal gender for generated vocals. Optional.
                  enum:
                    - m
                    - f
                  example: m
                styleWeight:
                  type: number
                  description: Weight of the provided style guidance. Range 0.00–1.00.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  example: 0.65
                weirdnessConstraint:
                  type: number
                  description: Constraint on creative deviation/novelty. Range 0.00–1.00.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  example: 0.65
                audioWeight:
                  type: number
                  description: >-
                    Weight of the input audio influence (where applicable).
                    Range 0.00–1.00.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  example: 0.65
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive task completion notifications when music
                    extension is complete.


                    For detailed callback format and implementation guide, see
                    [Upload and Extend Audio
                    Callbacks](https://docs.sunoapi.org/suno-api/upload-and-extend-audio-callbacks)

                    - Alternatively, you can use the get music generation
                    details endpoint to poll task status
                  example: https://api.example.com/callback
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/ApiResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: Task ID for tracking task status
                            example: 5c79****be8e
        '500':
          $ref: '#/components/responses/Error'
      callbacks:
        audioExtend:
          '{$request.body#/callBackUrl}':
            post:
              description: >-
                System will call this callback when audio generation is
                complete.


                ### Callback Example

                ```json

                {
                  "code": 200,
                  "msg": "All generated successfully.",
                  "data": {
                    "callbackType": "complete",
                    "task_id": "2fac****9f72",
                    "data": [
                      {
                        "id": "8551****662c",
                        "audio_url": "https://example.cn/****.mp3",
                        "source_audio_url": "https://example.cn/****.mp3",
                        "stream_audio_url": "https://example.cn/****",
                        "source_stream_audio_url": "https://example.cn/****",
                        "image_url": "https://example.cn/****.jpeg",
                        "source_image_url": "https://example.cn/****.jpeg",
                        "prompt": "[Verse] Night city lights shining bright",
                        "model_name": "chirp-v3-5",
                        "title": "Iron Man",
                        "tags": "electrifying, rock",
                        "createTime": "2025-01-01 00:00:00",
                        "duration": 198.44
                      }
                    ]
                  }
                }

                ```
              requestBody:
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        code:
                          type: integer
                          description: Status code
                          example: 200
                        msg:
                          type: string
                          description: Response message
                          example: All generated successfully
                        data:
                          type: object
                          properties:
                            callbackType:
                              type: string
                              description: >-
                                Callback type: text (text generation complete),
                                first (first track complete), complete (all
                                tracks complete)
                              enum:
                                - text
                                - first
                                - complete
                            task_id:
                              type: string
                              description: Task ID
                            data:
                              type: array
                              items:
                                type: object
                                properties:
                                  id:
                                    type: string
                                    description: Audio unique identifier (audioId)
                                  audio_url:
                                    type: string
                                    description: Audio file URL
                                  source_audio_url:
                                    type: string
                                    description: Original audio file URL
                                  stream_audio_url:
                                    type: string
                                    description: Streaming audio URL
                                  source_stream_audio_url:
                                    type: string
                                    description: Original streaming audio URL
                                  image_url:
                                    type: string
                                    description: Cover image URL
                                  source_image_url:
                                    type: string
                                    description: Original cover image URL
                                  prompt:
                                    type: string
                                    description: Generation prompt/lyrics
                                  model_name:
                                    type: string
                                    description: Model name used
                                  title:
                                    type: string
                                    description: Music title
                                  tags:
                                    type: string
                                    description: Music tags
                                  createTime:
                                    type: string
                                    description: Creation time
                                    format: date-time
                                  duration:
                                    type: number
                                    description: Audio duration (seconds)
              responses:
                '200':
                  description: Callback received successfully
components:
  schemas:
    ApiResponse:
      type: object
      properties:
        code:
          type: integer
          description: |-
            # Status Codes

            - ✅ 200 - Request successful
            - ⚠️ 400 - Invalid parameters
            - ⚠️ 401 - Unauthorized access
            - ⚠️ 404 - Invalid request method or path
            - ⚠️ 405 - Rate limit exceeded
            - ⚠️ 413 - Theme or prompt too long
            - ⚠️ 429 - Insufficient credits
            - ⚠️ 430 - Your call frequency is too high. Please try again later. 
            - ⚠️ 455 - System maintenance
            - ❌ 500 - Server error
          example: 200
          enum:
            - 200
            - 400
            - 401
            - 404
            - 405
            - 413
            - 429
            - 430
            - 455
            - 500
        msg:
          type: string
          description: Error message when code != 200
          example: success
  responses:
    Error:
      description: Server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        # 🔑 API Authentication


        All endpoints require authentication using Bearer Token.


        ## Get API Key


        1. Visit the [API Key Management Page](https://sunoapi.org/api-key) to
        obtain your API Key


        ## Usage


        Add to request headers:


        ```

        Authorization: Bearer YOUR_API_KEY

        ```


        > **⚠️ Note:**

        > - Keep your API Key secure and do not share it with others

        > - If you suspect your API Key has been compromised, reset it
        immediately from the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt


# Add Instrumental

> This endpoint generates a musical accompaniment tailored to an uploaded audio file — typically a vocal stem or melody track. It helps users instantly flesh out their vocal ideas with high-quality backing music, all without needing a producer.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/generate/add-instrumental
openapi: 3.0.0
info:
  title: intro
  description: API documentation for audio generation services
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://api.sunoapi.org
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: Music Generation
    description: Endpoints for creating and managing music generation tasks
  - name: Lyrics Generation
    description: Endpoints for lyrics generation and management
  - name: WAV Conversion
    description: Endpoints for converting music to WAV format
  - name: Vocal Removal
    description: Endpoints for vocal removal from music tracks
  - name: Music Video Generation
    description: Endpoints for generating MP4 videos from music tracks
  - name: Account Management
    description: Endpoints for account and credits management
paths:
  /api/v1/generate/add-instrumental:
    post:
      tags:
        - Music Generation
      summary: Add Instrumental
      operationId: add-instrumental
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - uploadUrl
                - title
                - negativeTags
                - tags
                - callBackUrl
              properties:
                uploadUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL of the uploaded music file to add instrumental to.  

                    - Required.  

                    - Must be a valid audio file URL accessible by the system.  

                    - The uploaded audio should be in a supported format (MP3,
                    WAV, etc.).
                  example: https://example.com/music.mp3
                title:
                  type: string
                  description: >-
                    The title of the music track.  

                    - Required.  

                    - This will be used as the title for the generated
                    instrumental track.
                  example: Relaxing Piano
                negativeTags:
                  type: string
                  description: >-
                    Music styles or traits to exclude from the generated
                    instrumental.  

                    - Required.  

                    - Use to avoid specific styles or instruments in the
                    instrumental version.  
                      Example: "Heavy Metal, Aggressive Drums"
                  example: Heavy Metal, Aggressive Drums
                tags:
                  type: string
                  description: >-
                    Music style and characteristics for the instrumental.  

                    - Required.  

                    - Describe the desired style, mood, and instruments for the
                    instrumental track.  
                      Example: "Relaxing Piano, Ambient, Peaceful"
                  example: Relaxing Piano, Ambient, Peaceful
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive task completion notifications when
                    instrumental generation is complete. The callback process
                    has three stages: `text` (text generation), `first` (first
                    track complete), `complete` (all tracks complete). Note: In
                    some cases, `text` and `first` stages may be skipped,
                    directly returning `complete`.


                    For detailed callback format and implementation guide, see
                    [Add Instrumental
                    Callbacks](https://docs.sunoapi.org/suno-api/add-instrumental-callbacks)

                    - Alternatively, you can use the Get Music Generation
                    Details interface to poll task status
                  example: https://api.example.com/callback
                vocalGender:
                  type: string
                  description: >-
                    Preferred vocal gender for any vocal elements. Optional.
                    Allowed values: 'm' (male), 'f' (female).
                  enum:
                    - m
                    - f
                  example: m
                styleWeight:
                  type: number
                  description: >-
                    Style adherence weight. Optional. Range: 0-1. Two decimal
                    places recommended.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  example: 0.61
                weirdnessConstraint:
                  type: number
                  description: >-
                    Creativity/novelty constraint. Optional. Range: 0-1. Two
                    decimal places recommended.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  example: 0.72
                audioWeight:
                  type: number
                  description: >-
                    Relative weight of audio consistency versus other controls.
                    Optional. Range: 0-1. Two decimal places recommended.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  example: 0.65
                model:
                  type: string
                  description: >-
                    Model version to use for generation. Optional. Default:
                    V4_5PLUS.
                  enum:
                    - V4_5PLUS
                    - V5
                  default: V4_5PLUS
                  example: V4_5PLUS
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/ApiResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: Task ID for tracking task status
                            example: 5c79****be8e
        '500':
          $ref: '#/components/responses/Error'
      callbacks:
        instrumentalAdded:
          '{request.body#/callBackUrl}':
            post:
              description: >-
                System will call this callback when instrumental generation is
                complete.


                ### Callback Example

                ```json

                {
                  "code": 200,
                  "msg": "All generated successfully.",
                  "data": {
                    "callbackType": "complete",
                    "task_id": "2fac****9f72",
                    "data": [
                      {
                        "id": "8551****662c",
                        "audio_url": "https://example.cn/****.mp3",
                        "source_audio_url": "https://example.cn/****.mp3",
                        "stream_audio_url": "https://example.cn/****",
                        "source_stream_audio_url": "https://example.cn/****",
                        "image_url": "https://example.cn/****.jpeg",
                        "source_image_url": "https://example.cn/****.jpeg",
                        "prompt": "[Instrumental] Relaxing piano melody",
                        "model_name": "chirp-v3-5",
                        "title": "Relaxing Piano Instrumental",
                        "tags": "relaxing, piano, instrumental",
                        "createTime": "2025-01-01 00:00:00",
                        "duration": 198.44
                      }
                    ]
                  }
                }

                ```
              requestBody:
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        code:
                          type: integer
                          description: Status code
                          example: 200
                        msg:
                          type: string
                          description: Response message
                          example: All generated successfully
                        data:
                          type: object
                          properties:
                            callbackType:
                              type: string
                              description: >-
                                Callback type: text (text generation complete),
                                first (first track complete), complete (all
                                tracks complete)
                              enum:
                                - text
                                - first
                                - complete
                            task_id:
                              type: string
                              description: Task ID
                            data:
                              type: array
                              items:
                                type: object
                                properties:
                                  id:
                                    type: string
                                    description: Audio unique identifier (audioId)
                                  audio_url:
                                    type: string
                                    description: Audio file URL
                                  source_audio_url:
                                    type: string
                                    description: Original audio file URL
                                  stream_audio_url:
                                    type: string
                                    description: Streaming audio URL
                                  source_stream_audio_url:
                                    type: string
                                    description: Original streaming audio URL
                                  image_url:
                                    type: string
                                    description: Cover image URL
                                  source_image_url:
                                    type: string
                                    description: Original cover image URL
                                  prompt:
                                    type: string
                                    description: Generation prompt/lyrics
                                  model_name:
                                    type: string
                                    description: Model name used
                                  title:
                                    type: string
                                    description: Music title
                                  tags:
                                    type: string
                                    description: Music tags
                                  createTime:
                                    type: string
                                    description: Creation time
                                    format: date-time
                                  duration:
                                    type: number
                                    description: Audio duration (seconds)
              responses:
                '200':
                  description: Callback received successfully
components:
  schemas:
    ApiResponse:
      type: object
      properties:
        code:
          type: integer
          description: |-
            # Status Codes

            - ✅ 200 - Request successful
            - ⚠️ 400 - Invalid parameters
            - ⚠️ 401 - Unauthorized access
            - ⚠️ 404 - Invalid request method or path
            - ⚠️ 405 - Rate limit exceeded
            - ⚠️ 413 - Theme or prompt too long
            - ⚠️ 429 - Insufficient credits
            - ⚠️ 430 - Your call frequency is too high. Please try again later. 
            - ⚠️ 455 - System maintenance
            - ❌ 500 - Server error
          example: 200
          enum:
            - 200
            - 400
            - 401
            - 404
            - 405
            - 413
            - 429
            - 430
            - 455
            - 500
        msg:
          type: string
          description: Error message when code != 200
          example: success
  responses:
    Error:
      description: Server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        # 🔑 API Authentication


        All endpoints require authentication using Bearer Token.


        ## Get API Key


        1. Visit the [API Key Management Page](https://sunoapi.org/api-key) to
        obtain your API Key


        ## Usage


        Add to request headers:


        ```

        Authorization: Bearer YOUR_API_KEY

        ```


        > **⚠️ Note:**

        > - Keep your API Key secure and do not share it with others

        > - If you suspect your API Key has been compromised, reset it
        immediately from the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt


# Add Vocals

> This endpoint layers AI-generated vocals on top of an existing instrumental. Given a prompt (e.g., lyrical concept or musical mood) and optional audio, it produces vocal output harmonized with the provided track.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/generate/add-vocals
openapi: 3.0.0
info:
  title: intro
  description: API documentation for audio generation services
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://api.sunoapi.org
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: Music Generation
    description: Endpoints for creating and managing music generation tasks
  - name: Lyrics Generation
    description: Endpoints for lyrics generation and management
  - name: WAV Conversion
    description: Endpoints for converting music to WAV format
  - name: Vocal Removal
    description: Endpoints for vocal removal from music tracks
  - name: Music Video Generation
    description: Endpoints for generating MP4 videos from music tracks
  - name: Account Management
    description: Endpoints for account and credits management
paths:
  /api/v1/generate/add-vocals:
    post:
      tags:
        - Music Generation
      summary: Add Vocals
      operationId: add-vocals
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - uploadUrl
                - callBackUrl
                - prompt
                - title
                - negativeTags
                - style
              properties:
                prompt:
                  type: string
                  description: >-
                    Description of the audio content to generate vocals for.  

                    - Required.  

                    - Provides context about the desired vocal style and
                    content.  

                    - The more detailed your prompt, the better the vocal
                    generation will match your vision.
                  example: A calm and relaxing piano track with soothing vocals
                title:
                  type: string
                  description: >-
                    The title of the music track.  

                    - Required.  

                    - This will be used as the title for the generated vocal
                    track.
                  example: Relaxing Piano with Vocals
                negativeTags:
                  type: string
                  description: >-
                    Music styles or vocal traits to exclude from the generated
                    track.  

                    - Required.  

                    - Use to avoid specific vocal styles or characteristics.  
                      Example: "Heavy Metal, Aggressive Vocals"
                  example: Heavy Metal, Aggressive Vocals
                style:
                  type: string
                  description: |-
                    The music and vocal style.  
                    - Required.  
                    - Examples: "Jazz", "Classical", "Electronic", "Pop".  
                    - Describes the overall genre and vocal approach.
                  example: Jazz
                vocalGender:
                  type: string
                  description: >-
                    Preferred vocal gender. Optional. Allowed values: 'm'
                    (male), 'f' (female).
                  enum:
                    - m
                    - f
                  example: m
                styleWeight:
                  type: number
                  description: >-
                    Style adherence weight. Optional. Range: 0-1. Two decimal
                    places recommended.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  example: 0.61
                weirdnessConstraint:
                  type: number
                  description: >-
                    Creativity/novelty constraint. Optional. Range: 0-1. Two
                    decimal places recommended.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  example: 0.72
                audioWeight:
                  type: number
                  description: >-
                    Relative weight of audio consistency versus other controls.
                    Optional. Range: 0-1. Two decimal places recommended.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  example: 0.65
                uploadUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL of the uploaded audio file to add vocals to.  

                    - Required.  

                    - Must be a valid audio file URL accessible by the system.  

                    - The uploaded audio should be in a supported format (MP3,
                    WAV, etc.).
                  example: https://example.com/instrumental.mp3
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive task completion notifications when vocal
                    generation is complete. The callback process has three
                    stages: `text` (text generation), `first` (first track
                    complete), `complete` (all tracks complete). Note: In some
                    cases, `text` and `first` stages may be skipped, directly
                    returning `complete`.


                    For detailed callback format and implementation guide, see
                    [Add Vocals
                    Callbacks](https://docs.sunoapi.org/suno-api/add-vocals-callbacks)

                    - Alternatively, you can use the Get Music Generation
                    Details interface to poll task status
                  example: https://api.example.com/callback
                model:
                  type: string
                  description: >-
                    Model version to use for generation. Optional. Default:
                    V4_5PLUS.
                  enum:
                    - V4_5PLUS
                    - V5
                  default: V4_5PLUS
                  example: V4_5PLUS
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/ApiResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: Task ID for tracking task status
                            example: 5c79****be8e
        '500':
          $ref: '#/components/responses/Error'
      callbacks:
        vocalsAdded:
          '{request.body#/callBackUrl}':
            post:
              description: >-
                System will call this callback when vocal generation is
                complete.


                ### Callback Example

                ```json

                {
                  "code": 200,
                  "msg": "All generated successfully.",
                  "data": {
                    "callbackType": "complete",
                    "task_id": "2fac****9f72",
                    "data": [
                      {
                        "id": "8551****662c",
                        "audio_url": "https://example.cn/****.mp3",
                        "source_audio_url": "https://example.cn/****.mp3",
                        "stream_audio_url": "https://example.cn/****",
                        "source_stream_audio_url": "https://example.cn/****",
                        "image_url": "https://example.cn/****.jpeg",
                        "source_image_url": "https://example.cn/****.jpeg",
                        "prompt": "[Verse] Calm and relaxing melodies with soothing vocals",
                        "model_name": "chirp-v3-5",
                        "title": "Relaxing Piano with Vocals",
                        "tags": "relaxing, piano, vocals, jazz",
                        "createTime": "2025-01-01 00:00:00",
                        "duration": 198.44
                      }
                    ]
                  }
                }

                ```
              requestBody:
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        code:
                          type: integer
                          description: Status code
                          example: 200
                        msg:
                          type: string
                          description: Response message
                          example: All generated successfully
                        data:
                          type: object
                          properties:
                            callbackType:
                              type: string
                              description: >-
                                Callback type: text (text generation complete),
                                first (first track complete), complete (all
                                tracks complete)
                              enum:
                                - text
                                - first
                                - complete
                            task_id:
                              type: string
                              description: Task ID
                            data:
                              type: array
                              items:
                                type: object
                                properties:
                                  id:
                                    type: string
                                    description: Audio unique identifier (audioId)
                                  audio_url:
                                    type: string
                                    description: Audio file URL
                                  source_audio_url:
                                    type: string
                                    description: Original audio file URL
                                  stream_audio_url:
                                    type: string
                                    description: Streaming audio URL
                                  source_stream_audio_url:
                                    type: string
                                    description: Original streaming audio URL
                                  image_url:
                                    type: string
                                    description: Cover image URL
                                  source_image_url:
                                    type: string
                                    description: Original cover image URL
                                  prompt:
                                    type: string
                                    description: Generation prompt/lyrics
                                  model_name:
                                    type: string
                                    description: Model name used
                                  title:
                                    type: string
                                    description: Music title
                                  tags:
                                    type: string
                                    description: Music tags
                                  createTime:
                                    type: string
                                    description: Creation time
                                    format: date-time
                                  duration:
                                    type: number
                                    description: Audio duration (seconds)
              responses:
                '200':
                  description: Callback received successfully
components:
  schemas:
    ApiResponse:
      type: object
      properties:
        code:
          type: integer
          description: |-
            # Status Codes

            - ✅ 200 - Request successful
            - ⚠️ 400 - Invalid parameters
            - ⚠️ 401 - Unauthorized access
            - ⚠️ 404 - Invalid request method or path
            - ⚠️ 405 - Rate limit exceeded
            - ⚠️ 413 - Theme or prompt too long
            - ⚠️ 429 - Insufficient credits
            - ⚠️ 430 - Your call frequency is too high. Please try again later. 
            - ⚠️ 455 - System maintenance
            - ❌ 500 - Server error
          example: 200
          enum:
            - 200
            - 400
            - 401
            - 404
            - 405
            - 413
            - 429
            - 430
            - 455
            - 500
        msg:
          type: string
          description: Error message when code != 200
          example: success
  responses:
    Error:
      description: Server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        # 🔑 API Authentication


        All endpoints require authentication using Bearer Token.


        ## Get API Key


        1. Visit the [API Key Management Page](https://sunoapi.org/api-key) to
        obtain your API Key


        ## Usage


        Add to request headers:


        ```

        Authorization: Bearer YOUR_API_KEY

        ```


        > **⚠️ Note:**

        > - Keep your API Key secure and do not share it with others

        > - If you suspect your API Key has been compromised, reset it
        immediately from the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt

# Get Music Generation Details

> Retrieve detailed information about a music generation task, including status, parameters, and results.

## OpenAPI

````yaml suno-api/suno-api.json get /api/v1/generate/record-info
openapi: 3.0.0
info:
  title: intro
  description: API documentation for audio generation services
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://api.sunoapi.org
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: Music Generation
    description: Endpoints for creating and managing music generation tasks
  - name: Lyrics Generation
    description: Endpoints for lyrics generation and management
  - name: WAV Conversion
    description: Endpoints for converting music to WAV format
  - name: Vocal Removal
    description: Endpoints for vocal removal from music tracks
  - name: Music Video Generation
    description: Endpoints for generating MP4 videos from music tracks
  - name: Account Management
    description: Endpoints for account and credits management
paths:
  /api/v1/generate/record-info:
    get:
      summary: Get Music Generation Details
      operationId: get-music-generation-details
      parameters:
        - in: query
          name: taskId
          description: >-
            The task ID returned from the Generate Music or Extend Music
            endpoints. Used to identify the specific generation task to query.
          required: true
          example: 5c79****be8e
          schema:
            type: string
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/ApiResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: Task ID
                          parentMusicId:
                            type: string
                            description: Parent music ID (only valid when extending music)
                          param:
                            type: string
                            description: Parameter information for task generation
                          response:
                            type: object
                            properties:
                              taskId:
                                type: string
                                description: Task ID
                              sunoData:
                                type: array
                                items:
                                  type: object
                                  properties:
                                    id:
                                      type: string
                                      description: Audio unique identifier (audioId)
                                    audioUrl:
                                      type: string
                                      description: Audio file URL
                                    streamAudioUrl:
                                      type: string
                                      description: Streaming audio URL
                                    imageUrl:
                                      type: string
                                      description: Cover image URL
                                    prompt:
                                      type: string
                                      description: Generation prompt/lyrics
                                    modelName:
                                      type: string
                                      description: Model name used
                                    title:
                                      type: string
                                      description: Music title
                                    tags:
                                      type: string
                                      description: Music tags
                                    createTime:
                                      type: string
                                      description: Creation time
                                      format: date-time
                                    duration:
                                      type: number
                                      description: Audio duration (seconds)
                          status:
                            type: string
                            description: Task status
                            enum:
                              - PENDING
                              - TEXT_SUCCESS
                              - FIRST_SUCCESS
                              - SUCCESS
                              - CREATE_TASK_FAILED
                              - GENERATE_AUDIO_FAILED
                              - CALLBACK_EXCEPTION
                              - SENSITIVE_WORD_ERROR
                          type:
                            type: string
                            enum:
                              - chirp-v3-5
                              - chirp-v4
                            description: Task type
                          operationType:
                            type: string
                            enum:
                              - generate
                              - extend
                              - upload_cover
                              - upload_extend
                            description: >-
                              Operation Type


                              - `generate`: Generate Music - Create new music
                              works using AI model

                              - `extend`: Extend Music - Extend or modify
                              existing music works

                              - `upload_cover`: Upload And Cover Audio - Create
                              new music works based on uploaded audio files

                              - `upload_extend`: Upload And Extend Audio -
                              Extend or modify music works based on uploaded
                              audio files
                          errorCode:
                            type: number
                            description: Error code, valid when task fails
                          errorMessage:
                            type: string
                            description: Error message, valid when task fails
              example:
                code: 200
                msg: success
                data:
                  taskId: 5c79****be8e
                  parentMusicId: ''
                  param: >-
                    {"prompt":"A calm piano
                    track","style":"Classical","title":"Peaceful
                    Piano","customMode":true,"instrumental":true,"model":"V4_5ALL"}
                  response:
                    taskId: 5c79****be8e
                    sunoData:
                      - id: 8551****662c
                        audioUrl: https://example.cn/****.mp3
                        streamAudioUrl: https://example.cn/****
                        imageUrl: https://example.cn/****.jpeg
                        prompt: '[Verse] 夜晚城市 灯火辉煌'
                        modelName: chirp-v3-5
                        title: 钢铁侠
                        tags: electrifying, rock
                        createTime: '2025-01-01 00:00:00'
                        duration: 198.44
                  status: SUCCESS
                  type: GENERATE
                  errorCode: null
                  errorMessage: null
        '500':
          $ref: '#/components/responses/Error'
components:
  schemas:
    ApiResponse:
      type: object
      properties:
        code:
          type: integer
          description: |-
            # Status Codes

            - ✅ 200 - Request successful
            - ⚠️ 400 - Invalid parameters
            - ⚠️ 401 - Unauthorized access
            - ⚠️ 404 - Invalid request method or path
            - ⚠️ 405 - Rate limit exceeded
            - ⚠️ 413 - Theme or prompt too long
            - ⚠️ 429 - Insufficient credits
            - ⚠️ 430 - Your call frequency is too high. Please try again later. 
            - ⚠️ 455 - System maintenance
            - ❌ 500 - Server error
          example: 200
          enum:
            - 200
            - 400
            - 401
            - 404
            - 405
            - 413
            - 429
            - 430
            - 455
            - 500
        msg:
          type: string
          description: Error message when code != 200
          example: success
  responses:
    Error:
      description: Server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        # 🔑 API Authentication


        All endpoints require authentication using Bearer Token.


        ## Get API Key


        1. Visit the [API Key Management Page](https://sunoapi.org/api-key) to
        obtain your API Key


        ## Usage


        Add to request headers:


        ```

        Authorization: Bearer YOUR_API_KEY

        ```


        > **⚠️ Note:**

        > - Keep your API Key secure and do not share it with others

        > - If you suspect your API Key has been compromised, reset it
        immediately from the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt


# Get Timestamped Lyrics

> Retrieve timestamped lyrics for synchronized display during audio playback.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/generate/get-timestamped-lyrics
openapi: 3.0.0
info:
  title: intro
  description: API documentation for audio generation services
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://api.sunoapi.org
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: Music Generation
    description: Endpoints for creating and managing music generation tasks
  - name: Lyrics Generation
    description: Endpoints for lyrics generation and management
  - name: WAV Conversion
    description: Endpoints for converting music to WAV format
  - name: Vocal Removal
    description: Endpoints for vocal removal from music tracks
  - name: Music Video Generation
    description: Endpoints for generating MP4 videos from music tracks
  - name: Account Management
    description: Endpoints for account and credits management
paths:
  /api/v1/generate/get-timestamped-lyrics:
    post:
      summary: Get Timestamped Lyrics
      operationId: get-timestamped-lyrics
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - taskId
                - audioId
              properties:
                taskId:
                  type: string
                  description: >-
                    The task ID of the music generation task. Required to
                    identify which generation task contains the lyrics.
                  example: 5c79****be8e
                audioId:
                  type: string
                  description: Audio ID of the track to retrieve lyrics for.
                  example: e231****-****-****-****-****8cadc7dc
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/ApiResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          alignedWords:
                            type: array
                            description: List of aligned lyrics words
                            items:
                              type: object
                              properties:
                                word:
                                  type: string
                                  description: Lyrics word
                                  example: |-
                                    [Verse]
                                    Waggin'
                                success:
                                  type: boolean
                                  description: Whether lyrics word is successfully aligned
                                  example: true
                                startS:
                                  type: number
                                  description: Word start time (seconds)
                                  example: 1.36
                                endS:
                                  type: number
                                  description: Word end time (seconds)
                                  example: 1.79
                                palign:
                                  type: integer
                                  description: Alignment parameter
                                  example: 0
                          waveformData:
                            type: array
                            description: Waveform data, used for audio visualization
                            items:
                              type: number
                            example:
                              - 0
                              - 1
                              - 0.5
                              - 0.75
                          hootCer:
                            type: number
                            description: Lyrics alignment accuracy score
                            example: 0.3803191489361702
                          isStreamed:
                            type: boolean
                            description: Whether it's streaming audio
                            example: false
              example:
                code: 200
                msg: success
                data:
                  alignedWords:
                    - word: |-
                        [Verse]
                        Waggin'
                      success: true
                      startS: 1.36
                      endS: 1.79
                      palign: 0
                  waveformData:
                    - 0
                    - 1
                    - 0.5
                    - 0.75
                  hootCer: 0.3803191489361702
                  isStreamed: false
        '500':
          $ref: '#/components/responses/Error'
components:
  schemas:
    ApiResponse:
      type: object
      properties:
        code:
          type: integer
          description: |-
            # Status Codes

            - ✅ 200 - Request successful
            - ⚠️ 400 - Invalid parameters
            - ⚠️ 401 - Unauthorized access
            - ⚠️ 404 - Invalid request method or path
            - ⚠️ 405 - Rate limit exceeded
            - ⚠️ 413 - Theme or prompt too long
            - ⚠️ 429 - Insufficient credits
            - ⚠️ 430 - Your call frequency is too high. Please try again later. 
            - ⚠️ 455 - System maintenance
            - ❌ 500 - Server error
          example: 200
          enum:
            - 200
            - 400
            - 401
            - 404
            - 405
            - 413
            - 429
            - 430
            - 455
            - 500
        msg:
          type: string
          description: Error message when code != 200
          example: success
  responses:
    Error:
      description: Server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        # 🔑 API Authentication


        All endpoints require authentication using Bearer Token.


        ## Get API Key


        1. Visit the [API Key Management Page](https://sunoapi.org/api-key) to
        obtain your API Key


        ## Usage


        Add to request headers:


        ```

        Authorization: Bearer YOUR_API_KEY

        ```


        > **⚠️ Note:**

        > - Keep your API Key secure and do not share it with others

        > - If you suspect your API Key has been compromised, reset it
        immediately from the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt


# Boost Music Style

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/style/generate
openapi: 3.0.0
info:
  title: intro
  description: API documentation for audio generation services
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://api.sunoapi.org
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: Music Generation
    description: Endpoints for creating and managing music generation tasks
  - name: Lyrics Generation
    description: Endpoints for lyrics generation and management
  - name: WAV Conversion
    description: Endpoints for converting music to WAV format
  - name: Vocal Removal
    description: Endpoints for vocal removal from music tracks
  - name: Music Video Generation
    description: Endpoints for generating MP4 videos from music tracks
  - name: Account Management
    description: Endpoints for account and credits management
paths:
  /api/v1/style/generate:
    post:
      summary: Boost Music Style
      operationId: boost-music-style
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - content
              properties:
                content:
                  type: string
                  description: >-
                    Style description. Please describe in concise and clear
                    language the music style you expect to generate. Example:
                    'Pop, Mysterious'
                  example: Pop, Mysterious
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/ApiResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: Task ID
                          param:
                            type: string
                            description: Request parameters
                          result:
                            type: string
                            description: The final generated music style text result.
                          creditsConsumed:
                            type: number
                            description: >-
                              Credits consumed, up to 5 digits, up to 2 decimal
                              places
                          creditsRemaining:
                            type: number
                            description: Credits remaining after this task
                          successFlag:
                            type: string
                            description: 'Execution result: 0-pending, 1-success, 2-failed'
                          errorCode:
                            type: number
                            description: Error code
                          errorMessage:
                            type: string
                            description: Error message
                          createTime:
                            type: string
                            description: Creation time
        '500':
          $ref: '#/components/responses/Error'
components:
  schemas:
    ApiResponse:
      type: object
      properties:
        code:
          type: integer
          description: |-
            # Status Codes

            - ✅ 200 - Request successful
            - ⚠️ 400 - Invalid parameters
            - ⚠️ 401 - Unauthorized access
            - ⚠️ 404 - Invalid request method or path
            - ⚠️ 405 - Rate limit exceeded
            - ⚠️ 413 - Theme or prompt too long
            - ⚠️ 429 - Insufficient credits
            - ⚠️ 430 - Your call frequency is too high. Please try again later. 
            - ⚠️ 455 - System maintenance
            - ❌ 500 - Server error
          example: 200
          enum:
            - 200
            - 400
            - 401
            - 404
            - 405
            - 413
            - 429
            - 430
            - 455
            - 500
        msg:
          type: string
          description: Error message when code != 200
          example: success
  responses:
    Error:
      description: Server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        # 🔑 API Authentication


        All endpoints require authentication using Bearer Token.


        ## Get API Key


        1. Visit the [API Key Management Page](https://sunoapi.org/api-key) to
        obtain your API Key


        ## Usage


        Add to request headers:


        ```

        Authorization: Bearer YOUR_API_KEY

        ```


        > **⚠️ Note:**

        > - Keep your API Key secure and do not share it with others

        > - If you suspect your API Key has been compromised, reset it
        immediately from the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt


# Generate Music Cover

> Create personalized cover images for generated music.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/suno/cover/generate
openapi: 3.0.0
info:
  title: intro
  description: API documentation for audio generation services
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://api.sunoapi.org
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: Music Generation
    description: Endpoints for creating and managing music generation tasks
  - name: Lyrics Generation
    description: Endpoints for lyrics generation and management
  - name: WAV Conversion
    description: Endpoints for converting music to WAV format
  - name: Vocal Removal
    description: Endpoints for vocal removal from music tracks
  - name: Music Video Generation
    description: Endpoints for generating MP4 videos from music tracks
  - name: Account Management
    description: Endpoints for account and credits management
paths:
  /api/v1/suno/cover/generate:
    post:
      summary: Create Suno Cover Task
      description: >-
        Generate personalized cover images based on original music tasks.


        ### Usage Guide

        - Use this interface to create personalized cover images for generated
        music

        - Requires the taskId of the original music task

        - Each music task can only generate a Cover once; duplicate requests
        will return the existing taskId

        - Results will be notified through the callback URL upon completion


        ### Parameter Details

        - `taskId` identifies the unique identifier of the original music
        generation task

        - `callBackUrl` receives callback address for completion notifications


        ### Developer Notes

        - Cover image file URLs will be retained for 14 days

        - If a Cover has already been generated for this music task, a 400
        status code and existing taskId will be returned

        - It's recommended to call this interface after music generation is
        complete
      operationId: generate-cover
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - taskId
                - callBackUrl
              properties:
                taskId:
                  type: string
                  description: >-
                    Original music task ID, should be the taskId returned by the
                    music generation interface.
                  example: 73d6128b3523a0079df10da9471017c8
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    URL address for receiving Cover generation task completion
                    updates. This parameter is required for all Cover generation
                    requests.


                    - The system will send POST requests to this URL when Cover
                    generation is complete, including task status and results

                    - Your callback endpoint should be able to accept JSON
                    payloads containing cover image URLs

                    - For detailed callback format and implementation guide, see
                    [Cover Generation
                    Callbacks](https://docs.sunoapi.org/suno-api/cover-suno-callbacks)

                    - Alternatively, you can use the Get Cover Details interface
                    to poll task status
                  example: https://api.example.com/callback
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                allOf:
                  - type: object
                    properties:
                      code:
                        type: integer
                        enum:
                          - 200
                          - 400
                          - 401
                          - 402
                          - 404
                          - 409
                          - 422
                          - 429
                          - 455
                          - 500
                        description: >-
                          Response status code


                          - **200**: Success - Request processed successfully

                          - **400**: Validation error - Cover already generated
                          for this task

                          - **401**: Unauthorized - Authentication credentials
                          missing or invalid

                          - **402**: Insufficient credits - Account doesn't have
                          enough credits for this operation

                          - **404**: Not found - Requested resource or endpoint
                          doesn't exist

                          - **409**: Conflict - Cover record already exists

                          - **422**: Validation error - Request parameters
                          failed validation checks

                          - **429**: Rate limited - Your call frequency is too
                          high. Please try again later.

                          - **455**: Service unavailable - System currently
                          undergoing maintenance

                          - **500**: Server error - Unexpected error occurred
                          while processing request

                          Build failed - Cover image generation failed
                      msg:
                        type: string
                        description: Error message when code != 200
                        example: success
                type: object
                properties:
                  code:
                    type: integer
                    format: int32
                    description: Status code
                    example: 200
                  msg:
                    type: string
                    description: Status message
                    example: success
                  data:
                    type: object
                    properties:
                      taskId:
                        type: string
                        description: Task ID
                        example: 21aee3c3c2a01fa5e030b3799fa4dd56
              example:
                code: 200
                msg: success
                data:
                  taskId: 21aee3c3c2a01fa5e030b3799fa4dd56
        '500':
          $ref: '#/components/responses/Error'
      callbacks:
        onCoverGenerated:
          '{$request.body#/callBackUrl}':
            post:
              summary: Cover generation completion callback
              description: >-
                When Cover generation is complete, the system will send a POST
                request to the provided callback URL to notify results
              requestBody:
                required: true
                content:
                  application/json:
                    schema:
                      allOf:
                        - type: object
                          properties:
                            code:
                              type: integer
                              enum:
                                - 200
                                - 500
                              description: >-
                                Response status code


                                - **200**: Success - Request processed
                                successfully

                                - **500**: Internal error - Please try again
                                later.
                            msg:
                              type: string
                              description: Error message when code != 200
                              example: success
                      type: object
                      required:
                        - code
                        - msg
                        - data
                      properties:
                        code:
                          type: integer
                          description: Status code, 200 indicates success
                          example: 200
                        msg:
                          type: string
                          description: Status message
                          example: success
                        data:
                          type: object
                          required:
                            - taskId
                            - images
                          properties:
                            taskId:
                              type: string
                              description: Unique identifier of the generation task
                              example: 21aee3c3c2a01fa5e030b3799fa4dd56
                            images:
                              type: array
                              items:
                                type: string
                              description: >-
                                Array of accessible cover image URLs, valid for
                                14 days
                              example:
                                - >-
                                  https://tempfile.aiquickdraw.com/s/1753958521_6c1b3015141849d1a9bf17b738ce9347.png
                                - >-
                                  https://tempfile.aiquickdraw.com/s/1753958524_c153143acc6340908431cf0e90cbce9e.png
              responses:
                '200':
                  description: Callback received successfully
components:
  responses:
    Error:
      description: Server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        # 🔑 API Authentication


        All endpoints require authentication using Bearer Token.


        ## Get API Key


        1. Visit the [API Key Management Page](https://sunoapi.org/api-key) to
        obtain your API Key


        ## Usage


        Add to request headers:


        ```

        Authorization: Bearer YOUR_API_KEY

        ```


        > **⚠️ Note:**

        > - Keep your API Key secure and do not share it with others

        > - If you suspect your API Key has been compromised, reset it
        immediately from the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt


# Replace Music Section

> Replace a specific time segment within existing music.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/generate/replace-section
openapi: 3.0.0
info:
  title: intro
  description: API documentation for audio generation services
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://api.sunoapi.org
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: Music Generation
    description: Endpoints for creating and managing music generation tasks
  - name: Lyrics Generation
    description: Endpoints for lyrics generation and management
  - name: WAV Conversion
    description: Endpoints for converting music to WAV format
  - name: Vocal Removal
    description: Endpoints for vocal removal from music tracks
  - name: Music Video Generation
    description: Endpoints for generating MP4 videos from music tracks
  - name: Account Management
    description: Endpoints for account and credits management
paths:
  /api/v1/generate/replace-section:
    post:
      summary: Replace Music Section
      description: >-
        Replace a specific time segment within existing music. This interface
        allows you to select a specific segment of music for regeneration and
        replacement.


        ### Usage Guide

        - This interface can replace specific time segments in already generated
        music

        - Requires providing the original music's task ID and the time range to
        be replaced

        - The replaced audio will naturally blend with the original music


        ### Parameter Details

        - `taskId`: Required parameter, original music's parent task ID

        - `audioId`: Required parameter, audio ID to replace (selected from the
        generated music list)

        - `prompt`: Required parameter, prompt describing the replacement
        segment content

        - `tags`: Required parameter, music style tags

        - `title`: Required parameter, music title

        - `infillStartS`: Required parameter, start time point for replacement
        (seconds, 2 decimal places)

        - `infillEndS`: Required parameter, end time point for replacement
        (seconds, 2 decimal places)

        - `negativeTags`: Optional parameter, music styles to exclude

        - `callBackUrl`: Optional parameter, callback address after task
        completion


        ### Time Range Instructions

        - `infillStartS` must be less than `infillEndS`

        - Time values are precise to 2 decimal places, e.g., 10.50 seconds

        - Replacement duration should not exceed 50% of the original music's
        total duration


        ### Developer Notes

        - Replacement segments will be regenerated based on the provided
        `prompt` and `tags`

        - Generated replacement segments will automatically blend with the
        original music's preceding and following parts

        - Generated files will be retained for 14 days

        - Query task status using the same interface as generating music
      operationId: replace-section
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - taskId
                - audioId
                - prompt
                - tags
                - title
                - infillStartS
                - infillEndS
              properties:
                taskId:
                  type: string
                  description: >-
                    Original task ID (parent task), used to identify the source
                    music for section replacement
                  example: 2fac****9f72
                audioId:
                  type: string
                  description: Audio ID of the track to replace.
                  example: e231****-****-****-****-****8cadc7dc
                prompt:
                  type: string
                  description: >-
                    Prompt for generating the replacement segment, typically
                    text describing the audio content
                  example: A calm and relaxing piano track.
                tags:
                  type: string
                  description: Music style tags, such as jazz, electronic, etc.
                  example: Jazz
                title:
                  type: string
                  description: Music title
                  example: Relaxing Piano
                negativeTags:
                  type: string
                  description: >-
                    Excluded music styles, used to avoid specific style elements
                    in the replacement segment
                  example: Rock
                infillStartS:
                  type: number
                  description: >-
                    Start time point for replacement (seconds), 2 decimal
                    places. Must be less than infillEndS. The time interval
                    (infillEndS - infillStartS) must be between 6 and 60
                    seconds.
                  example: 10.5
                  minimum: 0
                infillEndS:
                  type: number
                  description: >-
                    End time point for replacement (seconds), 2 decimal places.
                    Must be greater than infillStartS. The time interval
                    (infillEndS - infillStartS) must be between 6 and 60
                    seconds.
                  example: 20.75
                  minimum: 0
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    Callback URL for task completion. The system will send a
                    POST request to this URL when replacement is complete,
                    containing task status and results.


                    - Your callback endpoint should be able to accept POST
                    requests containing JSON payloads with replacement results

                    - For detailed callback format and implementation guide, see
                    [Replace Music Section
                    Callbacks](https://docs.sunoapi.org/suno-api/replace-section-callbacks)

                    - Alternatively, you can use the get music details interface
                    to poll task status
                  example: https://example.com/callback
            example:
              taskId: 2fac****9f72
              audioId: e231****-****-****-****-****8cadc7dc
              prompt: A calm and relaxing piano track.
              tags: Jazz
              title: Relaxing Piano
              negativeTags: Rock
              infillStartS: 10.5
              infillEndS: 20.75
              callBackUrl: https://example.com/callback
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - type: object
                    properties:
                      code:
                        type: integer
                        enum:
                          - 200
                          - 401
                          - 402
                          - 404
                          - 409
                          - 422
                          - 429
                          - 451
                          - 455
                          - 500
                        description: >-
                          Response status code


                          - **200**: Success - Request processed successfully

                          - **401**: Unauthorized - Authentication credentials
                          missing or invalid

                          - **402**: Insufficient credits - Account does not
                          have enough credits to perform this operation

                          - **404**: Not found - Requested resource or endpoint
                          does not exist

                          - **409**: Conflict - WAV record already exists

                          - **422**: Validation error - Request parameters
                          failed validation checks

                          - **429**: Rate limit exceeded - Exceeded request
                          limit for this resource

                          - **451**: Unauthorized - Failed to retrieve image.
                          Please verify any access restrictions set by you or
                          your service provider.

                          - **455**: Service unavailable - System is currently
                          undergoing maintenance

                          - **500**: Server error - Unexpected error occurred
                          while processing request
                      msg:
                        type: string
                        description: Error message when code != 200
                        example: success
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: >-
                              Task ID for tracking task status. You can use this
                              ID to query task details and results through the
                              "Get Music Details" interface.
                            example: 5c79****be8e
        '500':
          $ref: '#/components/responses/Error'
      callbacks:
        audioGenerated:
          '{request.body#/callBackUrl}':
            post:
              description: >-
                When audio generation is complete, the system will call this
                callback to notify the result.


                ### Callback Example

                ```json

                {
                  "code": 200,
                  "msg": "All generated successfully.",
                  "data": {
                    "callbackType": "complete",
                    "task_id": "2fac****9f72",
                    "data": [
                      {
                        "id": "e231****-****-****-****-****8cadc7dc",
                        "audio_url": "https://example.cn/****.mp3",
                        "stream_audio_url": "https://example.cn/****",
                        "image_url": "https://example.cn/****.jpeg",
                        "prompt": "A calm and relaxing piano track.",
                        "model_name": "chirp-v3-5",
                        "title": "Relaxing Piano",
                        "tags": "Jazz",
                        "createTime": "2025-01-01 00:00:00",
                        "duration": 198.44
                      }
                    ]
                  }
                }

                ```
              requestBody:
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        code:
                          type: integer
                          description: Status code
                          example: 200
                        msg:
                          type: string
                          description: Return message
                          example: All generated successfully
                        data:
                          type: object
                          properties:
                            callbackType:
                              type: string
                              description: >-
                                Callback type: text (text generation complete),
                                first (first song complete), complete (all
                                complete)
                              enum:
                                - text
                                - first
                                - complete
                            task_id:
                              type: string
                              description: Task ID
                            data:
                              type: array
                              items:
                                type: object
                                properties:
                                  id:
                                    type: string
                                    description: Audio unique identifier (audioId)
                                  audio_url:
                                    type: string
                                    description: Audio file URL
                                  stream_audio_url:
                                    type: string
                                    description: Streaming audio URL
                                  image_url:
                                    type: string
                                    description: Cover image URL
                                  prompt:
                                    type: string
                                    description: Generation prompt/lyrics
                                  model_name:
                                    type: string
                                    description: Model name used
                                  title:
                                    type: string
                                    description: Music title
                                  tags:
                                    type: string
                                    description: Music tags
                                  createTime:
                                    type: string
                                    description: Creation time
                                    format: date-time
                                  duration:
                                    type: number
                                    description: Audio duration (seconds)
              responses:
                '200':
                  description: Callback received successfully
                  content:
                    application/json:
                      schema:
                        allOf:
                          - type: object
                            properties:
                              code:
                                type: integer
                                enum:
                                  - 200
                                  - 400
                                  - 408
                                  - 413
                                  - 500
                                  - 501
                                  - 531
                                description: >-
                                  Response status code


                                  - **200**: Success - Request processed
                                  successfully

                                  - **400**: Validation error - Lyrics contain
                                  copyrighted content.

                                  - **408**: Rate limit exceeded - Timeout.

                                  - **413**: Conflict - Uploaded audio matches
                                  existing artwork.

                                  - **500**: Server error - Unexpected error
                                  occurred while processing request

                                  - **501**: Audio generation failed.

                                  - **531**: Server error - Sorry, generation
                                  failed due to issues. Your credits have been
                                  refunded. Please try again.
                              msg:
                                type: string
                                description: Error message when code != 200
                                example: success
                      example:
                        code: 200
                        msg: success
components:
  responses:
    Error:
      description: Server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        # 🔑 API Authentication


        All endpoints require authentication using Bearer Token.


        ## Get API Key


        1. Visit the [API Key Management Page](https://sunoapi.org/api-key) to
        obtain your API Key


        ## Usage


        Add to request headers:


        ```

        Authorization: Bearer YOUR_API_KEY

        ```


        > **⚠️ Note:**

        > - Keep your API Key secure and do not share it with others

        > - If you suspect your API Key has been compromised, reset it
        immediately from the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt


# Get Music Cover Details

> Get detailed information about music cover generation tasks.

## OpenAPI

````yaml suno-api/suno-api.json get /api/v1/suno/cover/record-info
openapi: 3.0.0
info:
  title: intro
  description: API documentation for audio generation services
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://api.sunoapi.org
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: Music Generation
    description: Endpoints for creating and managing music generation tasks
  - name: Lyrics Generation
    description: Endpoints for lyrics generation and management
  - name: WAV Conversion
    description: Endpoints for converting music to WAV format
  - name: Vocal Removal
    description: Endpoints for vocal removal from music tracks
  - name: Music Video Generation
    description: Endpoints for generating MP4 videos from music tracks
  - name: Account Management
    description: Endpoints for account and credits management
paths:
  /api/v1/suno/cover/record-info:
    get:
      summary: Get Cover Generation Details
      description: >-
        Get detailed information about Cover generation tasks.


        ### Usage Guide

        - Use this interface to check Cover generation task status

        - Access generated cover image URLs upon completion

        - Track processing progress and any errors that may occur


        ### Status Description

        - `0`: 待执行 (Pending)

        - `1`: 成功 (Success)

        - `2`: 生成中 (Generating)

        - `3`: 生成失败 (Generation failed)


        ### Developer Notes

        - Cover image URLs are only available when status is `SUCCESS` in the
        response

        - Error codes and messages are provided for failed tasks

        - After successful generation, cover images are retained for 14 days
      operationId: get-cover-details
      parameters:
        - in: query
          name: taskId
          description: >-
            Unique identifier of the Cover generation task to retrieve. This is
            the taskId returned when creating the Cover generation task.
          required: true
          example: 21aee3c3c2a01fa5e030b3799fa4dd56
          schema:
            type: string
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                allOf:
                  - type: object
                    properties:
                      code:
                        type: integer
                        enum:
                          - 200
                          - 400
                          - 401
                          - 402
                          - 404
                          - 409
                          - 422
                          - 429
                          - 455
                          - 500
                        description: >-
                          Response status code


                          - **200**: Success - Request processed successfully

                          - **400**: Format error - Parameters are not in valid
                          JSON format

                          - **401**: Unauthorized - Authentication credentials
                          missing or invalid

                          - **402**: Insufficient credits - Account doesn't have
                          enough credits for this operation

                          - **404**: Not found - Requested resource or endpoint
                          doesn't exist

                          - **409**: Conflict - Cover record already exists

                          - **422**: Validation error - Request parameters
                          failed validation checks

                          - **429**: Rate limited - Request rate limit exceeded
                          for this resource

                          - **455**: Service unavailable - System currently
                          undergoing maintenance

                          - **500**: Server error - Unexpected error occurred
                          while processing request
                      msg:
                        type: string
                        description: Error message when code != 200
                        example: success
                type: object
                properties:
                  code:
                    type: integer
                    format: int32
                    description: Status code
                    example: 200
                  msg:
                    type: string
                    description: Status message
                    example: success
                  data:
                    type: object
                    properties:
                      taskId:
                        type: string
                        description: Task ID
                        example: 21aee3c3c2a01fa5e030b3799fa4dd56
                      parentTaskId:
                        type: string
                        description: Original music task ID
                        example: 73d6128b3523a0079df10da9471017c8
                      callbackUrl:
                        type: string
                        description: Callback URL
                        example: https://api.example.com/callback
                      completeTime:
                        type: string
                        format: date-time
                        description: Completion callback time
                        example: '2025-01-15T10:35:27.000Z'
                      response:
                        type: object
                        description: Completion callback result
                        properties:
                          images:
                            type: array
                            items:
                              type: string
                            description: Cover image URL array
                            example:
                              - >-
                                https://tempfile.aiquickdraw.com/s/1753958521_6c1b3015141849d1a9bf17b738ce9347.png
                              - >-
                                https://tempfile.aiquickdraw.com/s/1753958524_c153143acc6340908431cf0e90cbce9e.png
                      successFlag:
                        type: integer
                        description: >-
                          Task status flag: 0-Pending, 1-Success, 2-Generating,
                          3-Generation failed
                        enum:
                          - 0
                          - 1
                          - 2
                          - 3
                        example: 1
                      createTime:
                        type: string
                        format: date-time
                        description: Creation time
                        example: '2025-01-15T10:33:01.000Z'
                      errorCode:
                        type: integer
                        format: int32
                        description: |-
                          Error code

                          - **200**: Success - Request processed successfully
                          - **500**: Internal error - Please try again later.
                        example: 200
                        enum:
                          - 200
                          - 500
                      errorMessage:
                        type: string
                        description: Error message
                        example: ''
              example:
                code: 200
                msg: success
                data:
                  taskId: 21aee3c3c2a01fa5e030b3799fa4dd56
                  parentTaskId: 73d6128b3523a0079df10da9471017c8
                  callbackUrl: https://api.example.com/callback
                  completeTime: '2025-01-15T10:35:27.000Z'
                  response:
                    images:
                      - >-
                        https://tempfile.aiquickdraw.com/s/1753958521_6c1b3015141849d1a9bf17b738ce9347.png
                      - >-
                        https://tempfile.aiquickdraw.com/s/1753958524_c153143acc6340908431cf0e90cbce9e.png
                  successFlag: 1
                  createTime: '2025-01-15T10:33:01.000Z'
                  errorCode: 200
                  errorMessage: ''
        '500':
          $ref: '#/components/responses/Error'
components:
  responses:
    Error:
      description: Server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        # 🔑 API Authentication


        All endpoints require authentication using Bearer Token.


        ## Get API Key


        1. Visit the [API Key Management Page](https://sunoapi.org/api-key) to
        obtain your API Key


        ## Usage


        Add to request headers:


        ```

        Authorization: Bearer YOUR_API_KEY

        ```


        > **⚠️ Note:**

        > - Keep your API Key secure and do not share it with others

        > - If you suspect your API Key has been compromised, reset it
        immediately from the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt


# Generate Persona

> Create a personalized music Persona based on generated music, giving the music a unique identity and characteristics.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/generate/generate-persona
openapi: 3.0.0
info:
  title: intro
  description: API documentation for audio generation services
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://api.sunoapi.org
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: Music Generation
    description: Endpoints for creating and managing music generation tasks
  - name: Lyrics Generation
    description: Endpoints for lyrics generation and management
  - name: WAV Conversion
    description: Endpoints for converting music to WAV format
  - name: Vocal Removal
    description: Endpoints for vocal removal from music tracks
  - name: Music Video Generation
    description: Endpoints for generating MP4 videos from music tracks
  - name: Account Management
    description: Endpoints for account and credits management
paths:
  /api/v1/generate/generate-persona:
    post:
      tags:
        - Music Generation
      summary: Generate Persona
      description: >-
        Create a personalized music Persona based on generated music, giving the
        music a unique identity and characteristics.


        ### Usage Guide

        - Use this endpoint to create Personas (music characters) for generated
        music

        - Requires the taskId from music generation related endpoints (generate,
        extend, cover, upload-extend) and audio ID

        - Customize the Persona name and description to give music unique
        personality

        - Generated Personas can be used for subsequent music creation and style
        transfer


        ### Parameter Details

        - `taskId`: Required parameter, can be obtained from the following
        endpoints:
          - Generate Music (/api/v1/generate)
          - Extend Music (/api/v1/generate/extend)
          - Upload And Cover Audio (/api/v1/generate/upload-cover)
          - Upload And Extend Audio (/api/v1/generate/upload-extend)
        - `audioId`: Required parameter, specifies the audio ID to create
        Persona for

        - `name`: Required parameter, assigns an easily recognizable name to the
        Persona

        - `description`: Required parameter, describes the musical
        characteristics, style, and personality of the Persona


        ### Developer Notes

        - **Important**: Ensure the music generation task is fully completed
        before calling this endpoint. If the music is still generating, this
        endpoint will return a failure

        - **Model Requirement**: Persona generation only supports taskId from
        music generated with models above v3_5 (v3_5 itself is not supported)

        - Recommend providing detailed descriptions for Personas to better
        capture musical characteristics

        - The returned `personaId` can be used in subsequent music generation
        requests to create music with similar style characteristics

        - You can apply the `personaId` to the following endpoints: Generate
        Music, Extend Music, Upload And Cover Audio, Upload And Extend Audio

        - Each audio ID can only generate one Persona
      operationId: generate-persona
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - taskId
                - audioId
                - name
                - description
              properties:
                taskId:
                  type: string
                  description: >-
                    Unique identifier of the original music generation task.
                    This can be a taskId returned from any of the following
                    endpoints:

                    - Generate Music (/api/v1/generate)

                    - Extend Music (/api/v1/generate/extend)

                    - Upload And Cover Audio (/api/v1/generate/upload-cover)

                    - Upload And Extend Audio (/api/v1/generate/upload-extend)
                  example: 5c79****be8e
                audioId:
                  type: string
                  description: Audio ID of the music track to create Persona for.
                  example: e231****-****-****-****-****8cadc7dc
                name:
                  type: string
                  description: >-
                    Name for the Persona. A descriptive name that captures the
                    essence of the musical style or character.
                  example: Electronic Pop Singer
                description:
                  type: string
                  description: >-
                    Detailed description of the Persona's musical
                    characteristics, style, and personality. Be specific about
                    genre, mood, instrumentation, and vocal qualities.
                  example: >-
                    A modern electronic music style pop singer, skilled in
                    dynamic rhythms and synthesizer tones
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - type: object
                    properties:
                      code:
                        type: integer
                        enum:
                          - 200
                          - 401
                          - 402
                          - 404
                          - 409
                          - 422
                          - 429
                          - 451
                          - 455
                          - 500
                        description: >-
                          Response Status Codes


                          - **200**: Success - Request has been processed
                          successfully  

                          - **401**: Unauthorized - Authentication credentials
                          are missing or invalid  

                          - **402**: Insufficient Credits - Account does not
                          have enough credits to perform the operation  

                          - **404**: Not Found - The requested resource or
                          endpoint does not exist  

                          - **409**: Conflict - Persona already exists for this
                          music

                          - **422**: Validation Error - The request parameters
                          failed validation checks  

                          - **429**: Rate Limited - Request limit has been
                          exceeded for this resource  

                          - **451**: Unauthorized - Failed to fetch the music
                          data. Kindly verify any access limits set by you or
                          your service provider  

                          - **455**: Service Unavailable - System is currently
                          undergoing maintenance  

                          - **500**: Server Error - An unexpected error occurred
                          while processing the request
                      msg:
                        type: string
                        description: Error message when code != 200
                        example: success
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          personaId:
                            type: string
                            description: >-
                              Unique identifier for the generated Persona. This
                              personaId can be used in subsequent music
                              generation requests (Generate Music, Extend Music,
                              Upload And Cover Audio, Upload And Extend Audio)
                              to create music with similar style
                              characteristics.
                            example: a1b2****c3d4
                          name:
                            type: string
                            description: Name of the Persona as provided in the request.
                            example: Electronic Pop Singer
                          description:
                            type: string
                            description: >-
                              Description of the Persona's musical
                              characteristics, style, and personality as
                              provided in the request.
                            example: >-
                              A modern electronic music style pop singer,
                              skilled in dynamic rhythms and synthesizer tones
        '500':
          $ref: '#/components/responses/Error'
components:
  responses:
    Error:
      description: Server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        # 🔑 API Authentication


        All endpoints require authentication using Bearer Token.


        ## Get API Key


        1. Visit the [API Key Management Page](https://sunoapi.org/api-key) to
        obtain your API Key


        ## Usage


        Add to request headers:


        ```

        Authorization: Bearer YOUR_API_KEY

        ```


        > **⚠️ Note:**

        > - Keep your API Key secure and do not share it with others

        > - If you suspect your API Key has been compromised, reset it
        immediately from the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt


# Generate Lyrics

> Create lyrics for music using AI models without generating audio tracks.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/lyrics
openapi: 3.0.0
info:
  title: intro
  description: API documentation for audio generation services
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://api.sunoapi.org
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: Music Generation
    description: Endpoints for creating and managing music generation tasks
  - name: Lyrics Generation
    description: Endpoints for lyrics generation and management
  - name: WAV Conversion
    description: Endpoints for converting music to WAV format
  - name: Vocal Removal
    description: Endpoints for vocal removal from music tracks
  - name: Music Video Generation
    description: Endpoints for generating MP4 videos from music tracks
  - name: Account Management
    description: Endpoints for account and credits management
paths:
  /api/v1/lyrics:
    post:
      summary: Generate Lyrics
      operationId: generate-lyrics
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - prompt
                - callBackUrl
              properties:
                prompt:
                  type: string
                  description: >-
                    Detailed description of the desired lyrics content.  

                    - Be specific about themes, moods, styles, and song
                    structure you want.  

                    - The more detailed your prompt, the more closely the
                    generated lyrics will match your vision.  

                    - The maximum word limit is 200 words.
                  example: A song about peaceful night in the city
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive lyrics generation results when
                    complete.  

                    - Required.  

                    - Unlike music generation, lyrics callback has only one
                    stage: `complete` (generation finished).


                    For detailed callback format and implementation guide, see
                    [Lyrics Generation
                    Callbacks](https://docs.sunoapi.org/suno-api/generate-lyrics-callbacks)

                    - Alternatively, you can use the get lyrics generation
                    details endpoint to poll task status
                  example: https://api.example.com/callback
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/ApiResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: Task ID for tracking task status
                            example: 5c79****be8e
        '500':
          $ref: '#/components/responses/Error'
      callbacks:
        audioLyricsGenerated:
          '{$request.body#/callBackUrl}':
            post:
              description: >-
                System will call this callback when lyrics generation is
                complete.


                ### Callback Example

                ```json

                {
                  "code": 200,
                  "msg": "All generated successfully.",
                  "data": {
                    "callbackType": "complete",
                    "taskId": "11dc****8b0f",
                    "data": [
                      {
                        "text": "[Verse]\n我穿越城市黑暗夜\n心中燃烧梦想的烈火",
                        "title": "钢铁侠",
                        "status": "complete",
                        "errorMessage": ""
                      },
                      {
                        "text": "[Verse]\n风在呼唤我名字\n钢铁盔甲闪得刺眼",
                        "title": "钢铁侠",
                        "status": "complete",
                        "errorMessage": ""
                      }
                    ]
                  }
                }

                ```
              requestBody:
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        code:
                          type: integer
                          description: Status code
                          example: 200
                        msg:
                          type: string
                          description: Response message
                          example: All generated successfully
                        data:
                          type: object
                          properties:
                            callbackType:
                              type: string
                              description: Callback type, fixed as complete
                              enum:
                                - complete
                              example: complete
                            taskId:
                              type: string
                              description: Task ID
                            data:
                              type: array
                              description: Generated lyrics list
                              items:
                                type: object
                                properties:
                                  text:
                                    type: string
                                    description: Lyrics content
                                  title:
                                    type: string
                                    description: Lyrics title
                                  status:
                                    type: string
                                    description: Generation status
                                    enum:
                                      - complete
                                      - failed
                                  errorMessage:
                                    type: string
                                    description: Error message, valid when status is failed
              responses:
                '200':
                  description: Callback received successfully
components:
  schemas:
    ApiResponse:
      type: object
      properties:
        code:
          type: integer
          description: |-
            # Status Codes

            - ✅ 200 - Request successful
            - ⚠️ 400 - Invalid parameters
            - ⚠️ 401 - Unauthorized access
            - ⚠️ 404 - Invalid request method or path
            - ⚠️ 405 - Rate limit exceeded
            - ⚠️ 413 - Theme or prompt too long
            - ⚠️ 429 - Insufficient credits
            - ⚠️ 430 - Your call frequency is too high. Please try again later. 
            - ⚠️ 455 - System maintenance
            - ❌ 500 - Server error
          example: 200
          enum:
            - 200
            - 400
            - 401
            - 404
            - 405
            - 413
            - 429
            - 430
            - 455
            - 500
        msg:
          type: string
          description: Error message when code != 200
          example: success
  responses:
    Error:
      description: Server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        # 🔑 API Authentication


        All endpoints require authentication using Bearer Token.


        ## Get API Key


        1. Visit the [API Key Management Page](https://sunoapi.org/api-key) to
        obtain your API Key


        ## Usage


        Add to request headers:


        ```

        Authorization: Bearer YOUR_API_KEY

        ```


        > **⚠️ Note:**

        > - Keep your API Key secure and do not share it with others

        > - If you suspect your API Key has been compromised, reset it
        immediately from the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt


# Get Lyrics Generation Details

> Retrieve detailed information about a lyrics generation task, including status, parameters, and results.

## OpenAPI

````yaml suno-api/suno-api.json get /api/v1/lyrics/record-info
openapi: 3.0.0
info:
  title: intro
  description: API documentation for audio generation services
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://api.sunoapi.org
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: Music Generation
    description: Endpoints for creating and managing music generation tasks
  - name: Lyrics Generation
    description: Endpoints for lyrics generation and management
  - name: WAV Conversion
    description: Endpoints for converting music to WAV format
  - name: Vocal Removal
    description: Endpoints for vocal removal from music tracks
  - name: Music Video Generation
    description: Endpoints for generating MP4 videos from music tracks
  - name: Account Management
    description: Endpoints for account and credits management
paths:
  /api/v1/lyrics/record-info:
    get:
      summary: Get Lyrics Generation Details
      operationId: get-lyrics-generation-details
      parameters:
        - in: query
          name: taskId
          description: >-
            The task ID returned from the Generate Lyrics endpoint. Used to
            retrieve detailed information about a specific lyrics generation
            task.
          required: true
          example: 11dc****8b0f
          schema:
            type: string
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/ApiResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: Task ID
                          param:
                            type: string
                            description: Parameter information for task generation
                          response:
                            type: object
                            properties:
                              taskId:
                                type: string
                                description: Task ID
                              data:
                                type: array
                                items:
                                  type: object
                                  properties:
                                    text:
                                      type: string
                                      description: Lyrics content
                                    title:
                                      type: string
                                      description: Lyrics title
                                    status:
                                      type: string
                                      description: Generation status
                                      enum:
                                        - complete
                                        - failed
                                    errorMessage:
                                      type: string
                                      description: >-
                                        Error message, valid when status is
                                        failed
                          status:
                            type: string
                            description: Task status
                            enum:
                              - PENDING
                              - SUCCESS
                              - CREATE_TASK_FAILED
                              - GENERATE_LYRICS_FAILED
                              - CALLBACK_EXCEPTION
                              - SENSITIVE_WORD_ERROR
                          type:
                            type: string
                            description: Task type
                            example: LYRICS
                          errorCode:
                            type: number
                            description: Error code, valid when task fails
                          errorMessage:
                            type: string
                            description: Error message, valid when task fails
              example:
                code: 200
                msg: success
                data:
                  taskId: 11dc****8b0f
                  param: '{"prompt":"A song about peaceful night in the city"}'
                  response:
                    taskId: 11dc****8b0f
                    data:
                      - text: |-
                          [Verse]
                          我穿越城市黑暗夜
                          心中燃烧梦想的烈火
                        title: 钢铁侠
                        status: complete
                        errorMessage: ''
                  status: SUCCESS
                  type: LYRICS
                  errorCode: null
                  errorMessage: null
        '500':
          $ref: '#/components/responses/Error'
components:
  schemas:
    ApiResponse:
      type: object
      properties:
        code:
          type: integer
          description: |-
            # Status Codes

            - ✅ 200 - Request successful
            - ⚠️ 400 - Invalid parameters
            - ⚠️ 401 - Unauthorized access
            - ⚠️ 404 - Invalid request method or path
            - ⚠️ 405 - Rate limit exceeded
            - ⚠️ 413 - Theme or prompt too long
            - ⚠️ 429 - Insufficient credits
            - ⚠️ 430 - Your call frequency is too high. Please try again later. 
            - ⚠️ 455 - System maintenance
            - ❌ 500 - Server error
          example: 200
          enum:
            - 200
            - 400
            - 401
            - 404
            - 405
            - 413
            - 429
            - 430
            - 455
            - 500
        msg:
          type: string
          description: Error message when code != 200
          example: success
  responses:
    Error:
      description: Server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        # 🔑 API Authentication


        All endpoints require authentication using Bearer Token.


        ## Get API Key


        1. Visit the [API Key Management Page](https://sunoapi.org/api-key) to
        obtain your API Key


        ## Usage


        Add to request headers:


        ```

        Authorization: Bearer YOUR_API_KEY

        ```


        > **⚠️ Note:**

        > - Keep your API Key secure and do not share it with others

        > - If you suspect your API Key has been compromised, reset it
        immediately from the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt


# Convert to WAV Format

> Convert existing music tracks to high-quality WAV format.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/wav/generate
openapi: 3.0.0
info:
  title: intro
  description: API documentation for audio generation services
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://api.sunoapi.org
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: Music Generation
    description: Endpoints for creating and managing music generation tasks
  - name: Lyrics Generation
    description: Endpoints for lyrics generation and management
  - name: WAV Conversion
    description: Endpoints for converting music to WAV format
  - name: Vocal Removal
    description: Endpoints for vocal removal from music tracks
  - name: Music Video Generation
    description: Endpoints for generating MP4 videos from music tracks
  - name: Account Management
    description: Endpoints for account and credits management
paths:
  /api/v1/wav/generate:
    post:
      summary: Convert to WAV Format
      operationId: convert-to-wav-format
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - taskId
                - audioId
                - callBackUrl
              properties:
                taskId:
                  type: string
                  description: 'The task ID of the music generation task. '
                  example: 5c79****be8e
                audioId:
                  type: string
                  description: >-
                    The audio ID of the specific track to convert.  

                    - Providing the specific `audioId` ensures the exact track
                    is converted, especially when a task has multiple tracks.
                  example: e231****-****-****-****-****8cadc7dc
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive WAV conversion completion notification.  

                    - Required.  

                    - The callback includes a single download URL for the
                    converted WAV file.


                    For detailed callback format and implementation guide, see
                    [WAV Format Conversion
                    Callbacks](https://docs.sunoapi.org/suno-api/convert-to-wav-format-callbacks)

                    - Alternatively, you can use the get WAV conversion details
                    endpoint to poll task status
                  example: https://api.example.com/callback
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - type: object
                    properties:
                      code:
                        type: integer
                        enum:
                          - 200
                          - 400
                          - 401
                          - 404
                          - 405
                          - 409
                          - 413
                          - 429
                          - 430
                          - 455
                          - 500
                        description: >-
                          # Status Codes


                          - ✅ 200 - Request successful

                          - ⚠️ 400 - Invalid parameters

                          - ⚠️ 401 - Unauthorized access

                          - ⚠️ 404 - Invalid request method or path

                          - ⚠️ 405 - Rate limit exceeded

                          - ⚠️ 409 - Conflict - WAV record already exists

                          - ⚠️ 413 - Theme or prompt too long

                          - ⚠️ 429 - Insufficient credits

                          - ⚠️ 430 - Your call frequency is too high. Please try
                          again later. 

                          - ⚠️ 455 - System maintenance

                          - ❌ 500 - Server error
                      msg:
                        type: string
                        description: Error message when code != 200
                        example: success
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: Task ID for tracking task status
                            example: 5c79****be8e
        '500':
          $ref: '#/components/responses/Error'
      callbacks:
        wavGenerated:
          '{$request.body#/callBackUrl}':
            post:
              description: >-
                System will call this callback when WAV format audio generation
                is complete.


                ### Callback Example

                ```json

                {
                  "code": 200,
                  "msg": "success",
                  "data": {
                    "audioWavUrl": "https://example.com/s/04e6****e727.wav",
                    "task_id": "988e****c8d3"
                  }
                }

                ```
              requestBody:
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        code:
                          type: integer
                          description: Status code
                          example: 200
                        msg:
                          type: string
                          description: Response message
                          example: success
                        data:
                          type: object
                          properties:
                            task_id:
                              type: string
                              description: Task ID
                            audioWavUrl:
                              type: string
                              description: WAV format audio file URL
              responses:
                '200':
                  description: Callback received successfully
components:
  responses:
    Error:
      description: Server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        # 🔑 API Authentication


        All endpoints require authentication using Bearer Token.


        ## Get API Key


        1. Visit the [API Key Management Page](https://sunoapi.org/api-key) to
        obtain your API Key


        ## Usage


        Add to request headers:


        ```

        Authorization: Bearer YOUR_API_KEY

        ```


        > **⚠️ Note:**

        > - Keep your API Key secure and do not share it with others

        > - If you suspect your API Key has been compromised, reset it
        immediately from the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt


# Get WAV Conversion Details

> Retrieve detailed information about a WAV format conversion task, including status and download link.

## OpenAPI

````yaml suno-api/suno-api.json get /api/v1/wav/record-info
openapi: 3.0.0
info:
  title: intro
  description: API documentation for audio generation services
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://api.sunoapi.org
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: Music Generation
    description: Endpoints for creating and managing music generation tasks
  - name: Lyrics Generation
    description: Endpoints for lyrics generation and management
  - name: WAV Conversion
    description: Endpoints for converting music to WAV format
  - name: Vocal Removal
    description: Endpoints for vocal removal from music tracks
  - name: Music Video Generation
    description: Endpoints for generating MP4 videos from music tracks
  - name: Account Management
    description: Endpoints for account and credits management
paths:
  /api/v1/wav/record-info:
    get:
      summary: Get WAV Conversion Details
      operationId: get-wav-conversion-details
      parameters:
        - in: query
          name: taskId
          description: >-
            The task ID returned from the Convert to WAV Format endpoint. Used
            to retrieve details about the conversion process, including status
            and download URL if available.
          required: true
          example: 988e****c8d3
          schema:
            type: string
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - type: object
                    properties:
                      code:
                        type: integer
                        enum:
                          - 200
                          - 400
                          - 401
                          - 404
                          - 405
                          - 409
                          - 413
                          - 429
                          - 430
                          - 455
                          - 500
                        description: >-
                          # Status Codes


                          - ✅ 200 - Request successful

                          - ⚠️ 400 - Invalid parameters

                          - ⚠️ 401 - Unauthorized access

                          - ⚠️ 404 - Invalid request method or path

                          - ⚠️ 405 - Rate limit exceeded

                          - ⚠️ 409 - Conflict - WAV record already exists

                          - ⚠️ 413 - Theme or prompt too long

                          - ⚠️ 429 - Insufficient credits

                          - ⚠️ 430 - Your call frequency is too high. Please try
                          again later. 

                          - ⚠️ 455 - System maintenance

                          - ❌ 500 - Server error
                      msg:
                        type: string
                        description: Error message when code != 200
                        example: success
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: Task ID
                          musicId:
                            type: string
                            description: >-
                              The ID of the source music track that was
                              converted to WAV format
                          callbackUrl:
                            type: string
                            description: >-
                              The callback URL that was provided in the
                              conversion request
                          completeTime:
                            type: string
                            description: The timestamp when the conversion was completed
                            format: date-time
                          response:
                            type: object
                            properties:
                              audioWavUrl:
                                type: string
                                description: WAV format audio file URL
                          successFlag:
                            type: string
                            description: Task status
                            enum:
                              - PENDING
                              - SUCCESS
                              - CREATE_TASK_FAILED
                              - GENERATE_WAV_FAILED
                              - CALLBACK_EXCEPTION
                          createTime:
                            type: string
                            description: Creation time
                            format: date-time
                          errorCode:
                            type: number
                            description: Error code, valid when task fails
                          errorMessage:
                            type: string
                            description: Error message, valid when task fails
              example:
                code: 200
                msg: success
                data:
                  taskId: 988e****c8d3
                  musicId: 8551****662c
                  callbackUrl: https://api.example.com/callback
                  completeTime: '2025-01-01 00:10:00'
                  response:
                    audioWavUrl: https://example.com/s/04e6****e727.wav
                  successFlag: SUCCESS
                  createTime: '2025-01-01 00:00:00'
                  errorCode: null
                  errorMessage: null
        '500':
          $ref: '#/components/responses/Error'
components:
  responses:
    Error:
      description: Server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        # 🔑 API Authentication


        All endpoints require authentication using Bearer Token.


        ## Get API Key


        1. Visit the [API Key Management Page](https://sunoapi.org/api-key) to
        obtain your API Key


        ## Usage


        Add to request headers:


        ```

        Authorization: Bearer YOUR_API_KEY

        ```


        > **⚠️ Note:**

        > - Keep your API Key secure and do not share it with others

        > - If you suspect your API Key has been compromised, reset it
        immediately from the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt


# Vocal & Instrument Stem Separation

> Use Suno’s official get‑stem API to split tracks created on our platform into clean vocal, accompaniment, or per‑instrument stems with state‑of‑the‑art source‑separation AI.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/vocal-removal/generate
openapi: 3.0.0
info:
  title: intro
  description: API documentation for audio generation services
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://api.sunoapi.org
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: Music Generation
    description: Endpoints for creating and managing music generation tasks
  - name: Lyrics Generation
    description: Endpoints for lyrics generation and management
  - name: WAV Conversion
    description: Endpoints for converting music to WAV format
  - name: Vocal Removal
    description: Endpoints for vocal removal from music tracks
  - name: Music Video Generation
    description: Endpoints for generating MP4 videos from music tracks
  - name: Account Management
    description: Endpoints for account and credits management
paths:
  /api/v1/vocal-removal/generate:
    post:
      summary: Separate Vocals from Music
      operationId: separate-vocals-from-music
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - taskId
                - audioId
                - callBackUrl
              properties:
                taskId:
                  type: string
                  description: >-
                    The task ID of the music generation task.  

                    - Required. This identifies the task containing the audio to
                    be processed.  

                    - Both `taskId` and `audioId` are needed for accurate track
                    identification.
                  example: 5c79****be8e
                audioId:
                  type: string
                  description: >-
                    The ID of the specific audio track to separate.  

                    - Required. This identifies which specific track within the
                    task to process.  

                    - Both `taskId` and `audioId` are needed for accurate track
                    identification.
                  example: e231****-****-****-****-****8cadc7dc
                type:
                  type: string
                  description: >-
                    Separation type.  

                    - `separate_vocal`: Separate vocals and accompaniment,
                    generating vocal track and instrumental track (default)  

                    - `split_stem`: Separate various instrument sounds,
                    generating vocals, backing vocals, drums, bass, guitar,
                    keyboard, strings, brass, woodwinds, percussion,
                    synthesizer, effects and other tracks
                  enum:
                    - separate_vocal
                    - split_stem
                  default: separate_vocal
                  example: separate_vocal
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive vocal separation results when processing
                    is complete.  

                    - Required.  

                    - The callback will include multiple URLs: original audio,
                    isolated vocals, instrumental track, and individual
                    instrument tracks.


                    For detailed callback format and implementation guide, see
                    [Vocal Separation
                    Callbacks](https://docs.sunoapi.org/suno-api/separate-vocals-from-music-callbacks)

                    - Alternatively, you can use the get vocal separation
                    details endpoint to poll task status
                  example: https://api.example.com/callback
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/ApiResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: Task ID for tracking task status
                            example: 5c79****be8e
        '500':
          $ref: '#/components/responses/Error'
      callbacks:
        vocalRemovalGenerated:
          '{$request.body#/callBackUrl}':
            post:
              description: |-
                System will call this callback when vocal removal is complete.

                ### separate_vocal type callback example
                ```json
                {
                  "code": 200,
                  "data": {
                    "task_id": "3e63b4cc88d52611159371f6af5571e7",
                    "vocal_removal_info": {
                      "instrumental_url": "https://file.aiquickdraw.com/s/d92a13bf-c6f4-4ade-bb47-f69738435528_Instrumental.mp3",
                      "origin_url": "",
                      "vocal_url": "https://file.aiquickdraw.com/s/3d7021c9-fa8b-4eda-91d1-3b9297ddb172_Vocals.mp3"
                    }
                  },
                  "msg": "vocal Removal generated successfully."
                }
                ```

                ### split_stem type callback example
                ```json
                {
                  "code": 200,
                  "data": {
                    "task_id": "e649edb7abfd759285bd41a47a634b10",
                    "vocal_removal_info": {
                      "origin_url": "",
                      "backing_vocals_url": "https://file.aiquickdraw.com/s/aadc51a3-4c88-4c8e-a4c8-e867c539673d_Backing_Vocals.mp3",
                      "bass_url": "https://file.aiquickdraw.com/s/a3c2da5a-b364-4422-adb5-2692b9c26d33_Bass.mp3",
                      "brass_url": "https://file.aiquickdraw.com/s/334b2d23-0c65-4a04-92c7-22f828afdd44_Brass.mp3",
                      "drums_url": "https://file.aiquickdraw.com/s/ac75c5ea-ac77-4ad2-b7d9-66e140b78e44_Drums.mp3",
                      "fx_url": "https://file.aiquickdraw.com/s/a8822c73-6629-4089-8f2a-d19f41f0007d_FX.mp3",
                      "guitar_url": "https://file.aiquickdraw.com/s/064dd08e-d5d2-4201-9058-c5c40fb695b4_Guitar.mp3",
                      "keyboard_url": "https://file.aiquickdraw.com/s/adc934e0-df7d-45da-8220-1dba160d74e0_Keyboard.mp3",
                      "percussion_url": "https://file.aiquickdraw.com/s/0f70884d-047c-41f1-a6d0-7044618b7dc6_Percussion.mp3",
                      "strings_url": "https://file.aiquickdraw.com/s/49829425-a5b0-424e-857a-75d4c63a426b_Strings.mp3",
                      "synth_url": "https://file.aiquickdraw.com/s/56b2d94a-eb92-4d21-bc43-3460de0c8348_Synth.mp3",
                      "vocal_url": "https://file.aiquickdraw.com/s/07420749-29a2-4054-9b62-e6a6f8b90ccb_Vocals.mp3",
                      "woodwinds_url": "https://file.aiquickdraw.com/s/d81545b1-6f94-4388-9785-1aaa6ecabb02_Woodwinds.mp3"
                    }
                  },
                  "msg": "vocal Removal generated successfully."
                }
                ```
              requestBody:
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        code:
                          type: integer
                          description: Status code
                          example: 200
                        msg:
                          type: string
                          description: Response message
                          example: vocal Removal generated successfully.
                        data:
                          type: object
                          properties:
                            task_id:
                              type: string
                              description: Task ID
                            vocal_removal_info:
                              type: object
                              properties:
                                instrumental_url:
                                  type: string
                                  description: >-
                                    Instrumental part audio URL (exists for
                                    separate_vocal type)
                                origin_url:
                                  type: string
                                  description: Original audio URL
                                vocal_url:
                                  type: string
                                  description: Vocal part audio URL
                                backing_vocals_url:
                                  type: string
                                  description: >-
                                    Backing vocals part audio URL (exists for
                                    split_stem type)
                                drums_url:
                                  type: string
                                  description: Drums part audio URL
                                bass_url:
                                  type: string
                                  description: Bass part audio URL
                                guitar_url:
                                  type: string
                                  description: Guitar part audio URL
                                keyboard_url:
                                  type: string
                                  description: >-
                                    Keyboard part audio URL (exists for
                                    split_stem type)
                                percussion_url:
                                  type: string
                                  description: >-
                                    Percussion part audio URL (exists for
                                    split_stem type)
                                strings_url:
                                  type: string
                                  description: >-
                                    Strings part audio URL (exists for
                                    split_stem type)
                                synth_url:
                                  type: string
                                  description: >-
                                    Synthesizer part audio URL (exists for
                                    split_stem type)
                                fx_url:
                                  type: string
                                  description: >-
                                    Effects part audio URL (exists for
                                    split_stem type)
                                brass_url:
                                  type: string
                                  description: >-
                                    Brass part audio URL (exists for split_stem
                                    type)
                                woodwinds_url:
                                  type: string
                                  description: >-
                                    Woodwinds part audio URL (exists for
                                    split_stem type)
              responses:
                '200':
                  description: Callback received successfully
components:
  schemas:
    ApiResponse:
      type: object
      properties:
        code:
          type: integer
          description: |-
            # Status Codes

            - ✅ 200 - Request successful
            - ⚠️ 400 - Invalid parameters
            - ⚠️ 401 - Unauthorized access
            - ⚠️ 404 - Invalid request method or path
            - ⚠️ 405 - Rate limit exceeded
            - ⚠️ 413 - Theme or prompt too long
            - ⚠️ 429 - Insufficient credits
            - ⚠️ 430 - Your call frequency is too high. Please try again later. 
            - ⚠️ 455 - System maintenance
            - ❌ 500 - Server error
          example: 200
          enum:
            - 200
            - 400
            - 401
            - 404
            - 405
            - 413
            - 429
            - 430
            - 455
            - 500
        msg:
          type: string
          description: Error message when code != 200
          example: success
  responses:
    Error:
      description: Server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        # 🔑 API Authentication


        All endpoints require authentication using Bearer Token.


        ## Get API Key


        1. Visit the [API Key Management Page](https://sunoapi.org/api-key) to
        obtain your API Key


        ## Usage


        Add to request headers:


        ```

        Authorization: Bearer YOUR_API_KEY

        ```


        > **⚠️ Note:**

        > - Keep your API Key secure and do not share it with others

        > - If you suspect your API Key has been compromised, reset it
        immediately from the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt


# Get Audio Separation Details

> Retrieve detailed information about a vocal separation task, including status and download links.

## OpenAPI

````yaml suno-api/suno-api.json get /api/v1/vocal-removal/record-info
openapi: 3.0.0
info:
  title: intro
  description: API documentation for audio generation services
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://api.sunoapi.org
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: Music Generation
    description: Endpoints for creating and managing music generation tasks
  - name: Lyrics Generation
    description: Endpoints for lyrics generation and management
  - name: WAV Conversion
    description: Endpoints for converting music to WAV format
  - name: Vocal Removal
    description: Endpoints for vocal removal from music tracks
  - name: Music Video Generation
    description: Endpoints for generating MP4 videos from music tracks
  - name: Account Management
    description: Endpoints for account and credits management
paths:
  /api/v1/vocal-removal/record-info:
    get:
      summary: Get Vocal Separation Details
      operationId: get-vocal-separation-details
      parameters:
        - in: query
          name: taskId
          description: >-
            The task ID returned from the Separate Vocals from Music endpoint.
            Used to retrieve detailed information about a specific vocal
            separation task, including download URLs for all separated audio
            components.
          required: true
          example: 5e72****97c7
          schema:
            type: string
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/ApiResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: Task ID
                          musicId:
                            type: string
                            description: >-
                              The ID of the source music track that was
                              processed for vocal separation
                          callbackUrl:
                            type: string
                            description: >-
                              The callback URL that was provided in the vocal
                              separation request
                          audioId:
                            type: string
                            description: >-
                              The audio ID of the track within the original
                              generation task
                          completeTime:
                            type: string
                            description: The timestamp when the separation was completed
                            format: date-time
                          response:
                            type: object
                            properties:
                              originUrl:
                                type: string
                                description: Original audio URL
                              instrumentalUrl:
                                type: string
                                description: >-
                                  Instrumental part audio URL (exists for
                                  separate_vocal type)
                              vocalUrl:
                                type: string
                                description: Vocal part audio URL
                              backingVocalsUrl:
                                type: string
                                description: >-
                                  Backing vocals part audio URL (exists for
                                  split_stem type)
                              drumsUrl:
                                type: string
                                description: Drums part audio URL
                              bassUrl:
                                type: string
                                description: Bass part audio URL
                              guitarUrl:
                                type: string
                                description: Guitar part audio URL
                              keyboardUrl:
                                type: string
                                description: >-
                                  Keyboard part audio URL (exists for split_stem
                                  type)
                              percussionUrl:
                                type: string
                                description: >-
                                  Percussion part audio URL (exists for
                                  split_stem type)
                              stringsUrl:
                                type: string
                                description: >-
                                  Strings part audio URL (exists for split_stem
                                  type)
                              synthUrl:
                                type: string
                                description: >-
                                  Synthesizer part audio URL (exists for
                                  split_stem type)
                              fxUrl:
                                type: string
                                description: >-
                                  Effects part audio URL (exists for split_stem
                                  type)
                              brassUrl:
                                type: string
                                description: >-
                                  Brass part audio URL (exists for split_stem
                                  type)
                              woodwindsUrl:
                                type: string
                                description: >-
                                  Woodwinds part audio URL (exists for
                                  split_stem type)
                          successFlag:
                            type: string
                            description: The current status of the vocal separation task
                            enum:
                              - PENDING
                              - SUCCESS
                              - CREATE_TASK_FAILED
                              - GENERATE_AUDIO_FAILED
                              - CALLBACK_EXCEPTION
                          createTime:
                            type: string
                            description: Creation time
                            format: date-time
                          errorCode:
                            type: number
                            description: Error code, valid when task fails
                          errorMessage:
                            type: string
                            description: Error message, valid when task fails
              examples:
                separate_vocal_type:
                  summary: separate_vocal type query details example
                  value:
                    code: 200
                    msg: success
                    data:
                      taskId: 3e63b4cc88d52611159371f6af5571e7
                      musicId: 376c687e-d439-42c1-b1e4-bcb43b095ec2
                      callbackUrl: >-
                        https://57312fc2e366.ngrok-free.app/api/v1/vocal-removal/test
                      audioId: e231****-****-****-****-****8cadc7dc
                      completeTime: 1753782937000
                      response:
                        originUrl: null
                        instrumentalUrl: >-
                          https://file.aiquickdraw.com/s/d92a13bf-c6f4-4ade-bb47-f69738435528_Instrumental.mp3
                        vocalUrl: >-
                          https://file.aiquickdraw.com/s/3d7021c9-fa8b-4eda-91d1-3b9297ddb172_Vocals.mp3
                        backingVocalsUrl: null
                        drumsUrl: null
                        bassUrl: null
                        guitarUrl: null
                        keyboardUrl: null
                        percussionUrl: null
                        stringsUrl: null
                        synthUrl: null
                        fxUrl: null
                        brassUrl: null
                        woodwindsUrl: null
                      successFlag: SUCCESS
                      createTime: 1753782854000
                      errorCode: null
                      errorMessage: null
                split_stem_type:
                  summary: split_stem type query details example
                  value:
                    code: 200
                    msg: success
                    data:
                      taskId: e649edb7abfd759285bd41a47a634b10
                      musicId: 376c687e-d439-42c1-b1e4-bcb43b095ec2
                      callbackUrl: >-
                        https://57312fc2e366.ngrok-free.app/api/v1/vocal-removal/test
                      audioId: e231****-****-****-****-****8cadc7dc
                      completeTime: 1753782459000
                      response:
                        originUrl: null
                        instrumentalUrl: null
                        vocalUrl: >-
                          https://file.aiquickdraw.com/s/07420749-29a2-4054-9b62-e6a6f8b90ccb_Vocals.mp3
                        backingVocalsUrl: >-
                          https://file.aiquickdraw.com/s/aadc51a3-4c88-4c8e-a4c8-e867c539673d_Backing_Vocals.mp3
                        drumsUrl: >-
                          https://file.aiquickdraw.com/s/ac75c5ea-ac77-4ad2-b7d9-66e140b78e44_Drums.mp3
                        bassUrl: >-
                          https://file.aiquickdraw.com/s/a3c2da5a-b364-4422-adb5-2692b9c26d33_Bass.mp3
                        guitarUrl: >-
                          https://file.aiquickdraw.com/s/064dd08e-d5d2-4201-9058-c5c40fb695b4_Guitar.mp3
                        keyboardUrl: >-
                          https://file.aiquickdraw.com/s/adc934e0-df7d-45da-8220-1dba160d74e0_Keyboard.mp3
                        percussionUrl: >-
                          https://file.aiquickdraw.com/s/0f70884d-047c-41f1-a6d0-7044618b7dc6_Percussion.mp3
                        stringsUrl: >-
                          https://file.aiquickdraw.com/s/49829425-a5b0-424e-857a-75d4c63a426b_Strings.mp3
                        synthUrl: >-
                          https://file.aiquickdraw.com/s/56b2d94a-eb92-4d21-bc43-3460de0c8348_Synth.mp3
                        fxUrl: >-
                          https://file.aiquickdraw.com/s/a8822c73-6629-4089-8f2a-d19f41f0007d_FX.mp3
                        brassUrl: >-
                          https://file.aiquickdraw.com/s/334b2d23-0c65-4a04-92c7-22f828afdd44_Brass.mp3
                        woodwindsUrl: >-
                          https://file.aiquickdraw.com/s/d81545b1-6f94-4388-9785-1aaa6ecabb02_Woodwinds.mp3
                      successFlag: SUCCESS
                      createTime: 1753782327000
                      errorCode: null
                      errorMessage: null
        '500':
          $ref: '#/components/responses/Error'
components:
  schemas:
    ApiResponse:
      type: object
      properties:
        code:
          type: integer
          description: |-
            # Status Codes

            - ✅ 200 - Request successful
            - ⚠️ 400 - Invalid parameters
            - ⚠️ 401 - Unauthorized access
            - ⚠️ 404 - Invalid request method or path
            - ⚠️ 405 - Rate limit exceeded
            - ⚠️ 413 - Theme or prompt too long
            - ⚠️ 429 - Insufficient credits
            - ⚠️ 430 - Your call frequency is too high. Please try again later. 
            - ⚠️ 455 - System maintenance
            - ❌ 500 - Server error
          example: 200
          enum:
            - 200
            - 400
            - 401
            - 404
            - 405
            - 413
            - 429
            - 430
            - 455
            - 500
        msg:
          type: string
          description: Error message when code != 200
          example: success
  responses:
    Error:
      description: Server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        # 🔑 API Authentication


        All endpoints require authentication using Bearer Token.


        ## Get API Key


        1. Visit the [API Key Management Page](https://sunoapi.org/api-key) to
        obtain your API Key


        ## Usage


        Add to request headers:


        ```

        Authorization: Bearer YOUR_API_KEY

        ```


        > **⚠️ Note:**

        > - Keep your API Key secure and do not share it with others

        > - If you suspect your API Key has been compromised, reset it
        immediately from the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt


# Base64 File Upload

> Upload temporary files via Base64 encoded data. Note: Uploaded files are temporary and automatically deleted after 3 days.

## OpenAPI

````yaml file-upload-api/file-upload-api.json post /api/file-base64-upload
openapi: 3.0.0
info:
  title: File Upload API
  description: >-
    File Upload Service API Documentation - Supporting multiple file upload
    methods, uploaded files are temporary and automatically deleted after 3 days
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://sunoapiorg.redpandaai.co
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: File Upload
    description: >-
      Multiple ways to upload temporary files, supporting Base64, file stream,
      and URL upload, files are automatically deleted after 3 days
paths:
  /api/file-base64-upload:
    post:
      summary: Base64 File Upload
      operationId: upload-file-base64
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Base64UploadRequest'
            examples:
              with_data_url:
                summary: Using data URL format
                value:
                  base64Data: >-
                    data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==
                  uploadPath: images/base64
                  fileName: test-image.png
              with_pure_base64:
                summary: Using pure Base64 string
                value:
                  base64Data: >-
                    iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==
                  uploadPath: documents/uploads
      responses:
        '200':
          $ref: '#/components/responses/SuccessResponse'
        '400':
          $ref: '#/components/responses/BadRequestError'
        '401':
          $ref: '#/components/responses/UnauthorizedError'
        '500':
          $ref: '#/components/responses/ServerError'
components:
  schemas:
    Base64UploadRequest:
      type: object
      properties:
        base64Data:
          type: string
          description: >-
            Base64 encoded file data. Supports pure Base64 strings or data URL
            format
          example: data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...
        uploadPath:
          type: string
          description: File upload path, without leading or trailing slashes
          example: images/base64
        fileName:
          type: string
          description: >-
            File name (optional), including file extension. If not provided, a
            random filename will be generated. If the same filename already
            exists, the old file will be overwritten, but changes may not be
            immediately visible due to caching
          example: my-image.png
      required:
        - base64Data
        - uploadPath
    ApiResponse:
      type: object
      properties:
        success:
          type: boolean
          description: Whether the request was successful
        code:
          $ref: '#/components/schemas/StatusCode'
        msg:
          type: string
          description: Response message
          example: File uploaded successfully
      required:
        - success
        - code
        - msg
    FileUploadResult:
      type: object
      properties:
        fileName:
          type: string
          description: File name
          example: uploaded-image.png
        filePath:
          type: string
          description: Complete file path in storage
          example: images/user-uploads/uploaded-image.png
        downloadUrl:
          type: string
          format: uri
          description: File download URL
          example: >-
            https://tempfile.redpandaai.co/xxx/images/user-uploads/uploaded-image.png
        fileSize:
          type: integer
          description: File size in bytes
          example: 154832
        mimeType:
          type: string
          description: File MIME type
          example: image/png
        uploadedAt:
          type: string
          format: date-time
          description: Upload timestamp
          example: '2025-01-01T12:00:00.000Z'
      required:
        - fileName
        - filePath
        - downloadUrl
        - fileSize
        - mimeType
        - uploadedAt
    StatusCode:
      type: integer
      enum:
        - 200
        - 400
        - 401
        - 405
        - 500
      description: Response status code
      x-enumDescriptions:
        '200': Success - Request has been processed successfully
        '400': >-
          Bad Request - Request parameters are incorrect or missing required
          parameters
        '401': Unauthorized - Authentication credentials are missing or invalid
        '405': Method Not Allowed - Request method is not supported
        '500': >-
          Server Error - An unexpected error occurred while processing the
          request
  responses:
    SuccessResponse:
      description: File uploaded successfully
      content:
        application/json:
          schema:
            allOf:
              - $ref: '#/components/schemas/ApiResponse'
              - type: object
                properties:
                  data:
                    $ref: '#/components/schemas/FileUploadResult'
          example:
            success: true
            code: 200
            msg: File uploaded successfully
            data:
              fileName: uploaded-image.png
              filePath: images/user-uploads/uploaded-image.png
              downloadUrl: >-
                https://tempfile.redpandaai.co/xxx/images/user-uploads/uploaded-image.png
              fileSize: 154832
              mimeType: image/png
              uploadedAt: '2025-01-01T12:00:00.000Z'
    BadRequestError:
      description: Request parameter error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ApiResponse'
          examples:
            missing_parameter:
              summary: Missing required parameter
              value:
                success: false
                code: 400
                msg: 'Missing required parameter: uploadPath'
            invalid_format:
              summary: Format error
              value:
                success: false
                code: 400
                msg: 'Base64 decoding failed: Invalid Base64 format'
    UnauthorizedError:
      description: Unauthorized access
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ApiResponse'
          example:
            success: false
            code: 401
            msg: 'Authentication failed: Invalid API Key'
    ServerError:
      description: Internal server error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ApiResponse'
          example:
            success: false
            code: 500
            msg: Internal server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        All APIs require authentication via Bearer Token.


        Get API Key:

        1. Visit [API Key Management Page](https://sunoapi.org/api-key) to get
        your API Key


        Usage:

        Add to request header:

        Authorization: Bearer YOUR_API_KEY


        Note:

        - Keep your API Key secure and do not share it with others

        - If you suspect your API Key has been compromised, reset it immediately
        in the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt


# File Stream Upload

## OpenAPI

````yaml file-upload-api/file-upload-api.json post /api/file-stream-upload
openapi: 3.0.0
info:
  title: File Upload API
  description: >-
    File Upload Service API Documentation - Supporting multiple file upload
    methods, uploaded files are temporary and automatically deleted after 3 days
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://sunoapiorg.redpandaai.co
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: File Upload
    description: >-
      Multiple ways to upload temporary files, supporting Base64, file stream,
      and URL upload, files are automatically deleted after 3 days
paths:
  /api/file-stream-upload:
    post:
      summary: File Stream Upload
      operationId: upload-file-stream
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
                  description: File to upload (binary data)
                uploadPath:
                  type: string
                  description: File upload path, without leading or trailing slashes
                  example: images/user-uploads
                fileName:
                  type: string
                  description: >-
                    File name (optional), including file extension. If not
                    provided, the original filename will be used. If the same
                    filename already exists, the old file will be overwritten,
                    but changes may not be immediately visible due to caching
                  example: my-image.jpg
              required:
                - file
                - uploadPath
      responses:
        '200':
          $ref: '#/components/responses/SuccessResponse'
        '400':
          $ref: '#/components/responses/BadRequestError'
        '401':
          $ref: '#/components/responses/UnauthorizedError'
        '500':
          $ref: '#/components/responses/ServerError'
components:
  responses:
    SuccessResponse:
      description: File uploaded successfully
      content:
        application/json:
          schema:
            allOf:
              - $ref: '#/components/schemas/ApiResponse'
              - type: object
                properties:
                  data:
                    $ref: '#/components/schemas/FileUploadResult'
          example:
            success: true
            code: 200
            msg: File uploaded successfully
            data:
              fileName: uploaded-image.png
              filePath: images/user-uploads/uploaded-image.png
              downloadUrl: >-
                https://tempfile.redpandaai.co/xxx/images/user-uploads/uploaded-image.png
              fileSize: 154832
              mimeType: image/png
              uploadedAt: '2025-01-01T12:00:00.000Z'
    BadRequestError:
      description: Request parameter error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ApiResponse'
          examples:
            missing_parameter:
              summary: Missing required parameter
              value:
                success: false
                code: 400
                msg: 'Missing required parameter: uploadPath'
            invalid_format:
              summary: Format error
              value:
                success: false
                code: 400
                msg: 'Base64 decoding failed: Invalid Base64 format'
    UnauthorizedError:
      description: Unauthorized access
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ApiResponse'
          example:
            success: false
            code: 401
            msg: 'Authentication failed: Invalid API Key'
    ServerError:
      description: Internal server error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ApiResponse'
          example:
            success: false
            code: 500
            msg: Internal server error
  schemas:
    ApiResponse:
      type: object
      properties:
        success:
          type: boolean
          description: Whether the request was successful
        code:
          $ref: '#/components/schemas/StatusCode'
        msg:
          type: string
          description: Response message
          example: File uploaded successfully
      required:
        - success
        - code
        - msg
    FileUploadResult:
      type: object
      properties:
        fileName:
          type: string
          description: File name
          example: uploaded-image.png
        filePath:
          type: string
          description: Complete file path in storage
          example: images/user-uploads/uploaded-image.png
        downloadUrl:
          type: string
          format: uri
          description: File download URL
          example: >-
            https://tempfile.redpandaai.co/xxx/images/user-uploads/uploaded-image.png
        fileSize:
          type: integer
          description: File size in bytes
          example: 154832
        mimeType:
          type: string
          description: File MIME type
          example: image/png
        uploadedAt:
          type: string
          format: date-time
          description: Upload timestamp
          example: '2025-01-01T12:00:00.000Z'
      required:
        - fileName
        - filePath
        - downloadUrl
        - fileSize
        - mimeType
        - uploadedAt
    StatusCode:
      type: integer
      enum:
        - 200
        - 400
        - 401
        - 405
        - 500
      description: Response status code
      x-enumDescriptions:
        '200': Success - Request has been processed successfully
        '400': >-
          Bad Request - Request parameters are incorrect or missing required
          parameters
        '401': Unauthorized - Authentication credentials are missing or invalid
        '405': Method Not Allowed - Request method is not supported
        '500': >-
          Server Error - An unexpected error occurred while processing the
          request
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        All APIs require authentication via Bearer Token.


        Get API Key:

        1. Visit [API Key Management Page](https://sunoapi.org/api-key) to get
        your API Key


        Usage:

        Add to request header:

        Authorization: Bearer YOUR_API_KEY


        Note:

        - Keep your API Key secure and do not share it with others

        - If you suspect your API Key has been compromised, reset it immediately
        in the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt


# URL File Upload

## OpenAPI

````yaml file-upload-api/file-upload-api.json post /api/file-url-upload
openapi: 3.0.0
info:
  title: File Upload API
  description: >-
    File Upload Service API Documentation - Supporting multiple file upload
    methods, uploaded files are temporary and automatically deleted after 3 days
  version: 1.0.0
  contact:
    name: Technical Support
    email: support@sunoapi.org
servers:
  - url: https://sunoapiorg.redpandaai.co
    description: API Server
security:
  - BearerAuth: []
tags:
  - name: File Upload
    description: >-
      Multiple ways to upload temporary files, supporting Base64, file stream,
      and URL upload, files are automatically deleted after 3 days
paths:
  /api/file-url-upload:
    post:
      summary: URL File Upload
      operationId: upload-file-url
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UrlUploadRequest'
            examples:
              image_from_url:
                summary: Download image from URL
                value:
                  fileUrl: https://example.com/images/sample.jpg
                  uploadPath: images/downloaded
                  fileName: my-downloaded-image.jpg
              document_from_url:
                summary: Download document from URL
                value:
                  fileUrl: https://example.com/docs/manual.pdf
                  uploadPath: documents/manuals
      responses:
        '200':
          $ref: '#/components/responses/SuccessResponse'
        '400':
          $ref: '#/components/responses/BadRequestError'
        '401':
          $ref: '#/components/responses/UnauthorizedError'
        '500':
          $ref: '#/components/responses/ServerError'
components:
  schemas:
    UrlUploadRequest:
      type: object
      properties:
        fileUrl:
          type: string
          format: uri
          description: File download URL, must be a valid HTTP or HTTPS address
          example: https://example.com/images/sample.jpg
        uploadPath:
          type: string
          description: File upload path, without leading or trailing slashes
          example: images/downloaded
        fileName:
          type: string
          description: >-
            File name (optional), including file extension. If not provided, a
            random filename will be generated. If the same filename already
            exists, the old file will be overwritten, but changes may not be
            immediately visible due to caching
          example: sample-image.jpg
      required:
        - fileUrl
        - uploadPath
    ApiResponse:
      type: object
      properties:
        success:
          type: boolean
          description: Whether the request was successful
        code:
          $ref: '#/components/schemas/StatusCode'
        msg:
          type: string
          description: Response message
          example: File uploaded successfully
      required:
        - success
        - code
        - msg
    FileUploadResult:
      type: object
      properties:
        fileName:
          type: string
          description: File name
          example: uploaded-image.png
        filePath:
          type: string
          description: Complete file path in storage
          example: images/user-uploads/uploaded-image.png
        downloadUrl:
          type: string
          format: uri
          description: File download URL
          example: >-
            https://tempfile.redpandaai.co/xxx/images/user-uploads/uploaded-image.png
        fileSize:
          type: integer
          description: File size in bytes
          example: 154832
        mimeType:
          type: string
          description: File MIME type
          example: image/png
        uploadedAt:
          type: string
          format: date-time
          description: Upload timestamp
          example: '2025-01-01T12:00:00.000Z'
      required:
        - fileName
        - filePath
        - downloadUrl
        - fileSize
        - mimeType
        - uploadedAt
    StatusCode:
      type: integer
      enum:
        - 200
        - 400
        - 401
        - 405
        - 500
      description: Response status code
      x-enumDescriptions:
        '200': Success - Request has been processed successfully
        '400': >-
          Bad Request - Request parameters are incorrect or missing required
          parameters
        '401': Unauthorized - Authentication credentials are missing or invalid
        '405': Method Not Allowed - Request method is not supported
        '500': >-
          Server Error - An unexpected error occurred while processing the
          request
  responses:
    SuccessResponse:
      description: File uploaded successfully
      content:
        application/json:
          schema:
            allOf:
              - $ref: '#/components/schemas/ApiResponse'
              - type: object
                properties:
                  data:
                    $ref: '#/components/schemas/FileUploadResult'
          example:
            success: true
            code: 200
            msg: File uploaded successfully
            data:
              fileName: uploaded-image.png
              filePath: images/user-uploads/uploaded-image.png
              downloadUrl: >-
                https://tempfile.redpandaai.co/xxx/images/user-uploads/uploaded-image.png
              fileSize: 154832
              mimeType: image/png
              uploadedAt: '2025-01-01T12:00:00.000Z'
    BadRequestError:
      description: Request parameter error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ApiResponse'
          examples:
            missing_parameter:
              summary: Missing required parameter
              value:
                success: false
                code: 400
                msg: 'Missing required parameter: uploadPath'
            invalid_format:
              summary: Format error
              value:
                success: false
                code: 400
                msg: 'Base64 decoding failed: Invalid Base64 format'
    UnauthorizedError:
      description: Unauthorized access
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ApiResponse'
          example:
            success: false
            code: 401
            msg: 'Authentication failed: Invalid API Key'
    ServerError:
      description: Internal server error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ApiResponse'
          example:
            success: false
            code: 500
            msg: Internal server error
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: >-
        All APIs require authentication via Bearer Token.


        Get API Key:

        1. Visit [API Key Management Page](https://sunoapi.org/api-key) to get
        your API Key


        Usage:

        Add to request header:

        Authorization: Bearer YOUR_API_KEY


        Note:

        - Keep your API Key secure and do not share it with others

        - If you suspect your API Key has been compromised, reset it immediately
        in the management page

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.sunoapi.org/llms.txt