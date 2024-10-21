FROM python:3.12.5

# Install system dependencies for TTS and Gunicorn
RUN apt-get update && apt-get install -y espeak-ng libespeak-ng-dev

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install NLTK punkt tokenizer
RUN python -m nltk.downloader punkt

# Optionally, download all NLTK resources (if needed)
# RUN python -m nltk.downloader all

# Install Gunicorn for production
RUN pip install gunicorn

# Expose the port the app runs on
EXPOSE 5000

# Run the application using Gunicorn
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

