# AI Assistant for Salesforce Documentation

## 1. Overview

This project implements a Retrieval-Augmented Generation (RAG) system designed to function as an intelligent assistant for Salesforce documentation. Users can ask questions in natural language, and the system retrieves relevant information from a pre-processed knowledge base of Salesforce help articles to generate accurate, context-aware answers.

The core objective is to provide a reliable and efficient way for users to find answers to their Salesforce-related questions, complete with source references to the original documentation. This approach aims to enhance user self-service capabilities, reduce the time spent searching for information, and improve the overall understanding of Salesforce features.

The system is architected as a web service, comprising a backend API built with FastAPI to handle the AI logic and a frontend user interface developed with Streamlit for interaction. The entire application is containerized using Docker, ensuring consistency across different environments and readiness for deployment.

## 2. Features

* **Natural Language Question Answering:** Accepts user queries in conversational language.
* **Contextualized and Referenced Answers:** Generates answers based on specific content retrieved from the Salesforce documentation. Each answer is accompanied by URLs to the source documents, allowing users to verify information and explore topics in more depth.
* **Confidence Scoring:** Provides a confidence score with each answer, derived from the language model's generation probabilities (logprobs). This helps users assess the reliability of the provided information.
* **Robust API Backend:** The AI functionalities are exposed via a RESTful API built with FastAPI, facilitating potential integrations with other systems.
* **Interactive Web Interface:** A Streamlit application offers an intuitive and user-friendly interface for querying the AI assistant.

## 3. Architecture and Technical Stack

The system employs a Retrieval-Augmented Generation (RAG) architecture:

1.  **User Interaction (Frontend):** The user submits a question through the Streamlit web interface.
2.  **API Request (Frontend to Backend):** The Streamlit application sends the user's question to the FastAPI backend API.
3.  **Query Embedding & Retrieval (Backend):**
    * The backend embeds the user's question into a high-dimensional vector using a Sentence Transformer model.
    * This query vector is then used to perform a similarity search against a pre-built FAISS index of Salesforce documentation chunks. The most semantically similar document chunks are retrieved.
4.  **Context Augmentation (Backend):** The retrieved text chunks (context) are combined with the original user question to form a comprehensive prompt for the language model.
5.  **Answer Generation (Backend):** The augmented prompt is sent to the OpenAI GPT-3.5 Turbo model. The model is instructed to generate an answer based *solely* on the provided context, minimizing hallucinations and ensuring relevance.
6.  **Response Formulation (Backend to Frontend):** The generated answer, along with source references and a confidence score, is packaged and returned to the Streamlit frontend for display to the user.

### Technology Choices and Justifications

| Component                | Technology Used                          | Justification                                                                                                                                                                                                                                                           |
| :----------------------- | :--------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Backend Framework** | **FastAPI** | Selected for its high performance (built on Starlette and Pydantic), asynchronous support crucial for I/O-bound operations like API calls, automatic data validation, and interactive API documentation (Swagger UI/OpenAPI). This makes it ideal for production-grade AI services. |
| **Frontend Framework** | **Streamlit** | Chosen for its simplicity and speed in developing interactive web applications for machine learning and data science projects. It allows for rapid prototyping and deployment of user-facing AI tools using pure Python.                                                    |
| **Embedding Model** | **SentenceTransformers (`all-MiniLM-L6-v2`)** | This model offers an excellent trade-off between embedding quality (semantic understanding) and computational efficiency. It is relatively lightweight, making it suitable for deployment in CPU-based containerized environments without sacrificing retrieval performance significantly. |
| **Vector Store & Search**| **FAISS (Facebook AI Similarity Search)**| Utilized for its highly optimized algorithms for efficient similarity search and clustering of dense vectors. As an in-memory library, it provides very fast lookups and simplifies the architecture by avoiding the need for a separate vector database server for this project's scale. |
| **Language Model (LLM)** | **OpenAI GPT-3.5 Turbo (via API)** | Leveraged for its advanced natural language understanding, instruction-following capabilities, and strong performance in generating coherent and contextually grounded answers. Using an API abstracts away the complexities of hosting and maintaining a large language model. |
| **Containerization** | **Docker & Docker Compose** | Employed to package the application and its dependencies into isolated containers. This ensures consistency across development, testing, and production environments, simplifies dependency management, and aligns with MLOps best practices for reproducibility and deployment. |
| **Deployment Platform** | **Hugging Face Spaces (Recommended)** | Chosen for its ease of use in deploying AI/ML applications, especially those containerized with Docker. It offers a seamless workflow from a GitHub repository to a live, shareable web application, including a generous free tier for CPU-based applications.           |
| **Environment Management**| **`python-dotenv`** | Used to manage environment variables (like API keys) securely by loading them from a `.env` file, keeping sensitive information out of version control.                                                                                                     |

## 4. Local Setup and Installation

