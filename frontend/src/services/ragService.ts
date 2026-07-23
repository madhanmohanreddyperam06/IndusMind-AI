// RAG Engine API Service
import axios from 'axios';
import API_CONFIG from '../config/api';
import type {
  GenerationRequest,
  GenerationResponse,
  Conversation,
  ConversationMessage,
  ProviderInfo,
  HealthCheckResponse,
  StreamingChunk
} from '../types/rag';

const API_BASE = API_CONFIG.BASE_URL_WITH_VERSION;

class RAGService {
  private baseURL = `${API_BASE}/rag`;

  // Generate answer
  async generateAnswer(request: GenerationRequest): Promise<GenerationResponse> {
    const response = await axios.post<GenerationResponse>(
      `${this.baseURL}/generate`,
      request
    );
    return response.data;
  }

  // Generate answer with streaming
  async generateAnswerStream(
    request: GenerationRequest,
    onChunk: (chunk: StreamingChunk) => void,
    onError: (error: Error) => void,
    onComplete: () => void
  ): Promise<void> {
    try {
      const response = await fetch(`${this.baseURL}/generate/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('Response body is not readable');
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6)) as StreamingChunk;
              onChunk(data);

              if (data.done) {
                onComplete();
                return;
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (error) {
      onError(error as Error);
    }
  }

  // Summarize text
  async summarizeText(
    text: string,
    maxLength: number = 200,
    style: string = 'concise'
  ): Promise<{ summary: string }> {
    const response = await axios.post(`${this.baseURL}/summarize`, {
      text,
      max_length: maxLength,
      style,
    });
    return response.data;
  }

  // Generate structured output
  async generateStructuredOutput(
    question: string,
    contextPackage: any,
    schemaDefinition: Record<string, any>,
    provider?: string
  ): Promise<{ output: Record<string, any> }> {
    const response = await axios.post(`${this.baseURL}/structured`, {
      question,
      context_package: contextPackage,
      schema_definition: schemaDefinition,
      provider,
    });
    return response.data;
  }

  // Conversation operations
  async createConversation(
    userId?: number,
    title?: string,
    metadata?: Record<string, any>
  ): Promise<Conversation> {
    const response = await axios.post(`${this.baseURL}/conversation/start`, {
      user_id: userId,
      title,
      metadata,
    });
    return response.data;
  }

  async addMessage(
    conversationId: string,
    role: 'user' | 'assistant' | 'system',
    content: string,
    metadata?: Record<string, any>
  ): Promise<ConversationMessage> {
    const response = await axios.post(
      `${this.baseURL}/conversation/message?conversation_id=${conversationId}`,
      {
        role,
        content,
        metadata,
      }
    );
    return response.data;
  }

  async getConversation(conversationId: string): Promise<Conversation> {
    const response = await axios.get<Conversation>(
      `${this.baseURL}/conversation/${conversationId}`
    );
    return response.data;
  }

  async deleteConversation(conversationId: string): Promise<void> {
    await axios.delete(`${this.baseURL}/conversation/${conversationId}`);
  }

  async getConversations(): Promise<Conversation[]> {
    try {
      const response = await axios.get<Conversation[]>(`${this.baseURL}/conversations`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
      // Return empty array if endpoint doesn't exist
      return [];
    }
  }

  // Provider operations
  async getProviders(): Promise<ProviderInfo[]> {
    const response = await axios.get<ProviderInfo[]>(`${this.baseURL}/providers`);
    return response.data;
  }

  async getConfig(): Promise<Record<string, any>> {
    const response = await axios.get(`${this.baseURL}/config`);
    return response.data;
  }

  async healthCheck(): Promise<HealthCheckResponse> {
    const response = await axios.get<HealthCheckResponse>(`${this.baseURL}/health`);
    return response.data;
  }

  // Debug
  async debugGeneration(request: GenerationRequest): Promise<any> {
    const response = await axios.post(`${this.baseURL}/debug`, request);
    return response.data;
  }
}

export const ragService = new RAGService();
