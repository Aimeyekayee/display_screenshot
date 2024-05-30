# Use the official Python image from the Docker Hub
FROM python:3.11.4-slim-bookworm

# Set the timezone
ENV TZ=Asia/Bangkok

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install dependencies for Edge WebDriver
RUN apt-get update && \
    apt-get install -y wget gnupg && \
    wget -q -O - https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.asc.gpg && \
    mv microsoft.asc.gpg /etc/apt/trusted.gpg.d/microsoft.asc.gpg && \
    wget -q https://packages.microsoft.com/config/debian/11/prod.list && \
    mv prod.list /etc/apt/sources.list.d/microsoft-prod.list && \
    chown root:root /etc/apt/trusted.gpg.d/microsoft.asc.gpg && \
    chown root:root /etc/apt/sources.list.d/microsoft-prod.list && \
    apt-get update && \
    apt-get install -y microsoft-edge-stable

# Download Edge WebDriver
RUN wget https://msedgedriver.azureedge.net/113.0.1774.57/edgedriver_linux64.zip && \
    apt-get install -y unzip && \
    unzip edgedriver_linux64.zip && \
    mv msedgedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/msedgedriver && \
    rm edgedriver_linux64.zip

# Copy the rest of the application code to the working directory
COPY . .

# Set the entry point to run the script
ENTRYPOINT ["python", "main.py"]
