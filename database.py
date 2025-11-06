"""
Database module for credential storage using SQLite
"""
import sqlite3
import os
from typing import List, Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64

class CredentialDatabase:
    def __init__(self, db_path: str = "credentials.db"):
        self.db_path = db_path
        self.encryption_key = self._get_or_create_key()
        self.cipher = Fernet(self.encryption_key)
        self._initialize_database()

    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = ".encryption_key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            # Generate a key based on machine-specific info
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key

    def _initialize_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create credentials table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host VARCHAR(255) NOT NULL,
                credential_type VARCHAR(50) NOT NULL,
                username VARCHAR(255),
                password_encrypted BLOB,
                domain VARCHAR(255),
                community_string_encrypted BLOB,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create execution history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host VARCHAR(255) NOT NULL,
                credential_type VARCHAR(50) NOT NULL,
                script_name VARCHAR(255),
                execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50),
                output TEXT
            )
        """)

        conn.commit()
        conn.close()

    def _encrypt(self, data: str) -> bytes:
        """Encrypt sensitive data"""
        if not data:
            return b''
        return self.cipher.encrypt(data.encode())

    def _decrypt(self, data: bytes) -> str:
        """Decrypt sensitive data"""
        if not data:
            return ''
        return self.cipher.decrypt(data).decode()

    def add_credential(self, host: str, credential_type: str, username: str = None,
                      password: str = None, domain: str = None,
                      community_string: str = None, description: str = None) -> int:
        """Add a new credential"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        password_encrypted = self._encrypt(password) if password else None
        community_encrypted = self._encrypt(community_string) if community_string else None

        cursor.execute("""
            INSERT INTO credentials
            (host, credential_type, username, password_encrypted, domain,
             community_string_encrypted, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (host, credential_type, username, password_encrypted, domain,
              community_encrypted, description))

        credential_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return credential_id

    def update_credential(self, credential_id: int, host: str = None,
                         credential_type: str = None, username: str = None,
                         password: str = None, domain: str = None,
                         community_string: str = None, description: str = None):
        """Update an existing credential"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Build update query dynamically
        updates = []
        params = []

        if host is not None:
            updates.append("host = ?")
            params.append(host)
        if credential_type is not None:
            updates.append("credential_type = ?")
            params.append(credential_type)
        if username is not None:
            updates.append("username = ?")
            params.append(username)
        if password is not None:
            updates.append("password_encrypted = ?")
            params.append(self._encrypt(password))
        if domain is not None:
            updates.append("domain = ?")
            params.append(domain)
        if community_string is not None:
            updates.append("community_string_encrypted = ?")
            params.append(self._encrypt(community_string))
        if description is not None:
            updates.append("description = ?")
            params.append(description)

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(credential_id)

        query = f"UPDATE credentials SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)

        conn.commit()
        conn.close()

    def delete_credential(self, credential_id: int):
        """Delete a credential"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM credentials WHERE id = ?", (credential_id,))
        conn.commit()
        conn.close()

    def get_credential(self, credential_id: int) -> Optional[Dict]:
        """Get a single credential by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM credentials WHERE id = ?", (credential_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_dict(row)
        return None

    def get_credentials_by_host(self, host: str) -> List[Dict]:
        """Get all credentials for a specific host"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM credentials WHERE host = ?", (host,))
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_dict(row) for row in rows]

    def get_all_credentials(self) -> List[Dict]:
        """Get all credentials"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM credentials ORDER BY host, credential_type")
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_dict(row) for row in rows]

    def _row_to_dict(self, row) -> Dict:
        """Convert database row to dictionary"""
        return {
            'id': row[0],
            'host': row[1],
            'credential_type': row[2],
            'username': row[3],
            'password': self._decrypt(row[4]) if row[4] else None,
            'domain': row[5],
            'community_string': self._decrypt(row[6]) if row[6] else None,
            'description': row[7],
            'created_at': row[8],
            'updated_at': row[9]
        }

    def add_execution_history(self, host: str, credential_type: str,
                             script_name: str, status: str, output: str):
        """Add execution history entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO execution_history
            (host, credential_type, script_name, status, output)
            VALUES (?, ?, ?, ?, ?)
        """, (host, credential_type, script_name, status, output))

        conn.commit()
        conn.close()

    def get_execution_history(self, limit: int = 100) -> List[Dict]:
        """Get execution history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM execution_history
            ORDER BY execution_time DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        return [{
            'id': row[0],
            'host': row[1],
            'credential_type': row[2],
            'script_name': row[3],
            'execution_time': row[4],
            'status': row[5],
            'output': row[6]
        } for row in rows]
