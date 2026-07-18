import { useState, useEffect } from 'react';
import { Wrench, Calendar, AlertTriangle, CheckCircle, Clock, Search } from 'lucide-react';

interface MaintenanceRecord {
  id: string;
  equipment_id: string;
  equipment_name: string;
  maintenance_type: 'preventive' | 'corrective' | 'predictive';
  status: 'scheduled' | 'in_progress' | 'completed' | 'overdue';
  scheduled_date: string;
  completed_date?: string;
  technician?: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
}

interface EquipmentStatus {
  equipment_id: string;
  equipment_name: string;
  status: 'operational' | 'maintenance' | 'offline' | 'degraded';
  last_maintenance: string;
  next_maintenance: string;
  failure_risk: number;
}

function Maintenance() {
  const [records, setRecords] = useState<MaintenanceRecord[]>([]);
  const [equipmentStatus, setEquipmentStatus] = useState<EquipmentStatus[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');

  useEffect(() => {
    loadMaintenanceData();
  }, []);

  const loadMaintenanceData = async () => {
    try {
      // In production, this would call actual backend endpoints
      // For now, using mock data
      setRecords([
        {
          id: '1',
          equipment_id: 'PUMP-101',
          equipment_name: 'Centrifugal Pump P101',
          maintenance_type: 'preventive',
          status: 'scheduled',
          scheduled_date: '2026-07-20',
          description: 'Quarterly inspection and lubrication',
          priority: 'medium',
        },
        {
          id: '2',
          equipment_id: 'COMP-204',
          equipment_name: 'Compressor C204',
          maintenance_type: 'corrective',
          status: 'in_progress',
          scheduled_date: '2026-07-15',
          technician: 'John Smith',
          description: 'Replace worn seals and bearings',
          priority: 'high',
        },
        {
          id: '3',
          equipment_id: 'BOILER-301',
          equipment_name: 'Industrial Boiler B301',
          maintenance_type: 'preventive',
          status: 'overdue',
          scheduled_date: '2026-07-10',
          description: 'Annual safety inspection and certification',
          priority: 'critical',
        },
      ]);

      setEquipmentStatus([
        {
          equipment_id: 'PUMP-101',
          equipment_name: 'Centrifugal Pump P101',
          status: 'operational',
          last_maintenance: '2026-04-15',
          next_maintenance: '2026-07-20',
          failure_risk: 0.15,
        },
        {
          equipment_id: 'COMP-204',
          equipment_name: 'Compressor C204',
          status: 'maintenance',
          last_maintenance: '2026-06-01',
          next_maintenance: '2026-07-15',
          failure_risk: 0.45,
        },
        {
          equipment_id: 'BOILER-301',
          equipment_name: 'Industrial Boiler B301',
          status: 'degraded',
          last_maintenance: '2026-01-10',
          next_maintenance: '2026-07-10',
          failure_risk: 0.85,
        },
      ]);
    } catch (error) {
      console.error('Failed to load maintenance data:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-900 border-green-200';
      case 'in_progress':
        return 'bg-blue-100 text-blue-900 border-blue-200';
      case 'scheduled':
        return 'bg-yellow-100 text-yellow-900 border-yellow-200';
      case 'overdue':
        return 'bg-red-100 text-red-900 border-red-200';
      default:
        return 'bg-gray-100 text-gray-900 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return CheckCircle;
      case 'in_progress':
        return Clock;
      case 'scheduled':
        return Calendar;
      case 'overdue':
        return AlertTriangle;
      default:
        return Wrench;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-600';
      case 'high':
        return 'bg-orange-500';
      case 'medium':
        return 'bg-yellow-500';
      case 'low':
        return 'bg-green-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getEquipmentStatusColor = (status: string) => {
    switch (status) {
      case 'operational':
        return 'bg-green-500';
      case 'maintenance':
        return 'bg-blue-500';
      case 'degraded':
        return 'bg-yellow-500';
      case 'offline':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const filteredRecords = records.filter((record) => {
    const matchesSearch =
      record.equipment_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      record.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || record.status === statusFilter;
    const matchesType = typeFilter === 'all' || record.maintenance_type === typeFilter;
    return matchesSearch && matchesStatus && matchesType;
  });

  const overdueCount = records.filter((r) => r.status === 'overdue').length;
  const inProgressCount = records.filter((r) => r.status === 'in_progress').length;
  const scheduledCount = records.filter((r) => r.status === 'scheduled').length;
  const highRiskCount = equipmentStatus.filter((e) => e.failure_risk > 0.7).length;

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-3">
        <div>
          <h1 className="text-xl md:text-2xl font-bold text-slate-900">Maintenance Intelligence</h1>
          <p className="text-xs md:text-sm text-slate-500">Maintenance records, schedules, and equipment status</p>
        </div>
        <button className="px-4 md:px-6 py-2 md:py-2.5 bg-blue-600 text-white rounded-lg text-xs md:text-sm hover:bg-blue-700 transition-colors self-start md:self-auto">
          Schedule Maintenance
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
        <div className="bg-white rounded-lg border border-slate-200 p-3 md:p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs md:text-sm text-slate-500">Overdue</p>
              <p className="text-xl md:text-2xl font-bold text-red-600">{overdueCount}</p>
            </div>
            <AlertTriangle className="h-6 w-6 md:h-8 md:w-8 text-red-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg border border-slate-200 p-3 md:p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs md:text-sm text-slate-500">In Progress</p>
              <p className="text-xl md:text-2xl font-bold text-blue-600">{inProgressCount}</p>
            </div>
            <Clock className="h-6 w-6 md:h-8 md:w-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg border border-slate-200 p-3 md:p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs md:text-sm text-slate-500">Scheduled</p>
              <p className="text-xl md:text-2xl font-bold text-yellow-600">{scheduledCount}</p>
            </div>
            <Calendar className="h-6 w-6 md:h-8 md:w-8 text-yellow-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg border border-slate-200 p-3 md:p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs md:text-sm text-slate-500">High Risk Equipment</p>
              <p className="text-xl md:text-2xl font-bold text-orange-600">{highRiskCount}</p>
            </div>
            <Wrench className="h-6 w-6 md:h-8 md:w-8 text-orange-500" />
          </div>
        </div>
      </div>

      {/* Equipment Status */}
      <div className="bg-white rounded-lg border border-slate-200 p-4 md:p-6">
        <h2 className="text-base md:text-lg font-semibold text-slate-900 mb-3 md:mb-4">Equipment Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4">
          {equipmentStatus.map((equipment) => (
            <div key={equipment.equipment_id} className="border border-slate-200 rounded-lg p-3 md:p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-medium text-slate-900">{equipment.equipment_name}</h3>
                <div className={`w-3 h-3 rounded-full ${getEquipmentStatusColor(equipment.status)}`} />
              </div>
              <div className="space-y-2 text-xs md:text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-500">Status:</span>
                  <span className="font-medium capitalize">{equipment.status.replace('_', ' ')}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Last Maintenance:</span>
                  <span className="font-medium">{new Date(equipment.last_maintenance).toLocaleDateString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Next Maintenance:</span>
                  <span className="font-medium">{new Date(equipment.next_maintenance).toLocaleDateString()}</span>
                </div>
                <div className="pt-2">
                  <div className="flex justify-between mb-1">
                    <span className="text-slate-500">Failure Risk:</span>
                    <span className="font-medium">{Math.round(equipment.failure_risk * 100)}%</span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        equipment.failure_risk > 0.7
                          ? 'bg-red-500'
                          : equipment.failure_risk > 0.4
                          ? 'bg-yellow-500'
                          : 'bg-green-500'
                      }`}
                      style={{ width: `${equipment.failure_risk * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Maintenance Records */}
      <div className="bg-white rounded-lg border border-slate-200">
        <div className="p-3 md:p-4 border-b border-slate-200">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
            <h2 className="text-base md:text-lg font-semibold text-slate-900">Maintenance Records</h2>
            <div className="flex items-center gap-2 md:gap-3">
              <div className="relative flex-1 md:flex-none">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search..."
                  className="pl-10 pr-4 py-2 border border-slate-300 rounded-lg text-xs md:text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 w-full"
                />
              </div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 md:px-4 py-2 border border-slate-300 rounded-lg text-xs md:text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Statuses</option>
                <option value="scheduled">Scheduled</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="overdue">Overdue</option>
              </select>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="px-3 md:px-4 py-2 border border-slate-300 rounded-lg text-xs md:text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Types</option>
                <option value="preventive">Preventive</option>
                <option value="corrective">Corrective</option>
                <option value="predictive">Predictive</option>
              </select>
            </div>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-slate-900 uppercase tracking-wider">Equipment</th>
                <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-slate-900 uppercase tracking-wider hidden md:table-cell">Type</th>
                <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-slate-900 uppercase tracking-wider hidden sm:table-cell">Status</th>
                <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-slate-900 uppercase tracking-wider hidden sm:table-cell">Date</th>
                <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-slate-900 uppercase tracking-wider hidden md:table-cell">Priority</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {filteredRecords.map((record) => {
                const StatusIcon = getStatusIcon(record.status);
                return (
                  <tr key={record.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                      <div className="text-xs md:text-sm font-medium text-slate-900">{record.equipment_name}</div>
                      <div className="text-xs text-slate-500 hidden md:block">{record.description}</div>
                    </td>
                    <td className="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap hidden md:table-cell">
                      <span className="text-xs md:text-sm capitalize">{record.maintenance_type.replace('_', ' ')}</span>
                    </td>
                    <td className="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap hidden sm:table-cell">
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(record.status)}`}>
                        <StatusIcon className="h-3 w-3" />
                        {record.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap text-xs md:text-sm text-slate-600 hidden sm:table-cell">
                      {new Date(record.scheduled_date).toLocaleDateString()}
                    </td>
                    <td className="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap hidden md:table-cell">
                      <div className={`w-2 h-2 md:w-3 md:h-3 rounded-full ${getPriorityColor(record.priority)}`} />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Maintenance;
