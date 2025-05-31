FROM python:3.10-slim

WORKDIR /app

# Install Streamlit + requests
RUN pip install --no-cache-dir streamlit requests

COPY . .

# Expose Streamlit port
EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
