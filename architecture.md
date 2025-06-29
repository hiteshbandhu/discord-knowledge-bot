# Project Architecture: Understanding the Discord Knowledge Bot

Welcome! This document is designed to help anyone, especially new contributors, understand how the Discord Knowledge Bot works under the hood. We'll break down its components, how they interact, and the reasoning behind our design choices.

## 1. What is the Discord Knowledge Bot?

Imagine a smart assistant for your Discord server. This bot's main job is to:
1.  **Capture Information:** It can "read" content from various online sources like web pages, YouTube videos, and even images.
2.  **Process & Store:** It intelligently processes this information and stores it in a way that makes it easy to find later.
3.  **Share Knowledge:** It can then provide summaries, answer questions, or deliver daily briefings directly within your Discord server.

Our goal is to make knowledge easily accessible and digestible for Discord communities.

## 2. Why This Architecture? (Design Philosophy)

We've chosen a modular and layered architecture for several key reasons:

*   **Modularity:** Each major function (like scraping, database interaction, or LLM processing) is separated into its own component.
    *   **Benefit:** This makes the code easier to understand, test, and maintain. If we want to add a new type of scraper, we only need to touch the `scrapers` module, not the entire bot.
*   **Scalability:** By separating concerns, we can potentially scale different parts of the system independently in the future if needed.
*   **Flexibility:** If we decide to switch databases, use a different LLM provider, or add new content sources, the impact on other parts of the system is minimized.
*   **Clarity:** A clear separation of duties helps new developers quickly grasp where specific functionalities reside.

## 3. Key Components Explained

Let's dive into the main building blocks of the bot:

### 3.1. The Discord Bot Core (`src/discord/discord_bot.py`)

*   **Role:** This is the "face" of our bot. It's the part that directly communicates with Discord.
*   **What it does:**
    *   **Listens for Commands:** It constantly listens for commands typed by users in Discord (e.g., `/brief`, `/scrape`).
    *   **Routes Requests:** Once a command is received, it acts like a central dispatcher, sending the request to the appropriate internal service to handle the actual work.
    *   **Sends Responses:** It takes the results from other services and formats them nicely before sending them back to the Discord channel.
    *   **Manages Scheduled Tasks:** It also handles automated tasks like sending out daily knowledge briefings.

### 3.2. The Scrapers (`src/adapters/scrapers/`)

*   **Role:** These are the "information gatherers." Their job is to go out to the internet and extract content from different types of sources.
*   **Why separate scrapers?** Different websites and media types require different techniques to extract content. Having separate scrapers keeps this complexity isolated.
*   **Components:**
    *   `firecrawl_adapter.py`: Designed to scrape content from regular web pages. We use an external service (Fircrawl) for robust web scraping.
    *   `youtube.py`: Specifically built to handle YouTube links, transcribing video content into text.
    *   `images.py`: Focuses on extracting text from images (e.g., using Optical Character Recognition - OCR).

### 3.3. The Databases (`src/database/`)

*   **Role:** This is where all the captured knowledge lives. We use two types of databases for different purposes.
*   **Why two databases?**
    *   **PostgreSQL (`pg_database.py`):** This is a traditional relational database. It's excellent for storing structured data like the original text content, metadata (like URL, date, author), and relationships between pieces of information. We use it for reliable, long-term storage and easy querying of specific entries.
    *   **ChromaDB (`chroma_db.py`):** This is a "vector database." It's specialized for storing numerical representations (called "embeddings") of text. These embeddings allow us to perform "semantic search" – meaning you can search for the *meaning* of content, not just exact keywords. For example, searching for "fast cars" might return results about "sports vehicles."
*   **How they work together:** When new content is scraped, the raw text goes into PostgreSQL, and its numerical "meaning" (embedding) goes into ChromaDB.

### 3.4. LLM Services (`src/services/llm/`)

