"""
Vision AI - Chat Interface
Clean minimal UI - ready for redesign.
"""
import streamlit as st
from PIL import Image
import time
import base64
from datetime import datetime
from typing import Dict, Any

from backend.chain import VisionChain
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from frontend.ui_components import (
    render_sidebar, 
    render_welcome_screen, 
    render_medicine_cards, 
    render_transparency_panel,
    render_chat_mode_selector,
    render_ambiguity_resolver
)

# Page configuration
st.set_page_config(
    page_title="Medical Vision AI",
    page_icon="💊",
    layout="wide"
)


def initialize_session_state():
    """Initialize Streamlit session state variables for medical context."""
    if "conversations" not in st.session_state:
        st.session_state.conversations = {}
    if "active_conversation_id" not in st.session_state:
        st.session_state.active_conversation_id = None
    if "chat_memory" not in st.session_state:
        st.session_state.chat_memory = InMemoryChatMessageHistory()
    if "vision_chain" not in st.session_state:
        st.session_state.vision_chain = VisionChain(st.session_state.chat_memory)
    if "last_uploaded_image_name" not in st.session_state:
        st.session_state.last_uploaded_image_name = None


def create_conversation(image: Image.Image, image_name: str, analysis: Dict[str, Any]) -> str:
    """Create a new conversation with pre-stored analysis."""
    conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    st.session_state.conversations[conversation_id] = {
        "title": image_name,
        "image": image,
        "image_name": image_name,
        "analysis": analysis,
        "messages": [],
        "created_at": datetime.now().isoformat()
    }
    
    return conversation_id


def switch_conversation(conversation_id: str):
    """Switch conversation and clear memory."""
    if conversation_id not in st.session_state.conversations:
        return
    st.session_state.active_conversation_id = conversation_id
    st.session_state.chat_memory.clear()
    
    conversation = st.session_state.conversations[conversation_id]
    for msg in conversation["messages"]:
        if isinstance(msg, HumanMessage):
            st.session_state.chat_memory.add_user_message(msg.content)
        elif isinstance(msg, AIMessage):
            st.session_state.chat_memory.add_ai_message(msg.content)


def add_message_to_conversation(role: str, content: str):
    """
    Add message to active conversation (UI storage only).
    IMPORTANT: Does NOT touch LangChain memory.
    """
    if not st.session_state.active_conversation_id:
        return
    
    if role == "human":
        message = HumanMessage(content=content)
    else:
        message = AIMessage(content=content)
    
    conversation = st.session_state.conversations[st.session_state.active_conversation_id]
    conversation["messages"].append(message)
    
    # Update title with first user message
    if role == "human" and len(conversation["messages"]) == 1:
        title_text = content[:27] + ("..." if len(content) > 27 else "")
        conversation["title"] = f"🔍 {title_text}"


def get_active_conversation() -> Dict[str, Any]:
    """Get the currently active conversation."""
    if not st.session_state.active_conversation_id:
        return None
    return st.session_state.conversations.get(st.session_state.active_conversation_id)


def main():
    """Main chat application logic."""
    initialize_session_state()
    
    # Handle conversation switching from sidebar
    if "switch_to_conversation" in st.session_state:
        switch_conversation(st.session_state.switch_to_conversation)
        del st.session_state.switch_to_conversation
    
    # Standard Header
    st.title("Medical Prescription Analyzer 🩺")
    st.caption("Structured Medical Intelligence Platform | Powered by Qubrid AI")
    st.divider()

    # Render sidebar and get model config + uploaded file
    model_config = render_sidebar()
    uploaded_file = model_config.pop("uploaded_file", None)
    chat_mode = model_config.pop("chat_mode", "Explain Prescription")
    
    # Handle image upload + Automated Analysis
    if uploaded_file is not None and st.session_state.last_uploaded_image_name != uploaded_file.name:
        image = Image.open(uploaded_file)
        with st.status("🔍 Analyzing Prescription handwriting...", expanded=True) as status:
            st.write("1. Running Vision OCR...")
            analysis = st.session_state.vision_chain.analyze_prescription(image)
            st.write("2. Normalizing medical entities...")
            st.write("3. Checking dosing schedule...")
            st.write("4. Safety audit complete.")
            status.update(label="Analysis Complete!", state="complete", expanded=False)
            
        conversation_id = create_conversation(image, uploaded_file.name, analysis)
        switch_conversation(conversation_id)
        st.session_state.last_uploaded_image_name = uploaded_file.name

    
    # Main chat area
    active_conv = get_active_conversation()
    
    if active_conv:
        # Layout: Extraction Cards on Left, Image View on Right (Col)
        col1, col2 = st.columns([2, 1])
        
        with col1:
            render_medicine_cards(active_conv["analysis"]["extraction"])
            
        with col2:
            with st.expander("🖼️ View Original Prescription", expanded=False):
                st.image(active_conv["image"], width="stretch")
            
            # Transparency Panel
            render_transparency_panel(
                active_conv["analysis"]["audit"], 
                st.session_state.vision_chain.qubrid_client.model_name
            )

        st.divider()
        
        # Ambiguity Resolver
        render_ambiguity_resolver(active_conv["analysis"]["audit"])
        
        # Display Messages
        for message in active_conv["messages"]:
            avatar = "👤" if message.type == "human" else "🤖"
            with st.chat_message("user" if message.type == "human" else "assistant", avatar=avatar):
                st.markdown(message.content)
        
        user_query = st.chat_input(f"Ask in {chat_mode} mode...")
        
        if user_query:
            add_message_to_conversation("human", user_query)
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_query)
            
            with st.chat_message("assistant", avatar="🤖"):
                message_placeholder = st.empty()
                full_response = ""
                
                try:
                    response = st.session_state.vision_chain.stream_with_mode(
                        image=active_conv["image"],
                        user_query=user_query,
                        mode=chat_mode,
                        extraction_context=active_conv["analysis"]["extraction"],
                        **model_config
                    )
                    
                    for chunk in response:
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                    add_message_to_conversation("ai", full_response)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        # Show welcome screen when no conversation is active
        render_welcome_screen()



if __name__ == "__main__":
    main()
