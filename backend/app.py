from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
from flask_cors import CORS

import os
from flask import Flask, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REACT_BUILD_DIR = os.path.join(BASE_DIR, '../frontend/build')

app = Flask(__name__, static_folder=REACT_BUILD_DIR, static_url_path="")
CORS(app, origins=["http://localhost:3000","https://chess-2-m2y4.onrender.com"])
DATABASE = 'tournament.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# -----------------------------
# Teams + Players endpoints
# -----------------------------

@app.route('/api/teams')
def get_teams():
    db = get_db_connection()
    teams = db.execute('SELECT * FROM teams').fetchall()
    out = []
    for t in teams:
        players = db.execute('SELECT * FROM players WHERE team_id = ? ORDER BY id', (t['id'],)).fetchall()
        out.append({
            'id': t['id'],
            'name': t['name'],
            'players': [dict(p) for p in players]
        })
    db.close()
    return jsonify(out)

@app.route('/api/team/<int:id>/edit-name', methods=['POST'])
def edit_team_name(id):
    data = request.get_json() or {}
    new_name = data.get('name', '').strip()
    if not new_name:
        return jsonify({'error': 'Team name is required'}), 400

    db = get_db_connection()
    db.execute('UPDATE teams SET name = ? WHERE id = ?', (new_name, id))
    db.commit()
    db.close()
    return jsonify({'message': 'Team name updated'}), 200

@app.route('/api/players', methods=['GET', 'POST'])
def players():
    db = get_db_connection()
    if request.method == 'GET':
        pls = db.execute('SELECT * FROM players').fetchall()
        out = [dict(p) for p in pls]
        db.close()
        return jsonify(out)
    else:
        data = request.get_json() or {}
        name = data.get('name')
        rating = data.get('rating', 0)
        team_id = data.get('team_id')
        if not name or team_id is None:
            db.close()
            return jsonify({'error': 'Name and team_id required'}), 400

        cur = db.execute(
            'INSERT INTO players (name, rating, team_id) VALUES (?, ?, ?)',
            (name, rating, team_id)
        )
        db.commit()
        new_id = cur.lastrowid
        db.close()
        return jsonify({'id': new_id, 'name': name, 'rating': rating, 'team_id': team_id}), 201

@app.route('/api/player/<int:id>/edit-name', methods=['POST'])
def edit_player_name(id):
    data = request.get_json() or {}
    new_name = data.get('name', '').strip()
    if not new_name:
        return jsonify({'error': 'Player name is required'}), 400

    db = get_db_connection()
    db.execute('UPDATE players SET name = ? WHERE id = ?', (new_name, id))
    db.commit()
    db.close()
    return jsonify({'message': 'Player name updated'}), 200

@app.route('/api/player/<int:id>/edit-rating', methods=['POST'])
def edit_player_rating(id):
    data = request.get_json() or {}
    try:
        new_rating = int(data.get('rating'))
    except:
        return jsonify({'error': 'Invalid rating'}), 400

    db = get_db_connection()
    db.execute('UPDATE players SET rating = ? WHERE id = ?', (new_rating, id))
    db.commit()
    db.close()
    return jsonify({'message': 'Player rating updated'}), 200

# -----------------------------
# Match endpoints
# -----------------------------

@app.route('/api/matches', methods=['GET'])
def matches():
    db = get_db_connection()
    matches = db.execute('''
        SELECT 
            m.id, m.round, m.team1_id, m.team2_id,
            m.team1_score, m.team2_score,
            r.start_time
        FROM matches m
        LEFT JOIN rounds r ON m.round = r.round
        ORDER BY m.round, m.id
    ''').fetchall()
    out = [dict(m) for m in matches]
    db.close()
    return jsonify(out)

@app.route('/api/matches/<int:match_id>/results', methods=['GET'])
def get_match_results(match_id):
    db = get_db_connection()
    rows = db.execute(
        'SELECT board, result FROM results WHERE match_id = ? ORDER BY board',
        (match_id,)
    ).fetchall()
    db.close()
    if not rows:
        return jsonify({'message': 'No results yet'}), 404
    return jsonify({'match_id': match_id, 'results': [dict(r) for r in rows]})

@app.route('/api/match/<int:match_id>/players', methods=['GET', 'POST'])
def match_players(match_id):
    db = get_db_connection()
    # ensure match exists
    m = db.execute('SELECT team1_id, team2_id FROM matches WHERE id = ?', (match_id,)).fetchone()
    if not m:
        db.close()
        return jsonify({'error': 'Match not found'}), 404

    if request.method == 'GET':
        t1, t2 = m['team1_id'], m['team2_id']
        p1 = db.execute('SELECT player_id FROM match_players WHERE match_id=? AND team_id=?',
                        (match_id, t1)).fetchall()
        p2 = db.execute('SELECT player_id FROM match_players WHERE match_id=? AND team_id=?',
                        (match_id, t2)).fetchall()
        db.close()
        return jsonify({
            'match_id': match_id,
            'team1_players': [r['player_id'] for r in p1],
            'team2_players': [r['player_id'] for r in p2]
        })
    else:
        data = request.get_json() or {}
        t1_list = data.get('team1_players', [])
        t2_list = data.get('team2_players', [])
        # basic validation
        if not isinstance(t1_list, list) or not isinstance(t2_list, list):
            db.close()
            return jsonify({'error': 'Lists required'}), 400

        db.execute('DELETE FROM match_players WHERE match_id = ?', (match_id,))
        for pid in t1_list:
            db.execute('INSERT INTO match_players (match_id, team_id, player_id) VALUES (?,?,?)',
                       (match_id, m['team1_id'], pid))
        for pid in t2_list:
            db.execute('INSERT INTO match_players (match_id, team_id, player_id) VALUES (?,?,?)',
                       (match_id, m['team2_id'], pid))
        db.commit()
        db.close()
        return jsonify({'message': 'Match players updated'}), 200

