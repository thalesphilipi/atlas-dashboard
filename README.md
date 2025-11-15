# Atlas Dashboard

Sistema de organização de dados pessoais desenvolvido em Flask com interface moderna e segura.



## 🚀 Características

- **Interface moderna**: Design responsivo com Tailwind CSS
- **Segurança**: Autenticação por senha master e rate limiting
- **Organização**: Sistema de categorias para organizar seus dados
- **Busca avançada**: Encontre rapidamente qualquer informação
- **Importação**: Carregue dados de arquivos JSON estruturados
- **Backup**: Funcionalidades para backup e restauração
- **Open Source**: Código aberto e gratuito

## 📋 Pré-requisitos

- Python 3.8+
- Flask
- SQLite (incluído no Python)

## 🔧 Instalação

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/atlas-dashboard.git
   cd atlas-dashboard
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente**
   ```bash
   cp .env.example .env
   ```
   
   Edite o arquivo `.env` e configure:
   - `SECRET_KEY`: Chave secreta única para sua instalação
   - `MASTER_PASSWORD`: Senha master para acesso ao sistema

4. **Execute a aplicação**
   ```bash
   python app.py
   ```

5. **Acesse o sistema**
   
   Abra seu navegador em `http://localhost:5000`


## 📊 Importação de Dados

O sistema permite importar dados de arquivos JSON. Coloque seu arquivo como `../dados_organizados.json` (pasta pai do projeto) com a seguinte estrutura:

```json
{
  "categoria1": [
    {
      "title": "Nome do item",
      "username": "usuario@exemplo.com", 
      "password": "senha123",
      "url": "https://exemplo.com",
      "notes": "Observações opcionais"
    }
  ],
  "categoria2": [
    // mais itens...
  ]
}
```

## 🔒 Segurança

- **Autenticação**: Sistema de senha master
- **Rate Limiting**: Proteção contra ataques de força bruta
- **Dados Locais**: Todos os dados ficam no seu computador
- **Criptografia**: Sessões protegidas com chave secreta

## 🛠️ Funcionalidades

### Dashboard
- Visão geral dos dados organizados
- Estatísticas de categorias e itens
- Acesso rápido aos itens recentes

### Organização
- Criação de categorias personalizadas
- Movimentação de itens entre categorias
- Edição e exclusão de dados

### Busca
- Busca por título, usuário, URL ou observações
- Filtros por categoria
- Resultados em tempo real

### Gerenciamento
- Alteração de senha master (atualização automática do .env)
- Remoção de duplicatas
- Operações em lote

## 💝 Apoie o Projeto

Se o Atlas Dashboard foi útil para você, considere fazer uma doação para ajudar no desenvolvimento:

### PIX (Brasil)

**Chave:** `+5535997541511`

![QR Code PIX](https://nexapp.com.br/wp-content/uploads/2025/06/qrcodedon.jpeg.webp)

### Criptomoedas

**MetaMask (ETH/BSC/Polygon):**
```
0x5da643C6d0E72C18fa5D63178Ea116e1309BD9d0
```

**Solana (SOL):**
```
YQLE7Heob5oXKy4nyjQCPP46xdFKzbTh7EGJ5jmTA1v
```

**Sui Network:**
```
0x2d9e999dd90ff4fdf321c01e1d6c3a2785ff4fcae3c67853a694d61aae82a233
```

Sua doação ajuda a:
- 🚀 Desenvolver novas funcionalidades
- 🛡️ Manter a segurança do sistema
- 📚 Criar documentação e tutoriais
- ❤️ Manter o projeto gratuito e open source

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Desenvolvedor

**Thales Philipi**
- LinkedIn: [https://www.linkedin.com/in/thalesphilipi/](https://www.linkedin.com/in/thalesphilipi/)
- Website: [NexApp.com.br](https://nexapp.com.br)

## 🆘 Suporte

Se você encontrar algum problema ou tiver sugestões:

1. Verifique se já existe uma [issue](https://github.com/seu-usuario/atlas-dashboard/issues) similar
2. Crie uma nova issue com detalhes do problema
3. Ou entre em contato através do LinkedIn

---

**Atlas Dashboard** - Organize seus dados pessoais de forma segura e eficiente.

*Desenvolvido com ❤️ por [Thales Philipi](https://www.linkedin.com/in/thalesphilipi/) | Powered by [NexApp.com.br](https://nexapp.com.br)*
