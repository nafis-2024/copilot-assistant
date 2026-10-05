import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

class LocalConversationStorage:
    """سیستم ذخیره‌سازی محلی برای گفتگوها و جلسات"""
    
    def __init__(self, base_dir: str = "data/guest_sessions"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.base_dir / "_metadata.json"
    
    def _session_path(self, session_id: str) -> Path:
        """مسیر فایل جلسه را بازگردانید"""
        return self.base_dir / f"{session_id}.json"
    
    def create_session(self, title: str = "", metadata: Dict[str, Any] = None) -> str:
        """جلسه جدیدی را ایجاد کنید"""
        session_id = str(uuid.uuid4())
        
        session_data = {
            "session_id": session_id,
            "title": title or f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "messages": [],
            "metadata": metadata or {}
        }
        
        path = self._session_path(session_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        self._update_metadata(session_id, "created")
        return session_id
    
    def save_message(self, session_id: str, role: str, content: str, metadata: Dict[str, Any] = None):
        """ذخیره‌سازی پیام در جلسه"""
        path = self._session_path(session_id)
        session = self.load_session(session_id)
        
        message = {
            "role": role,  # user, assistant, system
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        session["messages"].append(message)
        session["updated_at"] = datetime.utcnow().isoformat()
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(session, f, ensure_ascii=False, indent=2)
        
        self._update_metadata(session_id, "updated")
    
    def load_session(self, session_id: str) -> Dict[str, Any]:
        """بارگذاری جلسه"""
        path = self._session_path(session_id)
        
        if not path.exists():
            return {
                "session_id": session_id,
                "title": "New Conversation",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "messages": [],
                "metadata": {}
            }
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"[ERROR] فایل {session_id} خراب است.")
            return {
                "session_id": session_id,
                "title": "Corrupted Session",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "messages": [],
                "metadata": {}
            }
    
    def get_messages(self, session_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """دریافت پیام‌های جلسه"""
        session = self.load_session(session_id)
        messages = session.get("messages", [])
        
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """لیست تمام جلسات"""
        sessions = []
        for file in self.base_dir.glob("*.json"):
            if file.name != "_metadata.json":
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        sessions.append({
                            "session_id": data.get("session_id"),
                            "title": data.get("title"),
                            "created_at": data.get("created_at"),
                            "updated_at": data.get("updated_at"),
                            "message_count": len(data.get("messages", []))
                        })
                except:
                    pass
        
        return sorted(sessions, key=lambda x: x["updated_at"], reverse=True)
    
    def delete_session(self, session_id: str) -> bool:
        """حذف جلسه"""
        path = self._session_path(session_id)
        if path.exists():
            path.unlink()
            self._update_metadata(session_id, "deleted")
            return True
        return False
    
    def clear_session(self, session_id: str) -> bool:
        """پاک کردن پیام‌های جلسه"""
        path = self._session_path(session_id)
        if path.exists():
            session = self.load_session(session_id)
            session["messages"] = []
            session["updated_at"] = datetime.utcnow().isoformat()
            
            with open(path, "w", encoding="utf-8") as f:
                json.dump(session, f, ensure_ascii=False, indent=2)
            return True
        return False
    
    def export_session(self, session_id: str, format: str = "json") -> str:
        """صادر کردن جلسه"""
        session = self.load_session(session_id)
        
        if format == "json":
            return json.dumps(session, ensure_ascii=False, indent=2)
        elif format == "txt":
            lines = [f"=== {session['title']} ==="]
            lines.append(f"Created: {session['created_at']}")
            lines.append("\n")
            
            for msg in session["messages"]:
                lines.append(f"{msg['role'].upper()}:")
                lines.append(msg["content"])
                lines.append("---")
            
            return "\n".join(lines)
        
        return ""
    
    def _update_metadata(self, session_id: str, action: str):
        """به‌روزرسانی فایل ابرداده"""
        metadata = {}
        
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
            except:
                pass
        
        if session_id not in metadata:
            metadata[session_id] = {}
        
        metadata[session_id]["last_action"] = action
        metadata[session_id]["last_action_time"] = datetime.utcnow().isoformat()
        
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
