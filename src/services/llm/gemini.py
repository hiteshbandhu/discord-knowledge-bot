# services/llm/gemini.py

import os
from google import genai
from google.genai import types
from services.llm.prompts import SUMMARY_PROMPT, IMAGE_DESCRIPTION_PROMPT, LINK_SUMMARY_PROMPT
import base64
from dotenv import load_dotenv
load_dotenv()

# Initialize the Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model_name = "gemini-2.5-flash-preview-05-20"


def summarize_youtube_video(video_url: str) -> str:
    """
    Summarizes a YouTube video using the Gemini API.

    Args:
        video_url (str): The URL of the YouTube video.

    Returns:
        str: The summarized content.
    """
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part(
                    file_data=types.FileData(
                        file_uri=video_url,
                        mime_type="video/*",
                    )
                ),
                types.Part.from_text(text=SUMMARY_PROMPT),
            ],
        ),
    ]

    try:
        # Generate content using the non-streaming method
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
        )

        # Extract and return the text from the response
        return response.text.strip()
    except Exception as e:
        raise RuntimeError(f"Failed to summarize video: {e}")


def describe_image(image_bytes: bytes) -> str:
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(
                    mime_type="image/png",
                    data=base64.b64decode(base64_image),
                ),
                types.Part.from_text(text=IMAGE_DESCRIPTION_PROMPT),
            ],
        ),
    ]

    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=types.GenerateContentConfig(response_mime_type="text/plain")
    )

    return response.text.strip()



def summarize_text(text: str) -> str:
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"{text}\n\n{LINK_SUMMARY_PROMPT}")
            ],

        )
    ]

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(response_mime_type="text/plain")
        )
        return response.text.strip()
    except Exception as e:
        raise RuntimeError(f"Gemini text summary failed: {e}")
