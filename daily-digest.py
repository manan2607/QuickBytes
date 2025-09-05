import os
import requests
from datetime import datetime
from transformers import pipeline

def fetch_top_headlines():
    """Fetches top 5-10 headlines using a free news API."""
    news_api_key = os.environ.get("NEWS_API_KEY")
    if not news_api_key:
        raise ValueError("NEWS_API_KEY environment variable not set.")
    
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={news_api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("articles", [])[:10]
    except requests.RequestException as e:
        print(f"Error fetching news: {e}")
        return []

def summarize_article(text):
    """Summarizes an article using the Hugging Face model."""
    try:
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summary = summarizer(text, max_length=130, min_length=40, do_sample=False)
        return summary[0]["summary_text"]
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return "Summary not available."

def generate_digest_markdown(articles):
    """Generates the full Markdown content for the blog post, including Jekyll front matter."""
    today = datetime.now()
    post_title = f"Pocket-Sized News Digest – {today.strftime('%B %d, %Y')}"
    
    # Jekyll requires a YAML front matter at the top of the Markdown file
    markdown_content = f"""---
layout: post
title: "{post_title}"
date: {today.isoformat()}
---

Your daily dose of the most important news, summarized and delivered straight to you.

---

"""
    if articles:
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No Title")
            source = article.get("source", {}).get("name", "Unknown Source")
            url = article.get("url", "#")
            content = article.get("content", "")
            
            text_to_summarize = content if content and len(content) > 100 else article.get("description", "")
            
            summary = summarize_article(text_to_summarize)
            
            markdown_content += f"### {i}. {title}\n"
            markdown_content += f"> **Source:** [{source}]({url})\n\n"
            markdown_content += f"{summary}\n\n"
    else:
        markdown_content += "No articles could be fetched today. Please check the news API.\n\n"

    return post_title, markdown_content

if __name__ == "__main__":
    articles = fetch_top_headlines()
    post_title, markdown_content = generate_digest_markdown(articles)
    
    # Create a Jekyll-compliant filename (e.g., 2025-09-06-pocket-sized-news-digest.md)
    filename = f"{datetime.now().strftime('%Y-%m-%d')}-{post_title.replace(' ', '-').lower()}.md"
    
    # Ensure the _posts directory exists
    os.makedirs("_posts", exist_ok=True)
    
    filepath = os.path.join("_posts", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    print(f"Daily digest generated and saved to {filepath}")