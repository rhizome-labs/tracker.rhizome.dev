FROM python:3.11.0

# Create working directory
WORKDIR /code

# Copy requirements.txt
COPY ./requirements.txt /code/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy application files
COPY ./tracker_rhizome_dev /code/tracker_rhizome_dev

# Start application
CMD ["gunicorn", "tracker_rhizome_dev.app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080"]