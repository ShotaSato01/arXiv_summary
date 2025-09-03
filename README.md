arXiv-summary

実行すると昨日arXivに投稿された機械学習関連の論文のabstractの日本語訳が一覧になって出てきます  
arXivのAPIキーとLLMのAPIキーを使用しています。  

```
#ディレクトリ構成

code/
├── README.md
└── code/
    ├── arXiv.py arXivから論文をとってくる
    ├── main.py メインコード
    └── summary.py abstractを日本語に翻訳
```