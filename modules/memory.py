"""
Conversational Memory Manager — Context-Aware Dialogue (Simplified)
=================================================================
Implements memory management for multi-turn conversations without deprecated LangChain memory classes.
Maintains context across questions to enable natural follow-up queries.
"""

import sys
import os
from typing import List, Dict, Any, Optional, Tuple
import json
import time
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.config import LLM_MODEL

class SimpleConversationBuffer:
    """Simple conversation buffer replacement for deprecated LangChain memory."""
    
    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self.messages: List[Dict] = []
    
    def add_message(self, role: str, content: str):
        """Add a message to the buffer."""
        self.messages.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only recent messages  
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_messages(self) -> List[Dict]:
        """Get all messages."""
        return self.messages
    
    def clear(self):
        """Clear all messages."""
        self.messages = []

class ConversationalMemoryManager:
    """
    Simplified conversational memory manager with context awareness.
    """
    
    def __init__(self, 
                 max_messages: int = 20,
                 session_timeout: int = 3600):
        """
        Initialize memory manager.
        
        Args:
            max_messages: Maximum messages to keep per session
            session_timeout: Session timeout in seconds
        """
        self.max_messages = max_messages
        self.session_timeout = session_timeout
        
        # Session storage
        self.sessions: Dict[str, Dict] = {}
    
    def get_session_id(self, user_identifier: str = "default") -> str:
        """Generate or retrieve session ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H")
        return f"{user_identifier}_{timestamp}"
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions."""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            last_activity = session_data.get('last_activity')
            if last_activity:
                time_diff = current_time - last_activity
                if time_diff.total_seconds() > self.session_timeout:
                    expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
    
    def add_exchange(self, 
                    question: str, 
                    answer: str, 
                    session_id: Optional[str] = None,
                    context_docs: Optional[List] = None,
                    metadata: Optional[Dict] = None) -> str:
        """
        Add a question-answer exchange to memory.
        """
        if not session_id:
            session_id = self.get_session_id()
        
        self._cleanup_expired_sessions()
        
        # Initialize session if new
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'buffer': SimpleConversationBuffer(self.max_messages),
                'created_at': datetime.now(),
                'last_activity': datetime.now(),
                'exchange_count': 0,
                'topics': set(),
                'context_history': []
            }
        
        # Update session
        session = self.sessions[session_id]
        session['last_activity'] = datetime.now()
        session['exchange_count'] += 1
        
        # Add to buffer
        session['buffer'].add_message('human', question)
        session['buffer'].add_message('assistant', answer)
        
        # Extract topics from question
        topics = self._extract_topics(question)
        session['topics'].update(topics)
        
        # Store context information
        context_info = {
            'question': question,
            'answer': answer[:500] + "..." if len(answer) > 500 else answer,
            'timestamp': datetime.now().isoformat(),
            'doc_sources': [doc.metadata.get('source', 'unknown') for doc in (context_docs or [])],
            'metadata': metadata or {}
        }
        session['context_history'].append(context_info)
        
        # Keep only last 10 context entries
        if len(session['context_history']) > 10:
            session['context_history'] = session['context_history'][-10:]
        
        return session_id
    
    def _extract_topics(self, text: str) -> set:
        """Simple topic extraction from text."""
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 
                     'what', 'how', 'when', 'where', 'why', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
                     'has', 'had', 'do', 'does', 'did', 'can', 'could', 'should', 'would', 'will'}
        
        words = text.lower().split()
        topics = {word.strip('.,!?;:') for word in words 
                 if len(word) > 3 and word.lower() not in stop_words}
        
        return topics
    
    def get_conversation_context(self, 
                               session_id: str, 
                               include_sources: bool = True) -> Dict[str, Any]:
        """Get conversation context for a session."""
        if session_id not in self.sessions:
            return {
                'has_context': False,
                'message': 'No previous conversation found.'
            }
        
        session = self.sessions[session_id]
        messages = session['buffer'].get_messages()
        
        context = {
            'has_context': len(messages) > 0,
            'exchange_count': session['exchange_count'],
            'session_duration': str(datetime.now() - session['created_at']),
            'topics_discussed': list(session['topics']),
            'recent_messages': messages[-4:] if messages else [],  # Last 2 exchanges
        }
        
        if include_sources:
            recent_sources = set()
            for ctx in session['context_history'][-3:]:  # Last 3 exchanges
                recent_sources.update(ctx.get('doc_sources', []))
            context['recent_sources'] = list(recent_sources)
        
        return context
    
    def enhance_query_with_context(self, 
                                  query: str, 
                                  session_id: str) -> Tuple[str, Dict]:
        """Enhance a query with conversational context."""
        context = self.get_conversation_context(session_id)
        
        if not context['has_context']:
            return query, context
        
        # Check if query contains context-dependent pronouns or references
        context_indicators = ['that', 'this', 'it', 'they', 'them', 'summarize', 'explain more', 'tell me more', 'what about']
        
        query_lower = query.lower()
        needs_context = any(indicator in query_lower for indicator in context_indicators)
        
        if needs_context and context['recent_messages']:
            # Build context-enhanced query
            recent_topics = context['topics_discussed'][-5:]  # Last 5 topics
            
            enhanced_query = f"""
Context from previous conversation:
- Topics discussed: {', '.join(recent_topics)}
- Recent exchange: {context['recent_messages'][-2:]}

Current question: {query}

Please answer considering the conversation context above.
"""
            
            context['enhanced'] = True
            context['enhancement_reason'] = 'Context-dependent query detected'
            
            return enhanced_query, context
        
        return query, context
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the conversation session."""
        if session_id not in self.sessions:
            return {'exists': False}
        
        session = self.sessions[session_id]
        
        return {
            'exists': True,
            'session_id': session_id,
            'created_at': session['created_at'].isoformat(),
            'last_activity': session['last_activity'].isoformat(),
            'duration': str(datetime.now() - session['created_at']),
            'exchange_count': session['exchange_count'],
            'topics_count': len(session['topics']),
            'main_topics': list(session['topics'])[:10],  # Top 10 topics
            'message_count': len(session['buffer'].get_messages())
        }
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a specific session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def list_active_sessions(self) -> List[Dict]:
        """List all active sessions."""
        self._cleanup_expired_sessions()
        
        sessions = []
        for session_id, session_data in self.sessions.items():
            sessions.append({
                'session_id': session_id,
                'last_activity': session_data['last_activity'].isoformat(),
                'exchange_count': session_data['exchange_count'],
                'topics_count': len(session_data['topics'])
            })
        
        return sorted(sessions, key=lambda x: x['last_activity'], reverse=True)

# Global memory manager instance
memory_manager = ConversationalMemoryManager()

def get_memory_manager() -> ConversationalMemoryManager:
    """Get the global memory manager instance."""
    return memory_manager