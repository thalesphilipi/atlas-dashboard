# PDB:
# project_slug: atlas-dashboard
# purpose: Dashboard para organizar dados de senhas e informações pessoais
# db_engine: sqlite
# ui_style: minimal-inline
# version: 0.1.0

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from core.config import Config
from core.db import init_db, get_db_connection
from core.auth import require_auth
from core.utils import update_env_variable
from services.data_service import DataService
from services.import_service import ImportService
import os

# Configurar Flask com diretório de templates correto
app = Flask(__name__, template_folder='ui/templates')
app.config.from_object(Config)

# Inicializar banco
init_db()

@app.route('/')
@require_auth
def dashboard():
    """Dashboard principal"""
    data_service = DataService()
    stats = data_service.get_dashboard_stats()
    recent_items = data_service.get_recent_items(10)
    categories = data_service.get_categories()
    return render_template('dashboard.html', stats=stats, recent_items=recent_items, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login simples"""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == app.config['MASTER_PASSWORD']:
            session['authenticated'] = True
            return redirect(url_for('dashboard'))
        flash('Senha incorreta')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.pop('authenticated', None)
    return redirect(url_for('login'))

@app.route('/category/<category_name>')
@require_auth
def category_view(category_name):
    """Visualizar categoria específica"""
    data_service = DataService()
    items = data_service.get_items_by_category(category_name)
    categories = data_service.get_categories()
    return render_template('category.html', category_name=category_name, items=items, categories=categories)

@app.route('/search')
@require_auth
def search():
    """Busca global"""
    query = request.args.get('q', '')
    data_service = DataService()
    results = data_service.search_items(query) if query else []
    categories = data_service.get_categories()
    return render_template('search.html', query=query, results=results, categories=categories)

@app.route('/import-data', methods=['GET', 'POST'])
@require_auth
def import_data():
    """Importar dados do JSON"""
    if request.method == 'GET':
        # Mostrar página de confirmação
        return render_template('import.html')
    
    # POST - Verificar confirmações
    if not request.form.get('confirm1') or not request.form.get('confirm2'):
        flash('Você deve confirmar ambas as opções para prosseguir com a importação')
        return render_template('import.html')
    
    import_service = ImportService()
    json_path = os.path.join(os.path.dirname(__file__), '..', 'dados_organizados.json')
    
    try:
        result = import_service.import_from_json(json_path)
        flash(f'✅ Dados importados com sucesso: {result["imported"]} itens', 'success')
    except Exception as e:
        flash(f'❌ Erro na importação: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/remove-duplicates', methods=['POST'])
@require_auth
def remove_duplicates():
    """Remove dados duplicados do banco"""
    try:
        from remove_duplicates import remove_duplicates as remove_dups_func
        remove_dups_func()
        flash('✅ Duplicados removidos com sucesso!', 'success')
    except Exception as e:
        flash(f'❌ Erro ao remover duplicados: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/item/<int:item_id>')
@require_auth
def view_item(item_id):
    """Visualizar item específico"""
    data_service = DataService()
    item = data_service.get_item_by_id(item_id)
    if not item:
        flash('Item não encontrado')
        return redirect(url_for('dashboard'))
    return render_template('item_detail.html', item=item)

@app.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
@require_auth
def edit_item(item_id):
    """Editar item"""
    data_service = DataService()
    
    if request.method == 'POST':
        # Atualizar item
        data = {
            'source_file': request.form.get('source_file'),
            'raw_content': request.form.get('raw_content')
        }
        
        if data_service.update_item(item_id, data):
            flash('Item atualizado com sucesso')
            return redirect(url_for('view_item', item_id=item_id))
        else:
            flash('Erro ao atualizar item')
    
    item = data_service.get_item_by_id(item_id)
    if not item:
        flash('Item não encontrado')
        return redirect(url_for('dashboard'))
    
    return render_template('item_edit.html', item=item)

@app.route('/item/<int:item_id>/delete', methods=['POST'])
@require_auth
def delete_item(item_id):
    """Remover item"""
    data_service = DataService()
    
    if data_service.delete_item(item_id):
        flash('Item removido com sucesso')
    else:
        flash('Erro ao remover item')
    
    # Retornar para a página anterior ou para uma página específica
    return_url = request.form.get('return_url') or request.referrer or url_for('dashboard')
    return redirect(return_url)

@app.route('/bulk-delete', methods=['POST'])
@require_auth
def bulk_delete():
    """Remover múltiplos itens selecionados"""
    data_service = DataService()
    
    item_ids = request.form.getlist('item_ids')
    if not item_ids:
        flash('Nenhum item selecionado para remoção')
        return_url = request.form.get('return_url') or request.referrer or url_for('dashboard')
        return redirect(return_url)
    
    # Converter para inteiros e filtrar valores inválidos
    valid_ids = []
    for item_id in item_ids:
        try:
            valid_ids.append(int(item_id))
        except ValueError:
            continue
    
    if not valid_ids:
        flash('IDs de itens inválidos')
        return_url = request.form.get('return_url') or request.referrer or url_for('dashboard')
        return redirect(return_url)
    
    # Deletar itens em lote
    deleted_count = 0
    for item_id in valid_ids:
        if data_service.delete_item(item_id):
            deleted_count += 1
    
    if deleted_count > 0:
        if deleted_count == 1:
            flash('1 item removido com sucesso')
        else:
            flash(f'{deleted_count} itens removidos com sucesso')
    else:
        flash('Erro ao remover itens')
    
    return_url = request.form.get('return_url') or request.referrer or url_for('dashboard')
    return redirect(return_url)

@app.route('/bulk-move-category', methods=['POST'])
@require_auth
def bulk_move_category():
    """Mover múltiplos itens para nova categoria"""
    data_service = DataService()
    
    item_ids = request.form.getlist('item_ids')
    new_category = request.form.get('new_category', '').strip()
    
    if not item_ids:
        flash('❌ Nenhum item selecionado para mover', 'error')
        return_url = request.form.get('return_url') or request.referrer or url_for('dashboard')
        return redirect(return_url)
    
    if not new_category:
        flash('❌ Categoria de destino não informada', 'error')
        return_url = request.form.get('return_url') or request.referrer or url_for('dashboard')
        return redirect(return_url)
    
    # Converter para inteiros e filtrar valores inválidos
    valid_ids = []
    for item_id in item_ids:
        try:
            valid_ids.append(int(item_id))
        except ValueError:
            continue
    
    if not valid_ids:
        flash('❌ IDs de itens inválidos', 'error')
        return_url = request.form.get('return_url') or request.referrer or url_for('dashboard')
        return redirect(return_url)
    
    # Mover itens em lote
    moved_count = 0
    for item_id in valid_ids:
        if data_service.update_item_category(item_id, new_category):
            moved_count += 1
    
    if moved_count > 0:
        if moved_count == 1:
            flash(f'✅ 1 item movido para "{new_category}"', 'success')
        else:
            flash(f'✅ {moved_count} itens movidos para "{new_category}"', 'success')
    else:
        flash('❌ Erro ao mover itens', 'error')
    
    return_url = request.form.get('return_url') or request.referrer or url_for('dashboard')
    return redirect(return_url)

@app.route('/item/new', methods=['GET', 'POST'])
@require_auth
def new_item():
    """Cadastrar novo item"""
    data_service = DataService()
    
    if request.method == 'POST':
        # Criar novo item
        data = {
            'source_file': request.form.get('source_file'),
            'raw_content': request.form.get('raw_content'),
            'category_name': request.form.get('category_name')
        }
        
        if data_service.create_item(data):
            flash('Item cadastrado com sucesso')
            return redirect(url_for('dashboard'))
        else:
            flash('Erro ao cadastrar item')
    
    # Buscar categorias existentes
    categories = data_service.get_categories()
    return render_template('item_new.html', categories=categories)

@app.route('/item/<int:item_id>/move', methods=['GET', 'POST'])
@require_auth
def move_item(item_id):
    """Mover item para outra categoria"""
    data_service = DataService()
    
    if request.method == 'POST':
        new_category = request.form.get('new_category')
        
        if data_service.move_item_category(item_id, new_category):
            flash('Item movido com sucesso')
            return redirect(url_for('view_item', item_id=item_id))
        else:
            flash('Erro ao mover item')
    
    # Buscar item atual e categorias
    item = data_service.get_item_by_id(item_id)
    categories = data_service.get_categories()
    
    if not item:
        flash('Item não encontrado')
        return redirect(url_for('dashboard'))
    
    return render_template('item_move.html', item=item, categories=categories)

@app.route('/api/stats')
@require_auth
def api_stats():
    """API para estatísticas do dashboard"""
    data_service = DataService()
    stats = data_service.get_dashboard_stats()
    return jsonify(stats)

@app.route('/donate')
@require_auth
def donate():
    """Página de doação"""
    return render_template('donate.html')

@app.route('/change-password', methods=['GET', 'POST'])
@require_auth
def change_password():
    """Alterar senha master"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Verificar senha atual
        if current_password != app.config['MASTER_PASSWORD']:
            flash('Senha atual incorreta')
            return render_template('change_password.html')
        
        # Verificar se as senhas coincidem
        if new_password != confirm_password:
            flash('As senhas não coincidem')
            return render_template('change_password.html')
        
        # Verificar se a nova senha não está vazia
        if not new_password or len(new_password) < 6:
            flash('A nova senha deve ter pelo menos 6 caracteres')
            return render_template('change_password.html')
        
        try:
            # Atualizar a senha na configuração atual
            app.config['MASTER_PASSWORD'] = new_password
            
            # Atualizar automaticamente o arquivo .env
            update_env_variable('MASTER_PASSWORD', new_password)
            
            flash('Senha alterada com sucesso! A variável de ambiente foi atualizada automaticamente.')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Erro ao atualizar a senha: {str(e)}')
            return render_template('change_password.html')
    
    return render_template('change_password.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)