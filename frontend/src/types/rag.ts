// RAG Engine Types

export interface Citation {
  document_id: string;
  chunk_id: string;
  page_number?: number;
  section?: string;
  text_preview: string;
  confidence: number;
}

export interface ConfidenceScores {
  overall: number;
  evidence: number;
  retrieval: number;
  reasoning: number;
}

export interface GenerationStatistics {
  processing_time_ms: number;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  context_size: number;
  evidence_count: number;
  citation_count: number;
  provider: string;
}

export interface GenerationResponse {
  answer: string;
  summary: string;
  citations: Citation[];
  supporting_documents: string[];
  related_entities: Entity[];
  related_relationships: Relationship[];
  confidence: ConfidenceScores;
  follow_up_questions: string[];
  statistics: GenerationStatistics;
  conversation_id?: string;
}

export interface GenerationRequest {
  question: string;
  context_package: ContextPackage;
  provider?: string;
  temperature?: number;
  max_tokens?: number;
  conversation_id?: string;
}

export interface ContextPackage {
  question: string;
  retrieved_chunks: RetrievedChunk[];
  entities: Entity[];
  relationships: Relationship[];
  graph_context?: GraphContext;
}

export interface RetrievedChunk {
  chunk_id: string;
  document_id: string;
  text: string;
  score: number;
  page_number?: number;
  section?: string;
  metadata?: Record<string, any>;
}

export interface Entity {
  name: string;
  type: string;
  confidence: number;
  properties?: Record<string, any>;
}

export interface Relationship {
  source: string;
  target: string;
  type: string;
  confidence: number;
  properties?: Record<string, any>;
}

export interface GraphContext {
  graph_density: number;
  node_count: number;
  edge_count: number;
}

export interface Conversation {
  conversation_id: string;
  user_id?: number;
  title?: string;
  status: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationMessage {
  id: number;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  metadata?: Record<string, any>;
  tokens?: number;
  created_at: string;
}

export interface ProviderInfo {
  name: string;
  type: string;
  available: boolean;
  model?: string;
  capabilities: string[];
}

export interface HealthCheckResponse {
  status: string;
  providers: Record<string, boolean>;
  database: boolean;
  timestamp: number;
}

export interface StreamingChunk {
  chunk: string;
  is_final: boolean;
  done: boolean;
}
