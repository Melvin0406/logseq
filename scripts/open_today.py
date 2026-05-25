"""
Reads today's journal .md, converts it to HTML, and opens it in the browser.
Called by pull_and_open.bat after git pull so the HTML is always fresh.
"""

import sys
import datetime
import webbrowser
from pathlib import Path

import markdown as md

GRAPH_DIR = Path(__file__).parent.parent

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


def main():
    today = datetime.date.today()
    today_str = today.strftime("%Y年%m月%d日")
    journal_path = GRAPH_DIR / "journals" / today.strftime("%Y_%m_%d.md")

    if not journal_path.exists():
        print(f"No journal for today yet: {journal_path}")
        sys.exit(0)

    content = journal_path.read_text(encoding="utf-8")

    # Extract only the news section (stop before diary boilerplate)
    news_section = content.split("## 📔 今日の日記")[0].strip()

    body_html = md.markdown(news_section, extensions=["nl2br"])
    html = HTML_TEMPLATE.format(date=today_str, body=body_html)

    html_path = GRAPH_DIR / "assets" / "morning_news_today.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")

    webbrowser.open(html_path.as_uri())
    print(f"Opened: {html_path}")


if __name__ == "__main__":
    main()
