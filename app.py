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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)