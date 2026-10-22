
from src.rag_pipeline import create_rag_answer
from src.memory_store import initialize_memory_db


def get_project_brief():
    """Generate a structured brief from indexed project documents."""

    question = """
    Prepare a structured project intelligence brief for ShopSphere.

    Use these sections:
    1. Project status
    2. Deadlines and milestones
    3. Blockers and risks
    4. Action items and assigned owners
    5. Pending change requests and approvals

    Rules:
    - Base project facts on the retrieved documents.
    - Mention source filenames for important findings.
    - Distinguish confirmed facts from risks or inferences.
    - Do not assume a task is incomplete just because it appears
      in an older meeting note.
    - Do not treat a requested change as an approved change.
    - If information is missing or unclear, say so.
    - Keep the brief clear and concise.
    """

    return create_rag_answer(
        question,
        top=8,
        conversation_id="proj-ai",
    )


if __name__ == "__main__":
    initialize_memory_db()

    print("\n=== ShopSphere Project Intelligence Brief ===\n")

    try:
        brief = get_project_brief()
        print(brief)
    except Exception as error:
        print(f"Error generating project brief: {error}")
