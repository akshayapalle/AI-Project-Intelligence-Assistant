import os

from dotenv import load_dotenv
from openai import AzureOpenAI

from src.search_client import search_documents
from src.memory_store import (
    initialize_memory_db,
    get_recent_messages,
    save_exchange,
)

load_dotenv()


def create_rag_answer(question, top=5, conversation_id="project-default"):
    """Answer project questions using RAG and PostgreSQL chat memory."""

    endpoint = os.getenv("AOAI_CHAT_ENDPOINT")
    key = os.getenv("AOAI_CHAT_KEY")
    deployment = os.getenv("AOAI_CHAT_DEPLOYMENT")
    api_version = os.getenv("AOAI_API_VERSION_GPT")

    if not all([endpoint, key, deployment, api_version]):
        raise ValueError(
            "Check the Azure OpenAI settings in your .env file."
        )

    # Retrieve relevant project documents.
    results = search_documents(question, top=top)

    context_parts = []

    for result in results:
        context_parts.append(
            f"Source: {result.get('source', 'Unknown')}\n"
            f"Title: {result.get('title', 'Untitled')}\n"
            f"Content:\n{result.get('content', '')}"
        )

    context = "\n\n---\n\n".join(context_parts)

    # Retrieve previous messages from PostgreSQL.
    history = get_recent_messages(conversation_id, limit=10)

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=key,
        api_version=api_version,
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI Project Intelligence Assistant. "
                "Answer project questions using the supplied project "
                "documents and relevant conversation history. "
                "Use conversation history to understand follow-up "
                "questions, but use project documents as evidence "
                "for project facts. Do not invent facts. "
                "Distinguish dated updates from older records. "
                "Do not call something the latest unless the evidence "
                "supports that conclusion. "
                "Mention relevant source filenames. "
                "If evidence is insufficient, say so. "

                "Clearly distinguish between requested, proposed, "
                "approved, in-progress, and completed work. "
                "Approval status and implementation progress are "
                "separate facts. A report of development activity "
                "does not by itself prove formal approval. "
                "Do not infer approval, authorization, or completion "
                "unless the documents support it. "

                "Review relevant dated records and report conflicting "
                "evidence accurately. If one record says approval is "
                "pending or unconfirmed while another reports "
                "development activity, explicitly flag the discrepancy. "
                "Explain what each record establishes and what remains "
                "uncertain. Do not hide or silently reconcile conflicting "
                "records. Include the relevant dates and source filenames."
            ),
        }
    ]

    messages.extend(history)

    if context_parts:
        user_content = (
            f"Relevant project documents:\n{context}\n\n"
            f"Current question: {question}"
        )
    else:
        user_content = (
            "No relevant project documents were found. Do not invent "
            "project facts. If this is a follow-up question, use the "
            "available conversation history only where it supports "
            "the answer.\n\n"
            f"Current question: {question}"
        )

    messages.append(
        {
            "role": "user",
            "content": user_content,
        }
    )

    response = client.chat.completions.create(
        model=deployment,
        messages=messages,
        temperature=0.2,
        max_tokens=700,
    )

    answer = (
        response.choices[0].message.content
        or "The model returned an empty answer."
    )

    # Save the question and answer to PostgreSQL.
    save_exchange(conversation_id, question, answer)

    return answer


if __name__ == "__main__":
    try:
        initialize_memory_db()

        print("\n=== AI Project Intelligence Assistant ===")
        print("Conversation history is saved in PostgreSQL.")
        print("Type 'exit' to stop.\n")

        conversation_id = input(
            "Conversation ID (press Enter for 'project-default'): "
        ).strip()

        if not conversation_id:
            conversation_id = "project-default"

        print(f"\nContinuing conversation: {conversation_id}")
        print("Type 'exit' whenever you want to stop.\n")

        while True:
            question = input("You: ").strip()

            if question.lower() in ["exit", "quit"]:
                print("Assistant: Goodbye!")
                break

            if not question:
                continue

            try:
                answer = create_rag_answer(
                    question,
                    conversation_id=conversation_id,
                )
                print(f"\nAssistant: {answer}\n")

            except Exception as error:
                print(f"\nError: {error}\n")

    except Exception as error:
        print(f"\nStartup error: {error}")