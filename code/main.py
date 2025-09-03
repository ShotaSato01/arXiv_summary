# main.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from dotenv import load_dotenv

from arXiv import get_recent_papers, extract_paper_data, display_papers
from summary import LLMTranslator

def load_api_key(env_path: str = "key.env") -> str:
    load_dotenv(env_path)
    from os import getenv
    key = getenv("GEMINI_API_KEY")
    if not key:
        logging.error("❌ GEMINI_API_KEY が設定されていません（key.env を確認してください）。")
        raise SystemExit(1)
    logging.info("✅ APIキー読み込み完了")
    return key

def main():
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.info("🛰 arXiv→LLM 翻訳システム 起動（クイックモード）")

    api_key = load_api_key("key.env")
    days_back, categories, max_results = 1, ["cs.CL"], 100
    logging.info(f"設定: 過去{days_back}日, カテゴリ{categories}, 最大{max_results}件")

    try:
        raw = get_recent_papers(days_back, categories, max_results)
        if not raw:
            logging.warning("取得データなし。終了します。")
            return
        logging.info(f"✅ arXiv から {len(raw)} 件取得")
    except Exception as e:
        logging.error(f"❌ arXiv 取得時例外: {e}")
        return

    papers = extract_paper_data(raw)
    logging.info(f"✅ データ整形完了: {len(papers)} 件")
    display_papers(raw, title="取得論文一覧", show_full_abstract=False)

    translator = LLMTranslator(api_key)
    logging.info("🔄 翻訳処理開始 (delay=4.1s)")
    translated = translator.process_papers(papers, delay=4.1)
    if not translated:
        logging.warning("翻訳結果なし。終了します。")
        return
    logging.info(f"✅ 翻訳完了: {len(translated)} 件")

    translator.display_translated_papers(translated)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    txt_file, json_file = f"arxiv_translated_{ts}.txt", f"arxiv_translated_{ts}.json"
    try:
        translator.save_to_file(translated, txt_file)
        translator.save_to_json(translated, json_file)
        logging.info(f"✅ 保存完了: {txt_file}, {json_file}")
    except Exception as e:
        logging.error(f"❌ 保存時例外: {e}")

    logging.info("🎉 全処理完了！")

if __name__ == "__main__":
    main()
