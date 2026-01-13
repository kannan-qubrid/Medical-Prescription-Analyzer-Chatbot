"""
LangChain-based vision chain for image conversations.
Uses LangChain memory for conversation history management.
"""
import json
from typing import Iterator, Dict, Any, List
from PIL import Image
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from backend.qubrid_client import QubridVisionLLM
from backend.prompt import get_step_prompt, get_mode_prompt, GLOBAL_DISCLAIMER
from backend.utils import prepare_image_for_api


class VisionChain:
    """
    Evolved Vision chain for structured medical prescription analysis.
    
    Responsibilities:
    - Multi-step reasoning (OCR -> Normalize -> Audit)
    - Mode-based chat streaming
    - Structured JSON extraction
    """
    
    def __init__(self, memory: InMemoryChatMessageHistory):
        """
        Initialize the vision chain.
        """
        self.qubrid_client = QubridVisionLLM()
        self.memory = memory
    
    def analyze_prescription(self, image: Image.Image) -> Dict[str, Any]:
        """
        Execute the 4-step medical reasoning pipeline.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dict containing extraction results, ambiguities, and confidence.
        """
        image_data = prepare_image_for_api(image)
        
        # STEP 1: RAW OCR
        raw_ocr = self._call_non_streaming(
            prompt=get_step_prompt("ocr"),
            image_url=image_data,
            user_query="Please extract all text from this prescription."
        )
        
        # STEP 2: NORMALIZATION
        normalization_json_str = self._call_non_streaming(
            prompt=get_step_prompt("normalize"),
            user_query=f"Convert this OCR text into the medical JSON schema:\n\n{raw_ocr}"
        )
        
        try:
            extraction = json.loads(self._clean_json_response(normalization_json_str))
        except:
            extraction = {"medicines": [], "overall_confidence": 0}

        # STEP 3 & 4: AUDIT (Ambiguity & Safety)
        audit_json_str = self._call_non_streaming(
            prompt=get_step_prompt("audit"),
            user_query=f"Audit this extracted data for safety and ambiguity:\n\n{json.dumps(extraction)}"
        )
        
        try:
            audit = json.loads(self._clean_json_response(audit_json_str))
        except:
            audit = {"ambiguities": [], "safety_flags": [], "is_safe_to_display": False}
            
        return {
            "extraction": extraction,
            "audit": audit,
            "raw_ocr": raw_ocr
        }

    def stream_with_mode(
        self,
        image: Image.Image,
        user_query: str,
        mode: str,
        extraction_context: Dict[str, Any],
        **model_params
    ) -> Iterator[str]:
        """
        Stream response based on specific chat mode and extraction context.
        """
        system_prompt = get_mode_prompt(mode)
        
        # Inject extraction context into the conversation as a hidden system clarification
        context_msg = f"Context: The following verified data was extracted from the prescription: {json.dumps(extraction_context)}"
        
        messages = [
            {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
            {"role": "system", "content": [{"type": "text", "text": context_msg}]}
        ]
        
        # Add history
        for msg in self.memory.messages:
            messages.append(self._format_message_for_api(msg))
            
        # Add current query with image
        image_data = prepare_image_for_api(image)
        messages.append({
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_data}},
                {"type": "text", "text": user_query}
            ]
        })
        
        # Update memory
        self.memory.add_user_message(user_query)
        
        full_response = ""
        for chunk in self.qubrid_client.stream(messages=messages, **model_params):
            full_response += chunk
            yield chunk
            
        # Append disclaimer
        yield GLOBAL_DISCLAIMER
        self.memory.add_ai_message(full_response + GLOBAL_DISCLAIMER)

    def _call_non_streaming(self, prompt: str, user_query: str, image_url: str = None) -> str:
        """Helper for internal reasoning steps."""
        contents = [{"type": "text", "text": prompt}]
        
        user_content = []
        if image_url:
            user_content.append({"type": "image_url", "image_url": {"url": image_url}})
        user_content.append({"type": "text", "text": user_query})
        
        messages = [
            {"role": "system", "content": contents},
            {"role": "user", "content": user_content}
        ]
        
        response = ""
        for chunk in self.qubrid_client.stream(messages=messages, temperature=0.1):
            response += chunk
        return response

    def _clean_json_response(self, text: str) -> str:
        """Remove markdown artifacts from JSON responses."""
        return text.strip().replace("```json", "").replace("```", "")

    def _format_message_for_api(self, message) -> Dict[str, Any]:
        role = "system" if isinstance(message, SystemMessage) else \
               "user" if isinstance(message, HumanMessage) else "assistant"
        return {
            "role": role,
            "content": [{"type": "text", "text": message.content}]
        }

    def clear_memory(self):
        self.memory.clear()