import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useState } from 'react';
import Layout from './layout/Layout';
import Schedule from './pages/Schedule';
import Standings from './pages/Standings';
import Teams from './pages/Teams';
import BestPlayer from './pages/BestPlayer';

export default function App() {
  const [isAdmin, setIsAdmin] = useState(false);

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={<Layout isAdmin={isAdmin} setIsAdmin={setIsAdmin} />}
        >
          <Route index element={<Schedule />} /> {/* Renders Schedule at "/" */}
          <Route path="schedule" element={<Schedule />} />
          <Route path="standings" element={<Standings />} />
          <Route path="teams" element={<Teams />} />
          <Route path="best-player" element={<BestPlayer />} />
        </Route>
      </Routes>
    </Router>
  );
}
