import { useNavigate } from 'react-router-dom';
import { 
  FileText, 
  MessageSquare, 
  Network, 
  Wrench, 
  ShieldCheck, 
  TrendingUp,
  ArrowUp,
  ArrowDown,
  Clock,
  CheckCircle,
  AlertTriangle,
  Search
} from 'lucide-react';

interface KPICard {
  title: string;
  value: string | number;
  change: number;
  icon: any;
  color: string;
  link: string;
}

interface QuickAction {
  title: string;
  description: string;
  icon: any;
  link: string;
  color: string;
}

interface RecentActivity {
  id: number;
  action: string;
  item: string;
  time: string;
  type: 'document' | 'query' | 'maintenance' | 'compliance';
}

function Dashboard() {
  const navigate = useNavigate();

  const kpiData: KPICard[] = [
    {
      title: 'Total Documents',
      value: '1,247',
      change: 12.5,
      icon: FileText,
      color: 'bg-blue-500',
      link: '/dashboard/documents',
    },
    {
      title: 'AI Queries Today',
      value: '234',
      change: 18.2,
      icon: MessageSquare,
      color: 'bg-green-500',
      link: '/dashboard/copilot',
    },
    {
      title: 'Knowledge Graph Nodes',
      value: '15,891',
      change: 8.2,
      icon: Network,
      color: 'bg-purple-500',
      link: '/dashboard/graph',
    },
    {
      title: 'Pending Maintenance',
      value: '12',
      change: -5.3,
      icon: Wrench,
      color: 'bg-orange-500',
      link: '/dashboard/maintenance',
    },
    {
      title: 'Compliance Score',
      value: '94.2%',
      change: 2.1,
      icon: ShieldCheck,
      color: 'bg-emerald-500',
      link: '/dashboard/compliance',
    },
    {
      title: 'System Health',
      value: '98.5%',
      change: 0.5,
      icon: CheckCircle,
      color: 'bg-teal-500',
      link: '/dashboard/analytics',
    },
  ];

  const quickActions: QuickAction[] = [
    {
      title: 'Upload Document',
      description: 'Add new industrial documents',
      icon: FileText,
      link: '/dashboard/documents',
      color: 'bg-blue-500',
    },
    {
      title: 'Ask AI Copilot',
      description: 'Get answers from your knowledge base',
      icon: MessageSquare,
      link: '/dashboard/copilot',
      color: 'bg-green-500',
    },
    {
      title: 'Explore Graph',
      description: 'Visualize knowledge relationships',
      icon: Network,
      link: '/dashboard/graph',
      color: 'bg-purple-500',
    },
    {
      title: 'Schedule Maintenance',
      description: 'Plan equipment maintenance',
      icon: Wrench,
      link: '/dashboard/maintenance',
      color: 'bg-orange-500',
    },
  ];

  const recentActivity: RecentActivity[] = [
    { id: 1, action: 'Document uploaded', item: 'SOP-2026-042', time: '2 minutes ago', type: 'document' },
    { id: 2, action: 'AI query executed', item: 'Pump failure analysis', time: '15 minutes ago', type: 'query' },
    { id: 3, action: 'Maintenance completed', item: 'Compressor C204', time: '1 hour ago', type: 'maintenance' },
    { id: 4, action: 'Compliance audit passed', item: 'Safety standards', time: '2 hours ago', type: 'compliance' },
    { id: 5, action: 'Knowledge graph updated', item: 'Equipment relationships', time: '3 hours ago', type: 'document' },
    { id: 6, action: 'AI query executed', item: 'Boiler inspection requirements', time: '4 hours ago', type: 'query' },
  ];

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'document':
        return FileText;
      case 'query':
        return MessageSquare;
      case 'maintenance':
        return Wrench;
      case 'compliance':
        return ShieldCheck;
      default:
        return Clock;
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'document':
        return 'bg-blue-100 text-blue-600';
      case 'query':
        return 'bg-green-100 text-green-600';
      case 'maintenance':
        return 'bg-orange-100 text-orange-600';
      case 'compliance':
        return 'bg-emerald-100 text-emerald-600';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-3">
        <div>
          <h1 className="text-xl md:text-2xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-xs md:text-sm text-slate-500">Welcome to IndusMind AI Platform</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative w-full md:w-auto">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search..."
              className="pl-10 pr-4 py-2 border border-slate-300 rounded-lg text-xs md:text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 w-full"
            />
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 md:gap-4">
        {kpiData.map((kpi, index) => {
          const Icon = kpi.icon;
          return (
            <button
              key={index}
              onClick={() => navigate(kpi.link)}
              className="bg-white rounded-lg border border-slate-200 p-3 md:p-4 hover:shadow-md transition-shadow text-left"
            >
              <div className="flex items-center justify-between mb-2 md:mb-3">
                <div className={`p-1.5 md:p-2 rounded-lg ${kpi.color}`}>
                  <Icon className="h-4 w-4 md:h-5 md:w-5 text-white" />
                </div>
                <div className={`flex items-center gap-1 ${kpi.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {kpi.change >= 0 ? <ArrowUp className="h-2.5 w-2.5 md:h-3 md:w-3" /> : <ArrowDown className="h-2.5 w-2.5 md:h-3 md:w-3" />}
                  <span className="text-xs font-medium">{Math.abs(kpi.change)}%</span>
                </div>
              </div>
              <h3 className="text-xs text-slate-500 mb-0.5 md:mb-1 truncate">{kpi.title}</h3>
              <p className="text-sm md:text-xl font-bold text-slate-900">{kpi.value}</p>
            </button>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-base md:text-lg font-semibold text-slate-900 mb-3 md:mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
          {quickActions.map((action, index) => {
            const Icon = action.icon;
            return (
              <button
                key={index}
                onClick={() => navigate(action.link)}
                className="bg-white rounded-lg border border-slate-200 p-4 md:p-6 hover:shadow-md transition-shadow text-left group"
              >
                <div className={`p-2 md:p-3 rounded-lg ${action.color} mb-3 md:mb-4 group-hover:scale-110 transition-transform`}>
                  <Icon className="h-5 w-5 md:h-6 md:w-6 text-white" />
                </div>
                <h3 className="text-sm md:font-semibold text-slate-900 mb-1">{action.title}</h3>
                <p className="text-xs md:text-sm text-slate-500">{action.description}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg border border-slate-200 p-4 md:p-6">
        <div className="flex items-center justify-between mb-3 md:mb-4">
          <h2 className="text-base md:text-lg font-semibold text-slate-900">Recent Activity</h2>
          <button
            onClick={() => navigate('/dashboard/analytics')}
            className="text-xs md:text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            View All
          </button>
        </div>
        <div className="space-y-2 md:space-y-3">
          {recentActivity.map((activity) => {
            const Icon = getActivityIcon(activity.type);
            return (
              <div key={activity.id} className="flex items-start gap-3 md:gap-4 p-2 md:p-3 hover:bg-slate-50 rounded-lg transition-colors">
                <div className={`p-1.5 md:p-2 rounded-lg ${getActivityColor(activity.type)}`}>
                  <Icon className="h-3 w-3 md:h-4 md:w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs md:text-sm text-slate-700">
                    <span className="font-medium">{activity.action}</span>: <span className="truncate">{activity.item}</span>
                  </p>
                  <p className="text-xs text-slate-500">{activity.time}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* System Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
        <div className="bg-white rounded-lg border border-slate-200 p-4 md:p-6">
          <div className="flex items-center gap-3 mb-3 md:mb-4">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="h-4 w-4 md:h-5 md:w-5 text-green-600" />
            </div>
            <h3 className="text-sm md:font-semibold text-slate-900">System Status</h3>
          </div>
          <div className="space-y-2 md:space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-xs md:text-sm text-slate-500">API Server</span>
              <span className="text-xs md:text-sm font-medium text-green-600">Operational</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs md:text-sm text-slate-500">Database</span>
              <span className="text-xs md:text-sm font-medium text-green-600">Operational</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs md:text-sm text-slate-500">AI Services</span>
              <span className="text-xs md:text-sm font-medium text-green-600">Operational</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs md:text-sm text-slate-500">Knowledge Graph</span>
              <span className="text-xs md:text-sm font-medium text-green-600">Operational</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 p-4 md:p-6">
          <div className="flex items-center gap-3 mb-3 md:mb-4">
            <div className="p-2 bg-blue-100 rounded-lg">
              <TrendingUp className="h-4 w-4 md:h-5 md:w-5 text-blue-600" />
            </div>
            <h3 className="text-sm md:font-semibold text-slate-900">Weekly Summary</h3>
          </div>
          <div className="space-y-2 md:space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-xs md:text-sm text-slate-500">Documents Processed</span>
              <span className="text-xs md:text-sm font-medium text-slate-900">127</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs md:text-sm text-slate-500">AI Queries</span>
              <span className="text-xs md:text-sm font-medium text-slate-900">1,842</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs md:text-sm text-slate-500">Maintenance Tasks</span>
              <span className="text-xs md:text-sm font-medium text-slate-900">23</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs md:text-sm text-slate-500">Compliance Audits</span>
              <span className="text-xs md:text-sm font-medium text-slate-900">5</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 p-4 md:p-6">
          <div className="flex items-center gap-3 mb-3 md:mb-4">
            <div className="p-2 bg-orange-100 rounded-lg">
              <AlertTriangle className="h-4 w-4 md:h-5 md:w-5 text-orange-600" />
            </div>
            <h3 className="text-sm md:font-semibold text-slate-900">Alerts</h3>
          </div>
          <div className="space-y-2 md:space-y-3">
            <div className="flex items-start gap-2">
              <div className="w-1.5 h-1.5 md:w-2 md:h-2 mt-1 md:mt-1.5 rounded-full bg-red-500" />
              <div>
                <p className="text-xs md:text-sm font-medium text-slate-900">Pump P101 Maintenance Overdue</p>
                <p className="text-xs text-slate-500">3 days overdue</p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <div className="w-1.5 h-1.5 md:w-2 md:h-2 mt-1 md:mt-1.5 rounded-full bg-orange-500" />
              <div>
                <p className="text-xs md:text-sm font-medium text-slate-900">Environmental Permit Expiring</p>
                <p className="text-xs text-slate-500">Expires in 15 days</p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <div className="w-1.5 h-1.5 md:w-2 md:h-2 mt-1 md:mt-1.5 rounded-full bg-yellow-500" />
              <div>
                <p className="text-xs md:text-sm font-medium text-slate-900">Quality Audit Pending</p>
                <p className="text-xs text-slate-500">Due in 30 days</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
