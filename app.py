from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import math
import json
import pymysql


with open("main.json", "r") as c:
    paras = json.load(c)["paras"]

app = Flask(__name__)
app.config["SECRET_KEY"] = "@iamshahnaz"

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/todolist"
db = SQLAlchemy(app)


from flask import jsonify

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    desc = db.Column(db.String(160), nullable=False)
    done = db.Column(db.Boolean, default=False)


@app.route("/")
def home():

    todo_list = Todo.query.filter_by().all()
    last = math.ceil(len(todo_list) / int(paras["no_of_todos"]))

    page = request.args.get("page")
    if not str(page).isnumeric():
        page = 1

    page = int(page)
    todo_list = todo_list[
        (page - 1) * int(paras["no_of_todos"]) : (page - 1) * int(paras["no_of_todos"])
        + int(paras["no_of_todos"])
    ]

    # pagination logic
    if page == 1:
        next = "/?page=" + str(page + 1) if (page + 1) <= last else "#"
        prev = "#"

    elif page == last:
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        next = "/?page=" + str(page + 1)
        prev = "/?page=" + str(page - 1)

    return render_template(
        "index.html", paras=paras, todo_list=todo_list, prev=prev, next=next
    )


@app.route("/add", methods=["GET", "POST"])
def add_todo():
    if request.method == "POST":
        title = request.form.get("title")
        desc = request.form.get("desc")
        entry = Todo(title=title, desc=desc)
        db.session.add(entry)
        db.session.commit()
        flash(
            """<div class="alert alert-success alert-dismissible fade show" role="alert">
                <strong>Successfully added!</strong> Your task is successfully added to the list.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>""",
            "html",
        )

    return render_template("add.html")


@app.route("/delete/<string:sno>", methods=["GET", "POST"])
def delete(sno):
    todo_list = Todo.query.filter_by(sno=sno).first()
    db.session.delete(todo_list)
    db.session.commit()
    return redirect("/")

@app.route("/toggle_done/<string:sno>", methods=["POST"])
def toggle_done(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    if todo:
        todo.done = not todo.done
        db.session.commit()
        return jsonify({"success": True, "done": todo.done})
    return jsonify({"success": False}), 404


app.run(debug=True)
