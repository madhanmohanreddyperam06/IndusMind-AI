import { ChatInterface } from '../components/chat/ChatInterface';

function AICopilot() {
  return (
    <div className="h-full flex flex-col">
      <div className="mb-3 md:mb-4">
        <h1 className="text-xl md:text-2xl font-bold text-slate-900">AI Copilot</h1>
        <p className="text-xs md:text-sm text-slate-500">AI-powered engineering assistant</p>
      </div>
      <div className="flex-1 bg-white rounded-lg border border-slate-200 overflow-hidden">
        <ChatInterface />
      </div>
    </div>
  )
}

export default AICopilot
