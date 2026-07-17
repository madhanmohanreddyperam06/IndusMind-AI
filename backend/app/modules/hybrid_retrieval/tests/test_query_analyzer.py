"""Unit tests for query analyzer."""

import pytest
from app.modules.hybrid_retrieval.query_analyzer import QueryAnalyzer
from app.modules.hybrid_retrieval.schemas import QueryAnalysisRequest
from app.modules.hybrid_retrieval.enums import QuestionType, IntentType
from app.modules.hybrid_retrieval.exceptions import QueryAnalysisException


class TestQueryAnalyzer:
    """Test cases for QueryAnalyzer."""
    
    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = QueryAnalyzer()
        assert analyzer is not None
        assert analyzer.equipment_patterns is not None
        assert analyzer.component_patterns is not None
    
    def test_analyze_maintenance_question(self):
        """Test analysis of maintenance question."""
        analyzer = QueryAnalyzer()
        request = QueryAnalysisRequest(query="How do I maintain pump P-101?")
        
        response = analyzer.analyze(request)
        
        assert response.success is True
        assert response.analysis.question_type == QuestionType.MAINTENANCE
        assert "pump" in response.analysis.detected_equipment
        assert "p-101" in response.analysis.detected_equipment
    
    def test_analyze_failure_question(self):
        """Test analysis of failure question."""
        analyzer = QueryAnalyzer()
        request = QueryAnalysisRequest(query="Why did the valve fail?")
        
        response = analyzer.analyze(request)
        
        assert response.success is True
        assert response.analysis.question_type == QuestionType.FAILURE_ANALYSIS
        assert "valve" in response.analysis.detected_equipment
    
    def test_analyze_inspection_question(self):
        """Test analysis of inspection question."""
        analyzer = QueryAnalyzer()
        request = QueryAnalysisRequest(query="When should I inspect the motor?")
        
        response = analyzer.analyze(request)
        
        assert response.success is True
        assert response.analysis.question_type == QuestionType.INSPECTION
        assert "motor" in response.analysis.detected_equipment
    
    def test_analyze_compliance_question(self):
        """Test analysis of compliance question."""
        analyzer = QueryAnalyzer()
        request = QueryAnalysisRequest(query="What are the ISO standards for this equipment?")
        
        response = analyzer.analyze(request)
        
        assert response.success is True
        assert response.analysis.question_type == QuestionType.COMPLIANCE
        assert "iso" in response.analysis.detected_regulations
    
    def test_analyze_equipment_info_question(self):
        """Test analysis of equipment info question."""
        analyzer = QueryAnalyzer()
        request = QueryAnalysisRequest(query="What is the capacity of compressor C-201?")
        
        response = analyzer.analyze(request)
        
        assert response.success is True
        assert response.analysis.question_type == QuestionType.EQUIPMENT_INFO
        assert "compressor" in response.analysis.detected_equipment
    
    def test_analyze_empty_query(self):
        """Test analysis of empty query."""
        analyzer = QueryAnalyzer()
        request = QueryAnalysisRequest(query="")
        
        with pytest.raises(QueryAnalysisException):
            analyzer.analyze(request)
    
    def test_analyze_whitespace_query(self):
        """Test analysis of whitespace-only query."""
        analyzer = QueryAnalyzer()
        request = QueryAnalysisRequest(query="   ")
        
        with pytest.raises(QueryAnalysisException):
            analyzer.analyze(request)
    
    def test_detect_equipment_patterns(self):
        """Test equipment pattern detection."""
        analyzer = QueryAnalyzer()
        request = QueryAnalysisRequest(query="Check pump P-101 and valve V-202")
        
        response = analyzer.analyze(request)
        
        assert len(response.analysis.detected_equipment) >= 2
        assert "pump" in response.analysis.detected_equipment
        assert "valve" in response.analysis.detected_equipment
    
    def test_detect_component_patterns(self):
        """Test component pattern detection."""
        analyzer = QueryAnalyzer()
        request = QueryAnalysisRequest(query="The bearing and seal need replacement")
        
        response = analyzer.analyze(request)
        
        assert len(response.analysis.detected_components) >= 2
        assert "bearing" in response.analysis.detected_components
        assert "seal" in response.analysis.detected_components
    
    def test_detect_activity_patterns(self):
        """Test activity pattern detection."""
        analyzer = QueryAnalyzer()
        request = QueryAnalysisRequest(query="We need to repair and inspect the equipment")
        
        response = analyzer.analyze(request)
        
        assert len(response.analysis.detected_activities) >= 2
        assert "repair" in response.analysis.detected_activities
        assert "inspect" in response.analysis.detected_activities
    
    def test_detect_date_patterns(self):
        """Test date pattern detection."""
        analyzer = QueryAnalyzer()
        request = QueryAnalysisRequest(query="Check the maintenance from 2024-01-15")
        
        response = analyzer.analyze(request)
        
        assert len(response.analysis.detected_dates) > 0
    
    def test_detect_regulation_patterns(self):
        """Test regulation pattern detection."""
        analyzer = QueryAnalyzer()
        request = QueryAnalysisRequest(query="Follow the ASTM and API standards")
        
        response = analyzer.analyze(request)
        
        assert len(response.analysis.detected_regulations) >= 2
        assert "astm" in response.analysis.detected_regulations
        assert "api" in response.analysis.detected_regulations
    
    def test_intent_detection_troubleshooting(self):
        """Test troubleshooting intent detection."""
        analyzer = QueryAnalyzer()
        request = QueryAnalysisRequest(query="How do I fix the problem with the pump?")
        
        response = analyzer.analyze(request)
        
        assert response.analysis.intent == IntentType.TROUBLESHOOTING
    
    def test_intent_detection_procedure(self):
        """Test procedure intent detection."""
        analyzer = QueryAnalyzer()
        request = QueryAnalysisRequest(query="What are the steps to replace the seal?")
        
        response = analyzer.analyze(request)
        
        assert response.analysis.intent == IntentType.PROCEDURE
    
    def test_intent_detection_status(self):
        """Test status intent detection."""
        analyzer = QueryAnalyzer()
        request = QueryAnalysisRequest(query="What is the current status of the motor?")
        
        response = analyzer.analyze(request)
        
        assert response.analysis.intent == IntentType.STATUS
    
    def test_confidence_calculation(self):
        """Test confidence calculation."""
        analyzer = QueryAnalyzer()
        request = QueryAnalysisRequest(query="How do I maintain pump P-101 with the bearing and seal?")
        
        response = analyzer.analyze(request)
        
        assert response.analysis.confidence > 0.5
        assert response.analysis.confidence <= 1.0
    
    def test_keyword_extraction(self):
        """Test keyword extraction."""
        analyzer = QueryAnalyzer()
        request = QueryAnalysisRequest(query="Pump maintenance procedure for bearing replacement")
        
        response = analyzer.analyze(request)
        
        assert len(response.analysis.keywords) > 0
        assert "pump" in response.analysis.keywords
        assert "maintenance" in response.analysis.keywords
    
    def test_analysis_timing(self):
        """Test analysis timing is recorded."""
        analyzer = QueryAnalyzer()
        request = QueryAnalysisRequest(query="How do I maintain the pump?")
        
        response = analyzer.analyze(request)
        
        assert response.analysis.analysis_time_ms > 0
        assert response.analysis.analysis_time_ms < 1000  # Should be fast
    
    def test_complex_query_analysis(self):
        """Test analysis of complex query."""
        analyzer = QueryAnalyzer()
        request = QueryAnalysisRequest(
            query="According to ASTM standards, how should I inspect the pump P-101 "
                  "bearing and seal during maintenance in the engineering department?"
        )
        
        response = analyzer.analyze(request)
        
        assert response.success is True
        assert len(response.analysis.detected_equipment) > 0
        assert len(response.analysis.detected_components) > 0
        assert len(response.analysis.detected_activities) > 0
        assert len(response.analysis.detected_regulations) > 0
        assert len(response.analysis.detected_departments) > 0
