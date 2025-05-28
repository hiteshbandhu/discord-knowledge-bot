from database.pg_database import save_to_postgres
from database.chroma_db import add_document
from models.database import ExtractedContent

def persist_to_db(content: ExtractedContent):

    try:
        # Save to Neon database
        result = save_to_postgres(
            url=content.url,
            content=content.content,
            summary=content.summary,
            source=content.metadata.get("source") if content.metadata else None,
            metadata=content.metadata
        )
        if result == "Already Indexed. Thanks for sending!":
            return result

        # Determine text to embed
        text_to_embed = content.content or content.summary
        if text_to_embed:
            metadata = {
                "url": content.url or "",
                "title": content.title or "",
                "media_type": content.media_type or "",
                "tags": ",".join(content.tags) if content.tags else "",
            }
            print("Adding to ChromaDB")
            add_document(doc_id=content.url, content=text_to_embed, metadata=metadata)

    except Exception as e:
        print(f"Error persisting to database: {e}")
        return f"Error persisting to database: {e}"

    return "Persisted to database ✅"
