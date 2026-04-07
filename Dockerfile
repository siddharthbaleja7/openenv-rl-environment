FROM python:3.11-slim

WORKDIR /app

# Install dependencies directly to be lightweight
RUN pip install --no-cache-dir pydantic openai fastapi uvicorn

# Copy project files
COPY . .

# Set default env vars
ENV PYTHONUNBUFFERED=1

# Expose HF Spaces port
EXPOSE 7860

# Run the FastAPI server by default
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
