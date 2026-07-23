import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ProcessingTimeline } from '../components/documents/ProcessingTimeline';
import { documentService } from '../services';
import type { ProcessingTimeline as ProcessingTimelineType } from '../types/documents';
import API_CONFIG from '../config/api';

interface Entity {
  entity_id: string;
  entity_type: string;
  name: string;
  normalized_name: string;
  confidence_score: number;
  page_number?: number;
  section?: string;
  context?: string;
  created_at: string;
}

interface Relationship {
  relationship_id: string;
  source_entity_id: string;
  target_entity_id: string;
  relationship_type: string;
  confidence_score: number;
  page_number?: number;
  evidence_text?: string;
  created_at: string;
}

interface KnowledgeStatistics {
  document_id: string;
  entity_count: number;
  unique_entity_count: number;
  relationship_count: number;
  entity_types: Record<string, number>;
  relationship_types: Record<string, number>;
  confidence_distribution: {
    entities: { high: number; medium: number; low: number };
    relationships: { high: number; medium: number; low: number };
  };
  duplicate_count: number;
  extraction_time_seconds: number;
}

function DocumentDetails() {
  const { documentId } = useParams<{ documentId: string }>();
  const navigate = useNavigate();
  
  const [activeTab, setActiveTab] = useState<'entities' | 'relationships' | 'statistics' | 'timeline'>('entities');
  const [entities, setEntities] = useState<Entity[]>([]);
  const [relationships, setRelationships] = useState<Relationship[]>([]);
  const [statistics, setStatistics] = useState<KnowledgeStatistics | null>(null);
  const [processingTimeline, setProcessingTimeline] = useState<ProcessingTimelineType | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [extracting, setExtracting] = useState(false);

  useEffect(() => {
    if (documentId) {
      loadExtractionData();
    }
  }, [documentId]);

  const loadExtractionData = async () => {
    setLoading(true);
    setError('');
    try {
      // Load entities
      const entitiesResponse = await fetch(`${API_CONFIG.BASE_URL_WITH_VERSION}/knowledge-extraction/entities/${documentId}`);
      if (entitiesResponse.ok) {
        const entitiesData = await entitiesResponse.json();
        setEntities(entitiesData.entities || []);
      }

      // Load relationships
      const relationshipsResponse = await fetch(`${API_CONFIG.BASE_URL_WITH_VERSION}/knowledge-extraction/relationships/${documentId}`);
      if (relationshipsResponse.ok) {
        const relationshipsData = await relationshipsResponse.json();
        setRelationships(relationshipsData.relationships || []);
      }

      // Load statistics
      const statsResponse = await fetch(`${API_CONFIG.BASE_URL_WITH_VERSION}/knowledge-extraction/statistics/${documentId}`);
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStatistics(statsData);
      }

      // Load processing timeline
      if (documentId) {
        try {
          const timeline = await documentService.getProcessingTimeline(parseInt(documentId));
          setProcessingTimeline(timeline);
        } catch (err) {
          console.error('Failed to load processing timeline:', err);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load extraction data');
    } finally {
      setLoading(false);
    }
  };

  const handleExtractKnowledge = async () => {
    setExtracting(true);
    setError('');
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL_WITH_VERSION}/knowledge-extraction/process/${documentId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ force_reextract: false }),
      });
      if (!response.ok) {
        throw new Error('Failed to extract knowledge');
      }
      await loadExtractionData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to extract knowledge');
    } finally {
      setExtracting(false);
    }
  };

  const getEntityTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      EQUIPMENT: 'bg-blue-100 text-blue-900',
      COMPONENT: 'bg-cyan-100 text-cyan-900',
      FAILURE: 'bg-red-100 text-red-900',
      CAUSE: 'bg-orange-100 text-orange-900',
      MAINTENANCE_ACTIVITY: 'bg-green-100 text-green-900',
      INSPECTION: 'bg-purple-100 text-purple-900',
      WORK_ORDER: 'bg-yellow-100 text-yellow-900',
      REGULATION: 'bg-indigo-100 text-indigo-900',
      STANDARD: 'bg-pink-100 text-pink-900',
      DOCUMENT_REFERENCE: 'bg-gray-100 text-gray-900',
      PERSON: 'bg-teal-100 text-teal-900',
      DEPARTMENT: 'bg-lime-100 text-lime-900',
      ORGANIZATION: 'bg-amber-100 text-amber-900',
      VENDOR: 'bg-rose-100 text-rose-900',
      LOCATION: 'bg-emerald-100 text-emerald-900',
      MEASUREMENT: 'bg-sky-100 text-sky-900',
      DATE: 'bg-violet-100 text-violet-900',
      PROCESS_PARAMETER: 'bg-fuchsia-100 text-fuchsia-900',
      RISK: 'bg-red-200 text-red-900',
      SAFETY: 'bg-green-200 text-green-900',
      QUALITY: 'bg-blue-200 text-blue-900',
    };
    return colors[type] || 'bg-gray-100 text-gray-900';
  };

  const getRelationshipTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      HAS_COMPONENT: 'bg-blue-100 text-blue-900',
      FAILED_DUE_TO: 'bg-red-100 text-red-900',
      CAUSED_BY: 'bg-orange-100 text-orange-900',
      PERFORMED_ON: 'bg-green-100 text-green-900',
      PERFORMED_BY: 'bg-purple-100 text-purple-900',
      INSPECTS: 'bg-cyan-100 text-cyan-900',
      REFERENCES: 'bg-yellow-100 text-yellow-900',
      APPLIES_TO: 'bg-indigo-100 text-indigo-900',
      LOCATED_IN: 'bg-emerald-100 text-emerald-900',
      ASSIGNED_TO: 'bg-pink-100 text-pink-900',
      RECORDED_IN: 'bg-gray-100 text-gray-900',
    };
    return colors[type] || 'bg-gray-100 text-gray-900';
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 md:py-6">
          <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-3">
            <div>
              <button
                onClick={() => navigate('/documents')}
                className="text-gray-600 hover:text-gray-900 mb-1 md:mb-2 text-xs md:text-sm"
              >
                ← Back to Documents
              </button>
              <h1 className="text-xl md:text-3xl font-semibold text-gray-900 tracking-tight">Document Details</h1>
              <p className="mt-0.5 md:mt-1 text-xs md:text-sm text-gray-600">Knowledge extraction for document {documentId}</p>
            </div>
            <button
              onClick={handleExtractKnowledge}
              disabled={extracting}
              className="bg-gray-900 text-white px-4 md:px-6 py-2 md:py-2.5 rounded-lg text-xs md:text-sm font-medium hover:bg-gray-800 transition-colors disabled:opacity-50 self-start md:self-auto"
            >
              {extracting ? 'Extracting...' : 'Extract Knowledge'}
            </button>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 md:py-4">
          <div className="bg-red-50 border border-red-200 text-red-700 px-3 md:px-4 py-2 md:py-3 rounded-lg text-xs md:text-sm">
            {error}
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 md:py-6">
        <div className="border-b border-gray-200 overflow-x-auto">
          <nav className="-mb-px flex space-x-4 md:space-x-8 min-w-max">
            <button
              onClick={() => setActiveTab('entities')}
              className={`${
                activeTab === 'entities'
                  ? 'border-gray-900 text-gray-900'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-3 md:py-4 px-1 border-b-2 font-medium text-xs md:text-sm`}
            >
              Entities {entities.length > 0 && `(${entities.length})`}
            </button>
            <button
              onClick={() => setActiveTab('relationships')}
              className={`${
                activeTab === 'relationships'
                  ? 'border-gray-900 text-gray-900'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-3 md:py-4 px-1 border-b-2 font-medium text-xs md:text-sm`}
            >
              Relationships {relationships.length > 0 && `(${relationships.length})`}
            </button>
            <button
              onClick={() => setActiveTab('statistics')}
              className={`${
                activeTab === 'statistics'
                  ? 'border-gray-900 text-gray-900'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-3 md:py-4 px-1 border-b-2 font-medium text-xs md:text-sm`}
            >
              Statistics
            </button>
            <button
              onClick={() => setActiveTab('timeline')}
              className={`${
                activeTab === 'timeline'
                  ? 'border-gray-900 text-gray-900'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-3 md:py-4 px-1 border-b-2 font-medium text-xs md:text-sm`}
            >
              Processing Timeline
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 md:py-6">
        {loading ? (
          <div className="text-center text-gray-600 py-12">Loading...</div>
        ) : (
          <>
            {/* Entities Tab */}
            {activeTab === 'entities' && (
              <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                {entities.length === 0 ? (
                  <div className="p-6 md:p-8 text-center text-xs md:text-sm text-gray-600">
                    No entities found. Click "Extract Knowledge" to extract entities from this document.
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full">
                      <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                          <th className="px-3 md:px-6 py-2 md:py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider">Name</th>
                          <th className="px-3 md:px-6 py-2 md:py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider">Type</th>
                          <th className="px-3 md:px-6 py-2 md:py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider hidden sm:table-cell">Confidence</th>
                          <th className="px-3 md:px-6 py-2 md:py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider hidden md:table-cell">Page</th>
                          <th className="px-3 md:px-6 py-2 md:py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider hidden lg:table-cell">Context</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {entities.map((entity) => (
                          <tr key={entity.entity_id} className="hover:bg-gray-50">
                            <td className="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                              <div className="text-xs md:text-sm font-medium text-gray-900">{entity.name}</div>
                              <div className="text-xs text-gray-500 hidden md:block">{entity.normalized_name}</div>
                            </td>
                            <td className="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                              <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getEntityTypeColor(entity.entity_type)}`}>
                                {entity.entity_type.replace('_', ' ')}
                              </span>
                            </td>
                            <td className="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap hidden sm:table-cell">
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                  className="bg-gray-900 h-2 rounded-full"
                                  style={{ width: `${entity.confidence_score * 100}%` }}
                                ></div>
                              </div>
                              <div className="text-xs text-gray-500 mt-1">{(entity.confidence_score * 100).toFixed(0)}%</div>
                            </td>
                            <td className="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap text-xs md:text-sm text-gray-600 hidden md:table-cell">
                              {entity.page_number || '-'}
                            </td>
                            <td className="px-3 md:px-6 py-3 md:py-4 text-xs md:text-sm text-gray-600 max-w-md truncate hidden lg:table-cell">
                              {entity.context || '-'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {/* Relationships Tab */}
            {activeTab === 'relationships' && (
              <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                {relationships.length === 0 ? (
                  <div className="p-6 md:p-8 text-center text-xs md:text-sm text-gray-600">
                    No relationships found. Click "Extract Knowledge" to extract relationships from this document.
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full">
                      <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                          <th className="px-3 md:px-6 py-2 md:py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider">Source Entity</th>
                          <th className="px-3 md:px-6 py-2 md:py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider">Relationship</th>
                          <th className="px-3 md:px-6 py-2 md:py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider hidden sm:table-cell">Target Entity</th>
                          <th className="px-3 md:px-6 py-2 md:py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider hidden md:table-cell">Confidence</th>
                          <th className="px-3 md:px-6 py-2 md:py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider hidden lg:table-cell">Evidence</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {relationships.map((rel) => (
                          <tr key={rel.relationship_id} className="hover:bg-gray-50">
                            <td className="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap text-xs md:text-sm text-gray-900">
                              {rel.source_entity_id}
                            </td>
                            <td className="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                              <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getRelationshipTypeColor(rel.relationship_type)}`}>
                                {rel.relationship_type.replace('_', ' ')}
                              </span>
                            </td>
                            <td className="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap text-xs md:text-sm text-gray-900 hidden sm:table-cell">
                              {rel.target_entity_id}
                            </td>
                            <td className="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap hidden md:table-cell">
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                  className="bg-gray-900 h-2 rounded-full"
                                  style={{ width: `${rel.confidence_score * 100}%` }}
                                ></div>
                              </div>
                              <div className="text-xs text-gray-500 mt-1">{(rel.confidence_score * 100).toFixed(0)}%</div>
                            </td>
                            <td className="px-3 md:px-6 py-3 md:py-4 text-xs md:text-sm text-gray-600 max-w-md truncate hidden lg:table-cell">
                              {rel.evidence_text || '-'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {/* Statistics Tab */}
            {activeTab === 'statistics' && (
              <div className="bg-white rounded-lg border border-gray-200 p-4 md:p-6">
                {!statistics ? (
                  <div className="text-center text-xs md:text-sm text-gray-600">
                    No statistics available. Extract knowledge to see statistics.
                  </div>
                ) : (
                  <div className="space-y-4 md:space-y-6">
                    {/* Overview */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
                      <div className="bg-gray-50 rounded-lg p-3 md:p-4">
                        <div className="text-xs md:text-sm text-gray-600">Total Entities</div>
                        <div className="text-lg md:text-2xl font-semibold text-gray-900">{statistics.entity_count}</div>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-3 md:p-4">
                        <div className="text-xs md:text-sm text-gray-600">Unique Entities</div>
                        <div className="text-lg md:text-2xl font-semibold text-gray-900">{statistics.unique_entity_count}</div>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-3 md:p-4">
                        <div className="text-xs md:text-sm text-gray-600">Relationships</div>
                        <div className="text-lg md:text-2xl font-semibold text-gray-900">{statistics.relationship_count}</div>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-3 md:p-4">
                        <div className="text-xs md:text-sm text-gray-600">Duplicates</div>
                        <div className="text-lg md:text-2xl font-semibold text-gray-900">{statistics.duplicate_count}</div>
                      </div>
                    </div>

                    {/* Entity Types */}
                    <div>
                      <h3 className="text-base md:text-lg font-medium text-gray-900 mb-2 md:mb-3">Entity Types</h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                        {Object.entries(statistics.entity_types).map(([type, count]) => (
                          <div key={type} className="flex justify-between bg-gray-50 rounded px-2 md:px-3 py-1.5 md:py-2">
                            <span className="text-xs md:text-sm text-gray-600">{type.replace('_', ' ')}</span>
                            <span className="text-xs md:text-sm font-medium text-gray-900">{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Relationship Types */}
                    <div>
                      <h3 className="text-base md:text-lg font-medium text-gray-900 mb-2 md:mb-3">Relationship Types</h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                        {Object.entries(statistics.relationship_types).map(([type, count]) => (
                          <div key={type} className="flex justify-between bg-gray-50 rounded px-2 md:px-3 py-1.5 md:py-2">
                            <span className="text-xs md:text-sm text-gray-600">{type.replace('_', ' ')}</span>
                            <span className="text-xs md:text-sm font-medium text-gray-900">{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Confidence Distribution */}
                    <div>
                      <h3 className="text-base md:text-lg font-medium text-gray-900 mb-2 md:mb-3">Confidence Distribution</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4">
                        <div className="bg-gray-50 rounded-lg p-3 md:p-4">
                          <h4 className="text-xs md:text-sm font-medium text-gray-900 mb-2">Entities</h4>
                          <div className="space-y-1.5 md:space-y-2">
                            <div className="flex justify-between">
                              <span className="text-xs md:text-sm text-gray-600">High (≥80%)</span>
                              <span className="text-xs md:text-sm font-medium text-gray-900">{statistics.confidence_distribution.entities.high}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-xs md:text-sm text-gray-600">Medium (50-79%)</span>
                              <span className="text-xs md:text-sm font-medium text-gray-900">{statistics.confidence_distribution.entities.medium}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-xs md:text-sm text-gray-600">Low (&lt;50%)</span>
                              <span className="text-xs md:text-sm font-medium text-gray-900">{statistics.confidence_distribution.entities.low}</span>
                            </div>
                          </div>
                        </div>
                        <div className="bg-gray-50 rounded-lg p-3 md:p-4">
                          <h4 className="text-xs md:text-sm font-medium text-gray-900 mb-2">Relationships</h4>
                          <div className="space-y-1.5 md:space-y-2">
                            <div className="flex justify-between">
                              <span className="text-xs md:text-sm text-gray-600">High (≥80%)</span>
                              <span className="text-xs md:text-sm font-medium text-gray-900">{statistics.confidence_distribution.relationships.high}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-xs md:text-sm text-gray-600">Medium (50-79%)</span>
                              <span className="text-xs md:text-sm font-medium text-gray-900">{statistics.confidence_distribution.relationships.medium}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-xs md:text-sm text-gray-600">Low (&lt;50%)</span>
                              <span className="text-xs md:text-sm font-medium text-gray-900">{statistics.confidence_distribution.relationships.low}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Extraction Time */}
                    <div className="bg-gray-50 rounded-lg p-3 md:p-4">
                      <div className="flex justify-between">
                        <span className="text-xs md:text-sm text-gray-600">Extraction Time</span>
                        <span className="text-xs md:text-sm font-medium text-gray-900">{statistics.extraction_time_seconds.toFixed(2)}s</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Processing Timeline Tab */}
            {activeTab === 'timeline' && (
              <div className="bg-white rounded-lg border border-gray-200 p-4 md:p-6">
                {!processingTimeline ? (
                  <div className="text-center text-xs md:text-sm text-gray-600">
                    No processing timeline available. Process the document to see the timeline.
                  </div>
                ) : (
                  <ProcessingTimeline timeline={processingTimeline} />
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default DocumentDetails;
