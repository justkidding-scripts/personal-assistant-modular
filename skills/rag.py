#!/usr/bin/env python3
import os
import re
import sys
import json
import time
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import logging

import numpy as np

# Enhanced RAG system detection with multiple paths
HAVE_RAG = False
RAGSystem = None
OLLAMA_AVAILABLE = False

# Try to import Ollama first
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Try multiple paths for RAG system
RAG_PATHS = [
    os.getenv("RAG_SRC_PATH", "/media/nike/backup-hdd/Modular Deepdive/RAG"),
    "/home/nike/ollama-enhancements",
    "/home/nike/products/modular-rag-system",
    "/home/nike/ollama-ocr-integration-fixed/modular-rag-system"
]

for rag_path in RAG_PATHS:
    if os.path.isdir(rag_path):
        try:
            sys.path.insert(0, rag_path)
            from ollama_rag_system import RAGSystem as _RAGSystem  # type: ignore
            RAGSystem = _RAGSystem
            HAVE_RAG = True
            break
        except Exception:
            continue

# Enhanced file support
SUPPORTED_EXTS = {
    ".txt", ".md", ".json", ".py", ".js", ".ts", ".html", ".css", 
    ".yaml", ".yml", ".toml", ".ini", ".conf", ".sh", ".bash", ".zsh",
    ".c", ".cpp", ".h", ".hpp", ".go", ".rs", ".java", ".php", ".rb", ".pl",
    ".sql", ".csv", ".xml", ".log", ".rst", ".tex", ".dockerfile"
}


def _read_text(path: Path) -> str:
    """Enhanced text reading with format-specific handling"""
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        
        # Format-specific processing
        if path.suffix.lower() == ".json":
            try:
                data = json.loads(content)
                return json.dumps(data, indent=2)
            except Exception:
                return content
        
        elif path.suffix.lower() in {".py", ".js", ".ts", ".go", ".rs", ".java", ".c", ".cpp"}:
            # Add metadata for code files
            return f"# File: {path}\n# Type: {path.suffix[1:]} code\n\n{content}"
        
        elif path.suffix.lower() == ".csv":
            # Basic CSV preview
            lines = content.split('\n')[:10]  # First 10 lines
            return f"# CSV File: {path}\n# Preview (first 10 lines):\n\n" + '\n'.join(lines)
        
        else:
            return content
            
    except Exception as e:
        return f"Error reading {path}: {e}"


def _simple_embed(text: str) -> np.ndarray:
    """Enhanced lightweight embedding with more features"""
    text = (text or "").lower()
    vec = np.zeros(256, dtype=np.float32)  # Increased dimensionality
    
    # Character frequency features (26 dims)
    letters = "abcdefghijklmnopqrstuvwxyz"
    for i, ch in enumerate(letters):
        vec[i] = text.count(ch) / max(len(text), 1)
    
    # Word-level features (50 dims)
    words = text.split()
    vec[26] = len(words) / max(len(text.split()), 1)  # words per char
    vec[27] = len(set(words)) / max(len(words), 1) if words else 0  # unique ratio
    
    # Common programming keywords
    prog_keywords = ['def', 'class', 'function', 'import', 'return', 'if', 'for', 'while', 'try', 'except']
    for i, kw in enumerate(prog_keywords):
        if i < 20:  # Use 20 slots
            vec[28 + i] = text.count(kw) / max(len(words), 1) if words else 0
    
    # Text structure features
    vec[48] = text.count('\n') / max(len(text), 1)  # line density
    vec[49] = text.count('.') / max(len(text), 1)   # sentence density
    vec[50] = text.count('(') / max(len(text), 1)   # parentheses density
    vec[51] = text.count('{') / max(len(text), 1)   # brace density
    
    # Hash-based features (remaining dims)
    h = hash(text)
    for i in range(52, 256):
        vec[i] = ((h >> (i % 64)) & 1) * 0.05  # Reduced weight
    
    # Normalize
    n = np.linalg.norm(vec)
    if n > 0:
        vec = vec / n
    return vec


