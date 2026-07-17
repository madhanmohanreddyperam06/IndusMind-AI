import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { documentApiService, Document, DocumentFilters, DocumentUpdate } from '../services/documentApi';

interface ProcessingStatus {
  document_id: string;
  processing_stage: string;
  processing_started_at?: string;
  processing_completed_at?: string;
  processing_duration_seconds?: number;
  parser_used?: string;
  ocr_used: boolean;
  ocr_provider?: string;
  error_message?: string;
}

interface DocumentStatistics {
  document_id: string;
  page_count: number;
  word_count: number;
  character_count: number;
  paragraph_count: number;
  table_count: number;
  image_count: number;
  section_count: number;
  language: string;
  estimated_reading_time?: number;
}

function Documents() {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState<DocumentFilters>({});
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showProcessingModal, setShowProcessingModal] = useState(false);
  const [showStatisticsModal, setShowStatisticsModal] = useState(false);
  const [processingStatus, setProcessingStatus] = useState<ProcessingStatus | null>(null);
  const [documentStatistics, setDocumentStatistics] = useState<DocumentStatistics | null>(null);
  const [processingLoading, setProcessingLoading] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, [page]);

  const loadDocuments = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await documentApiService.listDocuments(page, 20, filters);
      setDocuments(response.documents);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (files: File[]) => {
    try {
      for (const file of files) {
        await documentApiService.uploadDocument(file);
      }
      await loadDocuments();
      setShowUploadModal(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload documents');
    }
  };

  const handleDelete = async (documentId: string) => {
    try {
      await documentApiService.deleteDocument(documentId);
      await loadDocuments();
      setShowDeleteDialog(false);
      setSelectedDocument(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete document');
    }
  };

  const handleUpdate = async (documentId: string, updateData: DocumentUpdate) => {
    try {
      await documentApiService.updateDocument(documentId, updateData);
      await loadDocuments();
      setShowEditModal(false);
      setSelectedDocument(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update document');
    }
  };

  const handleDownload = async (documentId: string, filename: string) => {
    try {
      const blob = await documentApiService.downloadDocument(documentId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download document');
    }
  };

  const handleProcessDocument = async (documentId: string) => {
    setProcessingLoading(true);
    setError('');
    try {
      const response = await fetch(`http://localhost:8000/api/v1/document-processing/process/${documentId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ force_reprocess: false }),
      });
      if (!response.ok) {
        throw new Error('Failed to process document');
      }
      const status: ProcessingStatus = await response.json();
      setProcessingStatus(status);
      setShowProcessingModal(true);
      await loadDocuments();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process document');
    } finally {
      setProcessingLoading(false);
    }
  };

  const handleGetStatistics = async (documentId: string) => {
    setProcessingLoading(true);
    setError('');
    try {
      const response = await fetch(`http://localhost:8000/api/v1/document-processing/statistics/${documentId}`);
      if (!response.ok) {
        throw new Error('Failed to get document statistics');
      }
      const stats: DocumentStatistics = await response.json();
      setDocumentStatistics(stats);
      setShowStatisticsModal(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get document statistics');
    } finally {
      setProcessingLoading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-semibold text-gray-900 tracking-tight">Documents</h1>
              <p className="mt-1 text-gray-600">Manage your industrial documents</p>
            </div>
            <button
              onClick={() => setShowUploadModal(true)}
              className="bg-gray-900 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors"
            >
              Upload Document
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <input
              type="text"
              placeholder="Search by filename..."
              value={filters.filename || ''}
              onChange={(e) => setFilters({ ...filters, filename: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            />
            <select
              value={filters.category || ''}
              onChange={(e) => setFilters({ ...filters, category: e.target.value || undefined })}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            >
              <option value="">All Categories</option>
              <option value="OEM_MANUAL">OEM Manual</option>
              <option value="MAINTENANCE_MANUAL">Maintenance Manual</option>
              <option value="WORK_ORDER">Work Order</option>
              <option value="SOP">SOP</option>
              <option value="INSPECTION_REPORT">Inspection Report</option>
              <option value="INCIDENT_REPORT">Incident Report</option>
              <option value="AUDIT_REPORT">Audit Report</option>
              <option value="PID_DRAWING">P&ID Drawing</option>
              <option value="ENGINEERING_DRAWING">Engineering Drawing</option>
              <option value="EXCEL_DATA">Excel Data</option>
              <option value="COMPLIANCE_DOCUMENT">Compliance Document</option>
              <option value="QUALITY_DOCUMENT">Quality Document</option>
              <option value="OTHER">Other</option>
            </select>
            <select
              value={filters.status || ''}
              onChange={(e) => setFilters({ ...filters, status: e.target.value || undefined })}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            >
              <option value="">All Statuses</option>
              <option value="UPLOADED">Uploaded</option>
              <option value="QUEUED">Queued</option>
              <option value="PROCESSING">Processing</option>
              <option value="COMPLETED">Completed</option>
              <option value="FAILED">Failed</option>
              <option value="ARCHIVED">Archived</option>
            </select>
            <button
              onClick={loadDocuments}
              className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors"
            >
              Apply Filters
            </button>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            {error}
          </div>
        </div>
      )}

      {/* Documents Table */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="p-8 text-center text-gray-600">Loading documents...</div>
          ) : documents.length === 0 ? (
            <div className="p-8 text-center text-gray-600">No documents found</div>
          ) : (
            <table className="min-w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider">Document Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider">Category</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider">Size</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider">Upload Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider">Version</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-900 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-8 w-8 bg-gray-100 rounded-lg flex items-center justify-center">
                          <svg className="h-5 w-5 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{doc.document_name}</div>
                          <div className="text-xs text-gray-500">{doc.original_filename}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-900">
                        {doc.document_category.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {formatFileSize(doc.file_size)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {formatDate(doc.uploaded_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        doc.processing_status === 'COMPLETED' ? 'bg-green-100 text-green-900' :
                        doc.processing_status === 'PROCESSING' ? 'bg-yellow-100 text-yellow-900' :
                        doc.processing_status === 'FAILED' ? 'bg-red-100 text-red-900' :
                        'bg-gray-100 text-gray-900'
                      }`}>
                        {doc.processing_status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      v{doc.version}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => navigate(`/documents/${doc.id}`)}
                        className="text-gray-700 hover:text-gray-900 mr-3"
                      >
                        Details
                      </button>
                      <button
                        onClick={() => handleProcessDocument(doc.id)}
                        disabled={processingLoading}
                        className="text-gray-700 hover:text-gray-900 mr-3 disabled:opacity-50"
                      >
                        Process
                      </button>
                      <button
                        onClick={() => handleGetStatistics(doc.id)}
                        disabled={processingLoading}
                        className="text-gray-700 hover:text-gray-900 mr-3 disabled:opacity-50"
                      >
                        Statistics
                      </button>
                      <button
                        onClick={() => handleDownload(doc.id, doc.original_filename)}
                        className="text-gray-700 hover:text-gray-900 mr-3"
                      >
                        Download
                      </button>
                      <button
                        onClick={() => {
                          setSelectedDocument(doc);
                          setShowEditModal(true);
                        }}
                        className="text-gray-700 hover:text-gray-900 mr-3"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => {
                          setSelectedDocument(doc);
                          setShowDeleteDialog(true);
                        }}
                        className="text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-4 flex justify-center space-x-2">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="px-4 py-2 border border-gray-200 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Previous
            </button>
            <span className="px-4 py-2 text-sm text-gray-600">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage(Math.min(totalPages, page + 1))}
              disabled={page === totalPages}
              className="px-4 py-2 border border-gray-200 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        )}
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload Document</h2>
            <input
              type="file"
              multiple
              onChange={(e) => {
                if (e.target.files) {
                  handleUpload(Array.from(e.target.files));
                }
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm"
            />
            <div className="mt-4 flex justify-end space-x-3">
              <button
                onClick={() => setShowUploadModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && selectedDocument && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Edit Document</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Document Name</label>
                <input
                  type="text"
                  defaultValue={selectedDocument.document_name}
                  id="edit-document-name"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  defaultValue={selectedDocument.description || ''}
                  id="edit-document-description"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm"
                  rows={3}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select
                  defaultValue={selectedDocument.document_category}
                  id="edit-document-category"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm"
                >
                  <option value="UNKNOWN">Unknown</option>
                  <option value="OEM_MANUAL">OEM Manual</option>
                  <option value="MAINTENANCE_MANUAL">Maintenance Manual</option>
                  <option value="WORK_ORDER">Work Order</option>
                  <option value="SOP">SOP</option>
                  <option value="INSPECTION_REPORT">Inspection Report</option>
                  <option value="INCIDENT_REPORT">Incident Report</option>
                  <option value="AUDIT_REPORT">Audit Report</option>
                  <option value="PID_DRAWING">P&ID Drawing</option>
                  <option value="ENGINEERING_DRAWING">Engineering Drawing</option>
                  <option value="EXCEL_DATA">Excel Data</option>
                  <option value="COMPLIANCE_DOCUMENT">Compliance Document</option>
                  <option value="QUALITY_DOCUMENT">Quality Document</option>
                  <option value="OTHER">Other</option>
                </select>
              </div>
            </div>
            <div className="mt-6 flex justify-end space-x-3">
              <button
                onClick={() => setShowEditModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  const nameInput = document.getElementById('edit-document-name') as HTMLInputElement;
                  const descInput = document.getElementById('edit-document-description') as HTMLTextAreaElement;
                  const catInput = document.getElementById('edit-document-category') as HTMLSelectElement;
                  handleUpdate(selectedDocument.id, {
                    document_name: nameInput.value,
                    description: descInput.value || undefined,
                    document_category: catInput.value,
                  });
                }}
                className="px-4 py-2 bg-gray-900 text-white rounded-lg text-sm hover:bg-gray-800"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      {showDeleteDialog && selectedDocument && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Delete Document</h2>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete "{selectedDocument.document_name}"? This action cannot be undone.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteDialog(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(selectedDocument.id)}
                className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Processing Status Modal */}
      {showProcessingModal && processingStatus && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Processing Status</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Stage:</span>
                <span className="text-sm font-medium text-gray-900">{processingStatus.processing_stage}</span>
              </div>
              {processingStatus.parser_used && (
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Parser:</span>
                  <span className="text-sm font-medium text-gray-900">{processingStatus.parser_used}</span>
                </div>
              )}
              {processingStatus.ocr_used && (
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">OCR:</span>
                  <span className="text-sm font-medium text-gray-900">{processingStatus.ocr_provider || 'Yes'}</span>
                </div>
              )}
              {processingStatus.processing_duration_seconds && (
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Duration:</span>
                  <span className="text-sm font-medium text-gray-900">{processingStatus.processing_duration_seconds.toFixed(2)}s</span>
                </div>
              )}
              {processingStatus.error_message && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-700">{processingStatus.error_message}</p>
                </div>
              )}
            </div>
            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setShowProcessingModal(false)}
                className="px-4 py-2 bg-gray-900 text-white rounded-lg text-sm hover:bg-gray-800"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Statistics Modal */}
      {showStatisticsModal && documentStatistics && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Document Statistics</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Pages:</span>
                <span className="text-sm font-medium text-gray-900">{documentStatistics.page_count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Words:</span>
                <span className="text-sm font-medium text-gray-900">{documentStatistics.word_count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Characters:</span>
                <span className="text-sm font-medium text-gray-900">{documentStatistics.character_count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Paragraphs:</span>
                <span className="text-sm font-medium text-gray-900">{documentStatistics.paragraph_count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Tables:</span>
                <span className="text-sm font-medium text-gray-900">{documentStatistics.table_count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Images:</span>
                <span className="text-sm font-medium text-gray-900">{documentStatistics.image_count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Sections:</span>
                <span className="text-sm font-medium text-gray-900">{documentStatistics.section_count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Language:</span>
                <span className="text-sm font-medium text-gray-900">{documentStatistics.language}</span>
              </div>
              {documentStatistics.estimated_reading_time && (
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Reading Time:</span>
                  <span className="text-sm font-medium text-gray-900">{documentStatistics.estimated_reading_time} min</span>
                </div>
              )}
            </div>
            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setShowStatisticsModal(false)}
                className="px-4 py-2 bg-gray-900 text-white rounded-lg text-sm hover:bg-gray-800"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Documents;
