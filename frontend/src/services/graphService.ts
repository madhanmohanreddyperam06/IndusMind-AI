// Knowledge Graph API Service
import axios from 'axios';
import type {
  GraphNode,
  GraphRelationship,
  GraphPath,
  GraphSubgraph,
  EntityConnections,
  GraphStatistics,
  GraphSyncStatus
} from '../types/graph';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

class GraphService {
  private baseURL = `${API_BASE}/graph`;

  // Node operations
  async getNode(nodeId: string): Promise<GraphNode> {
    const response = await axios.post<GraphNode>(`${this.baseURL}/nodes/${nodeId}`);
    return response.data;
  }

  async createNode(node: Partial<GraphNode>): Promise<GraphNode> {
    const response = await axios.post<GraphNode>(`${this.baseURL}/nodes`, node);
    return response.data;
  }

  async updateNode(nodeId: string, node: Partial<GraphNode>): Promise<GraphNode> {
    const response = await axios.put<GraphNode>(`${this.baseURL}/nodes/${nodeId}`, node);
    return response.data;
  }

  async deleteNode(nodeId: string): Promise<void> {
    await axios.delete(`${this.baseURL}/nodes/${nodeId}`);
  }

  // Relationship operations
  async createRelationship(relationship: Partial<GraphRelationship>): Promise<GraphRelationship> {
    const response = await axios.post<GraphRelationship>(`${this.baseURL}/relationships`, relationship);
    return response.data;
  }

  async updateRelationship(
    relationshipId: string,
    relationship: Partial<GraphRelationship>
  ): Promise<GraphRelationship> {
    const response = await axios.put<GraphRelationship>(
      `${this.baseURL}/relationships/${relationshipId}`,
      relationship
    );
    return response.data;
  }

  async deleteRelationship(relationshipId: string): Promise<void> {
    await axios.delete(`${this.baseURL}/relationships/${relationshipId}`);
  }

  // Query operations
  async getNeighbors(nodeId: string, relationshipTypes?: string[]): Promise<GraphNode[]> {
    const response = await axios.post<GraphNode[]>(`${this.baseURL}/neighbors`, {
      node_id: nodeId,
      relationship_types: relationshipTypes,
    });
    return response.data;
  }

  async findShortestPath(sourceId: string, targetId: string): Promise<GraphPath> {
    const response = await axios.post<GraphPath>(`${this.baseURL}/path`, {
      source_id: sourceId,
      target_id: targetId,
    });
    return response.data;
  }

  async getSubgraph(centerNodeId: string, depth: number = 2): Promise<GraphSubgraph> {
    const response = await axios.post<GraphSubgraph>(`${this.baseURL}/subgraph`, {
      center_node_id: centerNodeId,
      depth,
    });
    return response.data;
  }

  // Entity-specific queries
  async getEquipmentConnections(entityId: string): Promise<EntityConnections> {
    const response = await axios.get<EntityConnections>(
      `${this.baseURL}/equipment/${entityId}/connections`
    );
    return response.data;
  }

  async getMaintenanceHistory(entityId: string): Promise<GraphNode[]> {
    const response = await axios.get<GraphNode[]>(`${this.baseURL}/entity/${entityId}/maintenance`);
    return response.data;
  }

  async getFailures(entityId: string): Promise<GraphNode[]> {
    const response = await axios.get<GraphNode[]>(`${this.baseURL}/entity/${entityId}/failures`);
    return response.data;
  }

  async getInspections(entityId: string): Promise<GraphNode[]> {
    const response = await axios.get<GraphNode[]>(`${this.baseURL}/entity/${entityId}/inspections`);
    return response.data;
  }

  async getVendors(entityId: string): Promise<GraphNode[]> {
    const response = await axios.get<GraphNode[]>(`${this.baseURL}/entity/${entityId}/vendors`);
    return response.data;
  }

  async getStandards(entityId: string): Promise<GraphNode[]> {
    const response = await axios.get<GraphNode[]>(`${this.baseURL}/entity/${entityId}/standards`);
    return response.data;
  }

  async getConnectedDocuments(entityId: string): Promise<GraphNode[]> {
    const response = await axios.get<GraphNode[]>(`${this.baseURL}/entity/${entityId}/documents`);
    return response.data;
  }

  async getConnectedPersonnel(entityId: string): Promise<GraphNode[]> {
    const response = await axios.get<GraphNode[]>(`${this.baseURL}/entity/${entityId}/personnel`);
    return response.data;
  }

  // Synchronization operations
  async syncDocument(documentId: number): Promise<GraphSyncStatus> {
    const response = await axios.post<GraphSyncStatus>(`${this.baseURL}/sync/document/${documentId}`);
    return response.data;
  }

  async syncAllDocuments(): Promise<{ status: string; message: string }> {
    const response = await axios.post(`${this.baseURL}/sync/all`);
    return response.data;
  }

  async rebuildGraph(): Promise<{ status: string; message: string }> {
    const response = await axios.post(`${this.baseURL}/rebuild`);
    return response.data;
  }

  async getSyncStatus(documentId: number): Promise<GraphSyncStatus> {
    const response = await axios.get<GraphSyncStatus>(`${this.baseURL}/sync/status/${documentId}`);
    return response.data;
  }

  // Graph management
  async initializeGraph(): Promise<{ status: string; message: string }> {
    const response = await axios.post(`${this.baseURL}/initialize`);
    return response.data;
  }

  async clearGraph(): Promise<{ status: string; message: string }> {
    const response = await axios.delete(`${this.baseURL}/clear`);
    return response.data;
  }

  // Statistics
  async getStatistics(): Promise<GraphStatistics> {
    const response = await axios.get<GraphStatistics>(`${this.baseURL}/statistics`);
    return response.data;
  }
}

export const graphService = new GraphService();
