# AI Project Intelligence Assistant

An AI-powered project management assistant that uses Retrieval-Augmented Generation (RAG) to answer questions about project documents, summarize project status, identify risks, track change requests, and maintain conversation history.

## Overview

The AI Project Intelligence Assistant helps teams find relevant information from project documents and make project information easier to understand. It retrieves relevant documents from Azure AI Search and uses Azure OpenAI to generate contextual answers with source filenames.

## Features

- **Project Intelligence Brief:** Generates a summary of project status, deadlines, risks, and action items.
- **Document-Based Q&A:** Answers project-related questions using relevant project documents.
- **Source References:** Includes source filenames to help users trace project information.
- **Conversation Memory:** Stores conversation history in PostgreSQL to support follow-up questions.
- **Change Request Workflow:** Tracks change requests, approval status, and assigned owners.
- **Microsoft OneDrive Integration:** Retrieves project files using Microsoft Graph.
- **Interactive Web Interface:** Provides a user interface built with Streamlit.

## Technology Stack

- Python
- Streamlit
- Azure OpenAI
- Azure AI Search
- Microsoft Graph API
- Microsoft OneDrive
- PostgreSQL
- Retrieval-Augmented Generation (RAG)

## Project Structure

```text
AI-Project-Intelligence-Assistant/
├── data/
├── src/
│   ├── app.py
│   ├── approval_workflow.py
│   ├── graph_client.py
│   ├── ingest_documents.py
│   ├── memory_store.py
│   ├── project_intelligence.py
│   ├── rag_pipeline.py
│   └── search_client.py
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── test_azure_openai.py
```

## Prerequisites

- Python 3.12 or a compatible version
- Azure OpenAI resource and deployment
- Azure AI Search service
- Microsoft Graph application credentials, if using OneDrive integration
- PostgreSQL database

## Setup and Installation

1. Clone or download this repository.
2. Open a terminal in the project directory.
3. Create and activate a virtual environment.

   ```bash
   python -m venv .venv
   ```

   Windows Command Prompt:

   ```cmd
   .venv\Scripts\activate
   ```

4. Install dependencies.

   ```bash
   pip install -r requirements.txt
   ```

5. Create a local `.env` file using `.env.example` as a template.
6. Add your own Azure, Microsoft Graph, and PostgreSQL configuration values to `.env`.
7. Ensure the required Azure services, database, and access permissions are configured.

## Run the Application

From the project root, run:

```bash
streamlit run src/app.py
```

Open the local URL shown in the terminal, usually `http://localhost:8501`.


## Project Status

This project currently includes document-based question answering, project brief generation, PostgreSQL conversation memory, OneDrive integration, and a change request approval workflow.

## Future Improvements

- Add automated tests.
- Add authentication and role-based access control.
- Improve approval workflow permissions and audit history.
- Deploy the application to a cloud hosting platform.
- Add monitoring, logging, and error handling improvements.


