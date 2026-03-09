
import sys
import os
import uuid

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.healing import smart_query
from modules.vector_db import load_vector_db
from modules.logger import setup_logger
from modules.memory import get_memory_manager

def main():
    logger, log_path = setup_logger()
    logger.info("--- Enhanced Self-Healing RAG System Started ---")
    print(f"🚀 Enhanced Self-Healing RAG with Memory & Evaluation")
    print(f"📝 Logs: {log_path}")
    print(f"🧠 Features: Semantic Chunking | Conversational Memory | RAGAS Evaluation")
    
    # Initialize memory manager
    memory_manager = get_memory_manager()
    session_id = memory_manager.get_session_id()
    print(f"🆔 Session ID: {session_id}")
    
    # Initial check (optional, smart_query handles it, but good for startup)
    vector_store = load_vector_db()
    if not vector_store:
        logger.warning("System Startup: VectorDB not found. It will be created on first query if needed.")
        print("⚠️  Vector database not found - will be created automatically when needed")
    else:
        try:
            count = vector_store._collection.count()
            print(f"📚 Vector database loaded: {count} document chunks available")
            logger.info(f"System Startup: VectorDB loaded with {count} chunks")
        except:
            print("📚 Vector database loaded")

    print("\n" + "="*60)
    print("🎯 Ask questions about your documents")
    print("💡 Follow-up questions use conversation context automatically")
    print("🔍 System provides confidence scores for all answers")
    print("="*60 + "\n")

    while True:
        try:
            query = input("💬 Your question (or 'quit'): ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                logger.info("User requested exit.")
                break
            
            if not query:
                continue
            
            print("\n🤔 Processing your question...")
            
            # Get enhanced response with all metadata
            response = smart_query(query, logger=logger, session_id=session_id)
            
            # Handle different response formats (for backward compatibility)
            if isinstance(response, dict):
                answer = response.get('answer', str(response))
                evaluation = response.get('evaluation')
                sources = response.get('sources', [])
                healing_triggered = response.get('healing_triggered', False)
                rewrite_triggered = response.get('rewrite_triggered', False)
                context_enhanced = response.get('context_enhanced', False)
                
                # Display answer
                print(f"\n📄 ANSWER:")
                print("-" * 40)
                try:
                    print(answer)
                except UnicodeEncodeError:
                    print(answer.encode('utf-8', errors='ignore').decode('utf-8'))
                
                # Display confidence score if available
                if evaluation and evaluation.get('overall_confidence') is not None:
                    from modules.ragas_eval import get_ragas_evaluator
                    evaluator = get_ragas_evaluator()
                    confidence_info = evaluator.get_confidence_category(evaluation['overall_confidence'])
                    
                    confidence = evaluation['overall_confidence']
                    category = confidence_info['category']
                    description = confidence_info['description']
                    
                    print(f"\n🎯 CONFIDENCE: {confidence:.1%} ({category})")
                    print(f"   {description}")
                    
                    # Show detailed scores if available
                    if evaluation.get('scores'):
                        print(f"\n📊 DETAILED SCORES:")
                        for metric, score in evaluation['scores'].items():
                            metric_name = metric.replace('_', ' ').title()
                            print(f"   • {metric_name}: {score:.1%}")
                
                # Show agent activity indicators
                activity_indicators = []
                if context_enhanced:
                    activity_indicators.append("🧠 Memory Context")
                if healing_triggered:
                    activity_indicators.append("🩺 Self-Healing")
                if rewrite_triggered:
                    activity_indicators.append("🔄 Query Rewriting")
                
                if activity_indicators:
                    print(f"\n🤖 AGENT ACTIVITY: {' | '.join(activity_indicators)}")
                
                # Show sources if available  
                if sources:
                    print(f"\n📚 SOURCES ({len(sources)}):")
                    for i, source in enumerate(sources[:3], 1):  # Show max 3 sources
                        source_name = os.path.basename(source.get('source', 'unknown'))
                        chunking_method = source.get('chunking_method', 'unknown')
                        print(f"   {i}. {source_name}")
                        if chunking_method == 'semantic':
                            print(f"      📝 Semantic chunk | Preview: {source.get('content_preview', '')[:100]}...")
                        else:
                            print(f"      📝 Character chunk | Preview: {source.get('content_preview', '')[:100]}...")
                
                # Show session info briefly
                statistics = response.get('statistics', {})
                if statistics:
                    docs_retrieved = statistics.get('docs_retrieved', 0)
                    docs_relevant = statistics.get('docs_relevant', 0)
                    if docs_retrieved > 0:
                        relevance_rate = (docs_relevant / docs_retrieved) * 100
                        print(f"\n📈 RETRIEVAL: {docs_relevant}/{docs_retrieved} chunks relevant ({relevance_rate:.0f}%)")
            
            else:
                # Backward compatibility: plain string response
                print(f"\n📄 ANSWER:")
                print("-" * 40)
                try:
                    print(response)
                except UnicodeEncodeError:
                    print(response.encode('utf-8', errors='ignore').decode('utf-8'))
            
            print("\n" + "="*60 + "\n")
            
        except KeyboardInterrupt:
            print(f"\n\n👋 Session ended. Goodbye!")
            logger.info("User interrupted with Ctrl+C")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Main loop error: {e}")
            print("Please try another question.\n")

    # Show session summary
    try:
        session_summary = memory_manager.get_session_summary(session_id)
        if session_summary.get('exists', False):
            exchange_count = session_summary.get('exchange_count', 0)
            duration = session_summary.get('duration', 'unknown')
            print(f"\n📊 SESSION SUMMARY:")
            print(f"   Questions answered: {exchange_count}")
            print(f"   Session duration: {duration}")
            print(f"   Session ID: {session_id}")
    except Exception as e:
        logger.warning(f"Could not display session summary: {e}")

if __name__ == "__main__":
    main()