@app.route('/api/match/<int:match_id>/submit-single', methods=['POST'])
def submit_single_result(match_id):
    data = request.get_json() or {}
    board = data.get('board')
    result = data.get('result')
    if board not in (1,2,3,4) or result not in ('A','B','D'):
        return jsonify({'error': 'Invalid data'}), 400

    db = get_db_connection()
    # overwrite any existing for this board
    db.execute('DELETE FROM results WHERE match_id=? AND board=?', (match_id, board))
    db.execute('INSERT INTO results (match_id, board, result) VALUES (?,?,?)',
               (match_id, board, result))

    # recompute total scores if 4 boards done
    res = db.execute('SELECT result FROM results WHERE match_id=?', (match_id,)).fetchall()
    if len(res)>0:
        a=0; b=0
        for r in res:
            if r['result']=='A': a+=1
            elif r['result']=='B': b+=1
            else: a+=0.5; b+=0.5
        db.execute('UPDATE matches SET team1_score=?, team2_score=? WHERE id=?',
                   (a,b,match_id))
    db.commit()
    db.close()
    return jsonify({'message':'Result submitted'}), 200

@app.route('/api/update-match', methods=['POST'])
def update_match_time():
    data = request.get_json() or {}
    rnd = data.get('round')
    dt = data.get('date_time')
    if rnd is None or not dt:
        return jsonify({'error':'Round & date_time required'}),400

    db = get_db_connection()
    db.execute('UPDATE rounds SET start_time = ? WHERE round = ?', (dt, rnd))
    db.commit()
    db.close()
    return jsonify({'message':'Round time updated'}),200

# -----------------------------
# Standings & Full Details
# -----------------------------

@app.route('/api/standings', methods=['GET'])
def standings():
    db = get_db_connection()
    teams = db.execute('SELECT id, name FROM teams').fetchall()
    stan = {t['id']:{'id':t['id'],'name':t['name'],'played':0,'match_points':0,'game_points':0} for t in teams}

    matches = db.execute('SELECT * FROM matches WHERE (team1_score+team2_score)=4.0').fetchall()
    for m in matches:
        t1,t2 = m['team1_id'], m['team2_id']
        s1,s2 = m['team1_score'], m['team2_score']
        stan[t1]['played']+=1; stan[t2]['played']+=1
        stan[t1]['game_points']+=s1; stan[t2]['game_points']+=s2
        if s1>s2: stan[t1]['match_points']+=2
        elif s2>s1: stan[t2]['match_points']+=2
        else:
            stan[t1]['match_points']+=1; stan[t2]['match_points']+=1

    db.close()
    out = sorted(stan.values(), key=lambda x:(-x['match_points'],-x['game_points']))
    return jsonify(out)

@app.route('/api/match/<int:match_id>/full-details', methods=['GET'])
def match_full_details(match_id):
    db = get_db_connection()
    m = db.execute('''
        SELECT m.id,m.round,m.team1_id,t1.name AS team1_name,
               m.team2_id,t2.name AS team2_name,
               r.start_time AS date_time,
               m.team1_score,m.team2_score
        FROM matches m
        JOIN teams t1 ON m.team1_id=t1.id
        JOIN teams t2 ON m.team2_id=t2.id
        JOIN rounds r ON m.round=r.round
        WHERE m.id=?
    ''', (match_id,)).fetchone()
    if not m:
        db.close()
        return jsonify({'error':'Match not found'}),404

    players = db.execute('''
        SELECT mp.board, mp.team_id, mp.player_id, p.name AS player_name
        FROM match_players mp JOIN players p ON mp.player_id=p.id
        WHERE mp.match_id=?
        ORDER BY mp.board, mp.team_id
    ''', (match_id,)).fetchall()

    results = db.execute('SELECT board, result FROM results WHERE match_id=? ORDER BY board', (match_id,)).fetchall()
    db.close()

    return jsonify({
        'match': dict(m),
        'players': [dict(p) for p in players],
        'results': [dict(r) for r in results]
    })

@app.route('/api/best_players')
def best_players():
    db = get_db_connection()
    rows = db.execute('''
        SELECT 
          mp.player_id, p.name AS player_name, t.name AS team_name,
          mp.board, r.result, m.team1_id, m.team2_id, p.team_id
        FROM results r
        JOIN match_players mp ON r.match_id=mp.match_id AND r.board=mp.board
        JOIN players p ON mp.player_id=p.id
        JOIN teams t ON p.team_id=t.id
        JOIN matches m ON r.match_id=m.id
    ''').fetchall()

    stats = {}
    for row in rows:
        pid = row['player_id']
        played_as = 'A' if row['team_id']==row['team1_id'] else 'B'
        res = row['result']
        if res=='D': pts=0.5
        elif res=='A': pts = 1 if played_as=='A' else 0
        elif res=='B': pts = 1 if played_as=='B' else 0
        else: continue

        if pid not in stats:
            stats[pid]={'id':pid,'name':row['player_name'],'team':row['team_name'],'points':0.0,'games':0}
        stats[pid]['points']+=pts
        stats[pid]['games']+=1

    db.close()
    players = list(stats.values())
    players.sort(key=lambda x:(-x['points'], x['name']))

    ranked=[]; last_pts=None; last_rank=0
    for i,p in enumerate(players,1):
        if p['points']!=last_pts:
            last_rank=i; last_pts=p['points']
        ranked.append({'rank':last_rank,**p})

    return jsonify({'players':ranked})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')
if __name__ == '__main__':
    app.run(debug=True)
