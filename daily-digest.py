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
            
    # Filter out articles with non-news phrases or sources
    banned_sources = [
        "google news", "google news (india)", "etf daily news",
        "prnewswire", "globenewswire", "marketwatch", "free republic"
    ]
    banned_phrases = ["bulletin", "quiz", "podcast", "review of", "the daily", "press release"]
    
    filtered_articles = [
        article for article in all_articles
        if not any(phrase in (article.get("title", "") + article.get("description", "")).lower() for phrase in banned_phrases)
        and article.get("source", {}).get("name", "").lower() not in banned_sources
    ]

    # Remove duplicates and return the top 10 most recent articles
    unique_articles = {article['url']: article for article in filtered_articles}.values()
    shuffled_articles = list(unique_articles)
    shuffled_articles.sort(key=lambda x: x['publishedAt'], reverse=True)
    
    return shuffled_articles[:10]

def summarize_article(text):
    """Summarizes an article using the Hugging Face model."""
    if not text or len(text) < 100:
        return text

    try:
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summary = summarizer(text, max_length=60, min_length=40, do_sample=False)
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
    <title>QuickBytess Daily Digest – {today}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@700&family=Roboto&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Roboto', sans-serif;
            line-height: 1.6;
            color: #e0e0e0;
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
            background-color: #121212;
        }}
        .container {{
            background: #1E1E1E;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        }}
        h1 {{
            font-family: 'Poppins', sans-serif;
            font-size: 2.5rem;
            color: #FFFFFF;
            border-bottom: 1px solid #333;
            padding-bottom: 1rem;
        }}
        .article-item {{
            margin: 2rem 0;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid #333;
        }}
        .article-item:last-child {{
            border-bottom: none;
        }}
        h2 {{
            font-family: 'Poppins', sans-serif;
            font-size: 1.4rem;
            font-weight: 700;
            margin-top: 0;
            color: #FFFFFF;
            line-height: 1.4;
        }}
        p.summary {{
            font-family: 'Roboto', sans-serif;
            font-size: 1rem;
            color: #B0B0B0;
            margin-top: 0.5rem;
        }}
        .source {{
            font-style: italic;
            color: #888;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }}
        a {{
            color: #FF9800;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .cta {{
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #333;
            text-align: center;
        }}
        .cta-link {{
            color: #FF9800;
            font-size: 1.1rem;
            font-weight: bold;
            text-decoration: none;
        }}
        .cta-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>QuickBytess Daily Digest – {today}</h1>
        <p class="summary">Your daily dose of the most important headlines, curated and summarized in just a few minutes.</p>
        <hr style="border-color: #333;">
"""
    if articles:
        for article in articles:
            title = article.get("title", "No Title")
            source = article.get("source", {}).get("name", "Unknown Source")
            url = article.get("url", "#")
            description = article.get("description", "")
            
            summary = summarize_article(description)
            
            html_content += f"""
        <div class="article-item">
            <h2>{title}</h2>
            <p class="summary">{summary}</p>
            <p class="source">Source: <a href="{url}" target="_blank">{source}</a></p>
        </div>
"""
    else:
        html_content += """
        <div class="article-item">
            <p>No articles could be fetched today. Please check the news API.</p>
        </div>
"""
    
    html_content += f"""
        <div class="cta">
            <hr style="border-color: #333;">
            <p>💌 Like this QuickBytes? <br> Get it daily in your inbox for FREE → <a class="cta-link" href="#">Subscribe Here</a></p>
        </div>
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