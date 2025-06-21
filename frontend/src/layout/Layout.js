import { Link, Outlet, useLocation } from 'react-router-dom';

export default function Layout({ isAdmin, setIsAdmin }) {
  const location = useLocation();
  const active = (path) =>
    location.pathname === path || (path === '/schedule' && location.pathname === '/') 
      ? 'font-bold text-blue-600'
      : '';

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow p-4 text-center text-2xl font-semibold">
        Chess Tournament 2025
      </header>

      <nav className="flex justify-between items-center bg-gray-100 px-6 py-2 text-lg">
        <div className="flex space-x-6">
          <Link to="/schedule" className={active('/schedule')}>Schedule & Results</Link>
          <Link to="/standings" className={active('/standings')}>Standings</Link>
          <Link to="/teams" className={active('/teams')}>Teams</Link>
          <Link to="/best-player" className={active('/best-player')}>Best Player</Link>
        </div>
        <button
          onClick={() => setIsAdmin(prev => !prev)}
          className={`px-3 py-1 rounded font-semibold ${
            isAdmin
              ? 'bg-yellow-500 text-white hover:bg-yellow-400'
              : 'bg-gray-300 text-gray-700 hover:bg-gray-400'
          }`}
        >
          {isAdmin ? 'Admin Mode: ON' : 'Admin Mode: OFF'}
        </button>
      </nav>

      <main className="p-4">
        <Outlet context={{ isAdmin }} />
      </main>
    </div>
  );
}
