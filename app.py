from flask import Flask, request, redirect, session, render_template_string
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
GUILD_ID = os.environ.get("GUILD_ID")
ROLE_ID = os.environ.get("ROLE_ID")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
REDIRECT_URI = os.environ.get("REDIRECT_URI")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" >
<head>
  <meta charset="UTF-8" />
  <title>Soft Feedback</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    * {
      box-sizing: border-box;
    }
    body {
      margin: 0;
      font-family: 'Poppins', sans-serif;
      background: linear-gradient(135deg, #b3e5fc, #ffccff);
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      overflow-x: hidden;
      color: #3a3a3a;
      animation: bgPulse 15s ease-in-out infinite;
    }

    @keyframes bgPulse {
      0%, 100% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
    }

    .container {
      background: white;
      border-radius: 25px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.15);
      max-width: 450px;
      width: 90vw;
      padding: 40px 35px 50px;
      position: relative;
      overflow: hidden;
    }

    h1 {
      font-weight: 600;
      font-size: 2.8rem;
      background: linear-gradient(90deg, #ff8efb, #2af598);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 35px;
      text-align: center;
    }

    #avatar {
      display: block;
      margin: 0 auto 25px;
      border-radius: 50%;
      width: 100px;
      box-shadow: 0 8px 20px rgba(255,140,233,0.5);
      animation: floatUpDown 4s ease-in-out infinite;
    }

    @keyframes floatUpDown {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-12px); }
    }

    h2 {
      font-weight: 600;
      font-size: 1.6rem;
      margin-bottom: 20px;
      text-align: center;
      color: #444;
    }

    form {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    textarea {
      resize: none;
      height: 130px;
      border-radius: 18px;
      border: 2px solid #d0c4fc;
      font-size: 1.1rem;
      padding: 15px 20px;
      font-family: 'Poppins', sans-serif;
      transition: border-color 0.3s ease;
    }

    textarea:focus {
      outline: none;
      border-color: #9a80f9;
      box-shadow: 0 0 8px #c9bfff;
    }

    label.toggle {
      display: flex;
      align-items: center;
      font-size: 1.1rem;
      color: #666;
      gap: 12px;
      cursor: pointer;
      user-select: none;
    }

    input[type="checkbox"] {
      width: 22px;
      height: 22px;
      accent-color: #ab6cff;
      cursor: pointer;
      border-radius: 5px;
    }

    .button {
      background: linear-gradient(135deg, #a275e6, #f88ffb);
      color: white;
      border: none;
      border-radius: 30px;
      padding: 18px 0;
      font-size: 1.5rem;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 8px 20px rgba(161, 117, 230, 0.65);
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      user-select: none;
    }
    .button:hover {
      filter: brightness(1.1);
      box-shadow: 0 12px 28px rgba(161, 117, 230, 0.9);
      transform: translateY(-3px);
    }

    .logout-btn {
      background: linear-gradient(135deg, #ff758c, #ff7eb3);
      box-shadow: 0 8px 20px rgba(255, 117, 132, 0.7);
    }

    a.button {
      text-decoration: none;
    }

    /* Icon container */
    .icon {
      width: 26px;
      height: 26px;
      fill: white;
      flex-shrink: 0;
      filter: drop-shadow(0 0 1px rgba(0,0,0,0.15));
    }

    /* Responsive */
    @media (max-width: 500px) {
      h1 { font-size: 2rem; }
      h2 { font-size: 1.3rem; }
      textarea { font-size: 1rem; }
      .button {
        font-size: 1.3rem;
        padding: 15px 0;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Soft Feedback</h1>

    {% if not session.get('user') %}
      <a href="{{ login_url }}" class="button">
        <svg class="icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M20 2H4C2.9 2 2 2.9 2 4v16a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2Zm-9.06 14.24c-1.12 0-2.03-.8-2.03-1.78h4.1c0 1-.9 1.78-2.07 1.78Zm5.14-3.25v2.03a4.78 4.78 0 0 1-1.42.14c-1.08 0-1.9-.52-2.48-1.02l-.06-.05-1.12 1.4c.36.3 1.23.92 2.86.92a6.34 6.34 0 0 0 3.67-1.11v-2.3c.18-.08.36-.17.52-.26a4.4 4.4 0 0 0 1.35-1.1 4.74 4.74 0 0 1-4.85-1.85Zm3.64 2.12a6.4 6.4 0 0 1-3.41 1.33 7.3 7.3 0 0 1-2.08.01c-1.22-.17-1.99-.8-2.15-1.06-.16-.25-.17-.45-.17-.45v-.16h.13c.13-.02.3-.06.47-.11a3.3 3.3 0 0 0 2.8-1.18l1.55 1.98a2.96 2.96 0 0 1-.14 1.04Zm-3.25-4.55v-2.25h.42c.44 0 .83.17 1.07.39.21.18.36.41.36.41l-1.85 1.45Zm-3.55-2.68-1.34 1.08a2.07 2.07 0 0 0-.69-1.1 4.27 4.27 0 0 0 2.03-.38Zm-6.44 4.93V6.91h8.64v6.55Z"/></svg>
        Connect to Discord
      </a>
    {% else %}
      <img id="avatar" src="{{ session['user']['avatar'] }}" alt="avatar" />
      <h2>Hello, {{ session['user']['username'] }}#{{ session['user']['discriminator'] }}</h2>

      <form method="POST" action="/submit">
        <label for="feedback" aria-label="Feedback input">Your Feedback</label>
        <textarea id="feedback" name="feedback" placeholder="Write something kind and honest..." required></textarea>

        <label class="toggle" for="anonymous">
          <input type="checkbox" id="anonymous" name="anonymous" />
          <svg class="icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10"/></svg>
          Submit anonymously
        </label>

        <button class="button" type="submit">
          <svg class="icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M2 12l18-12v24z"/></svg>
          Send Feedback
        </button>
      </form>

      <form method="POST" action="/logout" style="margin-top:20px;">
        <button class="button logout-btn" type="submit">
          <svg class="icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M16 13v-2H7v2h9zm2-7v14H5V6h13z"/></svg>
          Logout
        </button>
      </form>
    {% endif %}
  </div>
</body>
</html>
"""

@app.route("/")
def index():
    if not session.get('user'):
        login_url = (
            f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}"
            f"&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify%20guilds"
        )
        return render_template_string(HTML_TEMPLATE, login_url=login_url)
    else:
        # Check if user is in guild and has role
        user = session['user']
        guilds_resp = requests.get(
            "https://discord.com/api/users/@me/guilds",
            headers={"Authorization": f"Bearer {session['token']}"}
        )
        if guilds_resp.status_code != 200:
            session.clear()
            return redirect("/")
        guilds = guilds_resp.json()
        # Check guild and role membership
        in_guild = any(g['id'] == GUILD_ID for g in guilds)
        if not in_guild:
            session.clear()
            return f"You must join our server! <a href='https://discord.gg/u9NtDpXD7s'>Join here</a>"

        # Here you could add role check if you have a way (Discord API requires bot for role info)
        # For simplicity, we check guild membership only

        return render_template_string(HTML_TEMPLATE)

@app.route("/callback")
def callback():
    code = request.args.get('code')
    if not code:
        return redirect("/")
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "identify guilds"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_resp = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    token_json = token_resp.json()
    access_token = token_json.get("access_token")
    if not access_token:
        return "OAuth failed."

    # Get user info
    user_resp = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_json = user_resp.json()

    session['token'] = access_token
    session['user'] = {
        "id": user_json.get("id"),
        "username": user_json.get("username"),
        "discriminator": user_json.get("discriminator"),
        "avatar": f"https://cdn.discordapp.com/avatars/{user_json.get('id')}/{user_json.get('avatar')}.png" if user_json.get('avatar') else "https://cdn.discordapp.com/embed/avatars/0.png"
    }
    return redirect("/")

@app.route("/submit", methods=["POST"])
def submit():
    if not session.get('user'):
        return redirect("/")
    feedback = request.form.get("feedback")
    anonymous = request.form.get("anonymous")
    user = session['user']
    username = "Anonymous" if anonymous else f"{user['username']}#{user['discriminator']}"
    avatar = user['avatar']
    embed = {
        "embeds": [
            {
                "author": {"name": username, "icon_url": avatar},
                "title": "New Feedback",
                "description": feedback,
                "color": 3447003
            }
        ]
    }
    resp = requests.post(WEBHOOK_URL, json=embed)
    if resp.status_code == 204:
        return "Feedback sent! Thank you."
    else:
        return "Failed to send feedback."

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
