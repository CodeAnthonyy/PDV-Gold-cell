"""
Módulo de autenticação
Gerencia login, registro e verificação de usuários
"""

from database.engine import (
    register_user,
    login_user,
    get_total_users
)


def criar_primeiro_admin():
    """Verifica se existe usuário admin, se não, sugere criar"""
    total = get_total_users()
    return total == 0


def validar_credenciais(usuario, senha):
    """Valida as credenciais do usuário"""
    
    if not usuario or not senha:
        return {"status": False, "message": "Usuário e senha são obrigatórios!"}
    
    if len(usuario) < 3:
        return {"status": False, "message": "Usuário deve ter pelo menos 3 caracteres!"}
    
    if len(senha) < 4:
        return {"status": False, "message": "Senha deve ter pelo menos 4 caracteres!"}
    
    return {"status": True, "message": "Validação OK"}


def registrar_novo_usuario(usuario, senha):
    """Registra um novo usuário com validação"""
    
    # Valida as credenciais
    validacao = validar_credenciais(usuario, senha)
    if not validacao["status"]:
        return validacao
    
    # Registra o usuário
    return register_user(usuario, senha)


def autenticar_usuario(usuario, senha):
    """Autentica um usuário"""
    
    # Valida as credenciais
    validacao = validar_credenciais(usuario, senha)
    if not validacao["status"]:
        return validacao
    
    # Faz login
    return login_user(usuario, senha)
