import { useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../services/useAuth';

export default function Navbar() {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const avatarLabel = user?.full_name
    ? user.full_name.split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase()
    : user?.email?.charAt(0).toUpperCase() || 'U';

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/90 backdrop-blur-xl shadow-sm shadow-slate-200">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-4">
          <Link to="/" className="inline-flex items-center gap-3 rounded-3xl bg-slate-900 px-4 py-3 text-white shadow-lg shadow-slate-900/10 transition hover:bg-slate-800">
            <span className="font-bold">AI</span>
            <span className="text-sm font-medium">Summarizer</span>
          </Link>
          <nav className="hidden items-center gap-4 md:flex">
            <NavLink to="/" className={({ isActive }) => isActive ? 'text-slate-900 font-semibold' : 'text-slate-600 hover:text-slate-900'}>Home</NavLink>
            <NavLink to="/quiz" className={({ isActive }) => isActive ? 'text-slate-900 font-semibold' : 'text-slate-600 hover:text-slate-900'}>Quiz</NavLink>
            <NavLink to="/about" className={({ isActive }) => isActive ? 'text-slate-900 font-semibold' : 'text-slate-600 hover:text-slate-900'}>About</NavLink>
            <NavLink to="/leaderboard" className={({ isActive }) => isActive ? 'text-slate-900 font-semibold' : 'text-slate-600 hover:text-slate-900'}>Leaderboard</NavLink>
          </nav>
        </div>

        <div className="flex items-center gap-3">
          {!isAuthenticated ? (
            <div className="flex items-center gap-3">
              <Link to="/login" className="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50">Login</Link>
              <Link to="/register" className="rounded-full bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800">Register</Link>
            </div>
          ) : (
            <div className="relative">
              <button
                type="button"
                onClick={() => setDropdownOpen((prev) => !prev)}
                className="inline-flex h-11 w-11 items-center justify-center rounded-full bg-slate-900 text-sm font-semibold text-white shadow-lg shadow-slate-900/10"
              >
                {avatarLabel}
              </button>

              {dropdownOpen && (
                <div className="absolute right-0 mt-3 w-48 rounded-3xl border border-slate-200 bg-white p-3 shadow-lg shadow-slate-900/10">
                  <Link
                    to="/profile"
                    onClick={() => setDropdownOpen(false)}
                    className="block rounded-2xl px-3 py-2 text-sm text-slate-700 hover:bg-slate-100"
                  >
                    Profile
                  </Link>
                  <Link
                    to="/history"
                    onClick={() => setDropdownOpen(false)}
                    className="block rounded-2xl px-3 py-2 text-sm text-slate-700 hover:bg-slate-100"
                  >
                    History
                  </Link>
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="mt-2 w-full rounded-2xl bg-slate-900 px-3 py-2 text-sm font-semibold text-white hover:bg-slate-800"
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
