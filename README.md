# Personal Assistant MODULAR

A comprehensive, modular personal assistant with Discord integration, RAG (Retrieval-Augmented Generation) capabilities, health triage, and more.

## Features

### **RAG System (Retrieval-Augmented Generation)**
- Advanced document indexing and search
- SQLite backend with Ollama/OpenAI embeddings
- Support for .txt, .md, .json files
- Fallback similarity search system
- Discord file attachment indexing

### **Discord Integration**
- Full Discord bot with slash commands
- File attachment processing
- Interactive commands with reactions
- Both prefix (`!pa`) and slash command support

### **Health Triage**
- Preliminary health assessment
- Symptom analysis and categorization
- Medical disclaimer compliance
- Emergency guidance

### **Todo Management**
- Task tracking and organization
- Priority management
- Status updates

### **Text Summarization**
- Document summarization
- Content analysis

### **Web API**
- FastAPI-based REST API
- Interactive documentation
- Multiple interface options

### ️ **CLI Interface**
- Rich terminal interface
- Interactive shell mode
- Command completion

## Installation

### Quick Install
```bash
git clone https/github.com/nike/personal-assistant-modular.git
cd personal-assistant-modular
./install.sh
```

### Manual Installation
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Copy environment configuration
cp .env.example .env
# Edit .env with your configurations
```

## ️ Configuration

Create a `.env` file with your settings:

```env
# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_server_id_optional

# Ollama Configuration (Local LLM)
OLLAMA_BASE_URL=http/localhost:11434
OLLAMA_MODEL=llama3.2:3b

# OpenAI Configuration (Optional)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https/api.openai.com
OPENAI_MODEL=gpt-4o-mini

# RAG System
RAG_SRC_PATHpath/to/advanced/rag/system
```

## ‍️ Usage

### Discord Bot
```bash
# Start Discord bot
python discord_bot.py
# or
./start_bot.sh
```

**Discord Commands:**
- `!pa ask <question>` - Ask a general question
- `!pa rag_add <path>` - Index files for RAG
- `!pa rag_ask <question>` - Query indexed documents
- `!pa triage <symptoms>` - Health triage assessment
- `/rag_help` - Show RAG usage guide

### CLI Interface
```bash
# Interactive shell
python assistant_cli.py shell

# Direct commands
python assistant_cli.py ask "What's the weather like?"
python assistant_cli.py rag add /path/to/documents
python assistant_cli.py rag ask "What did I index?"
```

### Web API
```bash
# Start FastAPI server
python server.py
# Visit http/localhost:8000/docs for interactive API documentation
```

## ️ Architecture

```
PERSONAL-ASSISTANT-MODULAR/
├── skills/ # Modular skill system
│ ├── base.py # Base skill interface
│ ├── rag.py # RAG implementation
│ ├── health_triage.py # Health triage system
│ ├── todos.py # Todo management
│ └── summarizer.py # Text summarization
├── assistant.py # Core assistant logic
├── discord_bot.py # Discord integration
├── ️ assistant_cli.py # CLI interface
├── server.py # FastAPI web server
├── requirements.txt # Python dependencies
├── setup.py # Package configuration
├── install.sh # Installation script
├── start_bot.sh # Bot startup script
└── README.md # This file
```

## Skills System

The assistant uses a modular skill system. Each skill inherits from `BaseSkill`:

```python
from skills.base import BaseSkill

class CustomSkill(BaseSkill):
 name = "custom"

 def can_handle(self, text: str) -> bool:
 return text.startswith("custom")

 def handle(self, text: str) -> str:
 return "Custom response"
```

## RAG System Details

The RAG system supports multiple backends:

### Primary System
- **Storage**: SQLite with vector embeddings
- **Embeddings**: Ollama or OpenAI models
- **Search**: Semantic similarity search

### Fallback System
- **Storage**: In-memory document store
- **Embeddings**: Character frequency analysis
- **Search**: Basic similarity matching

## ️ Development

### Adding New Skills
1. Create a new file in `skills/`
2. Inherit from `BaseSkill`
3. Implement `can_handle()` and `handle()` methods
4. Add to `assistant.py` skills list

## License

MIT License - see LICENSE file for details

---

**Personal Assistant MODULAR** - Your comprehensive, modular AI assistant solution 