"""Prompt builder for RAG Engine."""

from typing import Dict, Any, Optional, List
from app.core.logging import setup_logging
from app.modules.rag_engine.constants import (
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_USER_PROMPT_TEMPLATE
)
from app.modules.rag_engine.exceptions import PromptBuildException
from .context_formatter import ContextFormatter

logger = setup_logging()


class PromptBuilder:
    """Build structured prompts for LLM generation."""
    
    def __init__(
        self,
        system_prompt: Optional[str] = None,
        user_prompt_template: Optional[str] = None
    ):
        """Initialize prompt builder.
        
        Args:
            system_prompt: Custom system prompt
            user_prompt_template: Custom user prompt template
        """
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        self.user_prompt_template = user_prompt_template or DEFAULT_USER_PROMPT_TEMPLATE
        self.context_formatter = ContextFormatter()
    
    def build_prompt(
        self,
        question: str,
        context_package: Dict[str, Any],
        instructions: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Build a complete prompt for LLM generation.
        
        Args:
            question: User question
            context_package: Context package from hybrid retrieval
            instructions: Additional instructions
            conversation_history: Previous conversation messages
            
        Returns:
            Complete prompt string
        """
        try:
            # Format context
            formatted_context = self.context_formatter.format_context(context_package)
            
            # Build instructions
            if not instructions:
                instructions = self._build_default_instructions(context_package)
            
            # Add conversation history if provided
            history_section = self._format_conversation_history(conversation_history)
            
            # Build user prompt
            user_prompt = self.user_prompt_template.format(
                question=question,
                context=formatted_context,
                instructions=instructions
            )
            
            # Combine with history
            if history_section:
                user_prompt = f"{history_section}\n\n{user_prompt}"
            
            # Combine system and user prompts
            full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
            
            logger.info(f"Built prompt with {self.context_formatter.estimate_tokens(full_prompt)} estimated tokens")
            
            return full_prompt
            
        except Exception as e:
            logger.error(f"Prompt building failed: {e}")
            raise PromptBuildException(f"Failed to build prompt: {str(e)}")
    
    def _build_default_instructions(self, context_package: Dict[str, Any]) -> str:
        """Build default instructions based on context.
        
        Args:
            context_package: Context package
            
        Returns:
            Instructions string
        """
        instructions = [
            "Answer the question using ONLY the provided context.",
            "If the context doesn't contain sufficient information, state that clearly.",
            "Include citations in the format [document_id:chunk_id] for each fact.",
            "Preserve technical terminology exactly as it appears in the context.",
            "Be precise and factual in your response."
        ]
        
        # Add specific instructions based on context
        if context_package.get('entities'):
            instructions.append("Reference the related entities when relevant to the answer.")
        
        if context_package.get('relationships'):
            instructions.append("Consider the relationships between entities when answering.")
        
        if context_package.get('graph_context'):
            instructions.append("Use the knowledge graph context to understand entity connections.")
        
        return "\n".join(instructions)
    
    def _format_conversation_history(self, history: Optional[List[Dict[str, str]]]) -> Optional[str]:
        """Format conversation history for prompt.
        
        Args:
            history: List of conversation messages
            
        Returns:
            Formatted history string or None
        """
        if not history:
            return None
        
        formatted = ["Conversation History:"]
        
        for msg in history[-5:]:  # Limit to last 5 messages
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            
            if role == 'user':
                formatted.append(f"  User: {content}")
            elif role == 'assistant':
                formatted.append(f"  Assistant: {content}")
        
        return "\n".join(formatted)
    
    def build_summarization_prompt(
        self,
        text: str,
        max_length: int = 200,
        style: str = "concise"
    ) -> str:
        """Build a prompt for text summarization.
        
        Args:
            text: Text to summarize
            max_length: Maximum summary length
            style: Summary style
            
        Returns:
            Summarization prompt
        """
        style_instructions = {
            "concise": "Provide a very brief summary in 2-3 sentences.",
            "detailed": "Provide a comprehensive summary covering all key points.",
            "bullet": "Provide a summary in bullet points.",
            "executive": "Provide an executive summary suitable for business stakeholders."
        }
        
        instruction = style_instructions.get(style, style_instructions["concise"])
        
        prompt = f"""{self.system_prompt}

Summarize the following text. {instruction}
Maximum length: {max_length} characters.

Text:
{text}

Summary:"""
        
        return prompt
    
    def build_structured_output_prompt(
        self,
        question: str,
        context_package: Dict[str, Any],
        schema_definition: Dict[str, Any]
    ) -> str:
        """Build a prompt for structured output generation.
        
        Args:
            question: User question
            context_package: Context package
            schema_definition: JSON schema for output
            
        Returns:
            Structured output prompt
        """
        formatted_context = self.context_formatter.format_context(context_package)
        
        prompt = f"""{self.system_prompt}

Question: {question}

Context:
{formatted_context}

Generate a response following this JSON schema:
{schema_definition}

Provide ONLY the JSON response, no additional text:"""
        
        return prompt
    
    def build_conversation_prompt(
        self,
        question: str,
        context_package: Dict[str, Any],
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Build a prompt for multi-turn conversation.
        
        Args:
            question: Current question
            context_package: Context package
            conversation_history: Previous conversation messages
            
        Returns:
            Conversation prompt
        """
        return self.build_prompt(
            question=question,
            context_package=context_package,
            conversation_history=conversation_history
        )
    
    def get_prompt_statistics(self, prompt: str) -> Dict[str, Any]:
        """Get statistics about a prompt.
        
        Args:
            prompt: Prompt string
            
        Returns:
            Prompt statistics
        """
        return {
            'length': len(prompt),
            'estimated_tokens': self.context_formatter.estimate_tokens(prompt),
            'line_count': len(prompt.split('\n')),
            'word_count': len(prompt.split())
        }
    
    def update_system_prompt(self, system_prompt: str) -> None:
        """Update the system prompt.
        
        Args:
            system_prompt: New system prompt
        """
        self.system_prompt = system_prompt
        logger.info("Updated system prompt")
    
    def update_user_prompt_template(self, template: str) -> None:
        """Update the user prompt template.
        
        Args:
            template: New user prompt template
        """
        self.user_prompt_template = template
        logger.info("Updated user prompt template")
