from flask import Flask, render_template, request
from datetime import date
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///records.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10))
    user_id = db.Column(db.String(20))
    name = db.Column(db.String(50))
    task = db.Column(db.Text)
    mistake = db.Column(db.Text)
    tsubutsubu = db.Column(db.Text)
    tomorrow = db.Column(db.Text)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        record = Record(
            date=date.today().isoformat(),
            user_id=request.form['user_id'],
            name=request.form['name'],
            task=request.form['task'],
            mistake=request.form['mistake'],
            tsubutsubu=request.form['tsubutsubu'],
            tomorrow=request.form['tomorrow']
        )
        db.session.add(record)
        db.session.commit()
        return "送信が完了しました！"
    return render_template("Tsubutsubu.html")
