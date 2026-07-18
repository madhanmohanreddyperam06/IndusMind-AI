import { GraphExplorer } from '../components/graph/GraphExplorer';

function KnowledgeGraph() {
  return (
    <div className="h-full flex flex-col">
      <div className="mb-3 md:mb-4">
        <h1 className="text-xl md:text-2xl font-bold text-slate-900">Knowledge Graph</h1>
        <p className="text-xs md:text-sm text-slate-500">Interactive knowledge graph visualization</p>
      </div>
      <div className="flex-1 bg-white rounded-lg border border-slate-200 overflow-hidden">
        <GraphExplorer />
      </div>
    </div>
  )
}

export default KnowledgeGraph
