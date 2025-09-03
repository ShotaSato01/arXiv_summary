# arXiv.py

import arxiv
from datetime import date, timedelta
from typing import List, Dict

def get_recent_papers(
    days_back: int = 1,
    categories: List[str] = None,
    max_results: int = 50
) -> List[arxiv.Result]:
    """
    arXiv から直近 days_back 日の論文を取得する。
    - categories: ['cs.LG', 'cs.AI', ...]
    - max_results: 最大取得件数
    """
    today = date.today()
    cutoff = today - timedelta(days=days_back)

    query = ""
    if categories:
        query = " OR ".join(f"cat:{c}" for c in categories)

    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )

    return [
        p for p in search.results()
        if p.published.date() >= cutoff
    ]


def extract_paper_data(papers: List[arxiv.Result]) -> List[Dict]:
    """
    arXiv の Result オブジェクトを dict に変換する。
    """
    data = []
    for p in papers:
        data.append({
            'id': p.entry_id.split('/')[-1],
            'title': p.title.strip(),
            'abstract': p.summary.strip(),
            'authors': [a.name for a in p.authors],
            'published': p.published.date().isoformat(),
            'categories': p.categories
        })
    return data


def display_papers(
    papers: List[arxiv.Result],
    title: str = "取得した論文一覧",
    show_full_abstract: bool = False
) -> None:
    """
    取得論文のタイトル／著者／公開日／要約をコンソール出力。
    """
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    for idx, p in enumerate(papers, 1):
        abs_txt = p.summary.strip()
        if not show_full_abstract and len(abs_txt) > 200:
            abs_txt = abs_txt[:200].rstrip() + "…"
        print(f"[{idx}] {p.title.strip()}")
        print(f"  著者: {', '.join(a.name for a in p.authors)}")
        print(f"  公開日: {p.published.date().isoformat()}")
        print(f"  要約: {abs_txt}\n")
