import { useState } from 'react';
import { BarChart3, FileText, MessageSquare, Network, AlertTriangle, CheckCircle, ArrowUp, ArrowDown } from 'lucide-react';

interface KPICard {
  title: string;
  value: string | number;
  change: number;
  icon: any;
  color: string;
}

interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    color: string;
  }[];
}

function Analytics() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d');

  const kpiData: KPICard[] = [
    {
      title: 'Total Documents',
      value: '1,247',
      change: 12.5,
      icon: FileText,
      color: 'bg-blue-500',
    },
    {
      title: 'AI Queries',
      value: '8,432',
      change: 23.7,
      icon: MessageSquare,
      color: 'bg-green-500',
    },
    {
      title: 'Knowledge Graph Nodes',
      value: '15,891',
      change: 8.2,
      icon: Network,
      color: 'bg-purple-500',
    },
    {
      title: 'Compliance Score',
      value: '94.2%',
      change: 2.1,
      icon: CheckCircle,
      color: 'bg-emerald-500',
    },
  ];

  const documentProcessingData: ChartData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Documents Processed',
        data: [45, 52, 38, 61, 55, 23, 18],
        color: '#3b82f6',
      },
    ],
  };

  const aiUsageData: ChartData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'AI Queries',
        data: [320, 450, 380, 520, 480, 210, 180],
        color: '#10b981',
      },
    ],
  };

  const complianceTrendData: ChartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Compliance Score',
        data: [89, 91, 88, 92, 93, 94],
        color: '#8b5cf6',
      },
    ],
  };

  const topIssues = [
    { id: 1, issue: 'Pump P101 Maintenance Overdue', severity: 'critical', count: 3 },
    { id: 2, issue: 'Safety Documentation Missing', severity: 'high', count: 5 },
    { id: 3, issue: 'Environmental Permit Expiring', severity: 'high', count: 1 },
    { id: 4, issue: 'Quality Audit Pending', severity: 'medium', count: 2 },
    { id: 5, issue: 'Equipment Calibration Due', severity: 'medium', count: 4 },
  ];

  const recentActivity = [
    { id: 1, action: 'Document uploaded', item: 'SOP-2026-042', time: '2 minutes ago' },
    { id: 2, action: 'AI query executed', item: 'Pump failure analysis', time: '15 minutes ago' },
    { id: 3, action: 'Knowledge graph updated', item: 'Equipment relationships', time: '1 hour ago' },
    { id: 4, action: 'Compliance audit completed', item: 'Safety standards', time: '2 hours ago' },
    { id: 5, action: 'Maintenance scheduled', item: 'Compressor C204', time: '3 hours ago' },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-900 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-900 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-900 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-900 border-green-200';
      default:
        return 'bg-gray-100 text-gray-900 border-gray-200';
    }
  };

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-3">
        <div>
          <h1 className="text-xl md:text-2xl font-bold text-slate-900">Analytics Dashboard</h1>
          <p className="text-xs md:text-sm text-slate-500">Executive KPIs and system performance metrics</p>
        </div>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value as any)}
          className="px-3 md:px-4 py-2 border border-slate-300 rounded-lg text-xs md:text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 self-start md:self-auto"
        >
          <option value="7d">Last 7 Days</option>
          <option value="30d">Last 30 Days</option>
          <option value="90d">Last 90 Days</option>
          <option value="1y">Last Year</option>
        </select>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
        {kpiData.map((kpi, index) => {
          const Icon = kpi.icon;
          return (
            <div key={index} className="bg-white rounded-lg border border-slate-200 p-3 md:p-6">
              <div className="flex items-center justify-between mb-2 md:mb-4">
                <div className={`p-1.5 md:p-3 rounded-lg ${kpi.color}`}>
                  <Icon className="h-4 w-4 md:h-6 md:w-6 text-white" />
                </div>
                <div className={`flex items-center gap-1 ${kpi.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {kpi.change >= 0 ? <ArrowUp className="h-2.5 w-2.5 md:h-4 md:w-4" /> : <ArrowDown className="h-2.5 w-2.5 md:h-4 md:w-4" />}
                  <span className="text-sm font-medium">{Math.abs(kpi.change)}%</span>
                </div>
              </div>
              <h3 className="text-xs md:text-sm text-slate-500 mb-0.5 md:mb-1">{kpi.title}</h3>
              <p className="text-lg md:text-2xl font-bold text-slate-900">{kpi.value}</p>
            </div>
          );
        })}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
        {/* Document Processing Chart */}
        <div className="bg-white rounded-lg border border-slate-200 p-4 md:p-6">
          <h2 className="text-base md:text-lg font-semibold text-slate-900 mb-3 md:mb-4">Document Processing</h2>
          <div className="h-48 md:h-64 flex items-end justify-between gap-1 md:gap-2">
            {documentProcessingData.labels.map((label, index) => (
              <div key={label} className="flex-1 flex flex-col items-center">
                <div
                  className="w-full bg-blue-500 rounded-t transition-all hover:bg-blue-600"
                  style={{ height: `${(documentProcessingData.datasets[0].data[index] / 70) * 100}%` }}
                />
                <span className="text-xs text-slate-500 mt-1 md:mt-2">{label}</span>
              </div>
            ))}
          </div>
          <div className="mt-3 md:mt-4 text-center">
            <span className="text-xs md:text-sm text-slate-500">Total: </span>
            <span className="text-xs md:text-sm font-medium text-slate-900">
              {documentProcessingData.datasets[0].data.reduce((a, b) => a + b, 0)} documents
            </span>
          </div>
        </div>

        {/* AI Usage Chart */}
        <div className="bg-white rounded-lg border border-slate-200 p-4 md:p-6">
          <h2 className="text-base md:text-lg font-semibold text-slate-900 mb-3 md:mb-4">AI Query Usage</h2>
          <div className="h-48 md:h-64 flex items-end justify-between gap-1 md:gap-2">
            {aiUsageData.labels.map((label, index) => (
              <div key={label} className="flex-1 flex flex-col items-center">
                <div
                  className="w-full bg-green-500 rounded-t transition-all hover:bg-green-600"
                  style={{ height: `${(aiUsageData.datasets[0].data[index] / 550) * 100}%` }}
                />
                <span className="text-xs text-slate-500 mt-1 md:mt-2">{label}</span>
              </div>
            ))}
          </div>
          <div className="mt-3 md:mt-4 text-center">
            <span className="text-xs md:text-sm text-slate-500">Total: </span>
            <span className="text-xs md:text-sm font-medium text-slate-900">
              {aiUsageData.datasets[0].data.reduce((a, b) => a + b, 0).toLocaleString()} queries
            </span>
          </div>
        </div>
      </div>

      {/* Compliance Trend Chart */}
      <div className="bg-white rounded-lg border border-slate-200 p-4 md:p-6">
        <h2 className="text-base md:text-lg font-semibold text-slate-900 mb-3 md:mb-4">Compliance Trend</h2>
        <div className="h-48 md:h-64 flex items-end justify-between gap-2 md:gap-4 overflow-x-auto">
          {complianceTrendData.labels.map((label, index) => (
            <div key={label} className="flex-1 flex flex-col items-center min-w-[40px] md:min-w-auto">
              <div
                className="w-full bg-purple-500 rounded-t transition-all hover:bg-purple-600"
                style={{ height: `${(complianceTrendData.datasets[0].data[index] / 100) * 100}%` }}
              />
              <span className="text-xs text-slate-500 mt-1 md:mt-2">{label}</span>
              <span className="text-xs font-medium text-slate-900 mt-0.5 md:mt-1">
                {complianceTrendData.datasets[0].data[index]}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
        {/* Top Issues */}
        <div className="bg-white rounded-lg border border-slate-200 p-4 md:p-6">
          <div className="flex items-center justify-between mb-3 md:mb-4">
            <h2 className="text-base md:text-lg font-semibold text-slate-900">Top Issues</h2>
            <AlertTriangle className="h-4 w-4 md:h-5 md:w-5 text-orange-500" />
          </div>
          <div className="space-y-2 md:space-y-3">
            {topIssues.map((issue) => (
              <div key={issue.id} className="flex items-center justify-between p-2 md:p-3 bg-slate-50 rounded-lg">
                <div className="flex-1 min-w-0">
                  <p className="text-xs md:text-sm font-medium text-slate-900 truncate">{issue.issue}</p>
                  <p className="text-xs text-slate-500">{issue.count} occurrences</p>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium capitalize border ${getSeverityColor(issue.severity)}`}>
                  {issue.severity}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg border border-slate-200 p-4 md:p-6">
          <div className="flex items-center justify-between mb-3 md:mb-4">
            <h2 className="text-base md:text-lg font-semibold text-slate-900">Recent Activity</h2>
            <BarChart3 className="h-4 w-4 md:h-5 md:w-5 text-blue-500" />
          </div>
          <div className="space-y-2 md:space-y-3">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-start gap-2 md:gap-3">
                <div className="w-1.5 h-1.5 md:w-2 md:h-2 mt-1.5 md:mt-2 rounded-full bg-blue-500" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs md:text-sm text-slate-700">
                    <span className="font-medium">{activity.action}</span>: <span className="truncate">{activity.item}</span>
                  </p>
                  <p className="text-xs text-slate-500">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Analytics;
