from src.database.pg_database import get_recent_entries

def generate_briefing():
    """Fetches recent entries and formats them into a briefing."""
    entries = get_recent_entries(limit=10)
    if not entries:
        return "No new knowledge captured in the last 24 hours."

    briefing = "**Elio's Memo: Daily Briefing**\n\n"
    briefing += "Here's a summary of what I've learned in the last 24 hours:\n\n"

    for entry in entries:
        url, summary, created_at = entry
        briefing += f"- **{summary}** ({url})\n"

    return briefing
