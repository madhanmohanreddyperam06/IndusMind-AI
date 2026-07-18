import { useLocation, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FileText, 
  Network, 
  Wrench, 
  ShieldCheck, 
  BarChart3, 
  User,
  LogOut,
  Settings,
  MessageSquare,
  ChevronLeft
} from 'lucide-react';
import { useUIStore, useAuthStore } from '../../stores';
import { cn } from '../../utils';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'AI Copilot', href: '/dashboard/copilot', icon: MessageSquare },
  { name: 'Documents', href: '/dashboard/documents', icon: FileText },
  { name: 'Knowledge Graph', href: '/dashboard/graph', icon: Network },
  { name: 'Maintenance', href: '/dashboard/maintenance', icon: Wrench },
  { name: 'Compliance', href: '/dashboard/compliance', icon: ShieldCheck },
  { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3 },
];

export function Sidebar() {
  const { sidebarOpen, toggleSidebar } = useUIStore();
  const { user, logout } = useAuthStore();
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <div
      className={cn(
        'fixed left-0 top-0 z-40 h-screen bg-slate-900 text-white transition-all duration-300',
        'md:hidden', // Hidden on desktop, only visible on mobile
        sidebarOpen ? 'w-64' : 'w-16',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full' // Mobile slide behavior
      )}
    >
      {/* Mobile Close Button */}
      <button
        onClick={toggleSidebar}
        className="absolute right-4 top-4 z-50 flex h-8 w-8 items-center justify-center rounded-full bg-slate-700 text-white hover:bg-slate-600"
        aria-label="Close sidebar"
      >
        <ChevronLeft className="h-5 w-5" />
      </button>

      {/* Logo */}
      <div className="flex h-16 items-center justify-center border-b border-slate-700 px-4">
        {sidebarOpen ? (
          <span className="text-xl font-bold">🧠 IndusMind AI</span>
        ) : (
          <span className="text-xl font-bold">🧠</span>
        )}
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-2">
        {navigation.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.href;

          return (
            <button
              key={item.name}
              onClick={() => {
                navigate(item.href);
                // Close sidebar on mobile after navigation
                toggleSidebar();
              }}
              className={cn(
                'flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              )}
              aria-label={item.name}
            >
              <Icon className="h-5 w-5 flex-shrink-0" />
              {sidebarOpen && <span>{item.name}</span>}
            </button>
          );
        })}
      </nav>

      {/* User Info */}
      <div className="absolute bottom-0 left-0 right-0 border-t border-slate-700 p-4">
        {sidebarOpen ? (
          <div className="space-y-3">
            {/* Profile Header */}
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-medium">
                {user?.full_name?.charAt(0) || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{user?.full_name || 'User'}</p>
                <p className="text-xs text-slate-400 truncate">{user?.email || 'user@example.com'}</p>
              </div>
            </div>

            {/* Profile Link */}
            <button
              onClick={() => {
                navigate('/dashboard/profile');
                toggleSidebar();
              }}
              className="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-300 hover:bg-slate-800 rounded-lg transition-colors"
            >
              <User className="h-4 w-4" />
              <span>Profile</span>
            </button>

            {/* Settings Link */}
            <button
              onClick={() => {
                navigate('/dashboard/settings');
                toggleSidebar();
              }}
              className="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-300 hover:bg-slate-800 rounded-lg transition-colors"
            >
              <Settings className="h-4 w-4" />
              <span>Settings</span>
            </button>

            <div className="border-t border-slate-700"></div>

            {/* Logout */}
            <button
              onClick={() => {
                logout();
                toggleSidebar();
              }}
              className="w-full flex items-center gap-3 px-3 py-2 text-sm text-red-400 hover:bg-red-900/20 rounded-lg transition-colors"
            >
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </button>
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-sm font-medium">
              {user?.full_name?.charAt(0) || 'U'}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
