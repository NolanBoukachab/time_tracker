#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
from functools import wraps

from flask import (
    Flask,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

# ----------------------------------------------------------------------------
# Database
# ----------------------------------------------------------------------------


def get_db():
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    if "db" not in g:
        g.db = sqlite3.connect("time_tracker.db", detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = dict_factory
    return g.db


def close_db(e):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with current_app.app_context():
        db = get_db()
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                hours INT NOT NULL,
                comments TEXT,
                FOREIGN KEY (user_id) REFERENCES user(id)
            );
            """
        )


# ----------------------------------------------------------------------------
# User
# ----------------------------------------------------------------------------


def load_user_from_session():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db()
            .execute("SELECT * FROM users WHERE id = :user_id", dict(user_id=user_id))
            .fetchone()
        )


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


# ----------------------------------------------------------------------------
# Application
# ----------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = "931572e9a910c8287c3b7fe24b73ae00e434eafbf41fe3c6f35ad830d7da89cb"
app.before_request(load_user_from_session)
app.before_first_request(init_db)
app.teardown_appcontext(close_db)


@app.context_processor
def inject_today_date():
    import datetime

    return dict(date=datetime.date)


@app.get("/")
@login_required
def home():
    db = get_db()
    events = db.execute(
        "SELECT * FROM events WHERE events.user_id = :user_id ORDER BY id DESC",
        dict(user_id=g.user["id"]),
    ).fetchall()
    return render_template("home.html", events=events)


@app.get("/add_event")
@login_required
def add_event():
    return render_template("add_event.html")


@app.post("/add_event")
@login_required
def submit_add_event():
    event_date = request.form.get("date")
    event_hours = request.form.get("hours")
    event_comments = request.form.get("comments") or ""

    db = get_db()
    db.execute(
        """INSERT INTO
            events(
                user_id,
                date,
                hours,
                comments
            )
            VALUES (
                :user_id,
                :date,
                :hours,
                :comments
            )""",
        dict(
            user_id=g.user["id"],
            date=event_date,
            hours=event_hours,
            comments=event_comments,
        ),
    )
    db.commit()

    flash("New event added!", "success")
    return redirect(url_for("home"))


@app.get("/register")
def register():
    return render_template("register.html")


@app.post("/register")
def submit_register():
    username = request.form.get("username")
    password = request.form.get("password")
    error = None
    db = get_db()

    try:
        db.execute(
            """INSERT INTO
                users(
                    username,
                    password
                )
                VALUES (
                    :username,
                    :password
                )""",
            dict(username=username, password=password),
        )
        db.commit()
    except db.IntegrityError:
        error = f"User {username} is already registered."
    else:
        return redirect(url_for("login"))

    flash(error, "warning")
    return redirect(url_for("register"))


@app.get("/login")
def login():
    return render_template("login.html")


@app.post("/login")
def submit_login():
    username = request.form.get("username")
    password = request.form.get("password")
    error = None
    db = get_db()

    user = db.execute(
        f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    ).fetchone()
    if user is None:
        error = "Incorrect credentials"

    if error is None:
        session.clear()
        session["user_id"] = user["id"]
        return redirect(url_for("home"))

    flash(error, "warning")
    return redirect(url_for("login"))


@app.get("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))
