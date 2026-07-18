import { FileText, ExternalLink } from 'lucide-react';
import type { Citation } from '../../types/rag';

interface CitationPanelProps {
  citations: Citation[];
}

export function CitationPanel({ citations }: CitationPanelProps) {
  if (citations.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
      <h3 className="text-sm font-semibold text-slate-900 mb-3 flex items-center gap-2">
        <FileText className="h-4 w-4" />
        Citations ({citations.length})
      </h3>
      <div className="space-y-3">
        {citations.map((citation, index) => (
          <div
            key={`${citation.document_id}-${citation.chunk_id}-${index}`}
            className="bg-white p-3 rounded border border-slate-200 hover:border-blue-300 transition-colors"
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                    [{citation.document_id}:{citation.chunk_id}]
                  </span>
                  {citation.page_number && (
                    <span className="text-xs text-slate-500">Page {citation.page_number}</span>
                  )}
                  {citation.section && (
                    <span className="text-xs text-slate-500">• {citation.section}</span>
                  )}
                </div>
                <p className="text-sm text-slate-700 line-clamp-2">{citation.text_preview}</p>
                <div className="mt-2 flex items-center gap-2">
                  <div className="flex-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-600 rounded-full"
                      style={{ width: `${citation.confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-slate-500">
                    {Math.round(citation.confidence * 100)}% confidence
                  </span>
                </div>
              </div>
              <button
                className="p-1.5 rounded hover:bg-slate-100 transition-colors"
                aria-label="View source document"
              >
                <ExternalLink className="h-4 w-4 text-slate-500" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
