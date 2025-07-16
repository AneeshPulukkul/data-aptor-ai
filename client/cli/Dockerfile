FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the CLI code
COPY . .

# Install the CLI
RUN pip install --no-cache-dir -e .

# Set the default command
ENTRYPOINT ["dataaptor"]
CMD ["--help"]
