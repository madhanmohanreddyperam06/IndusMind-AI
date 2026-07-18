// Document API Service
import axios from 'axios';
import type {
  Document,
  DocumentUploadResponse,
  ProcessedDocument,
  ProcessingTimeline,
  PaginatedResponse
} from '../types/documents';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

class DocumentService {
  private baseURL = `${API_BASE}/documents`;

  // Upload document
  async uploadDocument(file: File): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post<DocumentUploadResponse>(
      `${this.baseURL}/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  // Get all documents
  async getDocuments(
    page: number = 1,
    pageSize: number = 20,
    filters?: Record<string, any>
  ): Promise<PaginatedResponse<Document>> {
    const response = await axios.get<PaginatedResponse<Document>>(this.baseURL, {
      params: {
        page,
        page_size: pageSize,
        ...filters,
      },
    });
    return response.data;
  }

  // Get document by ID
  async getDocument(documentId: number): Promise<Document> {
    const response = await axios.get<Document>(`${this.baseURL}/${documentId}`);
    return response.data;
  }

  // Get processed document
  async getProcessedDocument(documentId: number): Promise<ProcessedDocument> {
    const response = await axios.get<ProcessedDocument>(
      `${this.baseURL}/${documentId}/processed`
    );
    return response.data;
  }

  // Process document
  async processDocument(documentId: number): Promise<{ status: string; message: string }> {
    const response = await axios.post(`${this.baseURL}/${documentId}/process`);
    return response.data;
  }

  // Delete document
  async deleteDocument(documentId: number): Promise<void> {
    await axios.delete(`${this.baseURL}/${documentId}`);
  }

  // Get processing timeline
  async getProcessingTimeline(documentId: number): Promise<ProcessingTimeline> {
    const response = await axios.get<ProcessingTimeline>(
      `${this.baseURL}/${documentId}/timeline`
    );
    return response.data;
  }

  // Search documents
  async searchDocuments(query: string, filters?: Record<string, any>): Promise<Document[]> {
    const response = await axios.get<Document[]>(`${this.baseURL}/search`, {
      params: {
        query,
        ...filters,
      },
    });
    return response.data;
  }

  // Get document statistics
  async getStatistics(): Promise<{
    total_documents: number;
    processed_documents: number;
    failed_documents: number;
    total_size: number;
    by_type: Record<string, number>;
  }> {
    const response = await axios.get(`${this.baseURL}/statistics`);
    return response.data;
  }
}

export const documentService = new DocumentService();
