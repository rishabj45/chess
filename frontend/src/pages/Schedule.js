import React, { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';

export default function Schedule() {
  const { isAdmin } = useOutletContext();
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [boardResults, setBoardResults] = useState({});

  useEffect(() => {
    fetchMatches();
  }, []);

  const fetchMatches = async () => {
    try {
      const res = await fetch('/api/matches');
      if (!res.ok) throw new Error('Failed to load schedule');
      const list = await res.json();
      const detailed = await Promise.all(
        list.map(async (m) => {
          const r = await fetch(`/api/match/${m.id}/full-details`);
          if (!r.ok) throw new Error(`Failed to load match ${m.id}`);
          return r.json();
        })
      );
      setMatches(detailed);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setError(err.message);
      setLoading(false);
    }
  };

  const formatTime = (dt) =>
    new Date(dt).toLocaleString(undefined, {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });

  const groupByRound = matches.reduce((acc, full) => {
    const rnd = full.match.round;
    acc[rnd] = acc[rnd] || [];
    acc[rnd].push(full);
    return acc;
  }, {});

  const handleRoundTimeUpdate = async (round, newDateTime) => {
    const iso = new Date(newDateTime).toISOString();
    const res = await fetch('/api/update-match', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ round: parseInt(round), date_time: iso }),
    });
    if (res.ok) {
      setMatches(prev =>
        prev.map(m =>
          m.match.round === parseInt(round)
            ? { ...m, match: { ...m.match, date_time: iso } }
            : m
        )
      );
    }
  };

  const submitBoardResult = async (matchId, board, result) => {
    const res = await fetch(`/api/match/${matchId}/submit-single`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ board, result }),
    });
    if (res.ok) {
      await fetchMatches(); // reload everything
    }
  };

  if (loading) return <div className="text-center p-8">Loading schedule…</div>;
  if (error) return <div className="text-red-600 text-center p-8">Error: {error}</div>;

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Tournament Schedule</h1>

      {Object.entries(groupByRound).map(([round, group]) => (
        <div key={round} className="mb-6">
          <h2 className="text-xl font-semibold mb-1">Round {round}</h2>

          {isAdmin ? (
            <input
              type="datetime-local"
              defaultValue={new Date(group[0].match.date_time).toISOString().slice(0, 16)}
              onBlur={(e) => handleRoundTimeUpdate(round, e.target.value)}
              className="mb-2 border px-2 py-1 rounded"
            />
          ) : (
            <p className="text-gray-600 mb-2">
              {formatTime(group[0].match.date_time)}
            </p>
          )}

          {group.map(({ match, players, results }) => {
            const team1 = match.team1_name;
            const team2 = match.team2_name;
            const hasResults = results && results.length > 0;

            const p1 = players.filter(p => p.team_id === match.team1_id);
            const p2 = players.filter(p => p.team_id === match.team2_id);

            const boardScores = results.reduce((acc, r) => {
              let scoreA = 0, scoreB = 0;
              if (r.result === 'A') scoreA = 1;
              else if (r.result === 'B') scoreB = 1;
              else if (r.result === 'D') { scoreA = 0.5; scoreB = 0.5; }
              acc[r.board] = { scoreA, scoreB, raw: r.result };
              return acc;
            }, {});

            return (
              <details key={match.id} className="border rounded-lg mb-4 shadow-sm">
                <summary className="flex justify-between items-center bg-blue-50 p-3 cursor-pointer">
                  <div>
                    <span className="font-medium">{team1}</span> vs{' '}
                    <span className="font-medium">{team2}</span>
                  </div>
                  {hasResults && (
                    <div className="text-gray-600 font-semibold">
                      ({match.team1_score}-{match.team2_score})
                    </div>
                  )}
                </summary>

                <div className="p-3 bg-white">
                  <ul className="space-y-1">
                    {[1, 2, 3, 4].map(board => {
                      const nameA = p1.find(x => x.board === board)?.player_name || `Board ${board}`;
                      const nameB = p2.find(x => x.board === board)?.player_name || `Board ${board}`;
                      const sc = boardScores[board];
                      const key = `${match.id}-${board}`;
                      const selected = boardResults[key] || '';

                      return (
                        <li key={board} className="flex justify-between items-center">
                          <span>{nameA} vs {nameB}</span>
                          {sc ? (
                            <span>{sc.scoreA}-{sc.scoreB}</span>
                          ) : isAdmin ? (
                            <div className="flex items-center space-x-2">
                              <select
                                value={selected}
                                onChange={(e) =>
                                  setBoardResults(prev => ({ ...prev, [key]: e.target.value }))
                                }
                                className="border rounded px-1 py-0.5"
                              >
                                <option value="">Result</option>
                                <option value="A">A wins</option>
                                <option value="B">B wins</option>
                                <option value="D">Draw</option>
                              </select>
                              <button
                                onClick={() => submitBoardResult(match.id, board, selected)}
                                disabled={!selected}
                                className="bg-blue-500 text-white px-2 py-1 rounded text-sm disabled:opacity-50"
                              >
                                Submit
                              </button>
                            </div>
                          ) : null}
                        </li>
                      );
                    })}
                  </ul>
                </div>
              </details>
            );
          })}
        </div>
      ))}
    </div>
  );
}
