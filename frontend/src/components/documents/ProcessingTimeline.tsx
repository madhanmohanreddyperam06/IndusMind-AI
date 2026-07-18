import { Clock, CheckCircle, XCircle, Loader2, FileText, Eye, Scan, Database, Network } from 'lucide-react';
import type { ProcessingTimeline as ProcessingTimelineType } from '../../types/documents';

interface ProcessingTimelineProps {
  timeline: ProcessingTimelineType;
}

export function ProcessingTimeline({ timeline }: ProcessingTimelineProps) {
  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'upload':
        return FileText;
      case 'ocr':
        return Scan;
      case 'extraction':
        return Eye;
      case 'graph_sync':
        return Network;
      case 'vector_index':
        return Database;
      default:
        return Clock;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-50';
      case 'failed':
        return 'text-red-600 bg-red-50';
      case 'in_progress':
        return 'text-blue-600 bg-blue-50';
      default:
        return 'text-slate-600 bg-slate-50';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return CheckCircle;
      case 'failed':
        return XCircle;
      case 'in_progress':
        return Loader2;
      default:
        return Clock;
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-slate-900">Processing Timeline</h3>
      <div className="relative">
        {/* Timeline Line */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-slate-200" />
        
        {/* Events */}
        <div className="space-y-4">
          {timeline.events.map((event, index) => {
            const Icon = getEventIcon(event.event_type);
            const StatusIcon = getStatusIcon(event.status);
            const isLast = index === timeline.events.length - 1;
            
            return (
              <div key={index} className="relative flex gap-4">
                {/* Icon */}
                <div className="relative z-10 flex-shrink-0">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${getStatusColor(event.status)}`}>
                    <Icon className="h-4 w-4" />
                  </div>
                  {!isLast && (
                    <div className="absolute left-4 top-8 bottom-0 w-0.5 -translate-x-1/2 bg-slate-200" />
                  )}
                </div>
                
                {/* Content */}
                <div className="flex-1 min-w-0 pb-4">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium text-slate-900 capitalize">
                          {event.event_type.replace('_', ' ')}
                        </p>
                        <StatusIcon className={`h-4 w-4 ${event.status === 'in_progress' ? 'animate-spin' : ''}`} />
                      </div>
                      <p className="text-xs text-slate-500 mt-1">
                        {new Date(event.timestamp).toLocaleString()}
                      </p>
                      {event.duration_ms && (
                        <p className="text-xs text-slate-400">
                          {event.duration_ms}ms
                        </p>
                      )}
                    </div>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium capitalize ${getStatusColor(event.status)}`}>
                      {event.status.replace('_', ' ')}
                    </span>
                  </div>
                  
                  {event.error_message && (
                    <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded">
                      <p className="text-xs text-red-700">{event.error_message}</p>
                    </div>
                  )}
                  
                  {event.metadata && Object.keys(event.metadata).length > 0 && (
                    <div className="mt-2 p-2 bg-slate-50 rounded">
                      <div className="space-y-1">
                        {Object.entries(event.metadata).map(([key, value]) => (
                          <div key={key} className="text-xs">
                            <span className="text-slate-500">{key}:</span>
                            <span className="ml-2 text-slate-700">{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
