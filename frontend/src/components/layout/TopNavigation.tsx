import { LogOut, Menu, LayoutDashboard, FileText, Network, Wrench, ShieldCheck, BarChart3, Settings, MessageSquare, User } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useUIStore, useAuthStore } from '../../stores';
import { cn } from '../../utils';
import { useState, useRef, useEffect } from 'react';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'AI Copilot', href: '/dashboard/copilot', icon: MessageSquare },
  { name: 'Documents', href: '/dashboard/documents', icon: FileText },
  { name: 'Knowledge Graph', href: '/dashboard/graph', icon: Network },
  { name: 'Maintenance', href: '/dashboard/maintenance', icon: Wrench },
  { name: 'Compliance', href: '/dashboard/compliance', icon: ShieldCheck },
  { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3 },
];

export function TopNavigation() {
  const { toggleSidebar } = useUIStore();
  const { user, logout } = useAuthStore();
  const location = useLocation();
  const navigate = useNavigate();
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowProfileDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <header className="fixed top-0 left-0 right-0 z-30 h-16 bg-gray-900 text-gray-100 border-b border-gray-800">
      <div className="max-w-[1400px] mx-auto px-4 md:px-6 h-full flex items-center justify-between">
        {/* Left Section */}
        <div className="flex items-center gap-4">
          {/* Mobile Menu Button */}
          <button
            onClick={toggleSidebar}
            className="md:hidden p-2 rounded-lg hover:bg-gray-800 transition-colors"
            aria-label="Toggle menu"
          >
            <Menu className="h-6 w-6 text-gray-300" />
          </button>

          {/* Logo */}
          <div className="flex items-center gap-2">
            <h1 className="text-xl md:text-xl font-semibold text-white tracking-tight">🧠 IndusMind AI</h1>
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-4 md:gap-6">
          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.href;

              return (
                <button
                  key={item.name}
                  onClick={() => navigate(item.href)}
                  className={cn(
                    'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                  )}
                  aria-label={item.name}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.name}</span>
                </button>
              );
            })}
          </nav>

          {/* User Menu */}
          <div className="relative hidden md:block" ref={dropdownRef}>
            <button
              onClick={() => setShowProfileDropdown(!showProfileDropdown)}
              className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-medium hover:bg-blue-700 transition-colors"
              aria-label="User menu"
            >
              {user?.full_name?.charAt(0) || 'U'}
            </button>

            {/* Profile Dropdown */}
            {showProfileDropdown && (
              <div className="absolute right-0 mt-2 w-64 bg-gray-800 rounded-lg shadow-lg border border-gray-700 py-2 z-50">
                {/* Profile Header */}
                <div className="px-4 py-3 border-b border-gray-700">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-medium">
                      {user?.full_name?.charAt(0) || 'U'}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">{user?.full_name || 'User'}</p>
                      <p className="text-xs text-gray-400">{user?.email || 'user@example.com'}</p>
                    </div>
                  </div>
                </div>

                {/* Profile Link */}
                <button
                  onClick={() => {
                    navigate('/dashboard/profile');
                    setShowProfileDropdown(false);
                  }}
                  className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 transition-colors"
                >
                  <User className="h-4 w-4" />
                  <span>Profile</span>
                </button>

                {/* Settings Link */}
                <button
                  onClick={() => {
                    navigate('/dashboard/settings');
                    setShowProfileDropdown(false);
                  }}
                  className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 transition-colors"
                >
                  <Settings className="h-4 w-4" />
                  <span>Settings</span>
                </button>

                <div className="border-t border-gray-700 my-1"></div>

                {/* Logout */}
                <button
                  onClick={() => {
                    logout();
                    setShowProfileDropdown(false);
                  }}
                  className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-400 hover:bg-red-900/20 transition-colors"
                >
                  <LogOut className="h-4 w-4" />
                  <span>Logout</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
