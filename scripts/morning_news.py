"""
Fetches anime and tech/AI news via Gemini (with Google Search grounding)
and appends it to today's Logseq journal page in natural Japanese.
"""

import os
import json
import datetime
from pathlib import Path

import google.generativeai as genai
from google.generativeai.types import Tool, GoogleSearchRetrieval

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GRAPH_DIR = Path(os.environ.get("LOGSEQ_GRAPH_DIR", Path(__file__).parent.parent))

genai.configure(api_key=GEMINI_API_KEY)


def get_journal_path() -> Path:
    today = datetime.date.today()
    filename = today.strftime("%Y_%m_%d") + ".md"
    journal_dir = GRAPH_DIR / "journals"
    journal_dir.mkdir(parents=True, exist_ok=True)
    return journal_dir / filename


def fetch_news() -> str:
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        tools=[Tool(google_search=GoogleSearchRetrieval())],
    )

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
- 難しい漢字や専門用語には必要に応じてルビや補足を添える

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

    response = model.generate_content(prompt)
    return response.text.strip()


def append_to_journal(news_text: str):
    path = get_journal_path()
    today_str = datetime.date.today().strftime("%Y年%m月%d日")

    header = f"## 🌅 おはようニュース — {today_str}\n"
    block = f"\n{header}\n{news_text}\n"

    existing = path.read_text(encoding="utf-8") if path.exists() else ""

    # Avoid duplicate entries if script is run twice
    if "おはようニュース" in existing and today_str in existing:
        print(f"Today's news already written to {path}. Skipping.")
        return

    with open(path, "a", encoding="utf-8") as f:
        f.write(block)

    print(f"News written to {path}")


if __name__ == "__main__":
    print("Fetching news from Gemini...")
    news = fetch_news()
    print("--- Generated content ---")
    print(news)
    print("-------------------------")
    append_to_journal(news)
