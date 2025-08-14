#!/usr/bin/env python3
"""
Open WebUI API Client Library

This module provides a Python class `OpenWebUIClient` for interacting with the
Open WebUI REST API, and a helper class `OpenWebUIMessageBuilder` for
constructing valid message payloads, including for multimodal inputs.

File uploads are handled by the OpenWebUIClient, not the message builder,
as they are attached at the top level of an API request.
"""

import base64
import mimetypes
from pathlib import Path
from typing import Dict, List, Any, Optional


class OpenWebUIMessageBuilder:
    """
    A helper class to construct the 'messages' payload for the Open WebUI API.

    This builder simplifies the creation of message lists, especially for
    multimodal chats involving text and images. Note that it does not handle
    file attachments, which are managed by the OpenWebUIClient at the request level.
    """

    def __init__(self, system_prompt: Optional[str] = None):
        """
        Initializes the message builder.

        Args:
            system_prompt: An optional initial system message to set the
                           behavior of the assistant.
        """
        self.messages: List[Dict[str, Any]] = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

    def add_user_message(self, text: str) -> 'OpenWebUIMessageBuilder':
        """
        Adds a standard text-only user message.

        Args:
            text: The text content of the user's message.

        Returns:
            The builder instance for chaining.
        """
        self.messages.append({"role": "user", "content": text})
        return self

    def add_user_message_with_images(
            self, text: str, image_paths: List[str]
    ) -> 'OpenWebUIMessageBuilder':
        """
        Adds a multimodal user message containing text and one or more images.

        Args:
            text: The text prompt accompanying the images.
            image_paths: A list of local file paths to the images.

        Returns:
            The builder instance for chaining.

        Raises:
            FileNotFoundError: If any image path is invalid.
        """
        content_parts: List[Dict[str, Any]] = [{"type": "text", "text": text}]

        for image_path in image_paths:
            path = Path(image_path)
            if not path.is_file():
                raise FileNotFoundError(f"Image file not found at path: {image_path}")

            # Guess MIME type and encode image to Base64
            mime_type, _ = mimetypes.guess_type(path)
            if not mime_type or not mime_type.startswith('image'):
                raise ValueError(f"Could not determine a valid image type for {image_path}")
            with open(path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            image_url = {"url": f"data:{mime_type};base64,{encoded_string}"}
            content_parts.append({"type": "image_url", "image_url": image_url})

        self.messages.append({"role": "user", "content": content_parts})
        return self

    def add_assistant_message(self, text: str) -> 'OpenWebUIMessageBuilder':
        """
        Adds a message from the assistant, useful for few-shot prompting.

        Args:
            text: The text content of the assistant's message.

        Returns:
            The builder instance for chaining.
        """
        self.messages.append({"role": "assistant", "content": text})
        return self

    def build(self) -> List[Dict[str, Any]]:
        """
        Returns the constructed list of messages.

        Returns:
            The final list of message dictionaries for the API request.
        """
        return self.messages
