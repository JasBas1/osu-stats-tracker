import os
from flask import Flask, jsonify
from ossapi import Ossapi

app = Flask(__name__)

CLIENT_ID = int(os.environ.get('OSU_CLIENT_ID'))
CLIENT_SECRET = os.environ.get('OSU_CLIENT_SECRET')

api = Ossapi(CLIENT_ID, CLIENT_SECRET)

@app.route('/player/<username>')
def get_player(username):
    user = api.user(username)
    return jsonify({
        'username': user.username,
        'global_rank': user.statistics.global_rank,
        'pp': user.statistics.pp,
        'accuracy': round(user.statistics.hit_accuracy, 2),
        'play_count': user.statistics.play_count,
        'country': user.country.name
    })

@app.route('/player/<username>/top')
def get_top_plays(username):
    user = api.user(username)
    scores = api.user_scores(user.id, 'best', limit=5)
    plays = []
    for s in scores:
        plays.append({
            'song': f"{s.beatmapset.artist} - {s.beatmapset.title}",
            'difficulty': s.beatmap.version,
            'pp': round(s.pp, 1),
            'rank': s.rank.value,
            'mods': [m.acronym for m in s.mods]
        })
    return jsonify({'username': user.username, 'top_plays': plays})

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'version': '1.1'})

@app.route('/')
def home():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>osu! Stats Tracker</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background-color: #1a1a2e;
            color: #ffffff;
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }
        h1 { font-size: 2.5rem; margin-bottom: 10px; color: #ff66aa; }
        p { color: #aaaaaa; margin-bottom: 30px; font-size: 1rem; }
        .search-box {
            display: flex;
            gap: 10px;
        }
        input {
            padding: 12px 20px;
            font-size: 1rem;
            border: 2px solid #ff66aa;
            border-radius: 8px;
            background: #16213e;
            color: #ffffff;
            outline: none;
            width: 280px;
        }
        input::placeholder { color: #666; }
        button {
            padding: 12px 24px;
            font-size: 1rem;
            background-color: #ff66aa;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover { background-color: #cc3377; }
        .results {
            margin-top: 40px;
            background: #16213e;
            border-radius: 12px;
            padding: 24px;
            width: 400px;
            display: none;
        }
        .stat { margin: 8px 0; font-size: 0.95rem; }
        .stat span { color: #ff66aa; font-weight: bold; }
        .error { color: #ff4444; margin-top: 20px; display: none; }
    </style>
</head>
<body>
    <h1>osu! Stats Tracker</h1>
    <p>Look up any osu! player's stats</p>
    <div class="search-box">
        <input type="text" id="username" placeholder="Enter osu! username" />
        <button onclick="search()">Search</button>
    </div>
    <div class="results" id="results">
        <div class="stat">Username: <span id="r-username"></span></div>
        <div class="stat">Global Rank: <span id="r-rank"></span></div>
        <div class="stat">PP: <span id="r-pp"></span></div>
        <div class="stat">Accuracy: <span id="r-acc"></span>%</div>
        <div class="stat">Play Count: <span id="r-plays"></span></div>
        <div class="stat">Country: <span id="r-country"></span></div>
    </div>
    <p class="error" id="error">Player not found. Check the username and try again.</p>
    <script>
        document.getElementById("username").addEventListener("keypress", function(e) {
            if (e.key === "Enter") search();
        });
        async function search() {
            const username = document.getElementById("username").value.trim();
            if (!username) return;
            document.getElementById("results").style.display = "none";
            document.getElementById("error").style.display = "none";
            try {
                const res = await fetch(`/player/${username}`);
                if (!res.ok) throw new Error();
                const data = await res.json();
                document.getElementById("r-username").textContent = data.username;
                document.getElementById("r-rank").textContent = "#" + data.global_rank.toLocaleString();
                document.getElementById("r-pp").textContent = data.pp.toLocaleString() + "pp";
                document.getElementById("r-acc").textContent = data.accuracy;
                document.getElementById("r-plays").textContent = data.play_count.toLocaleString();
                document.getElementById("r-country").textContent = data.country;
                document.getElementById("results").style.display = "block";
            } catch {
                document.getElementById("error").style.display = "block";
            }
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)