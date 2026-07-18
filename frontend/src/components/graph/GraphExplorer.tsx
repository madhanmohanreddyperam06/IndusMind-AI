import { useCallback, useState, useEffect } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
  BackgroundVariant,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Search, Filter } from 'lucide-react';
import { graphService } from '../../services';

const nodeTypes = {
  equipment: { color: '#3b82f6', label: 'Equipment' },
  component: { color: '#10b981', label: 'Component' },
  failure: { color: '#ef4444', label: 'Failure' },
  cause: { color: '#f59e0b', label: 'Cause' },
  maintenance: { color: '#8b5cf6', label: 'Maintenance' },
  inspection: { color: '#06b6d4', label: 'Inspection' },
  standard: { color: '#ec4899', label: 'Standard' },
  regulation: { color: '#6366f1', label: 'Regulation' },
  vendor: { color: '#14b8a6', label: 'Vendor' },
  location: { color: '#f97316', label: 'Location' },
  person: { color: '#84cc16', label: 'Person' },
  department: { color: '#a855f7', label: 'Department' },
  default: { color: '#64748b', label: 'Node' },
};

export function GraphExplorer() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const onConnect = useCallback(
    (params: Edge | Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const loadGraph = async () => {
    setIsLoading(true);
    try {
      // Load mock data for demonstration
      const mockNodes: Node[] = [
        { id: '1', type: 'default', position: { x: 250, y: 0 }, data: { labels: ['Equipment'], properties: { name: 'Pump P101' } } },
        { id: '2', type: 'default', position: { x: 100, y: 100 }, data: { labels: ['Component'], properties: { name: 'Motor M1' } } },
        { id: '3', type: 'default', position: { x: 400, y: 100 }, data: { labels: ['Component'], properties: { name: 'Impeller I1' } } },
        { id: '4', type: 'default', position: { x: 250, y: 200 }, data: { labels: ['Failure'], properties: { name: 'Seal Failure' } } },
        { id: '5', type: 'default', position: { x: 50, y: 200 }, data: { labels: ['Maintenance'], properties: { name: 'Scheduled Maintenance' } } },
        { id: '6', type: 'default', position: { x: 450, y: 200 }, data: { labels: ['Inspection'], properties: { name: 'Annual Inspection' } } },
      ];

      const mockEdges: Edge[] = [
        { id: 'e1-2', source: '1', target: '2', animated: true },
        { id: 'e1-3', source: '1', target: '3', animated: true },
        { id: 'e1-4', source: '1', target: '4' },
        { id: 'e2-4', source: '2', target: '4' },
        { id: 'e2-5', source: '2', target: '5' },
        { id: 'e3-6', source: '3', target: '6' },
      ];

      setNodes(mockNodes);
      setEdges(mockEdges);
    } catch (error) {
      console.error('Failed to load graph:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadGraph();
  }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      // Search for nodes matching the query
      // This would call graphService.getNode or a search endpoint
      console.log('Searching for:', searchQuery);
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  const handleNodeClick = (_: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  };

  const expandNeighbors = async (nodeId: string) => {
    try {
      await graphService.getNeighbors(nodeId);
      // Add neighbors to the graph
      console.log('Expanding neighbors for:', nodeId);
    } catch (error) {
      console.error('Failed to expand neighbors:', error);
    }
  };

  const toggleTypeFilter = (type: string) => {
    setSelectedTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  const getNodeColor = (node: Node) => {
    const labels = node.data?.labels || [];
    for (const label of labels) {
      const type = label.toLowerCase();
      if (nodeTypes[type as keyof typeof nodeTypes]) {
        return nodeTypes[type as keyof typeof nodeTypes].color;
      }
    }
    return nodeTypes.default.color;
  };

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 bg-white">
        <div className="flex items-center gap-3 flex-1">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search nodes..."
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={handleSearch}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Search
          </button>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSelectedTypes([])}
            className="flex items-center gap-2 px-3 py-2 text-sm bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
          >
            <Filter className="h-4 w-4" />
            Clear Filters
          </button>
          <button
            onClick={loadGraph}
            className="px-3 py-2 text-sm bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Type Filters */}
      <div className="px-4 py-2 border-b border-slate-200 bg-white flex items-center gap-2 overflow-x-auto">
        <span className="text-sm font-medium text-slate-600 whitespace-nowrap">Filter by type:</span>
        {Object.entries(nodeTypes).map(([type, config]) => (
          <button
            key={type}
            onClick={() => toggleTypeFilter(type)}
            className={`px-3 py-1 rounded-full text-xs whitespace-nowrap transition-colors ${
              selectedTypes.includes(type)
                ? 'bg-blue-600 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
            style={
              !selectedTypes.includes(type) ? { backgroundColor: `${config.color}20`, color: config.color } : {}
            }
          >
            {config.label}
          </button>
        ))}
      </div>

      {/* Graph Area */}
      <div className="flex-1 relative">
        {isLoading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-50">
            <div className="text-slate-500">Loading graph...</div>
          </div>
        ) : (
          <ReactFlow
            nodes={nodes.map((node) => ({
              ...node,
              style: {
                backgroundColor: getNodeColor(node),
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                padding: '8px',
                minWidth: '120px',
              },
            }))}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={handleNodeClick}
            fitView
          >
            <Background variant={BackgroundVariant.Dots} gap={20} size={1} />
            <Controls />
            <MiniMap />
          </ReactFlow>
        )}

        {/* Node Details Panel */}
        {selectedNode && (
          <div className="absolute top-4 right-4 w-80 bg-white rounded-lg shadow-lg border border-slate-200 p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-slate-900">Node Details</h3>
              <button
                onClick={() => setSelectedNode(null)}
                className="p-1 rounded hover:bg-slate-100"
              >
                ×
              </button>
            </div>
            <div className="space-y-3">
              <div>
                <label className="text-xs text-slate-500">ID</label>
                <p className="text-sm text-slate-900 font-mono">{selectedNode.id}</p>
              </div>
              <div>
                <label className="text-xs text-slate-500">Labels</label>
                <div className="flex flex-wrap gap-1 mt-1">
                  {(selectedNode.data?.labels || []).map((label: string, index: number) => (
                    <span
                      key={index}
                      className="px-2 py-0.5 bg-slate-100 text-slate-700 rounded text-xs"
                    >
                      {label}
                    </span>
                  ))}
                </div>
              </div>
              {selectedNode.data?.properties && (
                <div>
                  <label className="text-xs text-slate-500">Properties</label>
                  <div className="mt-1 space-y-1 max-h-40 overflow-y-auto">
                    {Object.entries(selectedNode.data.properties).map(([key, value]) => (
                      <div key={key} className="text-xs">
                        <span className="text-slate-500">{key}:</span>
                        <span className="ml-2 text-slate-900">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <button
                onClick={() => expandNeighbors(selectedNode.id)}
                className="w-full px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
              >
                Expand Neighbors
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
