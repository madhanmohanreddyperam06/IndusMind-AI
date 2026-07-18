import { CheckCircle, AlertCircle, XCircle } from 'lucide-react';
import type { ConfidenceScores } from '../../types/rag';

interface ConfidenceBadgeProps {
  confidence: ConfidenceScores;
  showDetails?: boolean;
}

export function ConfidenceBadge({ confidence, showDetails = false }: ConfidenceBadgeProps) {
  const getOverallLevel = () => {
    if (confidence.overall >= 0.8) return { level: 'high', color: 'bg-green-500', icon: CheckCircle };
    if (confidence.overall >= 0.5) return { level: 'medium', color: 'bg-yellow-500', icon: AlertCircle };
    return { level: 'low', color: 'bg-red-500', icon: XCircle };
  };

  const { level, color, icon: Icon } = getOverallLevel();

  if (!showDetails) {
    return (
      <div className="flex items-center gap-2">
        <Icon className={`h-4 w-4 ${color.replace('bg-', 'text-')}`} />
        <span className="text-sm font-medium capitalize">{level} confidence</span>
        <span className="text-sm text-slate-500">({Math.round(confidence.overall * 100)}%)</span>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Icon className={`h-4 w-4 ${color.replace('bg-', 'text-')}`} />
        <span className="text-sm font-semibold capitalize">{level} confidence</span>
        <span className="text-sm text-slate-500">({Math.round(confidence.overall * 100)}%)</span>
      </div>
      
      <div className="space-y-2 pl-6">
        <ConfidenceBar label="Retrieval" value={confidence.retrieval} />
        <ConfidenceBar label="Evidence" value={confidence.evidence} />
        <ConfidenceBar label="Reasoning" value={confidence.reasoning} />
      </div>
    </div>
  );
}

interface ConfidenceBarProps {
  label: string;
  value: number;
}

function ConfidenceBar({ label, value }: ConfidenceBarProps) {
  const getColor = () => {
    if (value >= 0.8) return 'bg-green-500';
    if (value >= 0.5) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-slate-600">{label}</span>
        <span className="text-slate-500">{Math.round(value * 100)}%</span>
      </div>
      <div className="h-1.5 bg-slate-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${getColor()} rounded-full transition-all`}
          style={{ width: `${value * 100}%` }}
        />
      </div>
    </div>
  );
}