class _FallbackStore:
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.docs: List[Tuple[str, str, np.ndarray]] = []  # (id, content, emb)

    def add_doc(self, content: str, doc_id: str = ""):
        if not content.strip():
            return
        emb = _simple_embed(content)
        if not doc_id:
            doc_id = f"doc_{len(self.docs)+1}"
        self.docs.append((doc_id, content, emb))

    def search(self, query: str, k: int = 3) -> List[Tuple[str, float, str]]:
        if not self.docs:
            return []
        qv = _simple_embed(query)
        sims = []
        for doc_id, content, emb in self.docs:
            score = float(np.dot(qv, emb))
            sims.append((doc_id, score, content))
        sims.sort(key=lambda x: x[1], reverse=True)
        return sims[:k]


class RAGSkill:
    name = "rag"

    def __init__(self):
        self.root = Path(__file__).parents[1]
        self.storage = self.root / "rag_storage"
        self.storage.mkdir(parents=True, exist_ok=True)
        
        # Enhanced initialization
        self.use_rag = False
        self.rag = None
        self.ollama_client = None
        self.last_query_time = 0
        self.cache = {}  # Simple query cache
        
        # Try Ollama client initialization
        if OLLAMA_AVAILABLE:
            try:
                import ollama
                self.ollama_client = ollama.Client()
            except Exception:
                pass

        # Try RAG system initialization with better error handling
        if HAVE_RAG and RAGSystem is not None:
            try:
                self.rag = RAGSystem(self.storage)
                self.use_rag = True
                print(f"✅ RAG system initialized with storage: {self.storage}")
            except Exception as e:
                print(f"⚠️ RAG system init failed: {e}")
                self.use_rag = False

        # Always initialize fallback
        self.fallback = _FallbackStore(self.storage)
        
        if not self.use_rag:
            print(f"🔄 Using fallback RAG storage: {self.storage}")

    def can_handle(self, text: str) -> bool:
        t = (text or "").strip().lower()
        return any(t.startswith(cmd) for cmd in [
            "rag add ", "rag ask ", "rag add_text ", "rag search ", "rag clear", "rag list",
            "rag index ", "rag summary ", "rag export "
        ]) or t in ["rag status", "rag help", "rag stats"]

    def handle(self, text: str) -> str:
        t = (text or "").strip()
        low = t.lower()
        
        # Enhanced command routing
        if low.startswith("rag add_text "):
            payload = t[len("rag add_text "):].strip()
            parts = payload.split("::", 1)
            if len(parts) != 2:
                return "Usage: rag add_text <doc_id> :: <content>"
            return self._cmd_add_text(parts[0].strip(), parts[1].strip())
        
        elif low.startswith("rag add ") or low.startswith("rag index "):
            path = t.split(None, 2)[2] if len(t.split()) > 2 else ""
            return self._cmd_add(path)
        
        elif low.startswith("rag ask ") or low.startswith("rag search "):
            q = " ".join(t.split()[2:])
            return self._cmd_ask(q)
        
        elif low.startswith("rag summary "):
            topic = " ".join(t.split()[2:])
            return self._cmd_summary(topic)
        
        elif low == "rag clear":
            return self._cmd_clear()
        
        elif low == "rag list":
            return self._cmd_list()
        
        elif low == "rag export":
            return self._cmd_export()
        
        elif low in ["rag status", "rag stats"]:
            return self._cmd_status()
        
        elif low == "rag help":
            return self._cmd_help()
        
        return self._cmd_help()

    def _iter_files(self, p: Path):
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS:
            yield p
        elif p.is_dir():
            for fp in p.rglob("*"):
                if fp.is_file() and fp.suffix.lower() in SUPPORTED_EXTS:
                    yield fp

    def _cmd_add(self, path_str: str) -> str:
        p = Path(path_str).expanduser().resolve()
        if not p.exists():
            return f"Path not found: {p}"
        count = 0
        for fp in self._iter_files(p):
            try:
                content = _read_text(fp)
                if self.use_rag and self.rag is not None:
                    self.rag.add_document(content, metadata={"path": str(fp)}, source="file")
                else:
                    self.fallback.add_doc(content, doc_id=str(fp))
                count += 1
            except Exception:
                continue
        return f"Indexed {count} documents from {p}"

    def _cmd_add_text(self, doc_id: str, content: str) -> str:
        if not content.strip():
            return "No content provided"
        if self.use_rag and self.rag is not None:
            try:
                self.rag.add_document(content, metadata={"path": doc_id}, source="discord_attachment")
                return f"Added: {doc_id}"
            except Exception:
                # fallback transparently
                pass
        self.fallback.add_doc(content, doc_id=doc_id)
        return f"Added (fallback): {doc_id}"

    def _cmd_ask(self, q: str) -> str:
        if not q:
            return "Provide a question after 'rag ask'"
        if self.use_rag and self.rag is not None:
            try:
                res = self.rag.query(q, max_results=3)
                if not res.documents:
                    return "No relevant documents found."
                lines = ["Results:"]
                for i, doc in enumerate(res.documents[:3], 1):
                    snippet = (doc.content or "")[:200].replace("\n", " ")
                    src = doc.metadata.get("path", doc.source)
                    lines.append(f"{i}. {snippet} ... [src: {src}]")
                return "\n".join(lines)
            except Exception as e:
                # fallback transparently
                pass
        hits = self.fallback.search(q, k=3)
        if not hits:
            return "No relevant documents found."
        lines = ["Results (fallback):"]
        for i, (doc_id, score, content) in enumerate(hits, 1):
            snippet = content[:200].replace("\n", " ")
            lines.append(f"{i}. {snippet} ... [score: {score:.2f}] [src: {doc_id}]")
        return "\n".join(lines)

    def _cmd_status(self) -> str:
        """Get RAG system status"""
        lines = ["🤖 RAG System Status:"]
        
        if self.use_rag and self.rag is not None:
            try:
                stats = self.rag.get_system_stats()
                total = stats.get("vector_store", {}).get("total_documents", 0)
                backend = stats.get("vector_store", {}).get("backend", "unknown")
                lines.append(f"✅ Primary RAG: {backend} backend, {total} documents")
            except Exception as e:
                lines.append(f"⚠️ Primary RAG error: {e}")
        else:
            lines.append("❌ Primary RAG: Not available")
        
        fb_docs = len(getattr(self.fallback, 'docs', []))
        lines.append(f"🔄 Fallback: {fb_docs} documents")
        
        if self.ollama_client:
            lines.append("✅ Ollama: Connected")
        else:
            lines.append("❌ Ollama: Not connected")
        
        lines.append(f"💾 Storage: {self.storage}")
        return "\n".join(lines)
    
    def _cmd_help(self) -> str:
        """Show help information"""
        return """🤖 RAG System Commands:
        
📁 Data Management:
  rag add <file_or_dir>     - Index files/directories
  rag add_text <id> :: <content> - Add text directly
  rag clear                 - Clear all documents
  rag list                  - List indexed documents
  
🔍 Querying:
  rag ask <question>        - Ask questions
  rag search <query>        - Search documents  
  rag summary <topic>       - Get topic summary
  
📊 Information:
  rag status               - Show system status
  rag stats                - Show detailed stats
  rag export               - Export document list
  rag help                 - Show this help
  
💡 Examples:
  rag add ~/Documents
  rag ask "What is machine learning?"
  rag add_text notes :: This is important info"""
    
    def _cmd_clear(self) -> str:
        """Clear all documents"""
        try:
            if self.use_rag and self.rag is not None:
                # If RAG system has a clear method
                if hasattr(self.rag, 'clear_documents'):
                    self.rag.clear_documents()
                    return "✅ Cleared primary RAG system"
            
            # Clear fallback
            self.fallback.docs.clear()
            self.cache.clear()
            return "✅ Cleared fallback documents"
            
        except Exception as e:
            return f"❌ Clear error: {e}"
    
    def _cmd_list(self) -> str:
        """List indexed documents"""
        lines = ["📚 Indexed Documents:"]
        
        if self.use_rag and self.rag is not None:
            try:
                # Try to get document list from RAG system
                if hasattr(self.rag, 'list_documents'):
                    docs = self.rag.list_documents()
                    for i, doc in enumerate(docs[:10], 1):
                        source = getattr(doc, 'source', 'unknown')
                        lines.append(f"{i}. {source}")
                    if len(docs) > 10:
                        lines.append(f"... and {len(docs)-10} more")
                    return "\n".join(lines)
            except Exception:
                pass
        
        # Fallback listing
        fb_docs = getattr(self.fallback, 'docs', [])
        if fb_docs:
            for i, (doc_id, content, _) in enumerate(fb_docs[:10], 1):
                preview = content[:50].replace('\n', ' ')
                lines.append(f"{i}. {doc_id}: {preview}...")
            if len(fb_docs) > 10:
                lines.append(f"... and {len(fb_docs)-10} more")
        else:
            lines.append("No documents indexed")
            
        return "\n".join(lines)
    
    def _cmd_export(self) -> str:
        """Export document information"""
        try:
            export_path = self.storage / f"rag_export_{int(time.time())}.json"
            
            export_data = {
                "timestamp": time.time(),
                "system_status": {
                    "use_rag": self.use_rag,
                    "have_ollama": self.ollama_client is not None,
                    "storage_path": str(self.storage)
                },
                "documents": []
            }
            
            # Export fallback docs
            fb_docs = getattr(self.fallback, 'docs', [])
            for doc_id, content, _ in fb_docs:
                export_data["documents"].append({
                    "id": doc_id,
                    "content_preview": content[:200],
                    "content_length": len(content),
                    "source": "fallback"
                })
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            return f"✅ Exported {len(export_data['documents'])} documents to {export_path}"
            
        except Exception as e:
            return f"❌ Export error: {e}"
    
    def _cmd_summary(self, topic: str) -> str:
        """Generate summary for a topic"""
        if not topic:
            return "Usage: rag summary <topic>"
        
        # Use cached result if recent
        cache_key = f"summary:{topic}"
        if cache_key in self.cache:
            cached_time, result = self.cache[cache_key]
            if time.time() - cached_time < 300:  # 5 minute cache
                return f"📋 Summary (cached): {result}"
        
        # Search for relevant documents
        search_results = self._search_docs(topic, k=5)
        
        if not search_results:
            return f"❌ No documents found for topic: {topic}"
        
        # Create summary from top results
        summary_parts = []
        for doc_id, score, content in search_results:
            # Take first 100 chars as snippet
            snippet = content[:100].replace('\n', ' ').strip()
            summary_parts.append(f"• {snippet}... (from {doc_id})")
        
        summary = f"📋 Summary for '{topic}':\n\n" + "\n".join(summary_parts)
        
        # Cache result
        self.cache[cache_key] = (time.time(), summary)
        
        return summary
    
    def _search_docs(self, query: str, k: int = 3) -> List[Tuple[str, float, str]]:
        """Internal method to search documents"""
        if self.use_rag and self.rag is not None:
            try:
                res = self.rag.query(query, max_results=k)
                if res.documents:
                    results = []
                    for doc in res.documents:
                        doc_id = doc.metadata.get("path", doc.source)
                        results.append((doc_id, 1.0, doc.content or ""))
                    return results
            except Exception:
                pass
        
        # Fallback search
        return self.fallback.search(query, k=k)
