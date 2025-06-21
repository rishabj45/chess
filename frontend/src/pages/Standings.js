// src/pages/Standings.js
import React, { useEffect, useState } from 'react';

export default function Standings() {
  const [table, setTable] = useState([]);

  useEffect(() => {
    fetch('/api/standings')
      .then(res => res.json())
      .then(data => setTable(data))
      .catch(console.error);
  }, []);

  return (
    <table className="w-full table-auto bg-white shadow rounded">
      <thead className="bg-gray-200">
        <tr>
          <th>#</th>
          <th>Team</th>
          <th>Played</th>
          <th>MatchPts</th>
          <th>GamePts</th>
        </tr>
      </thead>
      <tbody>
        {table.map((t, i) => (
          <tr key={t.id} className="border-t">
            <td>{i + 1}</td>
            <td>{t.name}</td>
            <td className="text-center">{t.played}</td>
            <td className="text-center">{t.match_points}</td>
            <td className="text-center">{t.game_points}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
