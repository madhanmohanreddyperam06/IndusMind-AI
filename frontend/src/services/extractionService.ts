// Knowledge Extraction API Service
import axios from 'axios';
import API_CONFIG from '../config/api';
import type {
  ExtractedEntity,
  ExtractedRelationship,
  ExtractionStatistics,
  EntityAlias,
  EntityOccurrence,
  RelationshipEvidence,
  PaginatedResponse
} from '../types/extraction';

const API_BASE = API_CONFIG.BASE_URL_WITH_VERSION;

class ExtractionService {
  private baseURL = `${API_BASE}/knowledge-extraction`;

  // Entity operations
  async getEntities(
    documentId?: number,
    entityType?: string,
    page: number = 1,
    pageSize: number = 50
  ): Promise<PaginatedResponse<ExtractedEntity>> {
    const response = await axios.get<PaginatedResponse<ExtractedEntity>>(`${this.baseURL}/entities`, {
      params: {
        document_id: documentId,
        entity_type: entityType,
        page,
        page_size: pageSize,
      },
    });
    return response.data;
  }

  async getEntity(entityId: number): Promise<ExtractedEntity> {
    const response = await axios.get<ExtractedEntity>(`${this.baseURL}/entities/${entityId}`);
    return response.data;
  }

  async getEntityAliases(entityId: number): Promise<EntityAlias[]> {
    const response = await axios.get<EntityAlias[]>(`${this.baseURL}/entities/${entityId}/aliases`);
    return response.data;
  }

  async getEntityOccurrences(entityId: number): Promise<EntityOccurrence[]> {
    const response = await axios.get<EntityOccurrence[]>(`${this.baseURL}/entities/${entityId}/occurrences`);
    return response.data;
  }

  // Relationship operations
  async getRelationships(
    documentId?: number,
    relationshipType?: string,
    page: number = 1,
    pageSize: number = 50
  ): Promise<PaginatedResponse<ExtractedRelationship>> {
    const response = await axios.get<PaginatedResponse<ExtractedRelationship>>(
      `${this.baseURL}/relationships`,
      {
        params: {
          document_id: documentId,
          relationship_type: relationshipType,
          page,
          page_size: pageSize,
        },
      }
    );
    return response.data;
  }

  async getRelationship(relationshipId: number): Promise<ExtractedRelationship> {
    const response = await axios.get<ExtractedRelationship>(
      `${this.baseURL}/relationships/${relationshipId}`
    );
    return response.data;
  }

  async getRelationshipEvidence(relationshipId: number): Promise<RelationshipEvidence[]> {
    const response = await axios.get<RelationshipEvidence[]>(
      `${this.baseURL}/relationships/${relationshipId}/evidence`
    );
    return response.data;
  }

  // Full extraction
  async extractFromDocument(documentId: number): Promise<{
    status: string;
    entities_count: number;
    relationships_count: number;
  }> {
    const response = await axios.post(`${this.baseURL}/extract/document/${documentId}`);
    return response.data;
  }

  async extractFromText(text: string): Promise<{
    entities: ExtractedEntity[];
    relationships: ExtractedRelationship[];
  }> {
    const response = await axios.post(`${this.baseURL}/extract/text`, { text });
    return response.data;
  }

  // Statistics
  async getStatistics(): Promise<ExtractionStatistics> {
    const response = await axios.get<ExtractionStatistics>(`${this.baseURL}/statistics`);
    return response.data;
  }

  async getDocumentStatistics(documentId: number): Promise<{
    entities_count: number;
    relationships_count: number;
    entity_type_distribution: Record<string, number>;
    relationship_type_distribution: Record<string, number>;
    average_confidence: number;
  }> {
    const response = await axios.get(`${this.baseURL}/statistics/document/${documentId}`);
    return response.data;
  }
}

export const extractionService = new ExtractionService();
