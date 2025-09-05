import os
import requests
import base64
from datetime import datetime
from transformers import pipeline

def fetch_top_headlines():
    """Fetches top 5-10 headlines using a free news API."""
    news_api_key = os.environ.get("NEWS_API_KEY")
    if not news_api_key:
        raise ValueError("NEWS_API_KEY environment variable not set.")
    
    # Using NewsAPI.org. You can replace with another service if needed.
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
        # Load the summarization model from Hugging Face
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
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
            
            text_to_summarize = content if content and len(content) > 100 else article.get("description", "")
            
            summary = summarize_article(text_to_summarize)
            
            markdown_content += f"### {i}. {title}\n"
            markdown_content += f"> **Source:** [{source}]({url})\n\n"
            markdown_content += f"{summary}\n\n"
    else:
        markdown_content += "No articles could be fetched today. Please check the news API.\n\n"

    return markdown_content

def post_to_wordpress(title, content):
    """Posts a new article to a WordPress site via its REST API."""
    # This is a placeholder URL. Replace it with your actual WordPress site URL.
    wordpress_url = "https://your-wordpress-site.com/wp-json/wp/v2/posts"
    
    # Replace with your WordPress username
    username = "manangupta.2607@gmail.com"
    password = os.environ.get("WORDPRESS_APP_PASSWORD")
    
    if not password:
        raise ValueError("WORDPRESS_APP_PASSWORD environment variable not set.")

    # The updated credentials line
    credentials = f"{username}:{password}"
    token = base64.b64encode(credentials.encode()).decode("utf-8")
    
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }

    post_data = {
        "title": title,
        "content": content,
        "status": "publish"
    }
    
    try:
        response = requests.post(wordpress_url, headers=headers, json=post_data)
        response.raise_for_status()
        print("Successfully posted to WordPress!")
        return response.json()
    except requests.RequestException as e:
        print(f"Error posting to WordPress: {e}")
        return None

if __name__ == "__main__":
    articles = fetch_top_headlines()
    digest_content = generate_digest_markdown(articles)
    
    # We still need a title for the blog post
    post_title = f"Pocket-Sized News Digest – {datetime.now().strftime('%B %d, %Y')}"
    
    # Post the content to WordPress
    post_to_wordpress(post_title, digest_content)
