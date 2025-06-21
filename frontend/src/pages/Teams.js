import React, { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';

export default function Teams() {
  const { isAdmin } = useOutletContext();
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTeams();
  }, []);

  const fetchTeams = async () => {
    try {
      const res = await fetch('http://127.0.0.1:5000/api/teams');
      if (!res.ok) throw new Error('Failed to fetch teams');
      const data = await res.json();
      setTeams(data);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setError(err.message);
      setLoading(false);
    }
  };

  const updateTeamName = async (teamId, name) => {
    await fetch(`http://127.0.0.1:5000/api/team/${teamId}/edit-name`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    });
    fetchTeams(); // refresh after update
  };

  const updatePlayer = async (playerId, field, value) => {
  // find current player
  const team = teams.find(t => t.players.some(p => p.id === playerId));
  const player = team.players.find(p => p.id === playerId);
  if (!player) return;

  if (field === 'name') {
    await fetch(`http://127.0.0.1:5000/api/player/${playerId}/edit-name`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: value }),
    });
  } else {
    // rating
    await fetch(`http://127.0.0.1:5000/api/player/${playerId}/edit-rating`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rating: parseInt(value, 10) }),
    });
  }

  // Refresh the data
  fetchTeams();
};


  if (loading) return <div className="text-center p-8">Loading teams…</div>;
  if (error) return <div className="text-red-600 text-center p-8">Error: {error}</div>;

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Teams</h1>

      {teams.map((team) => (
        <div key={team.id} className="border rounded mb-6 shadow">
          <div className="bg-gray-100 p-3">
            {isAdmin ? (
              <input
                defaultValue={team.name}
                onBlur={(e) => updateTeamName(team.id, e.target.value)}
                className="text-xl font-semibold border rounded px-2 py-1"
              />
            ) : (
              <h2 className="text-xl font-semibold">{team.name}</h2>
            )}
          </div>
          <div className="p-3">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b">
                  <th className="py-1">#</th>
                  <th className="py-1">Name</th>
                  <th className="py-1">Rating</th>
                </tr>
              </thead>
              <tbody>
                {team.players.map((player, idx) => (
                  <tr key={player.id} className="border-b">
                    <td className="py-1 pr-2">{idx + 1}</td>
                    <td className="py-1 pr-2">
                      {isAdmin ? (
                        <input
                          defaultValue={player.name}
                          onBlur={(e) =>
                            updatePlayer(player.id, 'name', e.target.value)
                          }
                          className="border rounded px-2 py-1 w-full"
                        />
                      ) : (
                        player.name
                      )}
                    </td>
                    <td className="py-1 pr-2">
                      {isAdmin ? (
                        <input
                          type="number"
                          defaultValue={player.rating}
                          onBlur={(e) =>
                            updatePlayer(player.id, 'rating', parseInt(e.target.value))
                          }
                          className="border rounded px-2 py-1 w-20"
                        />
                      ) : (
                        player.rating
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
}