To run this project locally, ensure you have Python (version 3.9 or newer), Docker, and Docker Compose installed on your system.

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-name>
    ```

2.  **Configure Environment Variables:**
    The backend requires an OpenAI API key. Create a `.env` file within the `backend` directory:
    ```bash
    touch backend/.env
    ```
    Add your OpenAI API key to this file:
    ```env
    # backend/.env
    OPENAI_API_KEY="your_openai_api_key_here"
    ```

3.  **Build and Run with Docker Compose:**
    From the root directory of the project, execute the following command:
    ```bash
    docker-compose up --build
    ```
    This command will build the Docker images for the frontend and backend services (if they don't exist or if changes are detected) and then start the containers.

    * The **backend API** will be accessible at `http://localhost:8000`. Interactive API documentation (Swagger UI) can be found at `http://localhost:8000/docs`.
    * The **Streamlit frontend** application will be accessible at `http://localhost:8501`.

## 5. Deployment

The application is designed for deployment using Docker containers. For a simple and shareable deployment, Hugging Face Spaces is recommended, utilizing a single Docker container strategy that combines the frontend and backend.

**Steps for Hugging Face Spaces Deployment:**

1.  **Code Adjustments for Single Container:**
    * Modify `frontend/streamlit_app.py` to make API calls to the backend at `http://localhost:8000` (as both will run in the same container network space).
    * In `frontend/streamlit_app.py`, add Python `subprocess` code at the beginning to start the Uvicorn server for the FastAPI backend when the Streamlit app launches.

2.  **Create a Unified Dockerfile:**
    Place a `Dockerfile` in the root of your project. This Dockerfile should:
    * Start from a Python base image.
    * Copy all project files (`frontend/`, `backend/`, etc.).
    * Install dependencies from both `frontend/requirements.txt` and `backend/requirements.txt`.
    * Expose the necessary ports (e.g., 8501 for Streamlit, 8000 for FastAPI).
    * Set the `CMD` to run the Streamlit application (e.g., `streamlit run frontend/streamlit_app.py --server.port=8501 --server.address=0.0.0.0`).

3.  **Push to GitHub:**
    Commit all changes, including the new root `Dockerfile` and any modifications to `frontend/streamlit_app.py`, and push them to a GitHub repository.

4.  **Create and Configure Hugging Face Space:**
    * Navigate to Hugging Face and create a new "Space".
    * Select "Docker" as the Space SDK and choose the "Blank" template.
    * Connect the Space to your GitHub repository and the appropriate branch.
    * In the Space settings, go to "Repository secrets" and add a new secret:
        * **Name:** `OPENAI_API_KEY`
        * **Value:** Your actual OpenAI API key.
    * The Space will automatically build the Docker image from your root `Dockerfile` and deploy the application. Once built, it will provide a public URL.

## 6. Evaluation Strategy

Evaluating the performance and reliability of the RAG system is crucial. The `backend/evaluation.py` script provides a foundational framework for this. A comprehensive evaluation strategy should focus on the following key RAG-specific metrics:

* **Context Precision:** Assesses the relevance of the document chunks retrieved by the vector search mechanism in relation to the user's query. Low precision indicates that the retrieval step is not finding appropriate context.
* **Faithfulness (or Groundedness):** Measures how well the generated answer aligns with the information present in the retrieved context. Low faithfulness suggests the LLM might be hallucinating or generating information not supported by the provided documents.
* **Answer Relevancy:** Evaluates whether the final generated answer directly addresses and satisfies the user's question. An answer can be faithful to the context but still not relevant to the original query.

**Methodology:**

1.  **Curated Dataset:** Create a representative dataset of question-answer pairs, ideally with known ground-truth answers and relevant document sources.
2.  **Metric Calculation:** For each question in the dataset:
    * Run the RAG pipeline to get the retrieved context and the generated answer.
    * Use LLM-assisted evaluation or human annotators to score the outputs against the defined metrics.
3.  **Frameworks:** For more systematic and automated evaluation, consider integrating frameworks such as:
    * **Ragas:** An open-source framework specifically designed for evaluating RAG pipelines.
    * **Evidently AI:** A tool for ML model monitoring and data/model drift detection, which can be adapted for evaluating aspects of RAG systems.

Regular evaluation helps in identifying bottlenecks, understanding model behavior, and guiding improvements to the retrieval, augmentation, or generation stages.

## 7. Future Improvements

* **Automated Evaluation Pipeline:** Integrate Ragas or a similar framework to establish a CI/CD pipeline for evaluation, allowing for continuous monitoring of RAG performance as components are updated.
* **Advanced Retrieval Strategies:** Explore more sophisticated retrieval techniques beyond basic dense vector search, such as hybrid search (combining keyword and semantic search), re-ranking of retrieved chunks, or query rewriting/expansion.
* **LLM Experimentation:**
    * Test different LLMs (e.g., newer OpenAI models, models from Anthropic, Cohere, or open-source alternatives like Llama 3 via Ollama, as explored in `backend/usingollama.py`).
    * Fine-tune a smaller, open-source LLM on a domain-specific dataset if high-quality Q&A pairs are available.
* **Conversational Context Management:** Implement chat history to enable multi-turn conversations, allowing the assistant to understand follow-up questions in the context of the ongoing dialogue.
