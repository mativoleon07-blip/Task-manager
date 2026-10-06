# Task Manager

A simple multi-user task manager. Register, log in, and manage your own to-do list.

Built with **Flask**, **SQLite**, and plain **HTML/CSS/JavaScript** (no frontend framework).

## Features
- User registration and login (passwords are hashed, never stored as plain text)
- Add, complete, and delete tasks
- Each user only sees their own tasks
- JSON API consumed by the frontend with `fetch`

## Tech
Python, Flask, Flask-SQLAlchemy, Flask-Login, SQLite, HTML, CSS, JavaScript

## Run it locally

```bash
git clone https://github.com/YOUR-USERNAME/task-manager.git
cd task-manager
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 app.py
```

Open http://127.0.0.1:5000

For anything beyond local use, set your own secret key first:

```bash
export SECRET_KEY="a-long-random-string"
```

## API

| Method | Route | Description |
|--------|-------|-------------|
| POST | /api/register | Create an account |
| POST | /api/login | Log in |
| POST | /api/logout | Log out |
| GET | /api/tasks | List your tasks |
| POST | /api/tasks | Add a task |
| PATCH | /api/tasks/<id> | Mark done / not done |
| DELETE | /api/tasks/<id> | Delete a task |

## Screenshot
_Add a screenshot of the app here._
