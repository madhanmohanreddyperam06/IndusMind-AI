"""Constants for RAG Engine module."""

# Prompt Templates
DEFAULT_SYSTEM_PROMPT = """You are an industrial knowledge intelligence assistant for IndusMind AI. 
Your role is to provide accurate, well-cited answers based on the provided context.

Guidelines:
- Answer ONLY using the provided context
- If information is insufficient, state "I could not find sufficient supporting information"
- Always cite your sources using the provided citation format
- Preserve technical terminology and entity names exactly as they appear
- Maintain document hierarchy in your responses
- Be precise and factual
- When uncertain, acknowledge it clearly"""

DEFAULT_USER_PROMPT_TEMPLATE = """Question: {question}

Context:
{context}

Instructions:
{instructions}

Provide a structured response with:
1. Direct answer
2. Supporting evidence with citations
3. Related entities and relationships
4. Confidence assessment"""

# Context Formatting
MAX_CONTEXT_TOKENS = 4000
MAX_RESPONSE_TOKENS = 2000
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9

# Confidence Thresholds
CONFIDENCE_THRESHOLD_HIGH = 0.8
CONFIDENCE_THRESHOLD_MEDIUM = 0.5
CONFIDENCE_THRESHOLD_LOW = 0.3

# Evidence Requirements
MIN_EVIDENCE_COUNT = 1
MIN_EVIDENCE_CONFIDENCE = 0.3

# Citation Format
CITATION_FORMAT = "[{doc_id}:{chunk_id}]"
CITATION_SEPARATOR = ", "

# Provider Names
PROVIDER_GEMINI = "gemini"
PROVIDER_OPENAI = "openai"
PROVIDER_OLLAMA = "ollama"
PROVIDER_MOCK = "mock"

# Streaming
STREAM_CHUNK_SIZE = 100
STREAM_DELAY_MS = 50

# Hallucination Detection
HALLUCINATION_THRESHOLD = 0.7
MIN_SOURCE_COVERAGE = 0.5

# Conversation
MAX_CONVERSATION_HISTORY = 10
MAX_CONTEXT_WINDOW = 8000
DEFAULT_SESSION_TIMEOUT = 3600  # seconds

# Response Structure
RESPONSE_SECTIONS = ["answer", "summary", "citations", "supporting_documents", 
                     "related_entities", "related_relationships", "confidence", 
                     "follow_up_questions", "statistics"]

# Error Messages
ERROR_INSUFFICIENT_EVIDENCE = "I could not find sufficient supporting information to answer this question."
ERROR_CONFLICTING_EVIDENCE = "The provided evidence contains conflicting information. Please clarify the question."
ERROR_NO_CONTEXT = "No context was provided for this question."
ERROR_PROVIDER_UNAVAILABLE = "The LLM provider is currently unavailable."
ERROR_GENERATION_FAILED = "Failed to generate response. Please try again."
