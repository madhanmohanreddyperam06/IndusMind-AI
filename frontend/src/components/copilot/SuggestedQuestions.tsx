import { Lightbulb } from 'lucide-react';

interface SuggestedQuestionsProps {
  questions: string[];
  onSelect: (question: string) => void;
}

export function SuggestedQuestions({ questions, onSelect }: SuggestedQuestionsProps) {
  if (questions.length === 0) {
    return null;
  }

  return (
    <div className="mb-4">
      <div className="flex items-center gap-2 mb-3">
        <Lightbulb className="h-4 w-4 text-yellow-500" />
        <h3 className="text-sm font-medium text-slate-700">Suggested Questions</h3>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        {questions.map((question, index) => (
          <button
            key={index}
            onClick={() => onSelect(question)}
            className="text-left px-4 py-3 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg text-sm text-slate-700 transition-colors"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
}
