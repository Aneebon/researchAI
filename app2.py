import os
import arxiv
import requests
import json
import gradio as gr
import google.generativeai as genai
import base64
import openai
from flask import Flask, request, jsonify

# --- API KEYS ---
CORE_API_KEY = "fRP6JobTrnxWiFQZ9m8v7eOl3KMc21aX"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Please set the GEMINI_API_KEY environment variable.")
genai.configure(api_key=GEMINI_API_KEY)

# --- GEMINI MODEL CONFIG ---
model_name = "gemini-1.5-flash"
generation_config = {
    "temperature": 0.1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}
model = genai.GenerativeModel(model_name=model_name, generation_config=generation_config)

# --- FETCH ARXIV ---
def fetch_latest_arxiv_papers(query="all", max_results=10):
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        client = arxiv.Client()
        results = list(client.results(search))
        return results
    except Exception as e:
        return []

# --- FETCH CORE ---
def fetch_latest_core_papers(query="all", max_results=10):
    base_url = "https://api.core.ac.uk/v3/search/works"
    headers = {
        "Authorization": f"Bearer {CORE_API_KEY}",
        "Content-Type": "application/json"
    }
    core_query = "*" if query == "all" else f'title:"{query}" OR description:"{query}"'
    data = {
        "q": core_query,
        "limit": max_results,
        "sort": "date"
    }
    try:
        response = requests.post(base_url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        results = response.json()
        return results.get('data', [])
    except Exception as e:
        return []

# --- GAP ANALYSIS ---
def identify_research_gaps_and_ideas(arxiv_papers, core_papers):
    all_papers_info = []
    for paper in arxiv_papers:
        all_papers_info.append({
            "title": paper.title,
            "summary": paper.summary
        })
    for paper in core_papers:
        all_papers_info.append({
            "title": paper.get('title', 'No Title'),
            "summary": paper.get('description', 'No Summary')
        })
    if not all_papers_info:
        return "No papers found from either source or an error occurred during fetching."
    paper_summaries = ""
    for paper in all_papers_info:
        paper_summaries += f"Title: {paper['title']}\nSummary: {paper['summary']}\n\n"
    prompt = f"""
Analyze the following research paper summaries on a similar topic from multiple sources (arXiv and CORE). Your goal is to identify potential research gaps and propose new, creative research ideas based on these gaps. Do not extract limitations mentioned within the papers. Focus on identifying areas that are not fully explored or where further work is needed based on the synthesis of the provided summaries.

Research Paper Summaries:
{paper_summaries}

Based on these summaries, identify:
1.  Potential research gaps (areas that seem under-researched or could be expanded upon).
2.  New research ideas that address these gaps.

Present your findings clearly.
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error communicating with Gemini API: {e}"

def write_research_article(research_gap_idea):
    prompt = f"""
Given the following research gap or idea:
{research_gap_idea}

Write a detailed research article about this topic. The article should include:
An engaging introduction to the topic
Background and current state of research
Explanation of the identified research gap
Potential approaches or methods to address this gap
Possible impact or applications
A concise conclusion

Use clear, academic language and cite hypothetical references in APA style if needed (e.g., (Author, Year)).
Format the output clearly with sections.
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error communicating with Gemini API: {e}"

def generate_illustration_description(research_gap_idea):
    prompt = f"""
Given the following research gap or idea:
{research_gap_idea}

Describe an academic-style illustration that could visually represent this research idea. The description should be suitable for input to an AI image generation model (such as DALL-E or Stable Diffusion) and clearly depict the core concept in a way appropriate for a scientific article. Focus on key visual elements, style (e.g., scientific diagram, conceptual illustration), and the overall message.

Example: "A neural network diagram overlaid with data points representing patient health metrics, illustrating the application of AI in personalized medicine."

Write only the description for the AI image generation model.
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error communicating with Gemini API for illustration description: {e}"

def generate_image_from_description(description):
    try:
        response = openai.Image.create(
            prompt=description,
            n=1,
            size="512x512",
            api_key=OPENAI_API_KEY
        )
        image_url = response['data'][0]['url']
        return image_url  # Return the URL for Gradio to display
    except Exception as e:
        print("DALL·E error:", e)
        return None

# Add this function before your Gradio Blocks section
def generate_and_show_image(idea):
    description = generate_illustration_description(idea)
    image_path = generate_image_from_description(description)
    return description, image_path

# --- GRADIO APP (Two-step workflow) ---
with gr.Blocks() as demo:
    gr.Markdown("# Research Gap Finder and Article Generator")
    gr.Markdown("**Step 1:** Enter a research topic to find research gaps and new ideas.")
    topic = gr.Textbox(label="Enter a research topic")
    gap_output = gr.Textbox(label="Research Gaps and New Ideas", lines=15)
    find_gaps_btn = gr.Button("Find Gaps and Ideas")

    gr.Markdown("**Step 2:** Enter or paste a research gap/idea from above to generate a research article or illustration description.")
    idea_input = gr.Textbox(label="Enter a research gap or idea")
    with gr.Row():
        article_btn = gr.Button("Generate Article")
        illustration_btn = gr.Button("Generate Illustration Description")
    article_output = gr.Textbox(label="Generated Article", lines=25)
    illustration_output = gr.Textbox(label="Illustration Description", lines=8)
    
    # New: Button and input for generating image from description
    gr.Markdown("**Step 3:** (Optional) Edit the illustration description if needed, then generate the image.")
    image_desc_input = gr.Textbox(label="Illustration Description for Image Generation", lines=8)
    generate_image_btn = gr.Button("Generate Image from Description")
    image_output = gr.Image(label="Generated Image")
    download_output = gr.File(label="Download Image")  # Add this line

    # Step 1: Find gaps and ideas
    def step1_find_gaps(topic):
        arxiv_papers = fetch_latest_arxiv_papers(query=topic, max_results=10)
        core_papers = fetch_latest_core_papers(query=topic, max_results=10)
        if not arxiv_papers and not core_papers:
            return "Could not fetch papers for the given topic from either source."
        return identify_research_gaps_and_ideas(arxiv_papers, core_papers)

    find_gaps_btn.click(step1_find_gaps, inputs=topic, outputs=gap_output)

    # Step 2: Generate article
    article_btn.click(write_research_article, inputs=idea_input, outputs=article_output)
    illustration_btn.click(
        generate_illustration_description,
        inputs=idea_input,
        outputs=illustration_output
    )

    # When user clicks "Generate Illustration Description", also fill the image_desc_input box
    illustration_btn.click(
        generate_illustration_description,
        inputs=idea_input,
        outputs=image_desc_input
    )

    # Step 3: Generate image from description
    def generate_image_and_file(description):
        image_path = generate_image_from_description(description)
        return image_path, image_path  # Return for both image and file

    generate_image_btn.click(
        generate_image_and_file,
        inputs=image_desc_input,
        outputs=[image_output, download_output]
    )

app = Flask(__name__)

@app.route("/api/gap", methods=["POST"])
def find_gap():
    data = request.json
    topic = data["topic"]
    arxiv_papers = fetch_latest_arxiv_papers(query=topic, max_results=10)
    core_papers = fetch_latest_core_papers(query=topic, max_results=10)
    if not arxiv_papers and not core_papers:
        return jsonify({"error": "Could not fetch papers for the given topic from either source."}), 400
    gaps = identify_research_gaps_and_ideas(arxiv_papers, core_papers)
    return jsonify({"result": gaps})

@app.route("/api/article", methods=["POST"])
def write_article():
    data = request.json
    idea = data["idea"]
    article = write_research_article(idea)
    return jsonify({"result": article})

if __name__ == "__main__":
    demo.launch(debug=True)
    app.run(host="0.0.0.0", port=7860)
