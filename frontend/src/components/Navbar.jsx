import { Link, useLocation, useNavigate } from 'react-router-dom'
import { LogOut, FileText, MessageSquare, Upload, Brain } from 'lucide-react'
import { logout } from '../services/api'

export default function Navbar() {
  const location = useLocation()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const navItems = [
    { path: '/chat', label: 'Chat', icon: MessageSquare },
    { path: '/upload', label: 'Upload', icon: Upload },
    { path: '/documents', label: 'Documents', icon: FileText },
  ]

  return (
    <nav className="glass border-b border-dark-700/50 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/chat" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-purple-600 
                          flex items-center justify-center shadow-lg shadow-primary-500/20 
                          group-hover:shadow-primary-500/40 transition-all duration-300">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold gradient-text">DocuQuery AI</span>
          </Link>

          {/* Nav Links */}
          <div className="flex items-center gap-1">
            {navItems.map(({ path, label, icon: Icon }) => (
              <Link
                key={path}
                to={path}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium 
                          transition-all duration-300 ${
                  location.pathname === path
                    ? 'bg-primary-500/15 text-primary-400 border border-primary-500/30'
                    : 'text-dark-400 hover:text-dark-200 hover:bg-dark-700/50'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{label}</span>
              </Link>
            ))}

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium 
                       text-dark-400 hover:text-red-400 hover:bg-red-500/10 
                       transition-all duration-300 ml-2"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
