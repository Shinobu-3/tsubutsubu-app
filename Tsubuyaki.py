from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///records.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ユーザーモデル
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))

# つぶやき記録モデル
class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.String(10))
    task = db.Column(db.String(100))
    comment = db.Column(db.Text)
    mistake = db.Column(db.Text)

# ユーザー登録画面
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            return "このIDはすでに使われています。"
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

# ログイン画面
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["user_id"]
        password = request.form["password"]
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["user_id"] = user.id
            return redirect(url_for("form"))
        else:
            return "ログイン失敗。IDまたはパスワードが間違っています。"
    return render_template("login.html")

# 入力画面
@app.route("/form", methods=["GET", "POST"])
def form():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        selected_tasks = request.form.getlist("tasks")
        today = date.today().isoformat()
        for task in selected_tasks:
            if task == "その他":
                task_name = request.form.get("task_その他") or "その他"
            else:
                task_name = task
            comment = request.form.get(f"comment_{task}")
            mistake = request.form.get(f"mistake_{task}")
            new_record = Record(
                user_id=session["user_id"],
                date=today,
                task=task_name,
                comment=comment,
                mistake=mistake
            )
            db.session.add(new_record)
        db.session.commit()
        return redirect(url_for("thanks"))

    return render_template("Tsubutsubu.html")

# 完了画面
@app.route("/thanks")
def thanks():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("thanks.html")

# ログアウト
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

# アプリ起動時にDB作成
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
