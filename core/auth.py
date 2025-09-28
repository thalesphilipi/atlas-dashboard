from functools import wraps
from flask import session, redirect, url_for, request
import time

# Rate limiting simples
last_action_time = {}

def require_auth(f):
    """Decorator para rotas que precisam de autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Rate limiting básico
        client_ip = request.remote_addr
        current_time = time.time()
        
        if client_ip in last_action_time:
            if current_time - last_action_time[client_ip] < 2:
                time.sleep(1)  # Delay de 1 segundo
        
        last_action_time[client_ip] = current_time
        
        # Verificar autenticação
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function