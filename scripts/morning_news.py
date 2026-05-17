"""
Fetches anime and tech/AI news via Gemini (with Google Search grounding),
appends it to today's Logseq journal page, and opens an HTML version in
the browser so Yomitan works for on-demand Japanese lookups.
"""

import os
import sys
import datetime
import webbrowser
from pathlib import Path

import markdown as md
from google import genai
from google.genai import types

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GRAPH_DIR = Path(os.environ.get("LOGSEQ_GRAPH_DIR", Path(__file__).parent.parent))

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🌅 おはようニュース — {date}</title>
  <style>
    :root {{
      --bg: #1e1e2e;
      --surface: #2a2a3e;
      --text: #cdd6f4;
      --accent: #89b4fa;
      --muted: #6c7086;
      --anime: #f38ba8;
      --tech: #a6e3a1;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: "Noto Serif JP", "Hiragino Mincho ProN", "Yu Mincho", Georgia, serif;
      font-size: 1.15rem;
      line-height: 2;
      padding: 2.5rem 1rem;
    }}
    .container {{
      max-width: 720px;
      margin: 0 auto;
    }}
    .page-title {{
      font-size: 1.4rem;
      color: var(--accent);
      margin-bottom: 2rem;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid var(--muted);
    }}
    h2 {{
      font-size: 1.15rem;
      margin: 2rem 0 0.8rem;
      padding: 0.3rem 0.75rem;
      border-radius: 4px;
      display: inline-block;
    }}
    h2:nth-of-type(1) {{ background: #3d1f25; color: var(--anime); }}
    h2:nth-of-type(2) {{ background: #1f3d24; color: var(--tech); }}
    ul {{ list-style: none; padding: 0; }}
    li {{
      padding: 0.6rem 0 0.6rem 1.2rem;
      border-bottom: 1px solid #2e2e42;
      text-indent: -1.2rem;
      padding-left: 2rem;
    }}
    li::before {{
      content: "・";
      color: var(--muted);
    }}
    .footer {{
      margin-top: 3rem;
      font-size: 0.8rem;
      color: var(--muted);
      text-align: center;
    }}
  </style>
</head>
<body>
  <div class="container">
    <p class="page-title">🌅 おはようニュース — {date}</p>
    {body}
    <p class="footer">Yomitan: hover over any word to look it up ✦ {date}</p>
  </div>
</body>
</html>
"""


def get_journal_path() -> Path:
    today = datetime.date.today()
    filename = today.strftime("%Y_%m_%d") + ".md"
    journal_dir = GRAPH_DIR / "journals"
    journal_dir.mkdir(parents=True, exist_ok=True)
    return journal_dir / filename


def fetch_news() -> str:
    client = genai.Client(api_key=GEMINI_API_KEY)
    today_str = datetime.date.today().strftime("%Y年%m月%d日")

    prompt = f"""
あなたはN1レベルの自然な日本語でニュースを書くライターです。
今日は{today_str}です。

以下の2カテゴリについて、最新ニュースをそれぞれ3〜4件調べて、
Logseqのジャーナルページに追記するMarkdown形式で書いてください。

**要件:**
- N1レベルの自然な日本語（硬すぎず、読みやすい）
- 各ニュースは箇条書き（`- `）で記載
- カテゴリは見出し（`## `）で区切る
- 各ニュース項目は1〜2文で要点を簡潔にまとめる

**出力フォーマット（このまま使う）:**

## 📺 アニメニュース
- （ニュース1）
- （ニュース2）
- （ニュース3）

## 💻 テクノロジー・AIニュース
- （ニュース1）
- （ニュース2）
- （ニュース3）
- （ニュース4）

上記フォーマットのみ出力してください。前置きや説明は不要です。
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )
    return response.text.strip()


DIARY_BOILERPLATE = """\
## 📔 今日の日記

**天気：**
**気分：**

今日は

---

**今日の一言（印象に残った表現・単語）：**
"""


def append_to_journal(news_text: str) -> Path:
    path = get_journal_path()
    today_str = datetime.date.today().strftime("%Y年%m月%d日")
    header = f"## 🌅 おはようニュース — {today_str}\n"
    block = f"\n{header}\n{news_text}\n\n{DIARY_BOILERPLATE}"

    existing = path.read_text(encoding="utf-8") if path.exists() else ""

    if "おはようニュース" in existing and today_str in existing:
        print(f"Today's news already in journal — skipping write.")
    else:
        with open(path, "a", encoding="utf-8") as f:
            f.write(block)
        print(f"News written to {path}")

    return path


def open_in_browser(news_text: str):
    today_str = datetime.date.today().strftime("%Y年%m月%d日")
    body_html = md.markdown(news_text, extensions=["nl2br"])
    html = HTML_TEMPLATE.format(date=today_str, body=body_html)

    html_path = GRAPH_DIR / "assets" / "morning_news_today.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")

    webbrowser.open(html_path.as_uri())
    print(f"Opened in browser: {html_path}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("Fetching news from Gemini...")
    news = fetch_news()
    print("--- Generated content ---")
    print(news)
    print("-------------------------")
    append_to_journal(news)
    open_in_browser(news)
