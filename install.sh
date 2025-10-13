#!/bin/bash
# Personal Assistant MODULAR - Installation Script

echo "🚀 Installing Personal Assistant MODULAR..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
print_status "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
print_success "Python version: $python_version"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv .venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
print_status "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install the package in development mode
print_status "Installing Personal Assistant MODULAR..."
pip install -e .

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p rag_storage
mkdir -p logs

# Copy environment file template
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_status "Creating .env file from template..."
        cp .env.example .env
        print_warning "Please edit .env file with your configuration"
    else
        print_status "Creating basic .env file..."
        cat > .env << 'EOL'
# Personal Assistant Configuration
DISCORD_TOKEN=your_discord_bot_token_here
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com
OPENAI_MODEL=gpt-4o-mini
EOL
        print_warning "Please edit .env file with your configuration"
    fi
else
    print_status ".env file already exists"
fi

# Make scripts executable
print_status "Making scripts executable..."
chmod +x *.sh *.py

print_success "🎉 Personal Assistant MODULAR installed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys and configuration"
echo "2. For Discord: python discord_bot.py"
echo "3. For CLI: python assistant_cli.py --help"
echo "4. For Web API: python server.py"
echo ""
echo "Run './start_bot.sh' to start the Discord bot"
echo "Run 'python assistant_cli.py shell' for interactive mode"