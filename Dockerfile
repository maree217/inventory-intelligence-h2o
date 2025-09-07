FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
COPY ../requirements.txt ./base_requirements.txt

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r base_requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .
COPY ../shared ./shared

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]