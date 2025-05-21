from flask import Flask, render_template, request, redirect, url_for, session
from datetime import date
import csv
import os
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # セッション維持に必要（任意の文字列）

# ここに絶対パス取得のコードを書く
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, "users.csv")

# 登録画面
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # users.csvがなければ作成（ヘッダー付き）
        if not os.path.exists("users.csv"):
            with open("users.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["username", "password"])

        # 既存ユーザー確認
        with open("users.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["username"] == username:
                    return "このIDはすでに使われています。"

        # 新しいユーザーを追加
        with open("users.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([username, password])

        return redirect(url_for("login"))

    return render_template("register.html")


# ログイン画面
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print("入力されたユーザー名:", username)
        print("入力されたパスワード:", password)

        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.csv")
        if not os.path.exists(csv_path):
            return "ユーザーが登録されていません。"

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                print("CSVの行:", row)  # ← ここで内容を表示
                if row["username"] == username and row["password"] == password:
                    print("ログイン成功！")
                    session["user"] = username
                    return redirect(url_for("form"))

        return "ログイン失敗。IDまたはパスワードが間違っています。"

    return render_template("login.html")



# 入力画面
@app.route("/form", methods=["GET", "POST"])
def form():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        selected_tasks = request.form.getlist("tasks")
        today = date.today().isoformat()

        with open("records.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for task in selected_tasks:
                if task == "その他":
                    task_name = request.form.get("task_その他") or "その他"
                else:
                    task_name = task
                comment = request.form.get(f"comment_{task}", "")
                mistake = request.form.get(f"mistake_{task}", "")
                writer.writerow([session["user"], today, task_name, comment, mistake])

        return redirect(url_for("thanks"))

    return render_template("Tsubutsubu.html")



# 完了画面
# @app.route("/thanks")
# def thanks():
#     if "user" not in session:
#         return redirect(url_for("login"))
#     return render_template("thanks.html")
@app.route("/thanks")
def thanks():
    if "user" not in session:
        return redirect(url_for("login"))

    # Flaskアプリのベースディレクトリ（Tsubuyaki.pyがある場所）
    base_dir = os.path.dirname(os.path.abspath(__file__))
    image_dir = os.path.join(base_dir, 'static', 'images')  # ←絶対パスに変換

    images = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    random_image = random.choice(images)
    image_url = f"/static/images/{random_image}"  # これはブラウザ用の相対パスでOK

    return render_template("thanks.html", image_url=image_url)



# CSV初期化用（ヘッダーのみ作成）
@app.route("/export")
def export_csv():
    if os.path.exists("records.csv"):
        return "すでにCSVが存在します（records.csv）"
    else:
        with open("records.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["User ID", "Date", "Task", "Comment", "Mistake"])
        return "CSVファイルを新規作成しました（records.csv）"


# ログアウト
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))


# 初期画面リダイレクト
@app.route("/")
def index():
    return redirect(url_for("login"))


# Flaskアプリ起動
if __name__ == "__main__":
    app.run(debug=True)
