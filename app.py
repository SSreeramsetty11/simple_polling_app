from flask import Flask, request, redirect, render_template, url_for
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

from sports_votes import votes_sports
from players_votes import votes_players

def save_votes():
    with open("sports_votes.py", "w") as f:
        f.write(f"votes_sports = {votes_sports}\n")
    with open("players_votes.py", "w") as f:
        f.write(f"votes_players = {votes_players}\n")

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