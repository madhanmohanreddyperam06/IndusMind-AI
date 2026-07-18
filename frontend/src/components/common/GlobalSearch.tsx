import { useState, useEffect, useRef } from 'react';
import { Search, X, FileText, Network, MessageSquare, Wrench, ShieldCheck, ChevronRight } from 'lucide-react';

interface SearchResult {
  id: string;
  type: 'document' | 'entity' | 'conversation' | 'maintenance' | 'compliance';
  title: string;
  description?: string;
  metadata?: Record<string, any>;
  link: string;
}

interface GlobalSearchProps {
  isOpen: boolean;
  onClose: () => void;
}

export function GlobalSearch({ isOpen, onClose }: GlobalSearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) {
      setQuery('');
      setResults([]);
      setSelectedIndex(0);
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === 'Escape') {
        onClose();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => Math.min(prev + 1, results.length - 1));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => Math.max(prev - 1, 0));
      } else if (e.key === 'Enter' && results.length > 0) {
        window.location.href = results[selectedIndex].link;
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, results, selectedIndex, onClose]);

  const handleSearch = async (searchQuery: string) => {
    setQuery(searchQuery);
    setSelectedIndex(0);

    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }

    setLoading(true);
    
    // Simulate API call with mock data
    await new Promise((resolve) => setTimeout(resolve, 300));

    const mockResults: SearchResult[] = [
      {
        id: '1',
        type: 'document',
        title: 'SOP-2026-042: Pump Maintenance Procedure',
        description: 'Standard operating procedure for centrifugal pump maintenance',
        metadata: { category: 'SOP', date: '2026-04-15' },
        link: '/documents/1',
      },
      {
        id: '2',
        type: 'document',
        title: 'Safety Inspection Report Q2 2026',
        description: 'Quarterly safety inspection findings and recommendations',
        metadata: { category: 'Inspection Report', date: '2026-06-30' },
        link: '/documents/2',
      },
      {
        id: '3',
        type: 'entity',
        title: 'Centrifugal Pump P101',
        description: 'Equipment entity in knowledge graph',
        metadata: { type: 'Equipment', confidence: 0.95 },
        link: '/graph?node=PUMP-101',
      },
      {
        id: '4',
        type: 'entity',
        title: 'Compressor C204',
        description: 'Equipment entity with maintenance records',
        metadata: { type: 'Equipment', confidence: 0.92 },
        link: '/graph?node=COMP-204',
      },
      {
        id: '5',
        type: 'conversation',
        title: 'Pump failure analysis',
        description: 'AI conversation about pump failure causes',
        metadata: { date: '2026-07-15', messages: 12 },
        link: '/copilot?conversation=5',
      },
      {
        id: '6',
        type: 'maintenance',
        title: 'Compressor C204 Maintenance',
        description: 'Scheduled maintenance for compressor unit',
        metadata: { status: 'in_progress', priority: 'high' },
        link: '/maintenance',
      },
      {
        id: '7',
        type: 'compliance',
        title: 'ISO 9001 Certification',
        description: 'Quality management system certification',
        metadata: { status: 'compliant', expiry: '2026-12-31' },
        link: '/compliance',
      },
    ];

    const filtered = mockResults.filter(
      (result) =>
        result.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        result.description?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    setResults(filtered);
    setLoading(false);
  };

  const getResultIcon = (type: string) => {
    switch (type) {
      case 'document':
        return FileText;
      case 'entity':
        return Network;
      case 'conversation':
        return MessageSquare;
      case 'maintenance':
        return Wrench;
      case 'compliance':
        return ShieldCheck;
      default:
        return Search;
    }
  };

  const getResultColor = (type: string) => {
    switch (type) {
      case 'document':
        return 'bg-blue-100 text-blue-600';
      case 'entity':
        return 'bg-purple-100 text-purple-600';
      case 'conversation':
        return 'bg-green-100 text-green-600';
      case 'maintenance':
        return 'bg-orange-100 text-orange-600';
      case 'compliance':
        return 'bg-emerald-100 text-emerald-600';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const getResultTypeLabel = (type: string) => {
    switch (type) {
      case 'document':
        return 'Document';
      case 'entity':
        return 'Knowledge Graph';
      case 'conversation':
        return 'Conversation';
      case 'maintenance':
        return 'Maintenance';
      case 'compliance':
        return 'Compliance';
      default:
        return 'Result';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 px-4">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative w-full max-w-2xl bg-white rounded-xl shadow-2xl overflow-hidden">
        {/* Search Input */}
        <div className="flex items-center border-b border-slate-200 p-4">
          <Search className="h-5 w-5 text-slate-400 mr-3" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="Search documents, knowledge graph, conversations..."
            className="flex-1 text-lg outline-none placeholder-slate-400"
          />
          {query && (
            <button
              onClick={() => handleSearch('')}
              className="ml-3 p-1 hover:bg-slate-100 rounded-full transition-colors"
            >
              <X className="h-5 w-5 text-slate-400" />
            </button>
          )}
          <div className="ml-4 flex items-center gap-2 text-xs text-slate-400">
            <kbd className="px-2 py-1 bg-slate-100 rounded">ESC</kbd>
            <span>to close</span>
          </div>
        </div>

        {/* Results */}
        <div className="max-h-96 overflow-y-auto">
          {loading ? (
            <div className="p-8 text-center text-slate-500">Searching...</div>
          ) : query && results.length === 0 ? (
            <div className="p-8 text-center text-slate-500">No results found for "{query}"</div>
          ) : !query ? (
            <div className="p-6">
              <p className="text-sm text-slate-500 mb-4">Quick Actions</p>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => {
                    window.location.href = '/documents';
                    onClose();
                  }}
                  className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-100 transition-colors text-left"
                >
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <FileText className="h-4 w-4 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-900">Upload Document</p>
                    <p className="text-xs text-slate-500">Add new documents</p>
                  </div>
                </button>
                <button
                  onClick={() => {
                    window.location.href = '/copilot';
                    onClose();
                  }}
                  className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-100 transition-colors text-left"
                >
                  <div className="p-2 bg-green-100 rounded-lg">
                    <MessageSquare className="h-4 w-4 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-900">Ask AI Copilot</p>
                    <p className="text-xs text-slate-500">Get answers</p>
                  </div>
                </button>
                <button
                  onClick={() => {
                    window.location.href = '/graph';
                    onClose();
                  }}
                  className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-100 transition-colors text-left"
                >
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <Network className="h-4 w-4 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-900">Explore Graph</p>
                    <p className="text-xs text-slate-500">View relationships</p>
                  </div>
                </button>
                <button
                  onClick={() => {
                    window.location.href = '/maintenance';
                    onClose();
                  }}
                  className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-100 transition-colors text-left"
                >
                  <div className="p-2 bg-orange-100 rounded-lg">
                    <Wrench className="h-4 w-4 text-orange-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-900">Schedule Maintenance</p>
                    <p className="text-xs text-slate-500">Plan tasks</p>
                  </div>
                </button>
              </div>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {results.map((result, index) => {
                const Icon = getResultIcon(result.type);
                return (
                  <button
                    key={result.id}
                    onClick={() => {
                      window.location.href = result.link;
                      onClose();
                    }}
                    className={`w-full flex items-start gap-4 p-4 hover:bg-slate-50 transition-colors text-left ${
                      index === selectedIndex ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className={`p-2 rounded-lg ${getResultColor(result.type)}`}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-medium text-slate-900 truncate">{result.title}</p>
                        <span className="text-xs text-slate-500 capitalize">
                          {getResultTypeLabel(result.type)}
                        </span>
                      </div>
                      {result.description && (
                        <p className="text-sm text-slate-500 truncate">{result.description}</p>
                      )}
                      {result.metadata && (
                        <div className="flex items-center gap-2 mt-1">
                          {Object.entries(result.metadata).slice(0, 2).map(([key, value]) => (
                            <span key={key} className="text-xs text-slate-400">
                              {key}: {String(value)}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <ChevronRight className="h-4 w-4 text-slate-400 mt-1" />
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-slate-200 p-3 bg-slate-50 flex items-center justify-between text-xs text-slate-500">
          <div className="flex items-center gap-4">
            <span>
              <kbd className="px-1.5 py-0.5 bg-white border border-slate-300 rounded">↑↓</kbd>
              <span className="ml-1">to navigate</span>
            </span>
            <span>
              <kbd className="px-1.5 py-0.5 bg-white border border-slate-300 rounded">Enter</kbd>
              <span className="ml-1">to select</span>
            </span>
          </div>
          <span>{results.length} results</span>
        </div>
      </div>
    </div>
  );
}
