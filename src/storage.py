"""Storage management for the OTP Forwarder Bot."""

import sqlite3
import json
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from .logger_setup import get_logger

logger = get_logger(__name__)


@dataclass
class SMSMessage:
    """SMS message data structure."""
    id: str
    sender: str
    message: str
    timestamp: str
    received_at: str
    forwarded: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SMSMessage':
        """Create from dictionary."""
        return cls(**data)


class Storage:
    """SQLite storage for SMS messages and bot state."""
    
    def __init__(self, db_path: str = "bot_data.db"):
        """Initialize storage with database path."""
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        logger.info(f"Storage initialized with database: {db_path}")
    
    async def initialize(self) -> bool:
        """Initialize the database and create tables."""
        try:
            # Run database initialization in a thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._init_database)
            logger.info("Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            return False
    
    def _init_database(self):
        """Initialize database tables (runs in thread pool)."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        
        # Create tables
        cursor = self.connection.cursor()
        
        # SMS messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sms_messages (
                id TEXT PRIMARY KEY,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                received_at TEXT NOT NULL,
                forwarded BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Bot state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.connection.commit()
        logger.info("Database tables created successfully")
    
    async def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed")
    
    async def save_sms(self, sms: SMSMessage) -> bool:
        """Save SMS message to database."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._save_sms_sync, sms)
            return True
        except Exception as e:
            logger.error(f"Failed to save SMS: {e}")
            return False
    
    def _save_sms_sync(self, sms: SMSMessage):
        """Save SMS message synchronously (runs in thread pool)."""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO sms_messages 
            (id, sender, message, timestamp, received_at, forwarded)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sms.id, sms.sender, sms.message, sms.timestamp, sms.received_at, sms.forwarded))
        self.connection.commit()
    
    async def get_recent_sms(self, limit: int = 10) -> List[SMSMessage]:
        """Get recent SMS messages."""
        try:
            loop = asyncio.get_event_loop()
            messages = await loop.run_in_executor(None, self._get_recent_sms_sync, limit)
            return messages
        except Exception as e:
            logger.error(f"Failed to get recent SMS: {e}")
            return []
    
    def _get_recent_sms_sync(self, limit: int) -> List[SMSMessage]:
        """Get recent SMS messages synchronously (runs in thread pool)."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT id, sender, message, timestamp, received_at, forwarded
            FROM sms_messages
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append(SMSMessage(
                id=row['id'],
                sender=row['sender'],
                message=row['message'],
                timestamp=row['timestamp'],
                received_at=row['received_at'],
                forwarded=bool(row['forwarded'])
            ))
        
        return messages
    
    async def get_last_sms(self) -> Optional[SMSMessage]:
        """Get the last SMS message."""
        messages = await self.get_recent_sms(1)
        return messages[0] if messages else None
    
    async def mark_forwarded(self, sms_id: str) -> bool:
        """Mark SMS as forwarded."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._mark_forwarded_sync, sms_id)
            return True
        except Exception as e:
            logger.error(f"Failed to mark SMS as forwarded: {e}")
            return False
    
    def _mark_forwarded_sync(self, sms_id: str):
        """Mark SMS as forwarded synchronously (runs in thread pool)."""
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE sms_messages 
            SET forwarded = TRUE 
            WHERE id = ?
        """, (sms_id,))
        self.connection.commit()
    
    async def set_state(self, key: str, value: str) -> bool:
        """Set bot state value."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._set_state_sync, key, value)
            return True
        except Exception as e:
            logger.error(f"Failed to set state: {e}")
            return False
    
    def _set_state_sync(self, key: str, value: str):
        """Set bot state value synchronously (runs in thread pool)."""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO bot_state (key, value)
            VALUES (?, ?)
        """, (key, value))
        self.connection.commit()
    
    async def get_state(self, key: str) -> Optional[str]:
        """Get bot state value."""
        try:
            loop = asyncio.get_event_loop()
            value = await loop.run_in_executor(None, self._get_state_sync, key)
            return value
        except Exception as e:
            logger.error(f"Failed to get state: {e}")
            return None
    
    def _get_state_sync(self, key: str) -> Optional[str]:
        """Get bot state value synchronously (runs in thread pool)."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT value FROM bot_state WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row['value'] if row else None
