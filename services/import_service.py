import json
from core.db import get_db_connection

class ImportService:
    """Serviço para importar dados do JSON original"""
    
    def import_from_json(self, json_path):
        """Importar dados do arquivo JSON"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conn = get_db_connection()
        imported_count = 0
        
        try:
            # Processar cada categoria
            for category_name, items in data.get('categories', {}).items():
                # Criar categoria se não existir
                category_id = self._get_or_create_category(conn, category_name)
                
                # Processar itens da categoria
                for item_data in items:
                    item_id = self._create_item(conn, category_id, item_data)
                    self._process_extracted_info(conn, item_id, item_data.get('extracted_info', {}))
                    imported_count += 1
            
            conn.commit()
            return {'imported': imported_count, 'status': 'success'}
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _get_or_create_category(self, conn, category_name):
        """Criar categoria se não existir"""
        # Verificar se existe
        result = conn.execute('SELECT id FROM categories WHERE name = ?', (category_name,)).fetchone()
        
        if result:
            return result[0]
        
        # Criar nova categoria
        cursor = conn.execute('INSERT INTO categories (name) VALUES (?)', (category_name,))
        return cursor.lastrowid
    
    def _create_item(self, conn, category_id, item_data):
        """Criar item no banco"""
        cursor = conn.execute('''
            INSERT INTO items (category_id, source_file, raw_content)
            VALUES (?, ?, ?)
        ''', (category_id, item_data.get('source_file', ''), item_data.get('raw_content', '')))
        
        return cursor.lastrowid
    
    def _process_extracted_info(self, conn, item_id, extracted_info):
        """Processar informações extraídas"""
        # Senhas
        for password in extracted_info.get('possible_passwords', []):
            conn.execute('INSERT INTO passwords (item_id, password) VALUES (?, ?)', (item_id, password))
        
        # Emails
        for email in extracted_info.get('emails', []):
            conn.execute('INSERT INTO emails (item_id, email) VALUES (?, ?)', (item_id, email))
        
        # URLs
        for url in extracted_info.get('urls', []):
            conn.execute('INSERT INTO urls (item_id, url) VALUES (?, ?)', (item_id, url))
        
        # Chaves privadas
        for key in extracted_info.get('possible_private_keys', []):
            conn.execute('INSERT INTO private_keys (item_id, key_value) VALUES (?, ?)', (item_id, key))
        
        # Seeds
        for seed in extracted_info.get('possible_seed', []):
            conn.execute('INSERT INTO seeds (item_id, seed_phrase) VALUES (?, ?)', (item_id, seed))