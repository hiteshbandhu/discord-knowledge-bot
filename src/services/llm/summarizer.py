from src.services.llm.gemini import generate_text_from_prompt

def summarize_entries(entries: list[tuple]) -> str:
    """Summarizes a list of database entries into a single, readable summary."""
    if not entries:
        return "No entries to summarize."

    # Prepare the content for the prompt
    content_to_summarize = ""
    for entry in entries:
        url, summary, _ = entry
        content_to_summarize += f"- {summary} ({url})\n"

    # Create the prompt for Gemini
    prompt = f"Please summarize the following entries into a concise list of bullet points. Each bullet point should represent one entry and be a single sentence:\n\n{content_to_summarize}"

    # Generate the summary
    summarized_text = generate_text_from_prompt(prompt)
    return summarized_text
