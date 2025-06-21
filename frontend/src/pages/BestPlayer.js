import React, { useEffect, useState } from 'react';

function BestPlayer() {
  const [players, setPlayers] = useState([]);

  useEffect(() => {
    fetch('/api/best_players')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data.players)) {
          setPlayers(data.players);
        } else {
          setPlayers([]); // fallback if API returns bad structure
        }
      })
      .catch(err => {
        console.error('Failed to fetch best players:', err);
        setPlayers([]);
      });
  }, []);

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Best Players</h1>

      {players.length === 0 ? (
        <p className="text-gray-600">No player results yet.</p>
      ) : (
        <table className="w-full border-collapse">
          <thead>
            <tr>
              <th className="border p-2">Rank</th>
              <th className="border p-2">Name</th>
              <th className="border p-2">Team</th>
              <th className="border p-2">Points</th>
              <th className="border p-2">Games</th>
              <th className="border p-2">Performance</th>
            </tr>
          </thead>
          <tbody>
            {players.map((p, idx) => (
              <tr key={p.player_id}>
                <td className="border p-2">{p.rank}</td>
                <td className="border p-2">{p.name}</td>
                <td className="border p-2">{p.team_name}</td>
                <td className="border p-2">{p.points}</td>
                <td className="border p-2">{p.games}</td>
                <td className="border p-2">{p.performance}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default BestPlayer;
