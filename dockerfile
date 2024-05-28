FROM ghcr.io/railwayapp/nixpacks:ubuntu-1716249803

# Set work directory
WORKDIR /app

# Copy Nix shell configuration
COPY shell.nix /app/

# Install Nix dependencies
RUN nix-env -if /app/shell.nix && nix-collect-garbage -d

# Copy application files
COPY . /app/

# Create virtual environment and install Python dependencies
RUN python -m venv --copies /opt/venv && . /opt/venv/bin/activate && pip install -r requirements.txt

# Set environment variables for Nix and Python
ENV PATH="/opt/venv/bin:$PATH"

# Command to run the application
CMD ["python", "main.py"]