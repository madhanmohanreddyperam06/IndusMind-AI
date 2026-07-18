import { useState } from 'react';
import { ChevronDown, Sparkles, Network, FileText, MessageSquare } from 'lucide-react';
import { ConfidenceBadge } from '../confidence/ConfidenceBadge';
import { CitationPanel } from '../citations/CitationPanel';
import type { GenerationResponse } from '../../types';

interface AIResponseCardProps {
  response: GenerationResponse;
}

export function AIResponseCard({ response }: AIResponseCardProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['answer']));

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      if (next.has(section)) {
        next.delete(section);
      } else {
        next.add(section);
      }
      return next;
    });
  };

  const Section = ({
    id,
    title,
    icon: Icon,
    children,
  }: {
    id: string;
    title: string;
    icon: any;
    children: React.ReactNode;
  }) => {
    const isExpanded = expandedSections.has(id);
    return (
      <div className="border border-slate-200 rounded-lg overflow-hidden">
        <button
          onClick={() => toggleSection(id)}
          className="w-full flex items-center justify-between px-4 py-3 bg-slate-50 hover:bg-slate-100 transition-colors"
        >
          <div className="flex items-center gap-2">
            <Icon className="h-4 w-4 text-slate-600" />
            <span className="text-sm font-medium text-slate-900">{title}</span>
          </div>
          <ChevronDown
            className={`h-4 w-4 text-slate-500 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          />
        </button>
        {isExpanded && <div className="p-4">{children}</div>}
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {/* Main Answer */}
      <Section
        id="answer"
        title="Answer"
        icon={MessageSquare}
      >
        <div className="prose prose-slate max-w-none">
          <p className="text-slate-700 whitespace-pre-wrap">{response.answer}</p>
        </div>
      </Section>

      {/* Summary */}
      {response.summary && (
        <Section id="summary" title="Summary" icon={FileText}>
          <p className="text-sm text-slate-600">{response.summary}</p>
        </Section>
      )}

      {/* Confidence */}
      <Section id="confidence" title="Confidence" icon={Sparkles}>
        <ConfidenceBadge confidence={response.confidence} showDetails />
      </Section>

      {/* Citations */}
      {response.citations.length > 0 && (
        <Section id="citations" title="Citations" icon={FileText}>
          <CitationPanel citations={response.citations} />
        </Section>
      )}

      {/* Related Entities */}
      {response.related_entities.length > 0 && (
        <Section id="entities" title="Related Entities" icon={Network}>
          <div className="flex flex-wrap gap-2">
            {response.related_entities.map((entity, index) => (
              <span
                key={`${entity.name}-${index}`}
                className="inline-flex items-center gap-1 px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm"
              >
                <span className="font-medium">{entity.name}</span>
                <span className="text-blue-500">•</span>
                <span className="text-blue-500">{entity.type}</span>
              </span>
            ))}
          </div>
        </Section>
      )}

      {/* Related Relationships */}
      {response.related_relationships.length > 0 && (
        <Section id="relationships" title="Related Relationships" icon={Network}>
          <div className="space-y-2">
            {response.related_relationships.map((rel, index) => (
              <div
                key={`${rel.source}-${rel.target}-${index}`}
                className="flex items-center gap-2 text-sm text-slate-600"
              >
                <span className="font-medium text-slate-900">{rel.source}</span>
                <span className="text-blue-600">{rel.type}</span>
                <span className="font-medium text-slate-900">{rel.target}</span>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Follow-up Questions */}
      {response.follow_up_questions.length > 0 && (
        <Section id="followup" title="Suggested Questions" icon={MessageSquare}>
          <div className="space-y-2">
            {response.follow_up_questions.map((question, index) => (
              <button
                key={index}
                className="w-full text-left px-4 py-2 bg-slate-50 hover:bg-slate-100 rounded-lg text-sm text-slate-700 transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </Section>
      )}

      {/* Statistics */}
      <Section id="statistics" title="Generation Statistics" icon={FileText}>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-slate-500">Processing Time:</span>
            <span className="ml-2 font-medium text-slate-900">
              {response.statistics.processing_time_ms}ms
            </span>
          </div>
          <div>
            <span className="text-slate-500">Total Tokens:</span>
            <span className="ml-2 font-medium text-slate-900">
              {response.statistics.total_tokens}
            </span>
          </div>
          <div>
            <span className="text-slate-500">Context Size:</span>
            <span className="ml-2 font-medium text-slate-900">
              {response.statistics.context_size}
            </span>
          </div>
          <div>
            <span className="text-slate-500">Provider:</span>
            <span className="ml-2 font-medium text-slate-900">
              {response.statistics.provider}
            </span>
          </div>
        </div>
      </Section>
    </div>
  );
}
