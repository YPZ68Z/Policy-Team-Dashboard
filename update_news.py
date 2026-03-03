import feedparser
import google.generativeai as genai
import os
import datetime

# 設定您的 Gemini API Key
API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# 戰略雷達：包含亞太與澳洲專屬 RSS 來源
RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/asia/rss.xml", 
    "https://feeds.bbci.co.uk/news/world/australia/rss.xml", 
    "https://www.abc.net.au/news/feed/2942460/rss.xml", 
    "https://techcrunch.com/category/policy/feed/", 
    "https://www.reutersagency.com/feed/?taxonomy=best-sectors&post_type=best" 
]

def fetch_news():
    articles = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:15]: 
            articles.append(f"Title: {entry.title}\nLink: {entry.link}\nSummary: {entry.get('summary', '')}\n")
    return "\n".join(articles)

def generate_war_room_briefing(raw_news):
    # 維持優化後 12+4 戰略配額
    prompt = f"""
    You are the Chief Intelligence Officer for Meta's APAC Public Policy team.
    Review the following raw news items. You must select exactly 16 items based on the following strict allocation:
    
    Category A (12 items): Global Geopolitics & Meta APAC Policy Team must-knows (Tech regulation, AI, cross-strait tensions).
    Category B (4 items): Exclusively focused on Australia (e.g., Australian federal politics, eSafety regulation, News Media Bargaining Code).
    
    For each item, write a sharp, executive-level summary of exactly 100 words in Traditional Chinese (繁體中文) , then write a sharp, executive-level summary of exactly 50 words in English.
    Focus on the "Impact on Tech/Meta" and "Strategic Geopolitical value".
    
    Output the result in strict, clean HTML format. 
    Use <h1> for the main dashboard title.
    Use <h2> for "Category A: APAC & Global Geopolitics" and "Category B: Australia Strategic Radar".
    Use <h3> for the title of each news item.
    Use <a href> for links, and <p> for the summary. 
    Do not use markdown blocks in the final output, just pure raw HTML.
    
    Raw News:
    {raw_news}
    """
    response = model.generate_content(prompt)
    return response.text

def update_html(briefing_html):
    # 抓取標準 UTC 時間並加上標籤
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    current_time_utc = utc_now.strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # 注入 RWD 響應式設計與放大字體 (CSS)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>L8 Policy War Room Dashboard</title>
        <style>
            /* 基礎字體放大至 18px，提升手機閱讀舒適度 */
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
                line-height: 1.7; 
                padding: 5%; 
                max-width: 900px; 
                margin: auto; 
                background-color: #f4f4f9; 
                font-size: 18px; 
                color: #1c1e21;
            }}
            h1 {{ color: #1c1e21; border-bottom: 2px solid #1877f2; padding-bottom: 10px; font-size: 1.8em; line-height: 1.3; }}
            h2 {{ color: #1877f2; font-size: 1.4em; margin-top: 40px; border-left: 4px solid #1877f2; padding-left: 10px; }}
            h3 {{ font-size: 1.2em; margin-bottom: 5px; color: #1c1e21; }}
            .update-time {{ color: #606770; font-size: 0.9em; margin-bottom: 30px; background: #e4e6eb; display: inline-block; padding: 5px 10px; border-radius: 5px; font-weight: bold; }}
            .news-item {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 25px; }}
            .news-item a {{ text-decoration: none; color: #1877f2; font-weight: bold; font-size: 0.9em; display: inline-block; margin-bottom: 10px; }}
            .news-item a:hover {{ text-decoration: underline; }}
            .summary {{ color: #4b4f56; }}
            
            /* 手機版微調 */
            @media (max-width: 600px) {{
                body {{ font-size: 17px; padding: 15px; }}
                h1 {{ font-size: 1.5em; }}
                .news-item {{ padding: 20px; }}
            }}
        </style>
    </head>
    <body>
        <h1>Meta APAC Public Policy Intelligence Dashboard</h1>
        <div class="update-time">最後更新時間 (Last Sync): {current_time_utc}</div>
        {briefing_html}
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as file:
        file.write(html_content)

if __name__ == "__main__":
    print("Fetching raw intelligence...")
    raw_data = fetch_news()
    print("Generating executive briefings via LLM...")
    briefing = generate_war_room_briefing(raw_data)
    briefing = briefing.replace("```html", "").replace("```", "")
    print("Updating Dashboard...")
    update_html(briefing)
    print("War Room update complete.")
