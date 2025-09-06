import os
import requests
from datetime import datetime
from transformers import pipeline
import random

def fetch_diverse_news():
    """Fetches a diverse set of news articles by topic and shuffles them."""
    news_api_key = os.environ.get("NEWS_API_KEY")
    if not news_api_key:
        raise ValueError("NEWS_API_KEY environment variable not set.")
    
    topics = [
        "artificial intelligence",
        "climate change",
        "global economy",
        "scientific discovery",
        "international politics",
        "space exploration",
        "medical research",
        "movie industry",
        "sports",
        "culture"
    ]
    
    base_url = "https://newsapi.org/v2/everything"
    all_articles = []
    
    for topic in topics:
        params = {
            "q": topic,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": 2,
            "apiKey": news_api_key
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            all_articles.extend(data.get("articles", []))
        except requests.RequestException as e:
            print(f"Error fetching news for topic '{topic}': {e}")
            
    unique_articles = {article['url']: article for article in all_articles}.values()
    shuffled_articles = list(unique_articles)
    random.shuffle(shuffled_articles)
    
    return shuffled_articles[:10]

def summarize_article(text):
    """Summarizes an article using the Hugging Face model."""
    try:
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summary = summarizer(text, max_length=130, min_length=40, do_sample=False)
        return summary[0]["summary_text"]
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return "Summary not available."

def generate_html_digest(articles):
    """Generates the full HTML content for the blog post."""
    today = datetime.now().strftime("%B %d, %Y")
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QuickBytes Daily Digest – {today}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #e0e0e0;
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
            background-color: #121212;
        }}
        .container {{
            background: #1e1e1e;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }}
        h1 {{
            font-size: 2.5rem;
            color: #bb86fc;
            border-bottom: 2px solid #333;
            padding-bottom: 1rem;
        }}
        .article-item {{
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #333;
        }}
        .article-item:last-child {{
            border-bottom: none;
        }}
        h2 {{
            font-size: 1.5rem;
            margin-top: 0;
            color: #f0f0f0;
        }}
        .source {{
            font-style: italic;
            color: #a0a0a0;
            font-size: 0.9rem;
        }}
        a {{
            color: #bb86fc;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌍 Today in 2 Minutes – {today}</h1>
        <p>Your daily dose of the most important news, summarized and delivered straight to you.</p>
        <hr style="border-color: #333;">
"""
    if articles:
        for article in articles:
            title = article.get("title", "No Title")
            source = article.get("source", {}).get("name", "Unknown Source")
            url = article.get("url", "#")
            content = article.get("content", "")
            
            text_to_summarize = content if content and len(content) > 100 else article.get("description", "")
            
            summary = summarize_article(text_to_summarize)
            
            html_content += f"""
        <div class="article-item">
            <h2>{title}</h2>
            <p class="source">Source: <a href="{url}" target="_blank">{source}</a></p>
            <p>{summary}</p>
        </div>
"""
    else:
        html_content += """
        <div class="article-item">
            <p>No articles could be fetched today. Please check the news API.</p>
        </div>
"""
    
    html_content += """
    </div>
</body>
</html>
"""
    return html_content

if __name__ == "__main__":
    articles = fetch_diverse_news()
    html_content = generate_html_digest(articles)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("Daily digest generated and saved to index.html")