import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores';

function Profile() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/signin');
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-slate-500 text-sm">Please log in to view your profile</div>
      </div>
    );
  }

  // Debug: log user data
  console.log('Profile user data:', user);

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-2xl mx-auto px-4 py-6 md:py-8">
        <div className="bg-white rounded-lg shadow-sm border border-slate-200">
          {/* Profile Card */}
          <div className="px-6 py-8">
            {/* Avatar */}
            <div className="flex items-center justify-center mb-6">
              <div className="w-20 h-20 md:w-24 md:h-24 bg-blue-600 rounded-full flex items-center justify-center text-white text-2xl md:text-3xl font-semibold">
                {user.full_name?.charAt(0).toUpperCase() || user.email?.charAt(0).toUpperCase() || 'U'}
              </div>
            </div>

            {/* User Details */}
            <div className="space-y-4">
              <div className="text-center">
                <h1 className="text-xl md:text-2xl font-semibold text-slate-900 mb-1">
                  {user.full_name || 'User'}
                </h1>
                <p className="text-sm text-slate-500">Member since {formatDate(user.created_at)}</p>
              </div>

              <div className="pt-6 border-t border-slate-200 space-y-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Full Name</label>
                  <p className="text-sm md:text-base text-slate-900 font-medium">{user.full_name || 'Not set'}</p>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Email Address</label>
                  <p className="text-sm md:text-base text-slate-900">{user.email || 'Not set'}</p>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Date Joined</label>
                  <p className="text-sm md:text-base text-slate-900">{formatDate(user.created_at)}</p>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">User ID</label>
                  <p className="text-sm md:text-base text-slate-900 font-mono">{user.id || 'Not set'}</p>
                </div>
              </div>
            </div>

            {/* Logout Button */}
            <div className="pt-6 mt-6 border-t border-slate-200">
              <button
                onClick={handleLogout}
                className="w-full px-4 py-2.5 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Profile;
