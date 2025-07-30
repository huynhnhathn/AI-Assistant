import os
import logging
from typing import Dict, List, Any, Optional
import litellm
from litellm import completion

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.model = os.getenv("LITELLM_MODEL", "gpt-3.5-turbo")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "1000"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
        # Set API keys from environment
        if os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        if os.getenv("ANTHROPIC_API_KEY"):
            os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")
        
        # Configure LiteLLM
        litellm.set_verbose = False
        
        logger.info(f"LLM Service initialized with model: {self.model}")
    
    async def generate_response(
        self, 
        query: str, 
        context: List[str] = None,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """Generate response using LiteLLM"""
        try:
            # Build system prompt
            system_prompt = self._build_system_prompt(context)
            
            # Build messages
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history if available
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Keep last 10 messages
            
            # Add current query
            messages.append({"role": "user", "content": query})
            
            logger.info(f"Generating response using model: {self.model}")
            
            # Call LiteLLM
            response = completion(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            assistant_response = response.choices[0].message.content
            logger.info("Response generated successfully")
            
            return assistant_response
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            # Fallback response
            return "I apologize, but I'm having trouble generating a response right now. Please try again later."
    
    def _build_system_prompt(self, context: List[str] = None) -> str:
        """Build system prompt with context"""
        base_prompt = """You are a helpful AI assistant. You provide accurate, helpful, and concise responses to user questions.

Guidelines:
- Be helpful, harmless, and honest
- If you don't know something, say so
- Use the provided context to answer questions when relevant
- Keep responses clear and well-structured
- Be conversational but professional"""

        if context and len(context) > 0:
            context_text = "\n\n".join(context)
            base_prompt += f"""

Context information:
{context_text}

Use this context to help answer the user's question, but don't mention that you're using context unless specifically asked."""

        return base_prompt
    
    async def summarize_text(self, text: str, max_length: int = 200) -> str:
        """Summarize text content"""
        try:
            messages = [
                {
                    "role": "system", 
                    "content": f"Summarize the following text in no more than {max_length} characters. Be concise but capture the key points."
                },
                {"role": "user", "content": text}
            ]
            
            response = completion(
                model=self.model,
                messages=messages,
                max_tokens=100,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            return text[:max_length] + "..." if len(text) > max_length else text
    
    async def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"Extract up to {max_keywords} important keywords or key phrases from the following text. Return them as a comma-separated list."
                },
                {"role": "user", "content": text}
            ]
            
            response = completion(
                model=self.model,
                messages=messages,
                max_tokens=100,
                temperature=0.3
            )
            
            keywords_text = response.choices[0].message.content
            keywords = [k.strip() for k in keywords_text.split(",")]
            return keywords[:max_keywords]
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }