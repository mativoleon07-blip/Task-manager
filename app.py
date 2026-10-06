import os

from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Set SECRET_KEY as an environment variable in real use.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"

db = SQLAlchemy(app)
login_manager = LoginManager(app)


# ---------- Database models ----------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    tasks = db.relationship("Task", backref="owner", lazy=True)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def to_dict(self):
        return {"id": self.id, "title": self.title, "done": self.done}


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    return jsonify(error="Not logged in"), 401


# ---------- Pages (just serve the HTML files) ----------

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect("/tasks")
    return redirect("/login")


@app.route("/login")
def login_page():
    return app.send_static_file("login.html")


@app.route("/register")
def register_page():
    return app.send_static_file("register.html")


@app.route("/tasks")
def tasks_page():
    if not current_user.is_authenticated:
        return redirect("/login")
    return app.send_static_file("tasks.html")


# ---------- Auth API ----------

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify(error="Username and password are required."), 400
    if len(username) > 50:
        return jsonify(error="Username is too long (max 50)."), 400
    if len(password) < 6:
        return jsonify(error="Password must be at least 6 characters."), 400
    if User.query.filter_by(username=username).first():
        return jsonify(error="That username is already taken."), 400

    user = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return jsonify(ok=True)


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify(ok=True)
    return jsonify(error="Wrong username or password."), 401


@app.route("/api/logout", methods=["POST"])
@login_required
def api_logout():
    logout_user()
    return jsonify(ok=True)


@app.route("/api/me")
@login_required
def api_me():
    return jsonify(username=current_user.username)


# ---------- Tasks API ----------

@app.route("/api/tasks", methods=["GET"])
@login_required
def get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.id).all()
    return jsonify([t.to_dict() for t in tasks])


@app.route("/api/tasks", methods=["POST"])
@login_required
def add_task():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()
    if not title:
        return jsonify(error="Task title cannot be empty."), 400
    if len(title) > 200:
        return jsonify(error="Task title is too long (max 200)."), 400

    task = Task(title=title, user_id=current_user.id)
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@app.route("/api/tasks/<int:task_id>", methods=["PATCH"])
@login_required
def update_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify(error="Task not found."), 404

    data = request.get_json(silent=True) or {}
    task.done = bool(data.get("done", task.done))
    db.session.commit()
    return jsonify(task.to_dict())


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify(error="Task not found."), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify(ok=True)


# Create tables whenever the app loads (works with python3 app.py and flask run)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
