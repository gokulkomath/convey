# Use a slim Python base image
FROM python:3.10-slim

# Prevent interactive debconf prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    vlc \
    alacritty \
    cava \
    wget \
    curl \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    x11-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Brave browser (optional, only if you're using it in subprocess)
RUN curl -fsSLo brave.deb https://github.com/brave/brave-browser/releases/latest/download/brave-browser_amd64.deb && \
    apt install -y ./brave.deb && rm brave.deb || true

# Set the working directory inside the container
WORKDIR /app

# Copy project files into the container
COPY . .

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install yt-dlp (as it's used via subprocess)
RUN pip install yt-dlp

# Expose Rasa action server port
EXPOSE 5055

# Start the Rasa SDK action server
CMD ["rasa", "run", "--enable-api"]
