"""Query analyzer for understanding user questions."""

import re
import time
from typing import List, Dict, Any, Optional
from app.modules.hybrid_retrieval.schemas import (
    QueryAnalysis,
    DetectedEntity,
    QueryAnalysisRequest,
    QueryAnalysisResponse
)
from app.modules.hybrid_retrieval.enums import QuestionType, IntentType
from app.modules.hybrid_retrieval.exceptions import QueryAnalysisException
from app.modules.hybrid_retrieval.constants import (
    QUESTION_TYPE_MAINTENANCE,
    QUESTION_TYPE_FAILURE_ANALYSIS,
    QUESTION_TYPE_INSPECTION,
    QUESTION_TYPE_COMPLIANCE,
    QUESTION_TYPE_EQUIPMENT_INFO,
    QUESTION_TYPE_DOCUMENT_LOOKUP,
    QUESTION_TYPE_RELATIONSHIP_EXPLORATION,
    QUESTION_TYPE_ROOT_CAUSE_ANALYSIS,
    QUESTION_TYPE_GENERAL
)
from app.core.logging import setup_logging

logger = setup_logging()


class QueryAnalyzer:
    """Analyzer for understanding user queries."""
    
    def __init__(self):
        """Initialize query analyzer."""
        # Industrial terminology patterns
        self.equipment_patterns = [
            r'\b(pump|valve|motor|compressor|turbine|boiler|reactor|exchanger|filter|sensor|actuator)\b',
            r'\b(p-\d+|v-\d+|m-\d+|c-\d+)\b',  # Equipment IDs like P-101, V-202
            r'\b(pump-\d+|valve-\d+|motor-\d+)\b'  # Named equipment
        ]
        
        self.component_patterns = [
            r'\b(seal|bearing|impeller|shaft|gasket|nozzle|diaphragm|piston|rotor|stator)\b'
        ]
        
        self.activity_patterns = [
            r'\b(maintenance|repair|replace|inspect|clean|calibrate|adjust|test|monitor)\b',
            r'\b(overhaul|service|troubleshoot|diagnose|fix)\b'
        ]
        
        self.date_patterns = [
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',  # MM/DD/YYYY or MM-DD-YYYY
            r'\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b',  # YYYY-MM-DD
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
            r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b'
        ]
        
        self.regulation_patterns = [
            r'\b(ISO|ASTM|API|ASME|IEC|IEEE|NFPA|OSHA|EPA|FDA)\b',
            r'\b(standard|regulation|compliance|code|spec)\b'
        ]
        
        self.department_patterns = [
            r'\b(maintenance|engineering|operations|quality|safety|procurement|hr|it)\b',
            r'\b(department|division|unit|team)\b'
        ]
        
        # Question type keywords
        self.question_type_keywords = {
            QUESTION_TYPE_MAINTENANCE: ['maintenance', 'repair', 'service', 'overhaul', 'fix'],
            QUESTION_TYPE_FAILURE_ANALYSIS: ['failure', 'broke', 'broken', 'malfunction', 'fault', 'error'],
            QUESTION_TYPE_INSPECTION: ['inspect', 'check', 'examine', 'audit', 'review'],
            QUESTION_TYPE_COMPLIANCE: ['compliance', 'regulation', 'standard', 'certify', 'certified'],
            QUESTION_TYPE_EQUIPMENT_INFO: ['what is', 'describe', 'specification', 'capacity', 'rating'],
            QUESTION_TYPE_DOCUMENT_LOOKUP: ['document', 'manual', 'procedure', 'sop', 'where is'],
            QUESTION_TYPE_RELATIONSHIP_EXPLORATION: ['connected to', 'related to', 'linked with', 'associated'],
            QUESTION_TYPE_ROOT_CAUSE_ANALYSIS: ['why', 'cause', 'reason', 'root cause', 'origin']
        }
        
        # Intent keywords
        self.intent_keywords = {
            IntentType.INFORMATION: ['what', 'how', 'describe', 'explain', 'tell me'],
            IntentType.TROUBLESHOOTING: ['problem', 'issue', 'troubleshoot', 'diagnose', 'fix'],
            IntentType.PROCEDURE: ['how to', 'procedure', 'steps', 'process', 'method'],
            IntentType.STATUS: ['status', 'current', 'now', 'is it'],
            IntentType.HISTORY: ['history', 'past', 'previous', 'before', 'last'],
            IntentType.COMPARISON: ['compare', 'difference', 'versus', 'vs', 'better'],
            IntentType.ANALYSIS: ['analyze', 'evaluate', 'assess', 'review']
        }
    
    def analyze(self, request: QueryAnalysisRequest) -> QueryAnalysisResponse:
        """Analyze a user query.
        
        Args:
            request: Query analysis request
            
        Returns:
            Query analysis response
            
        Raises:
            QueryAnalysisException: If analysis fails
        """
        start_time = time.time()
        
        try:
            query = request.query.strip()
            
            if not query:
                raise QueryAnalysisException("Query cannot be empty", query)
            
            # Detect entities and keywords
            detected_entities = self._detect_entities(query)
            detected_equipment = self._extract_equipment(query)
            detected_components = self._extract_components(query)
            detected_activities = self._extract_activities(query)
            detected_dates = self._extract_dates(query)
            detected_regulations = self._extract_regulations(query)
            detected_standards = self._extract_standards(query)
            detected_departments = self._extract_departments(query)
            keywords = self._extract_keywords(query)
            
            # Classify question type
            question_type = self._classify_question_type(query)
            
            # Detect intent
            intent = self._detect_intent(query)
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                query,
                detected_entities,
                question_type,
                intent
            )
            
            analysis_time_ms = (time.time() - start_time) * 1000
            
            analysis = QueryAnalysis(
                original_query=query,
                question_type=question_type,
                intent=intent,
                detected_entities=detected_entities,
                detected_equipment=detected_equipment,
                detected_components=detected_components,
                detected_activities=detected_activities,
                detected_dates=detected_dates,
                detected_regulations=detected_regulations,
                detected_standards=detected_standards,
                detected_departments=detected_departments,
                keywords=keywords,
                confidence=confidence,
                analysis_time_ms=analysis_time_ms
            )
            
            logger.info(f"Query analysis completed in {analysis_time_ms:.2f}ms for query: {query[:50]}...")
            
            return QueryAnalysisResponse(
                analysis=analysis,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            raise QueryAnalysisException(f"Failed to analyze query: {str(e)}", request.query)
    
    def _detect_entities(self, query: str) -> List[DetectedEntity]:
        """Detect entities in the query.
        
        Args:
            query: Query text
            
        Returns:
            List of detected entities
        """
        entities = []
        query_lower = query.lower()
        
        # Check for equipment patterns
        for pattern in self.equipment_patterns:
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                entity = DetectedEntity(
                    entity_id=None,
                    entity_type="Equipment",
                    entity_name=match.group(),
                    confidence=0.8,
                    start_position=match.start(),
                    end_position=match.end()
                )
                entities.append(entity)
        
        # Check for component patterns
        for pattern in self.component_patterns:
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                entity = DetectedEntity(
                    entity_id=None,
                    entity_type="Component",
                    entity_name=match.group(),
                    confidence=0.7,
                    start_position=match.start(),
                    end_position=match.end()
                )
                entities.append(entity)
        
        return entities
    
    def _extract_equipment(self, query: str) -> List[str]:
        """Extract equipment names from query.
        
        Args:
            query: Query text
            
        Returns:
            List of equipment names
        """
        equipment = []
        query_lower = query.lower()
        
        for pattern in self.equipment_patterns:
            matches = re.findall(pattern, query_lower)
            equipment.extend(matches)
        
        return list(set(equipment))
    
    def _extract_components(self, query: str) -> List[str]:
        """Extract component names from query.
        
        Args:
            query: Query text
            
        Returns:
            List of component names
        """
        components = []
        query_lower = query.lower()
        
        for pattern in self.component_patterns:
            matches = re.findall(pattern, query_lower)
            components.extend(matches)
        
        return list(set(components))
    
    def _extract_activities(self, query: str) -> List[str]:
        """Extract maintenance activities from query.
        
        Args:
            query: Query text
            
        Returns:
            List of activity names
        """
        activities = []
        query_lower = query.lower()
        
        for pattern in self.activity_patterns:
            matches = re.findall(pattern, query_lower)
            activities.extend(matches)
        
        return list(set(activities))
    
    def _extract_dates(self, query: str) -> List[str]:
        """Extract dates from query.
        
        Args:
            query: Query text
            
        Returns:
            List of dates
        """
        dates = []
        query_lower = query.lower()
        
        for pattern in self.date_patterns:
            matches = re.findall(pattern, query_lower)
            dates.extend(matches)
        
        return list(set(dates))
    
    def _extract_regulations(self, query: str) -> List[str]:
        """Extract regulation references from query.
        
        Args:
            query: Query text
            
        Returns:
            List of regulation references
        """
        regulations = []
        query_lower = query.lower()
        
        for pattern in self.regulation_patterns:
            matches = re.findall(pattern, query_lower)
            regulations.extend(matches)
        
        return list(set(regulations))
    
    def _extract_standards(self, query: str) -> List[str]:
        """Extract standard references from query.
        
        Args:
            query: Query text
            
        Returns:
            List of standard references
        """
        standards = []
        query_lower = query.lower()
        
        # Standards are often mentioned with regulation patterns
        for pattern in self.regulation_patterns:
            matches = re.findall(pattern, query_lower)
            standards.extend(matches)
        
        return list(set(standards))
    
    def _extract_departments(self, query: str) -> List[str]:
        """Extract department names from query.
        
        Args:
            query: Query text
            
        Returns:
            List of department names
        """
        departments = []
        query_lower = query.lower()
        
        for pattern in self.department_patterns:
            matches = re.findall(pattern, query_lower)
            departments.extend(matches)
        
        return list(set(departments))
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query.
        
        Args:
            query: Query text
            
        Returns:
            List of keywords
        """
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
            'how', 'what', 'where', 'when', 'why', 'who', 'which', 'that',
            'this', 'these', 'those', 'it', 'its', 'they', 'them', 'their',
            'for', 'of', 'with', 'at', 'by', 'from', 'in', 'on', 'to', 'into',
            'through', 'during', 'before', 'after', 'above', 'below', 'between',
            'under', 'again', 'further', 'then', 'once'
        }
        
        # Tokenize and filter
        words = re.findall(r'\b[a-zA-Z]+\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return list(set(keywords))
    
    def _classify_question_type(self, query: str) -> QuestionType:
        """Classify the type of question.
        
        Args:
            query: Query text
            
        Returns:
            Question type
        """
        query_lower = query.lower()
        scores = {}
        
        # Score each question type based on keyword matches
        for qtype, keywords in self.question_type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            scores[qtype] = score
        
        # Return the type with highest score
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                for qtype, score in scores.items():
                    if score == max_score:
                        return QuestionType(qtype)
        
        return QuestionType(QUESTION_TYPE_GENERAL)
    
    def _detect_intent(self, query: str) -> IntentType:
        """Detect user intent.
        
        Args:
            query: Query text
            
        Returns:
            Intent type
        """
        query_lower = query.lower()
        scores = {}
        
        # Score each intent based on keyword matches
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            scores[intent] = score
        
        # Return the intent with highest score
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                for intent, score in scores.items():
                    if score == max_score:
                        return Intent(intent)
        
        return IntentType.INFORMATION
    
    def _calculate_confidence(
        self,
        query: str,
        detected_entities: List[DetectedEntity],
        question_type: QuestionType,
        intent: IntentType
    ) -> float:
        """Calculate confidence in the analysis.
        
        Args:
            query: Query text
            detected_entities: Detected entities
            question_type: Question type
            intent: Intent type
            
        Returns:
            Confidence score (0-1)
        """
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on detected entities
        if detected_entities:
            confidence += 0.2 * min(len(detected_entities) / 3, 1.0)
        
        # Increase confidence if question type is not general
        if question_type != QuestionType(QUESTION_TYPE_GENERAL):
            confidence += 0.15
        
        # Increase confidence if query length is reasonable
        if 10 <= len(query.split()) <= 50:
            confidence += 0.1
        
        # Cap at 1.0
        return min(confidence, 1.0)
