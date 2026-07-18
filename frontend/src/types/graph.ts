// Knowledge Graph Types

export interface GraphNode {
  id: string;
  labels: string[];
  properties: Record<string, any>;
}

export interface GraphRelationship {
  id: string;
  type: string;
  source: string;
  target: string;
  properties: Record<string, any>;
}

export interface GraphPath {
  nodes: GraphNode[];
  relationships: GraphRelationship[];
  length: number;
}

export interface GraphSubgraph {
  center_node: string;
  nodes: GraphNode[];
  relationships: GraphRelationship[];
}

export interface EntityConnections {
  entity_id: string;
  components: GraphNode[];
  failures: GraphNode[];
  maintenance: GraphNode[];
  inspections: GraphNode[];
  vendors: GraphNode[];
  standards: GraphNode[];
  documents: GraphNode[];
  personnel: GraphNode[];
}

export interface GraphStatistics {
  node_count: number;
  relationship_count: number;
  entity_types: Record<string, number>;
  relationship_types: Record<string, number>;
  connected_components: number;
  average_degree: number;
}

export interface GraphSyncStatus {
  document_id: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  nodes_synced: number;
  relationships_synced: number;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
}
