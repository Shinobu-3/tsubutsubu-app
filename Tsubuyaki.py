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
        if not os.path.exists(csv_path):
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["username", "password"])

        # 既存ユーザー確認
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["username"].strip() == username.strip():
                    return "このIDはすでに使われています。"

        # 新しいユーザーを追加
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([username, password])

        return redirect(url_for("login"))

    return render_template("register.html")


# ログイン画面
@app.route("/login", methods=["GET", "POST"])
def login():
    next_page = request.args.get("next", url_for("form"))  # デフォルトは form（つぶやき画面）

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        next_page = request.form.get("next", url_for("form"))  # POSTから再取得

        print("入力されたユーザー名:", username)
        print("入力されたパスワード:", password)

        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.csv")
        if not os.path.exists(csv_path):
            return "ユーザーが登録されていません。"

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                print("CSVの行:", row)
                if row["username"] == username and row["password"] == password:
                    print("ログイン成功！")
                    session["user_id"] = username  # ← mypage に合わせて user_id に統一
                    return redirect(next_page)

        return "ログイン失敗。IDまたはパスワードが間違っています。"

    return render_template("login.html", next=next_page)




# 入力画面
@app.route("/form", methods=["GET", "POST"])
def form():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        selected_tasks = request.form.getlist("tasks")
        today = date.today().isoformat()

        # CSVファイルの絶対パスを取得（Flaskファイルと同じ場所に保存）
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "records.csv")

        with open(file_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for task in selected_tasks:
                if task == "その他":
                    task_name = request.form.get("task_その他") or "その他"
                else:
                    task_name = task
                comment = request.form.get(f"comment_{task}", "")
                mistake = request.form.get(f"mistake_{task}", "")
                writer.writerow([session["user_id"], today, task_name, comment, mistake])

        return redirect(url_for("thanks"))

    return render_template("Tsubutsubu.html")

# 完了画面

@app.route("/thanks")
def thanks():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Flaskアプリのベースディレクトリ（Tsubuyaki.pyがある場所）
    base_dir = os.path.dirname(os.path.abspath(__file__))
    image_dir = os.path.join(base_dir, 'static', 'images','food')  # ←絶対パスに変換

    # 日本語タイトル対応表（← ここに } を追加して閉じます！）
    title_dict = {
        "ichigocake": "いちごのショートケーキ",
        "katsucurry": "カツカレー",
        "hamburg": "ハンバーグ",
        "chouxalacreame": "シュークリーム",
        "takoyaki": "たこやき",
        "dorayaki": "どら焼き",
        "hamburger": "ハンバーガー",
        "nikuman": "肉まん",
        "norimaki": "海苔巻き",
        "pizza": "ピザ",
        "takoyaki": "たこやき",
        "montblanc":"モンブラン",
        "gateauauchocolat":"ガトーショコラ",
        "eclairauchocolat":"チョコエクレア"

    }
     # dice.png 以外の画像一覧を取得
    images = [f for f in os.listdir(image_dir)
              if f.lower().endswith(('.png', '.jpg', '.jpeg'))
              and f != 'dice.jpg']

    # ファイル名からタイトル生成（例：01_cookie.jpg → cookie）
    image_info = []
    for filename in images:
        name = os.path.splitext(filename)[0]
        key = name.split("_", 1)[-1] if "_" in name else name
        title = title_dict.get(key.lower(), key)
        image_info.append({"file": filename, "title": title})

    return render_template("thanks.html", images=image_info)


# CSV初期化用（ヘッダーのみ作成）
import os

@app.route("/export")

def export_csv():
    file_path = os.path.abspath("records.csv")
    print("CSVファイルの保存先:", file_path)

    if os.path.exists(file_path):
        return "すでにCSVが存在します（records.csv）"
    else:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["User ID", "Date", "Task", "Comment", "Mistake"])
        return "CSVファイルを新規作成しました（records.csv）"
    
@app.route("/mypage", methods=["GET"])
def mypage():
    if "user_id" not in session:
        return redirect(url_for("login", next=request.path))

    user_id = session["user_id"]
    selected_date = request.args.get("date")  # URLパラメータから日付を取得
    user_records = []

    base_dir = os.path.dirname(os.path.abspath(__file__))
    record_path = os.path.join(base_dir, "records.csv")

    if not os.path.exists(record_path):
        return "記録ファイル（records.csv）が見つかりません。"

    with open(record_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["User ID"] == user_id:
                if not selected_date or row["Date"] == selected_date:
                    user_records.append(row)

    return render_template("mypage.html", records=user_records, user_id=user_id, selected_date=selected_date)

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
