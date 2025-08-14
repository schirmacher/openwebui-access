# Open WebUI Access Python Library & Tutorial

This repository provides a Python library to access an open-webui instance and a detailed tutorial for interacting with the [Open WebUI](https://open-webui.com/) REST API. It is designed to be a simple, yet powerful, starting point for developers looking to integrate LLM functionalities from their Open WebUI instance into their Python applications.

The library handles various interactions, from simple text queries to complex multimodal chats and document-based Retrieval-Augmented Generation (RAG). The tutorial script demonstrates each feature with clear, runnable examples.

## Features

- **Simple & Streaming Chat:** Perform standard request/response chats or stream responses for a live, interactive feel.
- **Multimodal Support:** Send queries that include both text and images.
- **File Uploads for RAG:** Upload documents (PDFs, DOCX, etc.) and ask questions about their content. The model will use the documents to generate answers and provide citations.
- **Automatic File Management:** A context manager handles the uploading and—crucially—the automatic deletion of temporary files from the server after your query is complete.
- **Guaranteed JSON Mode:** Force models that support it to return valid JSON objects, perfect for structured data extraction.
- **Conversation History:** A convenient message builder makes it easy to maintain conversational context.
- **Full Control:** Easily configure the model, system prompt, temperature, and other generation parameters.

## Prerequisites

Before you begin, ensure you have the following:

1.  **Python 3.7+**.
2.  An **active Open WebUI instance**. You will need its base URL (e.g., `http://localhost:8080`).
3.  An **API Key** from your Open WebUI instance. You can generate one in the WebUI under `Settings > Account > API Keys`.
4.  **Python packages**. You can install all required packages using the provided `requirements.txt` file.

## Installation and Setup

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set Environment Variables:**
    The tutorial script reads its configuration from environment variables. This is the most secure way to handle sensitive data like API keys.

    **In JetBrains PyCharm (Environment variables section in Run/Debug Configurations):**
    ```
    PYTHONUNBUFFERED=1;OPENWEBUI_URL=http://your-open-webui-host:8080;OPENWEBUI_API_KEY=your-api-key-here;OPENWEBUI_MODEL=llama3:latest;OPENWEBUI_MULTIMODAL_MODEL=llava:latest
    ```

    **On Linux/macOS:**
    ```bash
    export OPENWEBUI_URL="http://your-open-webui-host:8080"
    export OPENWEBUI_API_KEY="your-api-key-here"
    export OPENWEBUI_MODEL="llama3:latest" # A good general-purpose model
    export OPENWEBUI_MULTIMODAL_MODEL="llava:latest" # A model that can process images (e.g., LLaVA)
    ```

    **On Windows (Command Prompt):**
    ```powershell
    setx OPENWEBUI_URL "http://your-open-webui-host:8080"
    setx OPENWEBUI_API_KEY "your-api-key-here"
    setx OPENWEBUI_MODEL "llama3:latest"
    setx OPENWEBUI_MULTIMODAL_MODEL "llava:latest"
    ```
    *Note: After using `setx`, you may need to open a new terminal for the variables to be available.*

## Core Library: `openwebui_access.py`

This file contains the core logic for communicating with the Open WebUI API. It consists of two main classes.

### `OpenWebUIMessageBuilder`

This is a helper class designed to correctly construct the `messages` payload required by the API. It simplifies managing conversation history and creating complex multimodal messages.

-   `__init__(system_prompt: str)`: Initializes the builder. You can optionally provide a `system_prompt` to define the AI's personality, role, or instructions (e.g., "You are a helpful assistant who always responds in JSON format.").
-   `add_user_message(text: str)`: Adds a standard text message from the user.
-   `add_user_message_with_images(text: str, image_paths: list)`: Adds a multimodal message from the user, containing both text and one or more images. The builder handles the complexity of reading the image files, encoding them in Base64, and formatting the payload correctly.
-   `add_assistant_message(text: str)`: Adds a message from the assistant. This is useful for maintaining conversation history or for providing "few-shot" examples to guide the model's responses.
-   `build()`: Returns the final, properly formatted list of message dictionaries, ready to be sent to the API.

### `OpenWebUIClient`

This is the main client for making requests to the Open WebUI API.

-   `__init__(base_url: str, api_key: str)`: Initializes the client with your Open WebUI URL and API key. It sets up a `requests.Session` for efficient and persistent connections.
-   `get_models()`: Fetches and returns a list of all models available on your Open WebUI instance.
-   `chat_completion(...)`: Sends a request for a **non-streaming** chat completion. The entire response is returned at once after the model has finished generating it.
-   `stream_chat_completion(...)`: Sends a request for a **streaming** chat completion. This returns a generator that yields response chunks as they are generated by the model, allowing you to display the response in real-time.
-   `upload_file(file_path: str)`: Uploads a single file (e.g., a PDF or DOCX) to the Open WebUI server. This is the first step for performing Retrieval-Augmented Generation (RAG). It returns a dictionary containing the file's `id` on the server.
-   `delete_file(file_id: str)`: Deletes a previously uploaded file from the server using its `id`.
-   `upload_and_manage_files(file_paths: list)`: A powerful **context manager** that automates the file management lifecycle for RAG. It uploads a list of files, allows you to use them within its `with` block, and then **automatically deletes them** from the server afterward, preventing clutter. This is the recommended way to handle file uploads.

## Tutorial Walkthrough: `openwebui_client_tutorial.py`

This script provides a series of runnable examples that demonstrate every major feature of the client library. To run it, ensure your environment variables are set and execute:

```bash
python openwebui_access_tutorial.py
```

---

### Use Case 1: List Available Models
Demonstrates how to query the API to get a list of all the models you have pulled into your Open WebUI instance. This is a great first step to verify your connection and see what models you can use.

### Use Case 2: Simple Chat Completion (Non-Streaming)
Shows the most basic interaction: asking a question and receiving the complete answer in a single response. This is suitable for backend tasks where a final, complete text is needed.

### Use Case 3: Streaming Chat Completion
Demonstrates how to receive the model's response as a "stream" of text chunks. The tutorial shows how to print these chunks to the console as they arrive, creating a "live typing" effect similar to the ChatGPT interface.

### Use Case 4: Conversational Context
This example illustrates how to build a multi-turn conversation. It uses the `OpenWebUIMessageBuilder` to keep track of the conversation history (user questions and assistant answers), so the model can understand follow-up questions.

### Use Case 5: Setting Model Persona with a System Prompt
Shows the power of the `system_prompt`. The same user query is sent twice: once with a factual, scientific persona, and once with a salty pirate persona. This highlights how the system prompt can dramatically shape the tone and style of the model's output.

### Use Case 6: Robust JSON Extraction
A practical example of "prompt engineering" to get structured data. It demonstrates a multi-part strategy:
1.  A strict system prompt demanding JSON output.
2.  Few-shot examples to show the model the exact format.
3.  Client-side parsing to reliably extract the JSON block from the model's raw response.

### Use Case 7: Guaranteed JSON Mode
This showcases a more modern and reliable method for getting JSON. By setting `response_format={"type": "json_object"}`, it instructs the model (if supported) to guarantee its output is a valid JSON object. This is less work than prompt engineering but depends on model compatibility.

### Use Case 8: Controlling Generation with Parameters
Illustrates how to use the `temperature` parameter to control the randomness of the model's output. A low temperature (e.g., 0.1) produces focused, deterministic responses, while a high temperature (e.g., 1.0) encourages more creative and diverse answers.

### Use Case 9: Single Image Query (Multimodal)
Your first step into multimodal AI. This example uses `add_user_message_with_images` to send an image along with a text prompt. The model then analyzes the image to answer the question. This requires a multimodal model like LLaVA.

### Use Case 10: Multi-Image Conversational Query
A more advanced multimodal scenario. It sends multiple images in the first turn, asks a question about them, and then asks a follow-up question in the second turn, demonstrating that the model retains context about the images across a conversation.

### Use Case 11: Single File RAG Query with Citations
This is a powerful demonstration of Retrieval-Augmented Generation (RAG).
1.  A PDF document is created and uploaded using the `upload_and_manage_files` context manager.
2.  A question is asked that can only be answered using information from the PDF.
3.  The model reads the document, generates an answer, and includes citations (e.g., `[1]`) that link back to the source document.
4.  The context manager automatically cleans up the uploaded file from the server.

### Use Case 12: Multi-File RAG Conversational Query
The most comprehensive example. It uploads multiple documents (a PDF and a DOCX), asks a question that requires synthesizing information from both, and then asks a follow-up question. This showcases the model's ability to work with a knowledge base of several documents and maintain conversational context. The response includes citations for each document used.