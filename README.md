# AI Assistant for Salesforce Documentation

## 1. Overview

This project is a Retrieval-Augmented Generation (RAG) system designed to answer questions about Salesforce documentation. It functions as an AI-powered chatbot that takes a user's question, finds the most relevant information from a prepared knowledge base of Salesforce help articles, and generates a detailed, accurate answer.

The primary goal is to provide users with quick, context-aware answers to their Salesforce-related queries, complete with source references to the original documentation, thereby increasing user trust and improving the support experience.

The application is architected as a modern web service with a multi-container setup, containerized with Docker, and designed for cloud deployment on platforms like Render.

## 2. Features

* **Question Answering:** Users can ask questions in natural language.
* **Referenced Answers:** The generated answers are based on specific chunks of text from the Salesforce documentation, and the original source URLs are provided.
* **Confidence Score:** Each answer includes a confidence score, calculated based on the language model's certainty in its generation, which helps the user gauge the reliability of the response.
* **Decoupled Architecture:** A robust FastAPI backend serves the AI logic, while an independent Streamlit frontend provides an interactive user interface.
* **Containerized:** Both frontend and backend services are individually containerized with Docker, ensuring clean separation and reproducibility.

## 3. Architecture and Tech Stack

The system follows a classic RAG architecture, implemented with two distinct services that communicate over an internal network.

1.  **Frontend Service (Streamlit Container):** A user submits a question through the Streamlit web app. The frontend service then sends a request to the backend service using its internal network address (e.g., `http://backend:8000`).
2.  **Backend Service (FastAPI Container):**
    * **Retrieval:** The backend receives the request, embeds the user's question into a vector using a Sentence Transformer model, and uses FAISS to find the most relevant document chunks from a pre-indexed vector database.
    * **Augmentation:** The retrieved text chunks are combined with the original question into a detailed prompt.
    * **Generation:** The prompt is sent to the OpenAI GPT-3.5 Turbo model to generate a final answer based *only* on the provided context.
3.  **Response:** The final answer, source references, and confidence score are sent back to the frontend to be displayed to the user.

### Technology Justification

| Component                | Technology                               | Justification                                                                                                                                                                                            |
| :----------------------- | :--------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Backend Framework** | **FastAPI** | Chosen for its high performance and native asynchronous support, making it ideal for I/O-bound tasks like API calls. Its automatic data validation and API documentation generation are crucial for building robust services. |
| **Frontend Framework** | **Streamlit** | Selected for its ability to rapidly create and deploy interactive web applications for machine learning with simple Python scripts, providing a fast path to a user-facing demo.               |
| **Embedding Model** | **SentenceTransformers (`all-MiniLM-L6-v2`)** | This model provides an excellent balance between embedding quality and computational efficiency, making it suitable for deployment in resource-constrained environments like free cloud tiers. |
| **Vector Store** | **FAISS** | An in-memory vector library chosen for its exceptional speed and efficiency in similarity search. It simplifies the architecture by avoiding the need for a separate, externally hosted vector database. |
| **Language Model** | **OpenAI GPT-3.5 Turbo** | Utilized via its API for state-of-the-art language comprehension and the ability to strictly follow instructions, which is critical for generating answers grounded in the provided context and reducing hallucinations.         |
| **Containerization** | **Docker & Docker Compose** | This setup was chosen to manage the multi-service application. It defines the application's entire environment, ensuring consistency from local development to production and cleanly separating the concerns of the frontend and backend. |
| **Deployment Platform** | **Render** | Selected for its excellent native support for deploying multi-container Docker applications via a `render.yaml` configuration file. It provides a simple developer experience, a direct Git-to-deploy workflow, and handles complex tasks like internal networking and secrets management. |

## 4. Local Setup and Installation

To run this project locally, you will need `Docker` and `Docker Compose` installed.

1.  **Clone the Repository**
    ```sh
    git clone <your-repository-url>
    cd <repository-directory>
    ```

2.  **Set Up Environment Variables**
    The application requires an OpenAI API key. Create a `.env` file in the `backend` directory:
    ```sh
    touch backend/.env
    ```
    Add your API key to this file:
    ```
    # backend/.env
    OPENAI_API_KEY="sk-..."
    ```

3.  **Build and Run with Docker Compose**
    From the root of the project directory, run:
    ```sh
    docker-compose up --build
    ```
    * The backend API will be available at `http://localhost:8000/docs`.
    * The Streamlit frontend will be available at `http://localhost:8501`.

## 5. Deployment on Render

This application is configured for deployment on Render using the `render.yaml` file present in the repository root.

1.  **Push Code to GitHub:** Ensure your repository is up-to-date with all the correct files (`docker-compose.yml`, `render.yaml`, `backend/Dockerfile`, `frontend/Dockerfile`, etc.).

2.  **Access Your Application:** https://frontend-p48r.onrender.com/#whatfix-salesforce-help-assistant .

## 6. Evaluation Strategy

Evaluating the performance of the RAG system is critical. The `evaluation.py` script provides a starting point. A robust evaluation would involve a curated set of questions to measure key metrics:

* **Context Precision:** Are the retrieved document chunks relevant to the question?
* **Faithfulness:** Does the generated answer stick to the provided context?
* **Answer Relevancy:** Is the answer relevant to the user's question?

