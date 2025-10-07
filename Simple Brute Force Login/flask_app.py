#!/usr/bin/env python3
from flask import Flask, request, render_template_string, jsonify
from pathlib import Path

APP = Flask(__name__)
USERS_FILE = Path("users.csv")
SUCCESS_TEXT = "Successfully Logged In"

def load_users():
    users = {}
    if not USERS_FILE.exists():
        USERS_FILE.write_text("admin,admin123\nuser,password\nroot,toor\ntest,test")
    raw = USERS_FILE.read_text(encoding="utf-8", errors="ignore")
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "," not in line:
            continue
        u, p = [x.strip() for x in line.split(",", 1)]
        users[u] = p
    return users

LOGIN_PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Login Portal</title>
  <style>
    html, body {
      height: 100%;
      margin: 0;
      padding: 0;
    }
    body {
      font-family: 'Segoe UI', Arial, sans-serif;
      background: #fff;
      height: 100vh;
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      min-width: 100vw;
    }
    .container {
      background: #fff;
      border-radius: 16px;
      box-shadow: 0 8px 32px rgba(31, 38, 135, 0.13);
      padding: 40px 28px 28px 28px;
      width: 370px;
      display: flex;
      flex-direction: column;
      align-items: stretch;
      text-align: center;
    }
    h2 {
      margin-top: 0;
      margin-bottom: 18px;
      font-size: 2.1em;
      color: #333a50;
      letter-spacing: 1.2px;
      font-weight: 700;
    }
    label {
      font-weight: 600;
      margin-top: 20px;
      display: block;
      text-align: left;
      margin-bottom: 7px;
      color: #333a50;
    }
    input[type="text"], input[type="password"] {
      width: 100%;
      padding: 10px 12px;
      margin-bottom: 15px;
      border: 1px solid #d4d9e3;
      border-radius: 7px;
      font-size: 1em;
      background: #f9f9fb;
      transition: border-color 0.2s;
    }
    input[type="text"]:focus,
    input[type="password"]:focus {
      border-color: #7dbff7;
      outline: none;
    }
    button {
      width: 100%;
      padding: 12px 0;
      background: #4285f4;
      color: #fff;
      border: none;
      border-radius: 7px;
      font-size: 1.1em;
      font-weight: 700;
      cursor: pointer;
      margin-top: 10px;
      box-shadow: 0 2px 8px rgba(66, 133, 244, 0.10);
      transition: background 0.2s, transform 0.15s;
    }
    button:hover {
      background: #2563eb;
      transform: translateY(-2px) scale(1.025);
    }
    .note {
      font-size: 13px;
      color: #9094a4;
      margin-top: 18px;
      letter-spacing: 0.5px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Login</h2>
    <form method="post" action="/login" autocomplete="off">
      <label for="username">Username</label>
      <input id="username" name="username" type="text" required placeholder="Enter your username" autocomplete="off">
      <label for="password">Password</label>
      <input id="password" name="password" type="password" required placeholder="Enter your password" autocomplete="off">
      <button type="submit">Login</button>
    </form>
  </div>
</body>
</html>
"""

SUCCESS_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Login Successful</title>
  <style>
    html, body {
      height: 100%;
      margin: 0;
      padding: 0;
    }
    body {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      background: #fff;
    }
    .center-message {
      text-align: center;
      width: 100vw;
    }
    .success {
      color: #24bb33;
      font-size: 2.8em;
      font-weight: bold;
      margin-bottom: 18px;
    }
    .welcome {
      font-size: 1.5em;
      color: #183367;
    }
  </style>
</head>
<body>
  <div class="center-message">
    <div class="success">Successfully Logged In</div>
    <div class="welcome">Welcome, {{ username }}!</div>
  </div>
</body>
</html>
"""

FAIL_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Invalid Credentials</title>
  <style>
    html, body {
      height: 100%;
      margin: 0;
      padding: 0;
    }
    body {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      background: #fff;
    }
    .center-message {
      text-align: center;
      width: 100vw;
    }
    .fail {
      color: #eb2222;
      font-size: 2.2em;
      font-weight: bold;
      margin-bottom: 18px;
    }
  </style>
</head>
<body>
  <div class="center-message">
    <div class="fail">Invalid credentials</div>
  </div>
</body>
</html>
"""

@APP.route("/", methods=["GET"])
def index():
    return render_template_string(LOGIN_PAGE)

@APP.route("/login", methods=["POST"])
def login():
    users = load_users()
    if request.is_json:
        data = request.get_json(silent=True) or {}
        username = data.get("username", "")
        password = data.get("password", "")
    else:
        username = request.form.get("username", "")
        password = request.form.get("password", "")
    real_pass = users.get(username)
    if real_pass and password == real_pass:
        return render_template_string(SUCCESS_HTML, username=username), 200
    return render_template_string(FAIL_HTML), 200

@APP.route("/api/login", methods=["POST"])
def api_login():
    users = load_users()
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")
    real_pass = users.get(username)
    if real_pass and password == real_pass:
        return jsonify({"status": "ok", "user": username}), 200
    return jsonify({"status": "fail"}), 200

if __name__ == "__main__":
    print("Starting server on http://127.0.0.1:5000")
    print("Users file:", USERS_FILE.resolve())
    APP.run(host="127.0.0.1", port=5000, debug=True)
