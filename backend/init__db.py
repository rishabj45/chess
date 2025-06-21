# backend/init_db.py

import sqlite3
import string
from schedule_utils import generate_round_robin  # your round-robin generator

DB_PATH = 'tournament.db'
NUM_TEAMS = 5  # change this to initialize a different number of teams

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        rating INTEGER DEFAULT 1000,
        team_id INTEGER,
        FOREIGN KEY (team_id) REFERENCES teams(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        round INTEGER,
        team1_id INTEGER,
        team2_id INTEGER,
        team1_score REAL DEFAULT 0,
        team2_score REAL DEFAULT 0,
        FOREIGN KEY (team1_id) REFERENCES teams(id),
        FOREIGN KEY (team2_id) REFERENCES teams(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        board INTEGER,
        result TEXT,
        FOREIGN KEY (match_id) REFERENCES matches(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS match_players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        board INTEGER,
        team_id INTEGER,
        player_id INTEGER,
        FOREIGN KEY (match_id) REFERENCES matches(id),
        FOREIGN KEY (team_id) REFERENCES teams(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS rounds (
        round INTEGER PRIMARY KEY,
        start_time TEXT DEFAULT '2025-06-20 10:00'
    )''')

    # 2. Insert default teams
    team_ids = []
    for i in range(NUM_TEAMS):
        team_name = f"Team {string.ascii_uppercase[i]}"
        c.execute('INSERT INTO teams (name) VALUES (?)', (team_name,))
        team_ids.append(c.lastrowid)

    # 3. Insert 4 players per team
    for idx, team_id in enumerate(team_ids):
        for j in range(4):
            player_name = f"Player {string.ascii_uppercase[idx]}{j+1}"
            c.execute('INSERT INTO players (name, team_id) VALUES (?, ?)', (player_name, team_id))

    # 4. Generate match schedule
    pairs_by_round = generate_round_robin(team_ids)

    for round_no, matches in enumerate(pairs_by_round, start=1):
        default_time = f'2025-06-{19 + round_no:02d} 10:00'
        c.execute('INSERT OR IGNORE INTO rounds (round, start_time) VALUES (?, ?)', (round_no, default_time))

        for t1, t2 in matches:
            c.execute('INSERT INTO matches (round, team1_id, team2_id) VALUES (?, ?, ?)', (round_no, t1, t2))
            match_id = c.lastrowid

            # Get top 4 players from each team
            c.execute('SELECT id FROM players WHERE team_id=? ORDER BY id LIMIT 4', (t1,))
            team1_players = [row[0] for row in c.fetchall()]

            c.execute('SELECT id FROM players WHERE team_id=? ORDER BY id LIMIT 4', (t2,))
            team2_players = [row[0] for row in c.fetchall()]

            for board_no in range(1, 5):
                if board_no <= len(team1_players):
                    c.execute('''
                        INSERT INTO match_players (match_id, board, team_id, player_id)
                        VALUES (?, ?, ?, ?)
                    ''', (match_id, board_no, t1, team1_players[board_no - 1]))
                if board_no <= len(team2_players):
                    c.execute('''
                        INSERT INTO match_players (match_id, board, team_id, player_id)
                        VALUES (?, ?, ?, ?)
                    ''', (match_id, board_no, t2, team2_players[board_no - 1]))

    conn.commit()
    conn.close()
    print(f"Initialized tournament with {NUM_TEAMS} teams.")

if __name__ == '__main__':
    init_db()
