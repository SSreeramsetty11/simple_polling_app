from flask import Flask, request, redirect, render_template, url_for
import matplotlib.pyplot as plt
import os
import json

app = Flask(__name__)

# Get the current working directory dynamically
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # Ensures correct path on PythonAnywhere and local machine

SPORTS_VOTES_FILE = os.path.join(BASE_DIR, "sports_votes.json")
PLAYERS_VOTES_FILE = os.path.join(BASE_DIR, "players_votes.json")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Ensure the 'static' folder exists
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)


def load_votes():
    print(SPORTS_VOTES_FILE)
    print(PLAYERS_VOTES_FILE)
    if not os.path.exists(SPORTS_VOTES_FILE):
        with open(SPORTS_VOTES_FILE, "w") as f:
            json.dump({}, f)  # Create an empty JSON file with {}
    if not os.path.exists(PLAYERS_VOTES_FILE):
        with open(PLAYERS_VOTES_FILE, "w") as f:
            json.dump({}, f)  # Create an empty JSON file with {}
    
    with open(SPORTS_VOTES_FILE, "r") as f:
        sports = json.load(f)
    with open(PLAYERS_VOTES_FILE, "r") as f:
        players = json.load(f)
    
    return sports, players

# loads the data from the file for the first time only
votes_sports, votes_players = load_votes() 


def save_votes():
    with open(SPORTS_VOTES_FILE, "w") as f:
        json.dump(votes_sports, f, indent=4)
    with open(PLAYERS_VOTES_FILE, "w") as f:
        json.dump(votes_players, f, indent=4)     

def generate_chart(data, title, filename):
    plt.figure(figsize=(6, 4))
    plt.bar(data.keys(), data.values(), color="skyblue")
    plt.title(title)
    plt.xlabel("Options")
    plt.ylabel("Votes")
    plt.yticks(range(0, max(data.values()) + 1))  # Ensure y-axis shows whole numbers
    plt.xticks(rotation=45)  # Rotate x-axis labels to prevent overlap
    plt.tight_layout()

    plt.savefig(filename)
    plt.close()

def generate_player_chart(sport):
    player_votes = votes_players[sport]
    filename = f"static/{sport}_player_chart.png"
    generate_chart(player_votes, f"Favorite Players in {sport}", filename)
    return filename

@app.route("/", methods=["GET", "POST"])
def poll_sport():
    if request.method == "POST":
        sport = request.form.get("sport")
        if sport in votes_sports:
            votes_sports[sport] += 1
            save_votes()
            return redirect(url_for("poll_player", sport=sport))
    return render_template("poll_sport.html", sports=votes_sports.keys())

@app.route("/poll/<sport>", methods=["GET", "POST"])
def poll_player(sport):
    if request.method == "POST":
        player = request.form.get("player")
        if player:
            if player not in votes_players[sport]:
                votes_players[sport][player] = 0
            votes_players[sport][player] += 1
            save_votes()
            return redirect(url_for("results"))
    return render_template("poll_player.html", sport=sport, players=votes_players[sport])

@app.route("/results")
def results():
    generate_chart(votes_sports, "Favorite Sport", "static/sports_chart.png")
    for sport in votes_players:
        generate_player_chart(sport)
    return render_template("results.html", sports_chart="static/sports_chart.png", player_charts=[f"static/{sport}_player_chart.png" for sport in votes_players])

if __name__ == "__main__":
    app.run(debug=True)