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
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Soft Feedback</title>
  <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600&display=swap" rel="stylesheet">
  <style>
    body {
      margin: 0;
      padding: 30px 15px;
      font-family: 'Quicksand', sans-serif;
      background: linear-gradient(135deg, #fce4ec, #e0f7fa);
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      color: #333;
    }
    .container {
      background: white;
      border-radius: 24px;
      padding: 30px;
      width: 100%;
      max-width: 500px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.1);
      animation: fadeIn 0.5s ease-in-out;
    }
    h1 {
      font-size: 2.4em;
      background: linear-gradient(to right, #00bcd4, #e91e63);
      -webkit-background-clip: text;
      color: transparent;
      text-align: center;
      margin-bottom: 25px;
    }
    textarea {
      width: 100%;
      height: 120px;
      font-size: 16px;
      padding: 12px;
      border-radius: 14px;
      border: 1px solid #ccc;
      margin-top: 8px;
      resize: vertical;
      font-family: inherit;
    }
    label {
      font-size: 16px;
      font-weight: 600;
      margin-top: 18px;
      display: block;
    }
    .button {
      background: linear-gradient(90deg, #00c6ff, #0072ff);
      border: none;
      color: white;
      padding: 18px 32px;
      font-size: 18px;
      font-weight: 600;
      border-radius: 14px;
      cursor: pointer;
      width: 100%;
      margin-top: 22px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s ease;
    }
    .button:hover {
      transform: scale(1.03);
      box-shadow: 0 4px 14px rgba(0,0,0,0.12);
    }
    .button svg {
      width: 22px;
      height: 22px;
      margin-right: 10px;
      fill: white;
    }
    .logout-button {
      background: linear-gradient(90deg, #ff5f6d, #ffc371);
    }
    #avatar {
      border-radius: 50%;
      width: 90px;
      margin: 15px auto;
      display: block;
      box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    .toggle {
      display: flex;
      align-items: center;
      margin-top: 14px;
    }
    .toggle input {
      margin-right: 10px;
      transform: scale(1.3);
    }
    #userInfo {
      text-align: center;
      transition: opacity 0.3s ease;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(30px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Soft Feedback</h1>
    {% if not session.get('user') %}
      <a href="{{ login_url }}">
        <button class="button">
          <svg viewBox="0 0 24 24"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm.5 15h-1v-6h1v6zm0-8h-1V7h1v2z"/></svg>
          Connect to Discord
        </button>
      </a>
    {% else %}
      <div id="userInfo">
        <img id="avatar" src="{{ session['user']['avatar'] }}" alt="avatar">
        <h2>{{ session['user']['username'] }}#{{ session['user']['discriminator'] }}</h2>
      </div>
      <form method="POST" action="/submit">
        <label for="feedback">
          Feedback:
        </label>
        <textarea name="feedback" id="feedback" required placeholder="Write something nice..."></textarea>

        <label class="toggle">
          <input type="checkbox" name="anonymous" id="anonCheck"> Submit anonymously
        </label>

        <button class="button" type="submit">
          <svg viewBox="0 0 24 24"><path d="M2 21l21-9L2 3v7l15 2-15 2v7z"/></svg>
          Send Feedback
        </button>
      </form>
      <form method="POST" action="/logout">
        <button class="button logout-button" type="submit">
          <svg viewBox="0 0 24 24"><path d="M16 13v-2H7V8l-5 4 5 4v-3h9zm4-9H4c-1.1 0-2 .9-2 2v6h2V6h16v12H4v-4H2v6c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2z"/></svg>
          Logout
        </button>
      </form>
    {% endif %}
  </div>

  <script>
    const anonCheckbox = document.getElementById('anonCheck');
    const userInfo = document.getElementById('userInfo');

    if (anonCheckbox) {
      anonCheckbox.addEventListener('change', function () {
        userInfo.style.display = this.checked ? 'none' : 'block';
      });
    }
  </script>
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
        # Check if user is in guild
        user = session['user']
        guilds_resp = requests.get(
            "https://discord.com/api/users/@me/guilds",
            headers={"Authorization": f"Bearer {session['token']}"}
        )
        if guilds_resp.status_code != 200:
            session.clear()
            return redirect("/")
        guilds = guilds_resp.json()
        in_guild = any(g['id'] == GUILD_ID for g in guilds)
        if not in_guild:
            session.clear()
            return f"You must join our server! <a href='https://discord.gg/u9NtDpXD7s'>Join here</a>"

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

    # If anonymous, replace username and avatar accordingly
    if anonymous:
        username = "Anonymous"
        avatar = "https://cdn.discordapp.com/embed/avatars/0.png"
    else:
        username = f"{user['username']}#{user['discriminator']}"
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
