from core.db import get_db_connection

class DataService:
    """Serviço para operações com dados"""
    
    def get_dashboard_stats(self):
        """Estatísticas para o dashboard"""
        conn = get_db_connection()
        
        stats = {}
        
        # Total de categorias
        stats['total_categories'] = conn.execute('SELECT COUNT(*) FROM categories').fetchone()[0]
        
        # Total de itens
        stats['total_items'] = conn.execute('SELECT COUNT(*) FROM items').fetchone()[0]
        
        # Total de senhas
        stats['total_passwords'] = conn.execute('SELECT COUNT(*) FROM passwords').fetchone()[0]
        
        # Total de emails
        stats['total_emails'] = conn.execute('SELECT COUNT(*) FROM emails').fetchone()[0]
        
        # Total de chaves privadas
        stats['total_private_keys'] = conn.execute('SELECT COUNT(*) FROM private_keys').fetchone()[0]
        
        # Total de seeds
        stats['total_seeds'] = conn.execute('SELECT COUNT(*) FROM seeds').fetchone()[0]
        
        # Itens por categoria
        category_stats = conn.execute('''
            SELECT c.name, COUNT(i.id) as count
            FROM categories c
            LEFT JOIN items i ON c.id = i.category_id
            GROUP BY c.id, c.name
            ORDER BY count DESC
        ''').fetchall()
        
        stats['categories'] = [dict(row) for row in category_stats]
        
        conn.close()
        return stats
    
    def get_recent_items(self, limit=10):
        """Itens mais recentes"""
        conn = get_db_connection()
        
        items = conn.execute('''
            SELECT i.*, c.name as category_name
            FROM items i
            JOIN categories c ON i.category_id = c.id
            ORDER BY i.created_at DESC
            LIMIT ?
        ''', (limit,)).fetchall()
        
        conn.close()
        return [dict(row) for row in items]
    
    def get_item_by_id(self, item_id):
        """Buscar item específico por ID"""
        conn = get_db_connection()
        
        item = conn.execute('''
            SELECT i.*, c.name as category_name
            FROM items i
            JOIN categories c ON i.category_id = c.id
            WHERE i.id = ?
        ''', (item_id,)).fetchone()
        
        if not item:
            conn.close()
            return None
        
        item_dict = dict(item)
        
        # Buscar dados relacionados
        passwords = conn.execute('SELECT password FROM passwords WHERE item_id = ?', (item_id,)).fetchall()
        item_dict['passwords'] = [row[0] for row in passwords]
        
        emails = conn.execute('SELECT email FROM emails WHERE item_id = ?', (item_id,)).fetchall()
        item_dict['emails'] = [row[0] for row in emails]
        
        urls = conn.execute('SELECT url FROM urls WHERE item_id = ?', (item_id,)).fetchall()
        item_dict['urls'] = [row[0] for row in urls]
        
        keys = conn.execute('SELECT key_value FROM private_keys WHERE item_id = ?', (item_id,)).fetchall()
        item_dict['private_keys'] = [row[0] for row in keys]
        
        seeds = conn.execute('SELECT seed_phrase FROM seeds WHERE item_id = ?', (item_id,)).fetchall()
        item_dict['seeds'] = [row[0] for row in seeds]
        
        conn.close()
        return item_dict
    
    def update_item(self, item_id, data):
        """Atualizar item"""
        conn = get_db_connection()
        
        try:
            conn.execute('''
                UPDATE items 
                SET source_file = ?, raw_content = ?
                WHERE id = ?
            ''', (data['source_file'], data['raw_content'], item_id))
            
            conn.commit()
            conn.close()
            return True
        except:
            conn.rollback()
            conn.close()
            return False
    
    def delete_item(self, item_id):
        """Remover item e todos os dados relacionados"""
        conn = get_db_connection()
        
        try:
            # Remover dados relacionados
            conn.execute('DELETE FROM passwords WHERE item_id = ?', (item_id,))
            conn.execute('DELETE FROM emails WHERE item_id = ?', (item_id,))
            conn.execute('DELETE FROM urls WHERE item_id = ?', (item_id,))
            conn.execute('DELETE FROM private_keys WHERE item_id = ?', (item_id,))
            conn.execute('DELETE FROM seeds WHERE item_id = ?', (item_id,))
            
            # Remover item
            conn.execute('DELETE FROM items WHERE id = ?', (item_id,))
            
            conn.commit()
            conn.close()
            return True
        except:
            conn.rollback()
            conn.close()
            return False
    
    def update_item_category(self, item_id, category_name):
        """Atualizar categoria de um item"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Buscar ou criar categoria
            cursor.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
            category = cursor.fetchone()
            
            if not category:
                # Criar nova categoria
                cursor.execute('INSERT INTO categories (name) VALUES (?)', (category_name,))
                category_id = cursor.lastrowid
            else:
                category_id = category[0]
            
            # Atualizar item
            cursor.execute('UPDATE items SET category_id = ? WHERE id = ?', (category_id, item_id))
            
            conn.commit()
            conn.close()
            return True
        except:
            conn.rollback()
            conn.close()
            return False
    
    def create_item(self, data):
        """Criar novo item"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Buscar ou criar categoria
            category_name = data['category_name']
            cursor.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
            category = cursor.fetchone()
            
            if category:
                category_id = category['id']
            else:
                # Criar nova categoria
                cursor.execute('''
                    INSERT INTO categories (name, created_at)
                    VALUES (?, datetime('now'))
                ''', (category_name,))
                category_id = cursor.lastrowid
            
            # Inserir item
            cursor.execute('''
                INSERT INTO items (source_file, raw_content, category_id, created_at)
                VALUES (?, ?, ?, datetime('now'))
            ''', (data['source_file'], data['raw_content'], category_id))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao criar item: {e}")
            return False
        finally:
            conn.close()
    
    def get_categories(self):
        """Buscar todas as categorias"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT c.name, COUNT(i.id) as count
                FROM categories c
                LEFT JOIN items i ON c.id = i.category_id
                GROUP BY c.id, c.name
                ORDER BY c.name
            ''')
            
            categories = []
            for row in cursor.fetchall():
                categories.append({
                    'name': row[0],
                    'count': row[1]
                })
            
            return categories
        except Exception as e:
            print(f"Erro ao buscar categorias: {e}")
            return []
        finally:
            conn.close()
    
    def move_item_category(self, item_id, new_category):
        """Mover item para nova categoria"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Primeiro, verificar se a categoria existe ou criar uma nova
            cursor.execute('SELECT id FROM categories WHERE name = ?', (new_category,))
            category_row = cursor.fetchone()
            
            if category_row:
                category_id = category_row[0]
            else:
                # Criar nova categoria
                cursor.execute('''
                    INSERT INTO categories (name, created_at) 
                    VALUES (?, datetime('now'))
                ''', (new_category,))
                category_id = cursor.lastrowid
            
            # Atualizar o item com a nova categoria
            cursor.execute('''
                UPDATE items 
                SET category_id = ?
                WHERE id = ?
            ''', (category_id, item_id))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao mover item: {e}")
            return False
        finally:
            conn.close()
    
    def get_items_by_category(self, category_name):
        """Itens de uma categoria específica"""
        conn = get_db_connection()
        
        items = conn.execute('''
            SELECT i.*, c.name as category_name
            FROM items i
            JOIN categories c ON i.category_id = c.id
            WHERE c.name = ?
            ORDER BY i.source_file
        ''', (category_name,)).fetchall()
        
        # Buscar dados relacionados para cada item
        result = []
        for item in items:
            item_dict = dict(item)
            
            # Senhas
            passwords = conn.execute('SELECT password FROM passwords WHERE item_id = ?', (item['id'],)).fetchall()
            item_dict['passwords'] = [row[0] for row in passwords]
            
            # Emails
            emails = conn.execute('SELECT email FROM emails WHERE item_id = ?', (item['id'],)).fetchall()
            item_dict['emails'] = [row[0] for row in emails]
            
            # URLs
            urls = conn.execute('SELECT url FROM urls WHERE item_id = ?', (item['id'],)).fetchall()
            item_dict['urls'] = [row[0] for row in urls]
            
            # Chaves privadas
            keys = conn.execute('SELECT key_value FROM private_keys WHERE item_id = ?', (item['id'],)).fetchall()
            item_dict['private_keys'] = [row[0] for row in keys]
            
            # Seeds
            seeds = conn.execute('SELECT seed_phrase FROM seeds WHERE item_id = ?', (item['id'],)).fetchall()
            item_dict['seeds'] = [row[0] for row in seeds]
            
            result.append(item_dict)
        
        conn.close()
        return result
    
    def search_items(self, query):
        """Busca global nos itens"""
        conn = get_db_connection()
        
        search_term = f'%{query}%'
        
        items = conn.execute('''
            SELECT DISTINCT i.*, c.name as category_name
            FROM items i
            JOIN categories c ON i.category_id = c.id
            WHERE i.source_file LIKE ? OR i.raw_content LIKE ?
            ORDER BY i.source_file
            LIMIT 50
        ''', (search_term, search_term)).fetchall()
        
        conn.close()
        return [dict(row) for row in items]