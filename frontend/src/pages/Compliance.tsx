import { useState, useEffect } from 'react';
import { ShieldCheck, AlertTriangle, CheckCircle, Clock, FileText, Search } from 'lucide-react';

interface ComplianceRequirement {
  id: string;
  requirement_id: string;
  title: string;
  category: 'safety' | 'environmental' | 'quality' | 'operational';
  status: 'compliant' | 'non_compliant' | 'pending_review' | 'expiring_soon';
  due_date: string;
  last_audit: string;
  next_audit: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

interface ComplianceDocument {
  id: string;
  document_name: string;
  document_type: string;
  expiry_date: string;
  status: 'valid' | 'expiring' | 'expired';
  category: string;
}

function Compliance() {
  const [requirements, setRequirements] = useState<ComplianceRequirement[]>([]);
  const [documents, setDocuments] = useState<ComplianceDocument[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  useEffect(() => {
    loadComplianceData();
  }, []);

  const loadComplianceData = async () => {
    setLoading(true);
    try {
      // In production, this would call actual backend endpoints
      // For now, using mock data
      setRequirements([
        {
          id: '1',
          requirement_id: 'ISO-9001-001',
          title: 'Quality Management System',
          category: 'quality',
          status: 'compliant',
          due_date: '2026-12-31',
          last_audit: '2026-01-15',
          next_audit: '2026-12-15',
          description: 'ISO 9001 Quality Management System certification',
          severity: 'high',
        },
        {
          id: '2',
          requirement_id: 'OSHA-1910-001',
          title: 'Workplace Safety Standards',
          category: 'safety',
          status: 'non_compliant',
          due_date: '2026-07-15',
          last_audit: '2026-06-01',
          next_audit: '2026-07-15',
          description: 'OSHA 1910 workplace safety compliance',
          severity: 'critical',
        },
        {
          id: '3',
          requirement_id: 'EPA-40CFR-001',
          title: 'Environmental Emissions',
          category: 'environmental',
          status: 'expiring_soon',
          due_date: '2026-08-01',
          last_audit: '2026-01-20',
          next_audit: '2026-08-01',
          description: 'EPA environmental emissions monitoring',
          severity: 'high',
        },
        {
          id: '4',
          requirement_id: 'API-510-001',
          title: 'Pressure Vessel Inspection',
          category: 'operational',
          status: 'pending_review',
          due_date: '2026-09-01',
          last_audit: '2026-03-10',
          next_audit: '2026-09-01',
          description: 'API 510 pressure vessel inspection certification',
          severity: 'medium',
        },
      ]);

      setDocuments([
        {
          id: '1',
          document_name: 'ISO 9001 Certificate',
          document_type: 'Certificate',
          expiry_date: '2026-12-31',
          status: 'valid',
          category: 'Quality',
        },
        {
          id: '2',
          document_name: 'Safety Audit Report Q2 2026',
          document_type: 'Audit Report',
          expiry_date: '2026-09-30',
          status: 'valid',
          category: 'Safety',
        },
        {
          id: '3',
          document_name: 'Environmental Permit',
          document_type: 'Permit',
          expiry_date: '2026-08-01',
          status: 'expiring',
          category: 'Environmental',
        },
        {
          id: '4',
          document_name: 'Pressure Vessel Inspection',
          document_type: 'Inspection Report',
          expiry_date: '2026-03-15',
          status: 'expired',
          category: 'Operational',
        },
      ]);
    } catch (error) {
      console.error('Failed to load compliance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'compliant':
      case 'valid':
        return 'bg-green-100 text-green-900 border-green-200';
      case 'non_compliant':
      case 'expired':
        return 'bg-red-100 text-red-900 border-red-200';
      case 'pending_review':
        return 'bg-yellow-100 text-yellow-900 border-yellow-200';
      case 'expiring_soon':
      case 'expiring':
        return 'bg-orange-100 text-orange-900 border-orange-200';
      default:
        return 'bg-gray-100 text-gray-900 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'compliant':
      case 'valid':
        return CheckCircle;
      case 'non_compliant':
      case 'expired':
        return AlertTriangle;
      case 'pending_review':
        return Clock;
      case 'expiring_soon':
      case 'expiring':
        return AlertTriangle;
      default:
        return ShieldCheck;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
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

  const filteredRequirements = requirements.filter((req) => {
    const matchesSearch =
      req.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      req.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || req.status === statusFilter;
    const matchesCategory = categoryFilter === 'all' || req.category === categoryFilter;
    return matchesSearch && matchesStatus && matchesCategory;
  });

  const nonCompliantCount = requirements.filter((r) => r.status === 'non_compliant').length;
  const expiringSoonCount = requirements.filter((r) => r.status === 'expiring_soon').length;
  const pendingReviewCount = requirements.filter((r) => r.status === 'pending_review').length;
  const expiredDocsCount = documents.filter((d) => d.status === 'expired').length;

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-3">
        <div>
          <h1 className="text-xl md:text-2xl font-bold text-slate-900">Compliance Intelligence</h1>
          <p className="text-xs md:text-sm text-slate-500">Compliance monitoring, requirements, and documentation</p>
        </div>
        <button className="px-4 md:px-6 py-2 md:py-2.5 bg-blue-600 text-white rounded-lg text-xs md:text-sm hover:bg-blue-700 transition-colors self-start md:self-auto">
          Run Audit
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
        <div className="bg-white rounded-lg border border-slate-200 p-3 md:p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs md:text-sm text-slate-500">Non-Compliant</p>
              <p className="text-xl md:text-2xl font-bold text-red-600">{nonCompliantCount}</p>
            </div>
            <AlertTriangle className="h-6 w-6 md:h-8 md:w-8 text-red-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg border border-slate-200 p-3 md:p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs md:text-sm text-slate-500">Expiring Soon</p>
              <p className="text-xl md:text-2xl font-bold text-orange-600">{expiringSoonCount}</p>
            </div>
            <Clock className="h-6 w-6 md:h-8 md:w-8 text-orange-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg border border-slate-200 p-3 md:p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs md:text-sm text-slate-500">Pending Review</p>
              <p className="text-xl md:text-2xl font-bold text-yellow-600">{pendingReviewCount}</p>
            </div>
            <ShieldCheck className="h-6 w-6 md:h-8 md:w-8 text-yellow-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg border border-slate-200 p-3 md:p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs md:text-sm text-slate-500">Expired Documents</p>
              <p className="text-xl md:text-2xl font-bold text-red-600">{expiredDocsCount}</p>
            </div>
            <FileText className="h-6 w-6 md:h-8 md:w-8 text-red-500" />
          </div>
        </div>
      </div>

      {/* Compliance Requirements */}
      <div className="bg-white rounded-lg border border-slate-200">
        <div className="p-3 md:p-4 border-b border-slate-200">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
            <h2 className="text-base md:text-lg font-semibold text-slate-900">Compliance Requirements</h2>
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
                <option value="all">All Status</option>
                <option value="compliant">Compliant</option>
                <option value="non_compliant">Non-Compliant</option>
                <option value="pending_review">Pending Review</option>
                <option value="expiring_soon">Expiring Soon</option>
              </select>
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="px-3 md:px-4 py-2 border border-slate-300 rounded-lg text-xs md:text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Categories</option>
                <option value="safety">Safety</option>
                <option value="environmental">Environmental</option>
                <option value="quality">Quality</option>
                <option value="operational">Operational</option>
              </select>
            </div>
          </div>
        </div>

        <div className="divide-y divide-slate-200">
          {loading ? (
            <div className="p-8 text-center text-slate-500">Loading...</div>
          ) : filteredRequirements.length === 0 ? (
            <div className="p-8 text-center text-slate-500">No compliance requirements found</div>
          ) : (
            filteredRequirements.map((req) => {
              const StatusIcon = getStatusIcon(req.status);
              return (
                <div key={req.id} className="p-3 md:p-4 hover:bg-slate-50 transition-colors">
                  <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 md:gap-3 mb-2">
                        <div className={`p-1.5 md:p-2 rounded-lg ${getStatusColor(req.status)}`}>
                          <StatusIcon className="h-4 w-4 md:h-5 md:w-5" />
                        </div>
                        <div>
                          <h3 className="text-xs md:text-sm font-medium text-slate-900">{req.title}</h3>
                          <p className="text-xs text-slate-500 hidden md:block">{req.requirement_id}</p>
                        </div>
                      </div>
                      <p className="text-xs md:text-sm text-slate-700 mb-2 hidden md:block">{req.description}</p>
                      <div className="flex flex-wrap items-center gap-2 md:gap-4 text-xs md:text-sm text-slate-500">
                        <span className="capitalize">{req.category}</span>
                        <span className="hidden md:inline">•</span>
                        <span>Due: {new Date(req.due_date).toLocaleDateString()}</span>
                        <span className="hidden md:inline">•</span>
                        <span className="hidden md:inline">Last Audit: {new Date(req.last_audit).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <div className="flex md:flex-col items-center md:items-end gap-2 md:gap-2">
                      <div className={`px-2 md:px-3 py-1 rounded-full text-xs font-medium capitalize ${getStatusColor(req.status)}`}>
                        {req.status.replace('_', ' ')
                          .replace('non_compliant', 'Non-Compliant')
                          .replace('expiring_soon', 'Expiring Soon')
                          .replace('pending_review', 'Pending Review')}
                      </div>
                      <div className={`w-2 h-2 md:w-2 md:h-2 rounded-full ${getSeverityColor(req.severity)}`} />
                      <span className="text-xs text-slate-500 capitalize hidden md:inline">{req.severity}</span>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Compliance Documents */}
      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-900">Compliance Documents</h2>
          <button className="px-3 py-2 text-sm bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors">
            View All
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {documents.map((doc) => (
            <div key={doc.id} className="border border-slate-200 rounded-lg p-4 hover:bg-slate-50 transition-colors">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${getStatusColor(doc.status)}`}>
                      <FileText className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="font-medium text-slate-900">{doc.document_name}</h3>
                      <p className="text-sm text-slate-500">{doc.document_type}</p>
                    </div>
                  </div>
                  <div className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${getStatusColor(doc.status)}`}>
                    {doc.status.replace('_', ' ')}
                  </div>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-500">{doc.category}</span>
                  <span className="text-slate-500">
                    Expires: {new Date(doc.expiry_date).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}

export default Compliance;
