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
<title>Soft Feedback</title>
<style>
  body { font-family: 'Arial', sans-serif; background: #cceeff; text-align: center; padding: 50px; }
  .button { background: cyan; border: none; color: white; padding: 15px 30px; font-size: 20px; border-radius: 12px; cursor: pointer; }
  .button:hover { background: #00bcd4; }
  textarea { width: 80%; height: 100px; border-radius: 10px; border: 1px solid #ccc; font-size: 16px; padding: 10px; }
  label { font-size: 18px; margin-top: 15px; display: block; }
  #avatar { border-radius: 50%; width: 80px; margin: 15px auto; display: block; }
  .toggle { margin: 15px; }
</style>
</head>
<body>
<h1>Soft Feedback 💙</h1>
{% if not session.get('user') %}
  <a href="{{ login_url }}"><button class="button">Connect to Discord</button></a>
{% else %}
  <img id="avatar" src="{{ session['user']['avatar'] }}" alt="avatar">
  <h2>Hello, {{ session['user']['username'] }}#{{ session['user']['discriminator'] }}</h2>
  <form method="POST" action="/submit">
    <label for="feedback">Your Feedback:</label>
    <textarea name="feedback" id="feedback" required></textarea>
    <label class="toggle"><input type="checkbox" name="anonymous"> Submit anonymously</label>
    <br />
    <button class="button" type="submit">Send Feedback</button>
  </form>
  <form method="POST" action="/logout" style="margin-top:20px;">
    <button class="button" type="submit" style="background:#f44336;">Logout</button>
  </form>
{% endif %}
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