# summary.py

import time
import json
import logging
from typing import List, Dict, Optional

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

class LLMTranslator:
    """
    Google Generative AI (google-generativeai) を使い、
    arXiv 論文の abstract を日本語に翻訳するクラス。
    429 エラー時には指数バックオフでリトライします。
    """

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-lite"):
        genai.configure(api_key=api_key)
        self.model_name = model_name
        logging.info(f"LLMTranslator initialized: model={self.model_name}")

    def translate_paper(self, paper: Dict) -> Dict:
        """
        単一論文の dict を受け取り、translated_abstract を付与して返す。
        """
        # モデル／チャットセッションの生成
        model = genai.GenerativeModel(self.model_name)
        chat = model.start_chat()

        prompt = (
            "以下の arXiv 論文の要旨を日本語に翻訳してください。\n\n"
            f"タイトル: {paper['title']}\n"
            f"Abstract: {paper['abstract']}\n\n"
            "=== 日本語翻訳 ===\n"
        )
        try:
            resp = chat.send_message(prompt)
            translated = resp.text.strip()
        except Exception as e:
            logging.error(f"翻訳エラー (ID={paper.get('id')}): {e}")
            translated = ""
        out = paper.copy()
        out['translated_abstract'] = translated
        return out

    def translate_paper_with_retry(self, paper: Dict, max_retries: int = 3) -> Dict:
        """
        429(ResourceExhausted) 時に指数バックオフでリトライ。
        """
        backoff = 4
        for attempt in range(1, max_retries + 1):
            try:
                return self.translate_paper(paper)
            except ResourceExhausted:
                logging.warning(
                    f"429 エラー (ID={paper.get('id')}), {backoff}s 後にリトライ {attempt}/{max_retries}"
                )
                time.sleep(backoff)
                backoff *= 2
        logging.error(f"最大リトライ超過 (ID={paper.get('id')}), スキップします")
        out = paper.copy()
        out['translated_abstract'] = ""
        return out

    def process_papers(self, papers: List[Dict], delay: float = 4.1) -> List[Dict]:
        """
        複数論文を逐次翻訳し、delay 秒待機。15RPM以内を担保。
        """
        translated = []
        for paper in papers:
            tr = self.translate_paper_with_retry(paper)
            translated.append(tr)
            time.sleep(delay)
        return translated

    def display_translated_papers(self, papers: List[Dict]) -> None:
        """
        翻訳結果をコンソールに一覧出力。
        """
        print("\n" + "=" * 80)
        print("翻訳結果")
        print("=" * 80)
        for idx, p in enumerate(papers, 1):
            print(f"[{idx}] {p['title']}")
            print(p['translated_abstract'] + "\n")

    def save_to_file(self, papers: List[Dict], filename: Optional[str] = None) -> str:
        """
        テキスト形式で保存。戻り値はファイル名。
        """
        if filename is None:
            filename = f"translated_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            for p in papers:
                f.write(f"Title: {p['title']}\n")
                f.write(p['translated_abstract'] + "\n")
                f.write("-" * 40 + "\n")
        return filename

    def save_to_json(self, papers: List[Dict], filename: Optional[str] = None) -> str:
        """
        JSON形式で保存。戻り値はファイル名。
        """
        if filename is None:
            filename = f"translated_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
        return filename
