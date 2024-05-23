# Dockerfile
FROM python:3.10

# Ensures that the logs are shown in the docker logs
ENV PYTHONUNBUFFERED 1

# Create app directory (within container)
WORKDIR /usr/src/app

# Install dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy project files into docker
COPY . .

# Give permissions to the start script
RUN chmod +x docker_start.sh

EXPOSE 8000

CMD ["./docker_start.sh"]
