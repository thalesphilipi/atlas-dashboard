import os
import json
from datetime import datetime

def ensure_dir(path):
    """Garantir que diretório existe"""
    os.makedirs(path, exist_ok=True)

def format_datetime(dt_string):
    """Formatar datetime para exibição"""
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y %H:%M')
    except:
        return dt_string

def truncate_text(text, max_length=100):
    """Truncar texto com reticências"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + '...'

def safe_json_loads(json_string):
    """Carregar JSON de forma segura"""
    try:
        return json.loads(json_string)
    except:
        return {}

def update_env_variable(key, value):
    """Atualizar variável no arquivo .env"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    
    # Se .env não existe, criar baseado no .env.example
    if not os.path.exists(env_path):
        example_path = env_path + '.example'
        if os.path.exists(example_path):
            with open(example_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    # Ler arquivo .env atual
    lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    
    # Procurar e atualizar a variável
    updated = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f'{key}='):
            lines[i] = f'{key}={value}\n'
            updated = True
            break
    
    # Se não encontrou, adicionar no final
    if not updated:
        lines.append(f'{key}={value}\n')
    
    # Escrever arquivo atualizado
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    return True