arXiv-summary

実行すると昨日arXivに投稿された機械学習関連の論文のabstractの日本語訳が一覧(最大100件)になって出てきます  
arXivのAPIキーとLLMのAPIキーを使用しています。  

```
#ディレクトリ構成

code/
├── README.md
├── abs-ja/ #日本語の要約を格納
├── meta-data/ #論文のメタデータを格納
└── code/
    ├── arXiv.py #arXivから論文をとってくる
    ├── main.py #メインコード
    ├── summary.py #abstractを日本語に翻訳
    ├── message.py #Slackにメッセージを送信
    └── daily_runner.py #1日に1度コードを実行し、一連の処理を自動化
```
Thank you to arXiv for use of its open access interoperability. This service was not reviewed or approved by, nor does it necessarily express or reflect the policies or opinions of, arXiv
