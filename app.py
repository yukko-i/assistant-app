from flask import Flask, request, jsonify
import json
import openai
import os
from dotenv import load_dotenv
import traceback  # 例外処理用

# アプリの設定
app = Flask(__name__)

# 環境変数の読み込み
load_dotenv()

# OpenAI API キーの設定
openai.api_key = os.getenv("OPENAI_API_KEY")
assistant_id = "asst_CSeqLFic7vinIyAhuekFn78G"  # そのままでOK

@app.route("/", methods=["GET"])
def home():
    return "Flask API is running! Try /chat with a message."

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        # 例: ブラウザでアクセスしたときの説明を表示
        return "Welcome to the chatbot API! Use /chat with a POST request to send messages."

    if request.method == 'POST':
        try:
            data = request.json
            user_message = data.get("message", "")

            if not user_message:
                return jsonify({"error": "メッセージが空です"}), 400

            # 1️⃣ 新しいスレッドを作成
            thread = openai.beta.threads.create()

            # 2️⃣ ユーザーのメッセージをスレッドに追加
            openai.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_message
            )

            # 3️⃣ Assistantを実行
            run = openai.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant_id
            )

            # 4️⃣ 実際のレスポンスを取得
            import time
            while True:
                run_status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                if run_status.status == "completed":
                    break
                time.sleep(1)

            # 5️⃣ Assistantの返答を取得
            messages = openai.beta.threads.messages.list(thread_id=thread.id)
            assistant_reply = messages.data[0].content[0].text.value

            # ✅ 修正: `json.dumps()` を使い `ensure_ascii=False` を指定
            return app.response_class(
                response=json.dumps({"response": assistant_reply}, ensure_ascii=False),
                status=200,
                mimetype="application/json"
            )

        except Exception as e:
            # 例外が発生した場合、詳細なエラーメッセージを出力
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

# Flaskアプリケーションの実行
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)