FROM python:3.11.0

# Create working directory
WORKDIR /code

# Copy requirements.txt
COPY ./requirements.txt /code/requirements.txt

# Install Python dependencies
RUN apt update -y
RUN apt install build-essential -y
RUN apt install pkgconf -y
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN apt install nodejs -y
RUN apt install npm -y

# Copy application files
COPY ./tracker_rhizome_dev /code/tracker_rhizome_dev

# Generate CSS
RUN npm install
RUN npx tailwindcss -i ./tracker_rhizome_dev/app/css/main.css -o ./tracker_rhizome_dev/app/static/style.css --minify

# Start application
CMD ["gunicorn", "tracker_rhizome_dev.app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080"]