// Knowledge Extraction Types

export interface ExtractedEntity {
  id: number;
  document_id: number;
  entity_name: string;
  entity_type: EntityType;
  confidence: number;
  properties?: Record<string, any>;
  occurrence_count: number;
  first_occurrence_page?: number;
  created_at: string;
}

export type EntityType =
  | 'Equipment'
  | 'Component'
  | 'Failure'
  | 'Cause'
  | 'MaintenanceActivity'
  | 'Inspection'
  | 'WorkOrder'
  | 'Regulation'
  | 'Standard'
  | 'DocumentReference'
  | 'Person'
  | 'Department'
  | 'Organization'
  | 'Vendor'
  | 'Location'
  | 'Measurement'
  | 'Date'
  | 'ProcessParameter'
  | 'Risk'
  | 'Safety'
  | 'Quality';

export interface ExtractedRelationship {
  id: number;
  document_id: number;
  source_entity: string;
  target_entity: string;
  relationship_type: RelationshipType;
  confidence: number;
  properties?: Record<string, any>;
  evidence_count: number;
  created_at: string;
}

export type RelationshipType =
  | 'HAS_COMPONENT'
  | 'FAILED_DUE_TO'
  | 'CAUSED_BY'
  | 'PERFORMED_ON'
  | 'PERFORMED_BY'
  | 'INSPECTS'
  | 'REFERENCES'
  | 'APPLIES_TO'
  | 'LOCATED_IN'
  | 'ASSIGNED_TO'
  | 'RECORDED_IN';

export interface ExtractionStatistics {
  total_entities: number;
  total_relationships: number;
  entity_type_distribution: Record<EntityType, number>;
  relationship_type_distribution: Record<RelationshipType, number>;
  average_confidence: number;
  documents_processed: number;
}

export interface EntityAlias {
  id: number;
  entity_id: number;
  alias: string;
  confidence: number;
  created_at: string;
}

export interface EntityOccurrence {
  id: number;
  entity_id: number;
  document_id: number;
  page_number?: number;
  context: string;
  confidence: number;
  created_at: string;
}

export interface RelationshipEvidence {
  id: number;
  relationship_id: number;
  document_id: number;
  page_number?: number;
  context: string;
  confidence: number;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
