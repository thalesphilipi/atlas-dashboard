import sqlite3
import os
from datetime import datetime

def get_db_connection():
    """Conexão única com o banco SQLite"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'databases', 'app.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializar estrutura do banco"""
    conn = get_db_connection()
    
    # Tabela de categorias
    conn.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de itens
    conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            source_file TEXT NOT NULL,
            raw_content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    # Tabela de senhas
    conn.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            password TEXT NOT NULL,
            type TEXT DEFAULT 'password',
            FOREIGN KEY (item_id) REFERENCES items (id)
        )
    ''')
    
    # Tabela de emails
    conn.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            email TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items (id)
        )
    ''')
    
    # Tabela de URLs
    conn.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            url TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items (id)
        )
    ''')
    
    # Tabela de chaves privadas
    conn.execute('''
        CREATE TABLE IF NOT EXISTS private_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            key_value TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items (id)
        )
    ''')
    
    # Tabela de seeds
    conn.execute('''
        CREATE TABLE IF NOT EXISTS seeds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            seed_phrase TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items (id)
        )
    ''')
    
    # Índices para performance
    conn.execute('CREATE INDEX IF NOT EXISTS idx_items_category ON items(category_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_passwords_item ON passwords(item_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_emails_item ON emails(item_id)')
    
    conn.commit()
    conn.close()