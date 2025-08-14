#!/usr/bin/env python3
"""
Open WebUI API Client Library

This module provides a Python class `OpenWebUIClient` for interacting with the
Open WebUI REST API, and a helper class `OpenWebUIMessageBuilder` for
constructing valid message payloads, including for multimodal inputs.

File uploads are handled by the OpenWebUIClient, not the message builder,
as they are attached at the top level of an API request.
"""

import requests
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Iterator
from contextlib import contextmanager


class OpenWebUIClient:
    """
    A client for interacting with the Open WebUI REST API.
    """

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

    def get_models(self) -> List[Dict[str, Any]]:
        """Retrieves a list of available models from the API."""
        url = f"{self.base_url}/api/models"
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('data', [])

    def upload_file(self, file_path: str) -> Dict[str, Any]:
        """
        Uploads a file to be referenced in chat completions.
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found at path: {file_path}")

        url = f"{self.base_url}/api/v1/files/"

        headers = {
            "Authorization": self.session.headers["Authorization"],
            "Accept": "application/json"
        }

        with open(path, "rb") as f:
            files_payload = {'file': f}
            response = requests.post(url, headers=headers, files=files_payload)

        response.raise_for_status()
        return response.json()

    def delete_file(self, file_id: str) -> None:
        """
        Deletes a previously uploaded file from the server.
        """
        url = f"{self.base_url}/api/v1/files/{file_id}"
        response = self.session.delete(url)
        response.raise_for_status()

    @contextmanager
    def upload_and_manage_files(self, file_paths: List[str]) -> Iterator[List[Dict[str, Any]]]:
        """
        A context manager to upload files and ensure they are deleted afterward.
        """
        uploaded_file_data = []
        try:
            for path in file_paths:
                uploaded_file_data.append(self.upload_file(path))
            yield uploaded_file_data
        finally:
            if not uploaded_file_data:
                return

            print("\nCleaning up temporary files from server...")
            for file_data in uploaded_file_data:
                file_id = file_data.get('id')
                if file_id:
                    try:
                        self.delete_file(file_id)
                        # Use 'filename' as that is what the API returns
                        filename = file_data.get('filename', 'Unknown Filename')
                        print(f"  - Deleted: {filename} (ID: {file_id})")
                    except requests.exceptions.RequestException as e:
                        print(f"  - WARNING: Failed to delete file {file_id}: {e}")

    def chat_completion(self, model: str, messages: List[Dict[str, Any]],
                        temperature: float = 0.7, max_tokens: Optional[int] = None,
                        response_format: Optional[Dict[str, Any]] = None, # <-- ADDED PARAMETER
                        uploaded_files: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Sends a request for a standard chat completion, with optional file attachments.
        """
        url = f"{self.base_url}/api/chat/completions"
        payload = {"model": model, "messages": messages, "temperature": temperature, "stream": False}
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if response_format is not None:
            payload["response_format"] = response_format
        if uploaded_files:
            payload['files'] = [{'id': f['id'], 'type': 'file'} for f in uploaded_files]

        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def stream_chat_completion(self, model: str, messages: List[Dict[str, Any]],
                               temperature: float = 0.7,
                               response_format: Optional[Dict[str, Any]] = None, # <-- ADDED PARAMETER
                               uploaded_files: Optional[List[Dict[str, Any]]] = None) -> Iterator[Dict[str, Any]]:
        """
        Sends a request for a streaming chat completion, with optional file attachments.
        """
        url = f"{self.base_url}/api/chat/completions"
        payload = {"model": model, "messages": messages, "temperature": temperature, "stream": True}
        if response_format is not None:
            payload["response_format"] = response_format
        if uploaded_files:
            payload['files'] = [{'id': f['id'], 'type': 'file'} for f in uploaded_files]

        with self.session.post(url, json=payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    if data_str.strip() == '[DONE]':
                        break
                    try:
                        yield json.loads(data_str)
                    except json.JSONDecodeError:
                        print(f"\nWarning: Could not decode JSON chunk: {data_str}\n")
                        continue
