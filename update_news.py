import feedparser
import google.generativeai as genai
import os
import datetime

# 設定您的 Gemini API Key (稍後會在 GitHub Secrets 中設定)
API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# 設定要監控的全球戰略 RSS 來源 (地緣政治、經濟、科技政策)
# 1. 擴展戰略雷達：加入澳洲專屬 RSS 來源
RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/asia/rss.xml", # BBC 亞洲
    "https://feeds.bbci.co.uk/news/world/australia/rss.xml", # 新增：BBC 澳洲專區
    "https://www.abc.net.au/news/feed/2942460/rss.xml", # 新增：澳洲 ABC News (政治與政策)
    "https://techcrunch.com/category/policy/feed/", # TechCrunch 科技政策
    "https://www.reutersagency.com/feed/?taxonomy=best-sectors&post_type=best" # 路透社精選
]

def fetch_news():
    articles = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        # 為了確保 AI 有足夠的素材挑選澳洲新聞，將抓取量從 10 提升到 15
        for entry in feed.entries[:15]: 
            articles.append(f"Title: {entry.title}\nLink: {entry.link}\nSummary: {entry.get('summary', '')}\n")
    return "\n".join(articles)

def generate_war_room_briefing(raw_news):
    # 2. 升級 AI 戰略指令：強制配額 12+4
    prompt = f"""
    You are the Chief Intelligence Officer for Meta's APAC Public Policy team.
    Review the following raw news items. You must select exactly 16 items based on the following strict allocation:
    
    Category A (12 items): Global Geopolitics & Meta APAC Policy Team must-knows (Tech regulation, AI, cross-strait tensions).
    Category B (4 items): Exclusively focused on Australia (e.g., Australian commonwealth politics, eSafety regulation, News Media Bargaining Code, and ANZ regional dynamics).
    
    For each of the 16 items, write a sharp, executive-level summary of exactly 100 words in Traditional Chinese (繁體中文) and then write a sharp, executive-level summary of exactly 50 words in English. 
    Focus on the "Impact on Tech/Meta" and "Strategic Geopolitical value".
    
    Output the result in strict, clean HTML format. 
    Use <h1> for the main dashboard title.
    Use <h2> for "Category A: APAC & Global Geopolitics" and "Category B: Australia Strategic Radar".
    Use <h3> for the title of each news item.
    Use <a href> for links, and <p> for the 100-word summary. 
    Do not use markdown blocks (like ```html) in the final output, just pure raw HTML.
    
    Raw News:
    {raw_news}
    """
    response = model.generate_content(prompt)
    return response.text

def update_html(briefing_html):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>L8 Policy War Room Dashboard</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 900px; margin: auto; background-color: #f4f4f9; }}
            h1 {{ color: #1c1e21; border-bottom: 2px solid #1877f2; padding-bottom: 10px; }}
            .update-time {{ color: #606770; font-size: 0.9em; margin-bottom: 30px; }}
            .news-item {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            .news-item h2 {{ margin-top: 0; color: #1877f2; font-size: 1.2em; }}
            .news-item a {{ text-decoration: none; color: inherit; }}
            .news-item a:hover {{ text-decoration: underline; }}
            .summary {{ color: #1c1e21; }}
        </style>
    </head>
    <body>
        <h1>APAC Policy War Room Dashboard</h1>
        <div class="update-time">最後更新時間 (Last Sync): {current_time}</div>
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
    # 移除可能由 LLM 產生的 Markdown 標記，確保純 HTML
    briefing = briefing.replace("```html", "").replace("```", "")
    print("Updating Dashboard...")
    update_html(briefing)
    print("War Room update complete.")
