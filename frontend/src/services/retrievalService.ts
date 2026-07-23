// Hybrid Retrieval API Service
import axios from 'axios';
import API_CONFIG from '../config/api';
import type { ContextPackage, RetrievedChunk, Entity } from '../types/rag';

const API_BASE = API_CONFIG.BASE_URL_WITH_VERSION;

class RetrievalService {
  private baseURL = `${API_BASE}/retrieval`;

  // Execute hybrid retrieval query
  async executeQuery(
    query: string,
    sources?: string[],
    limit?: number,
    filters?: Record<string, any>
  ): Promise<ContextPackage> {
    const response = await axios.post<ContextPackage>(`${this.baseURL}/query`, {
      query,
      sources,
      limit,
      filters,
    });
    return response.data;
  }

  // Generate context package
  async generateContext(
    query: string,
    sources?: string[],
    limit?: number
  ): Promise<ContextPackage> {
    const response = await axios.post<ContextPackage>(`${this.baseURL}/context`, {
      query,
      sources,
      limit,
    });
    return response.data;
  }

  // Analyze query
  async analyzeQuery(query: string): Promise<{
    intent: string;
    entities: Entity[];
    question_type: string;
    confidence: number;
  }> {
    const response = await axios.post(`${this.baseURL}/analyze`, { query });
    return response.data;
  }

  // Expand query
  async expandQuery(query: string): Promise<{
    original_query: string;
    expanded_terms: string[];
    synonyms: Record<string, string[]>;
    related_entities: string[];
  }> {
    const response = await axios.post(`${this.baseURL}/expand`, { query });
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{
    status: string;
    components: Record<string, boolean>;
    latency_ms: number;
  }> {
    const response = await axios.get(`${this.baseURL}/health`);
    return response.data;
  }

  // Statistics
  async getStatistics(): Promise<{
    total_queries: number;
    average_latency_ms: number;
    source_usage: Record<string, number>;
    success_rate: number;
  }> {
    const response = await axios.get(`${this.baseURL}/statistics`);
    return response.data;
  }

  // Configuration
  async getConfig(): Promise<{
    default_sources: string[];
    default_limit: number;
    ranking_weights: Record<string, number>;
  }> {
    const response = await axios.get(`${this.baseURL}/config`);
    return response.data;
  }

  // Test retrieval
  async testRetrieval(
    query: string,
    sources: string[]
  ): Promise<{
    results: ContextPackage;
    performance: Record<string, number>;
  }> {
    const response = await axios.post(`${this.baseURL}/test`, {
      query,
      sources,
    });
    return response.data;
  }

  // Debug retrieval
  async debugRetrieval(query: string): Promise<{
    query_analysis: any;
    expanded_query: any;
    vector_results: RetrievedChunk[];
    graph_results: any;
    keyword_results: RetrievedChunk[];
    merged_results: RetrievedChunk[];
    ranked_results: RetrievedChunk[];
    context_package: ContextPackage;
    processing_time_ms: number;
  }> {
    const response = await axios.post(`${this.baseURL}/debug`, { query });
    return response.data;
  }
}

export const retrievalService = new RetrievalService();
