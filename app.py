from flask import Flask, request, jsonify, render_template
import json
import openai
import os
from dotenv import load_dotenv
import traceback

app = Flask(__name__)

# 環境変数の読み込み
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
assistant_id = "asst_CSeqLFic7vinIyAhuekFn78G"  # そのままでOK

# 1️⃣ ブラウザで `https://assistant-app-msft.onrender.com/` にアクセス → フォームを表示
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")  # `templates/index.html` を表示

# 2️⃣ API のエンドポイント `/chat`（GET → 説明 / POST → 実際の処理）
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        return "Welcome to the chatbot API! Use /chat with a POST request to send messages."

    if request.method == 'POST':
        try:
            data = request.json
            user_message = data.get("message", "")

            if not user_message:
                return jsonify({"error": "メッセージが空です"}), 400

            # 1️⃣ OpenAI API のスレッド作成
            thread = openai.beta.threads.create()

            # 2️⃣ ユーザーのメッセージをスレッドに追加
            openai.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_message
            )

            # 3️⃣ Assistant を実行
            run = openai.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant_id
            )

            # 4️⃣ レスポンス取得（完了するまで待機）
            import time
            while True:
                run_status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                if run_status.status == "completed":
                    break
                time.sleep(1)

            # 5️⃣ Assistant の返答を取得
            messages = openai.beta.threads.messages.list(thread_id=thread.id)
            assistant_reply = messages.data[0].content[0].text.value

            # ✅ JSON 形式でレスポンスを返す（日本語対応）
            return app.response_class(
                response=json.dumps({"response": assistant_reply}, ensure_ascii=False),
                status=200,
                mimetype="application/json"
            )

        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

# 3️⃣ Flaskアプリケーションの実行
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)