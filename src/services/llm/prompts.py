# Define the prompt for summarization

SUMMARY_PROMPT = (
    "Summarize this video in 5-6 bullet points for internal reference. "
    "Highlight key ideas, events, or insights. Skip sponsor messages or intros."
)

# services/llm/prompt.py

IMAGE_DESCRIPTION_PROMPT = (
    "Describe the image and extract any text present. "
    "Provide a concise description and include any readable text found within the image."
)

LINK_SUMMARY_PROMPT = (
    "Summarize the following web page content in 5–7 concise bullet points. "
    "Make it easy to skim and focus on key ideas or takeaways only."
)
