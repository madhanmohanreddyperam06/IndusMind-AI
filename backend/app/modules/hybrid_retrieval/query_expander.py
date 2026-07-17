"""Query expander for industrial terminology expansion."""

import re
import time
from typing import List, Dict, Any, Optional, Set
from sqlalchemy.orm import Session
from app.modules.hybrid_retrieval.schemas import (
    QueryExpansion,
    ExpandedTerm,
    QueryExpansionRequest,
    QueryExpansionResponse
)
from app.modules.hybrid_retrieval.enums import ExpansionStrategy
from app.modules.hybrid_retrieval.exceptions import QueryExpansionException
from app.modules.hybrid_retrieval.constants import (
    MAX_EXPANSION_TERMS,
    MIN_EXPANSION_CONFIDENCE,
    EXPANSION_SYNONYMS,
    EXPANSION_ACRONYMS,
    EXPANSION_ALIASES,
    EXPANSION_RELATED,
    EXPANSION_HIERARCHICAL
)
from app.core.logging import setup_logging

logger = setup_logging()


class QueryExpander:
    """Expander for industrial terminology in queries."""
    
    def __init__(self, db: Session = None):
        """Initialize query expander.
        
        Args:
            db: Database session for entity lookup
        """
        self.db = db
        
        # Industrial terminology dictionaries
        self.equipment_synonyms = {
            'pump': ['centrifugal pump', 'positive displacement pump', 'booster pump'],
            'valve': ['control valve', 'gate valve', 'globe valve', 'check valve', 'ball valve'],
            'motor': ['electric motor', 'induction motor', 'servo motor'],
            'compressor': ['air compressor', 'gas compressor', 'reciprocating compressor'],
            'turbine': ['steam turbine', 'gas turbine', 'hydro turbine'],
            'boiler': ['steam boiler', 'water tube boiler', 'fire tube boiler'],
            'reactor': ['chemical reactor', 'nuclear reactor', 'bioreactor'],
            'exchanger': ['heat exchanger', 'shell and tube exchanger', 'plate exchanger'],
            'filter': ['strainer', 'screen', 'cartridge filter', 'bag filter'],
            'sensor': ['transducer', 'detector', 'measuring device', 'instrument']
        }
        
        self.component_synonyms = {
            'seal': ['mechanical seal', 'gland seal', 'packing'],
            'bearing': ['roller bearing', 'ball bearing', 'journal bearing', 'thrust bearing'],
            'impeller': ['rotor', 'blade', 'propeller'],
            'shaft': ['axle', 'spindle', 'rod'],
            'gasket': ['seal', 'packing', 'washer'],
            'nozzle': ['spray nozzle', 'inlet', 'outlet'],
            'diaphragm': ['membrane', 'flexible seal'],
            'piston': ['plunger', 'ram'],
            'rotor': ['rotating element', 'armature'],
            'stator': ['stationary element', 'field']
        }
        
        self.acronym_expansions = {
            'p': ['pump', 'pressure', 'power'],
            'v': ['valve', 'voltage', 'velocity'],
            'm': ['motor', 'meter', 'maintenance', 'manual'],
            'c': ['compressor', 'controller', 'capacity'],
            't': ['temperature', 'tank', 'turbine'],
            'f': ['flow', 'filter', 'fan'],
            'l': ['level', 'liter', 'load'],
            'd': ['density', 'diameter', 'discharge'],
            'h': ['head', 'height', 'humidity'],
            's': ['speed', 'switch', 'sensor', 'standard'],
            'iso': ['international organization for standardization'],
            'astm': ['american society for testing and materials'],
            'api': ['american petroleum institute'],
            'asme': ['american society of mechanical engineers'],
            'iec': ['international electrotechnical commission'],
            'ieee': ['institute of electrical and electronics engineers'],
            'nfpa': ['national fire protection association'],
            'osha': ['occupational safety and health administration'],
            'epa': ['environmental protection agency'],
            'fda': ['food and drug administration']
        }
        
        self.activity_synonyms = {
            'maintenance': ['upkeep', 'service', 'repair', 'overhaul', 'preservation'],
            'repair': ['fix', 'restore', 'mend', 'recondition'],
            'replace': ['substitute', 'exchange', 'swap', 'change'],
            'inspect': ['examine', 'check', 'audit', 'review', 'survey'],
            'clean': ['purge', 'flush', 'wash', 'decontaminate'],
            'calibrate': ['adjust', 'tune', 'align', 'standardize'],
            'adjust': ['regulate', 'set', 'modify', 'tune'],
            'test': ['examine', 'evaluate', 'assess', 'verify'],
            'monitor': ['observe', 'track', 'watch', 'surveil'],
            'overhaul': ['rebuild', 'renovate', 'refurbish', 'restore']
        }
        
        self.regulation_aliases = {
            'iso': ['international standard', 'iso standard'],
            'astm': ['astm standard', 'material specification'],
            'api': ['api standard', 'petroleum standard'],
            'asme': ['asme code', 'pressure vessel code'],
            'iec': ['iec standard', 'electrical standard'],
            'ieee': ['ieee standard', 'electrical engineering standard'],
            'nfpa': ['nfpa code', 'fire code', 'safety code'],
            'osha': ['osha regulation', 'safety regulation'],
            'epa': ['epa regulation', 'environmental regulation'],
            'fda': ['fda regulation', 'food safety regulation']
        }
    
    def expand(self, request: QueryExpansionRequest) -> QueryExpansionResponse:
        """Expand a query with industrial terminology.
        
        Args:
            request: Query expansion request
            
        Returns:
            Query expansion response
            
        Raises:
            QueryExpansionException: If expansion fails
        """
        start_time = time.time()
        
        try:
            query = request.query.strip()
            
            if not query:
                raise QueryExpansionException("Query cannot be empty", query)
            
            # Determine expansion strategy
            strategy = request.strategy or EXPANSION_RELATED
            max_terms = request.max_terms or MAX_EXPANSION_TERMS
            
            # Perform expansion
            expanded_terms = self._expand_query(query, strategy, max_terms)
            
            # Build expanded query
            expanded_query = self._build_expanded_query(query, expanded_terms)
            
            expansion_time_ms = (time.time() - start_time) * 1000
            
            expansion = QueryExpansion(
                original_query=query,
                expanded_query=expanded_query,
                expanded_terms=expanded_terms,
                expansion_strategy=strategy,
                expansion_time_ms=expansion_time_ms
            )
            
            logger.info(f"Query expansion completed in {expansion_time_ms:.2f}ms, added {len(expanded_terms)} terms")
            
            return QueryExpansionResponse(
                expansion=expansion,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error expanding query: {e}")
            raise QueryExpansionException(f"Failed to expand query: {str(e)}", request.query)
    
    def _expand_query(
        self,
        query: str,
        strategy: str,
        max_terms: int
    ) -> List[ExpandedTerm]:
        """Expand query terms based on strategy.
        
        Args:
            query: Original query
            strategy: Expansion strategy
            max_terms: Maximum expansion terms
            
        Returns:
            List of expanded terms
        """
        expanded_terms = []
        query_lower = query.lower()
        words = re.findall(r'\b[a-zA-Z0-9-]+\b', query_lower)
        
        for word in words:
            # Skip common stop words
            if self._is_stop_word(word):
                continue
            
            # Apply expansion based on strategy
            if strategy == EXPANSION_SYNONYMS:
                expanded_terms.extend(self._expand_synonyms(word, words))
            elif strategy == EXPANSION_ACRONYMS:
                expanded_terms.extend(self._expand_acronyms(word, words))
            elif strategy == EXPANSION_ALIASES:
                expanded_terms.extend(self._expand_aliases(word, words))
            elif strategy == EXPANSION_RELATED:
                expanded_terms.extend(self._expand_related(word, words))
            elif strategy == EXPANSION_HIERARCHICAL:
                expanded_terms.extend(self._expand_hierarchical(word, words))
            else:
                # Default to related expansion
                expanded_terms.extend(self._expand_related(word, words))
        
        # Filter by confidence and limit
        filtered_terms = [
            term for term in expanded_terms
            if term.confidence >= MIN_EXPANSION_CONFIDENCE
        ]
        
        # Remove duplicates and sort by confidence
        unique_terms = {}
        for term in filtered_terms:
            key = term.expanded_term.lower()
            if key not in unique_terms or term.confidence > unique_terms[key].confidence:
                unique_terms[key] = term
        
        sorted_terms = sorted(unique_terms.values(), key=lambda x: x.confidence, reverse=True)
        
        return sorted_terms[:max_terms]
    
    def _expand_synonyms(self, word: str, context_words: List[str]) -> List[ExpandedTerm]:
        """Expand word with synonyms.
        
        Args:
            word: Word to expand
            context_words: Context words for disambiguation
            
        Returns:
            List of expanded terms
        """
        expanded = []
        
        # Check equipment synonyms
        if word in self.equipment_synonyms:
            for synonym in self.equipment_synonyms[word]:
                if synonym.lower() not in context_words:
                    expanded.append(ExpandedTerm(
                        original_term=word,
                        expanded_term=synonym,
                        expansion_type=EXPANSION_SYNONYMS,
                        confidence=0.8
                    ))
        
        # Check component synonyms
        if word in self.component_synonyms:
            for synonym in self.component_synonyms[word]:
                if synonym.lower() not in context_words:
                    expanded.append(ExpandedTerm(
                        original_term=word,
                        expanded_term=synonym,
                        expansion_type=EXPANSION_SYNONYMS,
                        confidence=0.75
                    ))
        
        # Check activity synonyms
        if word in self.activity_synonyms:
            for synonym in self.activity_synonyms[word]:
                if synonym.lower() not in context_words:
                    expanded.append(ExpandedTerm(
                        original_term=word,
                        expanded_term=synonym,
                        expansion_type=EXPANSION_SYNONYMS,
                        confidence=0.7
                    ))
        
        return expanded
    
    def _expand_acronyms(self, word: str, context_words: List[str]) -> List[ExpandedTerm]:
        """Expand word with acronym expansions.
        
        Args:
            word: Word to expand
            context_words: Context words for disambiguation
            
        Returns:
            List of expanded terms
        """
        expanded = []
        
        # Check if word is an acronym
        if word.lower() in self.acronym_expansions:
            for expansion in self.acronym_expansions[word.lower()]:
                if expansion.lower() not in context_words:
                    expanded.append(ExpandedTerm(
                        original_term=word,
                        expanded_term=expansion,
                        expansion_type=EXPANSION_ACRONYMS,
                        confidence=0.7
                    ))
        
        return expanded
    
    def _expand_aliases(self, word: str, context_words: List[str]) -> List[ExpandedTerm]:
        """Expand word with aliases.
        
        Args:
            word: Word to expand
            context_words: Context words for disambiguation
            
        Returns:
            List of expanded terms
        """
        expanded = []
        
        # Check regulation aliases
        if word.lower() in self.regulation_aliases:
            for alias in self.regulation_aliases[word.lower()]:
                if alias.lower() not in context_words:
                    expanded.append(ExpandedTerm(
                        original_term=word,
                        expanded_term=alias,
                        expansion_type=EXPANSION_ALIASES,
                        confidence=0.75
                    ))
        
        return expanded
    
    def _expand_related(self, word: str, context_words: List[str]) -> List[ExpandedTerm]:
        """Expand word with related terms.
        
        Args:
            word: Word to expand
            context_words: Context words for disambiguation
            
        Returns:
            List of expanded terms
        """
        expanded = []
        
        # Combine all expansion types
        expanded.extend(self._expand_synonyms(word, context_words))
        expanded.extend(self._expand_acronyms(word, context_words))
        expanded.extend(self._expand_aliases(word, context_words))
        
        # Lower confidence for related expansion
        for term in expanded:
            term.confidence *= 0.9
            term.expansion_type = EXPANSION_RELATED
        
        return expanded
    
    def _expand_hierarchical(self, word: str, context_words: List[str]) -> List[ExpandedTerm]:
        """Expand word with hierarchical terms.
        
        Args:
            word: Word to expand
            context_words: Context words for disambiguation
            
        Returns:
            List of expanded terms
        """
        expanded = []
        
        # Equipment hierarchy (general to specific)
        equipment_hierarchy = {
            'pump': ['centrifugal pump', 'positive displacement pump', 'gear pump', 'screw pump'],
            'valve': ['control valve', 'on-off valve', 'safety valve', 'relief valve'],
            'motor': ['ac motor', 'dc motor', 'servo motor', 'stepper motor']
        }
        
        if word in equipment_hierarchy:
            for specific in equipment_hierarchy[word]:
                if specific.lower() not in context_words:
                    expanded.append(ExpandedTerm(
                        original_term=word,
                        expanded_term=specific,
                        expansion_type=EXPANSION_HIERARCHICAL,
                        confidence=0.6
                    ))
        
        return expanded
    
    def _build_expanded_query(self, original_query: str, expanded_terms: List[ExpandedTerm]) -> str:
        """Build expanded query from original and expanded terms.
        
        Args:
            original_query: Original query
            expanded_terms: Expanded terms
            
        Returns:
            Expanded query string
        """
        if not expanded_terms:
            return original_query
        
        # Add expanded terms to query
        expansion_phrases = [term.expanded_term for term in expanded_terms]
        expanded_query = f"{original_query} {' '.join(expansion_phrases)}"
        
        return expanded_query
    
    def _is_stop_word(self, word: str) -> bool:
        """Check if word is a stop word.
        
        Args:
            word: Word to check
            
        Returns:
            True if stop word
        """
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
            'how', 'what', 'where', 'when', 'why', 'who', 'which', 'that',
            'this', 'these', 'those', 'it', 'its', 'they', 'them', 'their',
            'for', 'of', 'with', 'at', 'by', 'from', 'in', 'on', 'to', 'into',
            'through', 'during', 'before', 'after', 'above', 'below', 'between',
            'under', 'again', 'further', 'then', 'once', 'and', 'or', 'but', 'if',
            'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with',
            'about', 'against', 'between', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
            'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once'
        }
        
        return word.lower() in stop_words
    
    def expand_with_entities(self, query: str, entity_ids: List[str]) -> QueryExpansion:
        """Expand query using entity information from database.
        
        Args:
            query: Query to expand
            entity_ids: Entity IDs to use for expansion
            
        Returns:
            Query expansion result
        """
        # This would query the database for entity aliases and related terms
        # For now, return basic expansion
        request = QueryExpansionRequest(query=query)
        response = self.expand(request)
        return response.expansion
