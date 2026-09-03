import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🔔</span>
            <h1 className="text-xl font-bold text-gray-900">NotifyApp</h1>
          </div>

          {isAuthenticated && (
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">
                Hola, <span className="font-medium">{user?.username}</span>
              </span>
              <button
                onClick={handleLogout}
                className="text-sm text-red-600 hover:text-red-800 font-medium cursor-pointer"
              >
                Cerrar Sesión
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
