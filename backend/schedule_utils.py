# backend/schedule_utils.py

def generate_round_robin(team_ids):
    """
    Generate a round-robin schedule for the given list of team IDs.
    Returns a list of rounds, each round is a list of (team1_id, team2_id) tuples.
    """
    teams = list(team_ids)
    if len(teams) % 2 != 0:
        teams.append(None)  # Add a bye if odd number of teams

    n = len(teams)
    rounds = []
    for round_num in range(n - 1):
        round_matches = []
        for i in range(n // 2):
            t1 = teams[i]
            t2 = teams[n - 1 - i]
            if t1 is not None and t2 is not None:
                round_matches.append((t1, t2))
        # Rotate teams except the first
        teams = [teams[0]] + [teams[-1]] + teams[1:-1]
        rounds.append(round_matches)
    return rounds
