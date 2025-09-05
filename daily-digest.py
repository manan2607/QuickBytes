import os
import requests
from datetime import datetime
from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

if not NEWS_API_KEY:
    raise ValueError("NEWS_API_KEY environment variable not set.")

def fetch_top_headlines():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("articles", [])[:10]
    except requests.RequestException as e:
        print(f"Error fetching news: {e}")
        return []

def summarize_article(text):
    try:
        summary = summarizer(text, max_length=130, min_length=40, do_sample=False)
        return summary[0]["summary_text"]
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return "Summary not available."

def generate_digest_markdown(articles):
    """Generates the full Markdown content for the blog post."""
    today = datetime.now().strftime("%B %d, %Y")
    
    markdown_content = f"# 🌍 Today in 2 Minutes – {today}\n\n"
    markdown_content += "Your daily dose of the most important news, summarized and delivered straight to you.\n\n"
    markdown_content += "---\n\n"
    
    if articles:
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No Title")
            source = article.get("source", {}).get("name", "Unknown Source")
            url = article.get("url", "#")
            content = article.get("content", "")
            
            text_to_summarize = content if content else article.get("description", "")
            
            if text_to_summarize and len(text_to_summarize) > 100:
                summary = summarize_article(text_to_summarize)
            else:
                summary = "Brief summary unavailable for this article."

            markdown_content += f"### {i}. {title}\n"
            markdown_content += f"> **Source:** [{source}]({url})\n\n"
            markdown_content += f"{summary}\n\n"

    else:
        markdown_content += "No articles could be fetched today. Please check the news API.\n\n"

    markdown_content += "---\n\n"
    markdown_content += "💌 Enjoyed this quick digest?\n\n"
    markdown_content += f"Get it daily in your inbox for FREE → [Subscribe Here](https://your-substack-link.com)\n\n"
    markdown_content += """
<form action="https://yournewsletter.substack.com/subscribe" method="post" target="_blank">
  <input type="email" name="email" placeholder="Enter your email" required>
  <button type="submit">Subscribe</button>
</form>
"""
    return markdown_content

if __name__ == "__main__":
    articles = fetch_top_headlines()
    digest = generate_digest_markdown(articles)
    
    with open("daily_digest.md", "w", encoding="utf-8") as f:
        f.write(digest)
    
    print("Daily digest generated and saved to daily_digest.md")