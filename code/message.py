from os import getenv
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime

# 取得したボットトークンを設定
env_path = "../key.env"
load_dotenv(env_path)
slack_bot_token = getenv("SLACK_BOT_TOKEN")

client = WebClient(token=slack_bot_token)


ts = datetime.now().strftime("%Y%m%d")
channel_id = getenv("CHANNEL_ID") # 送信先のチャンネルID
file_path = f'../abs-ja/arxiv_translated_{ts}.txt' # 添付したいファイルのパス
initial_comment = "本日のレポートです！" # ファイルと一緒に送信するメッセージ
 
try:
    # files_upload_v2メソッドでファイルをアップロード
    response = client.files_upload_v2(
        channel=channel_id,
        file=file_path,
        title=f"論文abs-ja_{ts}", # Slack上でのファイルタイトル
        initial_comment=initial_comment,
    )
    print("ファイルが正常に送信されました。")

except FileNotFoundError:
    response = client.chat_postMessage(
        channel=channel_id,
        text="昨日は新しい論文が投稿されなかったようです...😢",
    )
    print(f"エラー: ファイルが見つかりません。パスを確認してください: {file_path}")
except SlackApiError as e:
    # エラーが発生した場合
    print(f"エラー: {e.response['error']}")