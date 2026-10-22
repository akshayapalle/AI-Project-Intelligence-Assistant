
import os

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient

from azure.search.documents import SearchClient
from src.ingest_documents import load_dataset

from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
)

load_dotenv()


def create_search_index():
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    api_key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv(
        "AZURE_SEARCH_INDEX_NAME",
        "project-documents"
    )

    if not endpoint or not api_key:
        raise ValueError(
            "AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY "
            "must be configured in .env"
        )

    client = SearchIndexClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(api_key),
    )

    fields = [
        SimpleField(
            name="id",
            type=SearchFieldDataType.String,
            key=True,
        ),
        SearchableField(
            name="title",
            type=SearchFieldDataType.String,
        ),
        SearchableField(
            name="content",
            type=SearchFieldDataType.String,
        ),
        SimpleField(
            name="source",
            type=SearchFieldDataType.String,
            filterable=True,
        ),
    ]

    index = SearchIndex(
        name=index_name,
        fields=fields,
    )

    result = client.create_or_update_index(index)

    print(f"Search index '{result.name}' is ready.")


def upload_documents():
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    api_key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv(
        "AZURE_SEARCH_INDEX_NAME",
        "project-documents",
    )

    if not endpoint or not api_key:
        raise ValueError(
            "AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY "
            "must be configured in .env"
        )

    client = SearchClient(
        endpoint=endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(api_key),
    )

    documents = load_dataset()

    if not documents:
        print("No documents to upload.")
        return

    results = client.merge_or_upload_documents(documents=documents)
    succeeded = sum(1 for result in results if result.succeeded)
    failed = len(results) - succeeded

    print(f"\nDocuments processed: {len(results)}")
    print(f"Successfully uploaded: {succeeded}")
    print(f"Failed: {failed}")

    for result in results:
        if not result.succeeded:
            print(f"Failed document ID: {result.key}")
            print(f"Error: {result.error_message}")



def search_documents(query, top=3):
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    api_key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv(
        "AZURE_SEARCH_INDEX_NAME",
        "project-documents",
    )

    if not endpoint or not api_key:
        raise ValueError(
            "AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY "
            "must be configured in .env"
        )

    client = SearchClient(
        endpoint=endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(api_key),
    )

    results = client.search(
        search_text=query,
        top=top,
        select=["title", "source", "content"],
    )

    documents = []

    for result in results:
        documents.append(dict(result))

    return documents




if __name__ == "__main__":
    upload_documents()