*   **Role:** These services bring the "intelligence" to the bot, powered by Large Language Models (LLMs).
*   **Why a separate LLM module?** This allows us to easily swap out different LLM providers (e.g., switch from Gemini to another model) or add new LLM-powered features without affecting other parts of the bot.
*   **Components:**
    *   `gemini.py`: Our primary interface for interacting with the Google Gemini LLM. It handles sending prompts and receiving responses.
    *   `summarizer.py`: Uses the LLM to condense long pieces of text into short, readable summaries.
    *   `prompts.py`: A collection of predefined "instructions" (prompts) that we send to the LLM to guide its behavior (e.g., "Summarize this text in bullet points").

### 3.5. Persistence Service (`src/services/persist/persist_to_db.py`)

*   **Role:** This service acts as the "data manager." It's responsible for taking the raw content from the scrapers and ensuring it's correctly saved into *both* our PostgreSQL and ChromaDB databases.
*   **What it does:** It orchestrates the process of storing the content, generating its embeddings (numerical representations), and then saving both the content and its embeddings.

### 3.6. Daily Briefing Service (`src/services/daily_briefing.py`)

*   **Role:** This service automates the delivery of knowledge.
*   **What it does:** At a scheduled time each day, it gathers the most recent information from the database, uses the LLM to summarize it, and then sends this summary to a designated Discord channel.

### 3.7. Utilities (`src/utils/`)

*   **Role:** This folder contains small, reusable helper functions that don't fit into the main components but are useful across the application.
*   **Example:** `detect_link_type.py`: This function is crucial for determining if a given URL is a regular webpage, a YouTube video, or something else, so the bot knows which scraper to use.

## 4. How Information Flows: Data Flow Diagrams

Let's visualize how data moves through the system.

### 4.1. Overall Data Flow (Scraping to Storage)

[[DIAGRAM IN [README](./README.md)]]

**Explanation:**
1.  A Discord user tells the bot to `/scrape` a URL.
2.  The `Discord Bot Core` receives this command and uses a utility to figure out what kind of link it is (webpage, YouTube, image).
3.  Based on the link type, the request is sent to the appropriate `Scraper`.
4.  The `Scraper` extracts the relevant content (text, transcription, OCR).
5.  The `Persistence Service` takes this extracted content.
6.  It then stores the raw content and any related information (metadata) in the `PostgreSQL Database`.
7.  At the same time, it generates a numerical "embedding" of the content's meaning and stores this in the `ChromaDB (Vector Database)`.

### 4.2. Daily Briefing Data Flow

This diagram illustrates how the daily briefing is generated and delivered.

```mermaid
graph TD
    J[Scheduler (Internal)] -->|1. Triggers Daily Briefing| K(Daily Briefing Service)
    K -->|2. Fetches Recent Entries| L[PostgreSQL Database]
    L -->|3. Recent Entries| M(LLM Summarizer Service)
    M -->|4. Summarized Text| N(Discord Bot Core)
    N -->|5. Sends Briefing to Channel| O[Discord Channel]
```

**Explanation:**
1.  An internal `Scheduler` (part of the bot's core) triggers the `Daily Briefing Service` at a set time.
2.  The `Daily Briefing Service` asks the `PostgreSQL Database` for all new knowledge entries since the last briefing.
3.  The `PostgreSQL Database` returns these `Recent Entries`.
4.  The `LLM Summarizer Service` takes these entries and uses the LLM to create a concise summary.
5.  The `Discord Bot Core` receives this `Summarized Text`.
6.  Finally, the `Discord Bot Core` sends the formatted `Briefing` message to the designated `Discord Channel`.

## 5. Getting Started

Now that you have a high-level understanding, you can dive into the code!
*   Start by looking at `src/main.py` to see how the bot is initialized.
*   Explore `src/discord/discord_bot.py` to understand how commands are handled.
*   Pick a service (e.g., a scraper or the summarizer) that interests you and see how it's implemented.

Feel free to ask questions and contribute!
