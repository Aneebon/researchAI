# researchAI
This project helps researchers and students quickly identify unexplored areas in scientific literature and brainstorm new research directions. It fetches recent papers from both arXiv and CORE, analyzes them using Google’s Gemini API, and presents actionable insights through an interactive Gradio web interface.
How It Works

This tool streamlines the process of discovering research gaps and generating new research ideas by combining open-access literature with advanced AI analysis-all in an easy-to-use web app.

Multi-Source Paper Retrieval
When you enter a research topic, the app automatically searches for relevant and recent papers from both arXiv and CORE, two of the world’s largest open-access research repositories. This ensures broad and up-to-date coverage across disciplines.

AI-Powered Content Analysis
Instead of just extracting limitations sections, the tool uses Google’s Gemini AI to read and synthesize the main ideas from multiple papers on the same topic. The AI reviews abstracts and summaries to understand current trends, methodologies, and findings.

Identification of Research Gaps
Gemini analyzes the collective body of literature to spot areas that are underexplored, disconnected, or missing entirely-these are potential research gaps. The process is similar to how modern AI tools like Insight7 and VOSviewer map and compare large volumes of research to highlight what’s new, what’s missing, and where contradictions or open questions remain.

Idea Generation
Based on the identified gaps, the AI creatively proposes new research questions or project ideas, helping you move from “what’s missing” to “what’s next.”

Interactive Results Display
All findings are presented in a clear, readable format using a Gradio web interface. You get synthesized research gaps and actionable new ideas in seconds, ready to inspire your next project or guide your literature review.
Stuff used:-
1. Large Language Models (LLMs)
Google Gemini API:
Provides state-of-the-art text understanding and generation, allowing the system to read, synthesize, and analyze multiple research papers to find gaps and propose new ideas.
(Comparable alternatives: OpenAI GPT-4, Anthropic Claude, Cohere Command, Hugging Face models).

2. Research Paper Aggregators and APIs
arXiv API:
Fetches recent and relevant open-access research papers in various fields.

CORE API:
Aggregates millions of open-access papers from repositories and journals worldwide, expanding coverage and diversity of sources.

3. Data Extraction and Summarization
Natural Language Processing (NLP):
Used to extract abstracts, summaries, and key information from papers, regardless of format.
Tools like Elicit, Consensus, and R Discovery automate data extraction and summarization for large-scale literature reviews.

4. Research Gap Identification Tools
AI-powered analysis:
Models like Gemini (or Insight7, Iris.ai, VOSviewer, Connected Papers) compare, cluster, and synthesize information from multiple papers to identify underexplored areas, trends, and gaps.

Visualization:
Tools such as VOSviewer and Connected Papers can visualize citation networks and topic clusters to highlight where research is dense or sparse.

5. User Interface
Gradio:
Provides a simple, interactive web interface for users to enter topics and view results without coding.

6. Supporting Libraries
Requests:
For making HTTP requests to APIs.

PyMuPDF:
For extracting text from PDF files (if needed).

tqdm:
For progress bars during batch processing.
