from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
import math
import json
import pymysql
from werkzeug.security import generate_password_hash , check_password_hash
from flask_login import UserMixin, LoginManager, login_required , login_user , logout_user , current_user


with open("main.json", "r") as c:
    paras = json.load(c)["paras"]

app = Flask(__name__)
app.config["SECRET_KEY"] = "@iamshahnaz"

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/todolist"
db = SQLAlchemy(app)


from flask import jsonify

class Users(db.Model , UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(200), default=False)
    username = db.Column(db.String(160), nullable=False , unique = True)
    password = db.Column(db.String(200), nullable = False)
   

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    desc = db.Column(db.String(160), nullable=False)
    done = db.Column(db.Boolean, default=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # link to Users

    user = db.relationship('Users', backref='todos')
   
# initialize Login manager

login_manager = LoginManager() 
login_manager.init_app(app)
login_manager.login_view = 'login'

# load user by id

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dash")
@login_required
def dash():

    todo_list = Todo.query.filter_by(user_id=current_user.id).all()
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
        "dash.html", paras=paras, todo_list=todo_list, prev=prev, next=next
    )
    
@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        username = request.form.get("username")
        new_password = request.form.get("password")
        password = generate_password_hash(new_password)
        existing_user = Users.query.filter_by(username = username).first()
        if existing_user:
             flash(
            """<div class="alert alert-danger alert-dismissible fade show" role="alert">
                <strong>Already Exist</strong> This Username is already exist. Try another!
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>""",
            "html",
        )
             return redirect("/register")
        else:
            user = Users(name = name , email = email , username = username , password = password)
            db.session.add(user)
            db.session.commit()
            flash(
                """<div class="alert alert-success alert-dismissible fade show" role="alert">
                    <strong>Successfully Registered!</strong> Registration Complete
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>""",
                "html",
            )
            return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Users.query.filter_by(username = username).first()
       
        if user and check_password_hash(user.password, password):
            login_user(user)
            session["user_id"] = user.id
            session["username"]= user.username
             
            flash(
                """<div class="alert alert-success alert-dismissible fade show" role="alert">
                    <strong>Login Successfully!</strong> 
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>""",
                "html",
            )
            return redirect("/dash")
    
        else:
            flash(
                """<div class="alert alert-danger alert-dismissible fade show" role="alert">
                    <strong>Invalid Username or Password!</strong> Try Again
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>""",
                "html",
            )
            return redirect("/login")
    return render_template("login.html")

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_todo():
    if "user_id" not in session:
        flash(
                """<div class="alert alert-warning alert-dismissible fade show" role="alert">
                    <strong>Please Login to Add Todos</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>""",
                "html",
            )
        return redirect("/login")
    if request.method == "POST":
        title = request.form.get("title")
        desc = request.form.get("desc")
        
        todo = Todo(title = title , desc = desc , user_id = session['user_id'])
        db.session.add(todo)
        db.session.commit()
        
        flash("""<div class="alert alert-warning alert-dismissible fade show" role="alert">
                    <strong>Todo Added Successfully</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>""",
                "html",)
        return redirect("/dash")
        

    return render_template("add.html")


@app.route("/delete/<string:sno>", methods=["GET", "POST"])
@login_required
def delete(sno):
    todo_list = Todo.query.filter_by(sno=sno).first()
    db.session.delete(todo_list)
    db.session.commit()
    flash("""<div class="alert alert-warning alert-dismissible fade show" role="alert">
                    <strong>Task Deleted</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>""",
                "html",)
    return redirect("/dash")

@app.route("/toggle_done/<string:sno>", methods=["POST"])
@login_required
def toggle_done(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    if todo:
        todo.done = not todo.done
        db.session.commit()
        return jsonify({"success": True, "done": todo.done})
    return jsonify({"success": False}), 404


@app.route("/logout")
def logout():
    logout_user()
    flash("""<div class="alert alert-warning alert-dismissible fade show" role="alert">
                    <strong>Logout</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>""",
                "html",)
    return redirect("/login")
    
app.run(debug=True)
