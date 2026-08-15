"""
Celery task definitions.
This task performs the real NLP pipeline, generates an embedding,
and updates the database.
"""

from app.worker.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.message import Message
from app.models.analysis_result import AnalysisResult, AnalysisStatus
from app.services.nlp_service import run_full_analysis
from app.services.embedding_service import store_embedding


@celery_app.task(name="process_conversation")
def process_conversation(conversation_id: str):
    """
    Background job triggered right after a conversation is ingested.

    Steps:
    1. Mark status as 'processing'
    2. Fetch and concatenate all messages in the conversation
    3. Run NLP (summary, sentiment, entities, key phrases)
    4. Generate and store an embedding vector in Qdrant (for semantic search)
    5. Save results into the insights JSONB column, mark 'completed'
    6. On any error, mark 'failed'
    """
    db = SessionLocal()

    try:
        analysis = (
            db.query(AnalysisResult)
            .filter(AnalysisResult.conversation_id == conversation_id)
            .first()
        )

        if not analysis:
            print(f"[Celery] No AnalysisResult found for {conversation_id}")
            return

        # Step 1: mark as processing
        analysis.status = AnalysisStatus.processing
        db.commit()

        # Step 2: fetch and concatenate the conversation's messages
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.asc())
            .all()
        )
        full_text = " ".join(m.text for m in messages)

        if not full_text.strip():
            raise ValueError("Conversation has no message text to analyze")

        # Step 3: run NLP
        insights = run_full_analysis(full_text)

        # Step 4: generate + store embedding for semantic search
        store_embedding(conversation_id, full_text)

        # Step 5: save results, mark completed
        analysis.insights = insights
        analysis.status = AnalysisStatus.completed
        db.commit()

        print(f"[Celery] Completed analysis for {conversation_id}: {insights}")
        return {"conversation_id": conversation_id, "status": "completed"}

    except Exception as e:
        db.rollback()
        analysis = (
            db.query(AnalysisResult)
            .filter(AnalysisResult.conversation_id == conversation_id)
            .first()
        )
        if analysis:
            analysis.status = AnalysisStatus.failed
            db.commit()

        print(f"[Celery] FAILED analysis for {conversation_id}: {e}")
        return {"conversation_id": conversation_id, "status": "failed", "error": str(e)}

    finally:
        db.close()