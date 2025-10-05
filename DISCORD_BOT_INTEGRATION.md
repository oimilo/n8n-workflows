# 🤖 Guia de Integração: API de Workflows + Bot Discord

## 📋 Visão Geral

Este guia mostra como:
1. ✅ Subir a API de workflows online (produção)
2. ✅ Criar endpoints otimizados para Discord Bot
3. ✅ Integrar o bot Discord com a API
4. ✅ Implementar comandos de busca e download

---

## 🚀 Parte 1: Subir a API Online

### Opção A: Deploy com Railway (Recomendado - Fácil)

**1. Criar conta no Railway:**
- Acesse: https://railway.app
- Faça login com GitHub
- Plano gratuito: $5 de crédito/mês

**2. Deploy direto do GitHub:**
```bash
# No Railway Dashboard:
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Escolha este repositório
4. Railway detecta automaticamente o Dockerfile
5. Click "Deploy"
```

**3. Configurar domínio:**
```bash
# No Railway:
Settings → Networking → Generate Domain
# Você receberá: https://seu-projeto.up.railway.app
```

**Pronto! API estará online em ~3 minutos** 🎉

---

### Opção B: Deploy com Render (Grátis)

**1. Criar conta no Render:**
- Acesse: https://render.com
- Plano gratuito disponível

**2. Criar Web Service:**
```yaml
# render.yaml (já incluído no projeto)
services:
  - type: web
    name: n8n-workflows-api
    env: docker
    plan: free
    healthCheckPath: /api/stats
```

**3. Deploy:**
```bash
1. Connect GitHub repository
2. Render detecta Dockerfile automaticamente
3. Click "Create Web Service"
```

---

### Opção C: Deploy com Docker (VPS/Cloud)

**1. Em qualquer servidor com Docker:**
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/n8n-workflows.git
cd n8n-workflows

# Build e start com Docker Compose
docker-compose up -d

# Verificar status
docker-compose ps
docker-compose logs -f
```

**2. Configurar Nginx (opcional):**
```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**3. SSL com Certbot:**
```bash
sudo certbot --nginx -d seu-dominio.com
```

---

## 🎯 Parte 2: Endpoints Disponíveis para o Bot

### 📊 1. Estatísticas Gerais
```http
GET /api/stats
```
**Resposta:**
```json
{
  "total": 2057,
  "active": 215,
  "triggers": {
    "Complex": 832,
    "Webhook": 521,
    "Manual": 478,
    "Scheduled": 226
  },
  "unique_integrations": 365
}
```

### 🔍 2. Buscar Workflows
```http
GET /api/workflows?q={query}&page={page}&per_page={limit}
```
**Parâmetros:**
- `q` - Termo de busca (ex: "telegram", "openai")
- `trigger` - Filtro: "Webhook", "Manual", "Scheduled", "Complex"
- `complexity` - Filtro: "low", "medium", "high"
- `active_only` - Boolean: mostrar só ativos
- `page` - Número da página (padrão: 1)
- `per_page` - Itens por página (máx: 100)

**Exemplo:**
```http
GET /api/workflows?q=telegram&per_page=5
```

**Resposta:**
```json
{
  "workflows": [
    {
      "id": 1,
      "filename": "0001_Telegram_Bot_Webhook.json",
      "name": "Telegram Bot Webhook",
      "active": true,
      "description": "Telegram bot automation",
      "trigger_type": "Webhook",
      "complexity": "medium",
      "node_count": 12,
      "integrations": ["Telegram", "HTTP Request"],
      "tags": ["bot", "messaging"]
    }
  ],
  "total": 119,
  "page": 1,
  "per_page": 5,
  "pages": 24
}
```

### 📥 3. Download de Workflow
```http
GET /api/workflows/{filename}/download
```
**Exemplo:**
```http
GET /api/workflows/0001_Telegram_Bot_Webhook.json/download
```
Retorna o arquivo JSON completo do workflow.

### 📂 4. Listar Categorias
```http
GET /api/categories
```
**Resposta:**
```json
{
  "categories": [
    "AI Agent Development",
    "Communication & Messaging",
    "Data Processing & Analysis",
    "E-commerce & Retail",
    ...
  ]
}
```

### 🏷️ 5. Buscar por Categoria
```http
GET /api/workflows/category/{category}
```
**Exemplo:**
```http
GET /api/workflows/category/Communication & Messaging
```

### 🔧 6. Detalhes de um Workflow
```http
GET /api/workflows/{filename}
```
**Resposta:**
```json
{
  "filename": "0001_Telegram_Bot_Webhook.json",
  "name": "Telegram Bot Webhook",
  "metadata": {
    "nodes": [...],
    "connections": {...},
    "settings": {...}
  }
}
```

---

## 🤖 Parte 3: Código do Bot Discord

### Estrutura do Bot

```python
# discord_bot.py
import discord
from discord.ext import commands
import aiohttp
import json

# Configuração
API_BASE_URL = "https://seu-dominio.com/api"  # ← Seu domínio aqui
BOT_TOKEN = "seu_token_discord"

# Criar bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Cliente HTTP para fazer requests
async def api_request(endpoint: str, params: dict = None):
    """Faz request para a API de workflows"""
    async with aiohttp.ClientSession() as session:
        url = f"{API_BASE_URL}{endpoint}"
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            return None

# ===== COMANDOS DO BOT =====

@bot.command(name="stats")
async def stats(ctx):
    """Mostra estatísticas dos workflows"""
    data = await api_request("/stats")
    
    if not data:
        await ctx.send("❌ Erro ao buscar estatísticas")
        return
    
    embed = discord.Embed(
        title="📊 Estatísticas de Workflows N8N",
        color=discord.Color.blue()
    )
    embed.add_field(name="Total", value=f"{data['total']} workflows", inline=True)
    embed.add_field(name="Ativos", value=f"{data['active']}", inline=True)
    embed.add_field(name="Integrações", value=f"{data['unique_integrations']}", inline=True)
    embed.add_field(
        name="Triggers",
        value=f"🔗 Webhook: {data['triggers'].get('Webhook', 0)}\n"
              f"⏰ Scheduled: {data['triggers'].get('Scheduled', 0)}\n"
              f"👆 Manual: {data['triggers'].get('Manual', 0)}\n"
              f"🔄 Complex: {data['triggers'].get('Complex', 0)}",
        inline=False
    )
    
    await ctx.send(embed=embed)


@bot.command(name="search")
async def search(ctx, *, query: str):
    """Busca workflows por termo
    Uso: !search telegram
    """
    data = await api_request("/workflows", {"q": query, "per_page": 10})
    
    if not data or not data.get('workflows'):
        await ctx.send(f"❌ Nenhum workflow encontrado para: **{query}**")
        return
    
    workflows = data['workflows']
    total = data['total']
    
    embed = discord.Embed(
        title=f"🔍 Resultados para: {query}",
        description=f"Encontrados {total} workflows (mostrando 10)",
        color=discord.Color.green()
    )
    
    for wf in workflows[:10]:
        integrations = ", ".join(wf.get('integrations', [])[:3])
        embed.add_field(
            name=f"{wf['name']}",
            value=f"📁 `{wf['filename']}`\n"
                  f"🔧 {integrations}\n"
                  f"📊 {wf['node_count']} nós | {wf['complexity']} complexity",
            inline=False
        )
    
    await ctx.send(embed=embed)


@bot.command(name="download")
async def download(ctx, filename: str):
    """Baixa um workflow específico
    Uso: !download 0001_Telegram_Bot_Webhook.json
    """
    # Buscar informações do workflow
    data = await api_request(f"/workflows/{filename}")
    
    if not data:
        await ctx.send(f"❌ Workflow não encontrado: **{filename}**")
        return
    
    # Criar embed com informações
    embed = discord.Embed(
        title=f"📥 {data['name']}",
        description=data.get('description', 'Sem descrição'),
        color=discord.Color.purple()
    )
    
    embed.add_field(name="Arquivo", value=f"`{filename}`", inline=False)
    embed.add_field(name="Nós", value=data.get('node_count', 'N/A'), inline=True)
    embed.add_field(name="Complexidade", value=data.get('complexity', 'N/A'), inline=True)
    embed.add_field(name="Trigger", value=data.get('trigger_type', 'N/A'), inline=True)
    
    # Link para download
    download_url = f"{API_BASE_URL}/workflows/{filename}/download"
    embed.add_field(
        name="📥 Download",
        value=f"[Clique aqui para baixar]({download_url})",
        inline=False
    )
    
    await ctx.send(embed=embed)


@bot.command(name="categories")
async def categories(ctx):
    """Lista todas as categorias disponíveis"""
    data = await api_request("/categories")
    
    if not data:
        await ctx.send("❌ Erro ao buscar categorias")
        return
    
    cats = data['categories']
    
    embed = discord.Embed(
        title="📂 Categorias Disponíveis",
        description=f"Total: {len(cats)} categorias",
        color=discord.Color.orange()
    )
    
    # Dividir em colunas
    half = len(cats) // 2
    embed.add_field(
        name="Categorias (1/2)",
        value="\n".join(f"• {cat}" for cat in cats[:half]),
        inline=True
    )
    embed.add_field(
        name="Categorias (2/2)",
        value="\n".join(f"• {cat}" for cat in cats[half:]),
        inline=True
    )
    
    embed.set_footer(text="Use !category <nome> para buscar workflows")
    
    await ctx.send(embed=embed)


@bot.command(name="category")
async def category(ctx, *, category_name: str):
    """Busca workflows por categoria
    Uso: !category Communication & Messaging
    """
    # URL encode da categoria
    from urllib.parse import quote
    encoded_cat = quote(category_name)
    
    data = await api_request(f"/workflows/category/{encoded_cat}")
    
    if not data or not data.get('workflows'):
        await ctx.send(f"❌ Nenhum workflow na categoria: **{category_name}**")
        return
    
    workflows = data['workflows']
    
    embed = discord.Embed(
        title=f"📂 Categoria: {category_name}",
        description=f"{len(workflows)} workflows encontrados",
        color=discord.Color.blue()
    )
    
    for wf in workflows[:10]:
        embed.add_field(
            name=wf['name'],
            value=f"`{wf['filename']}`",
            inline=False
        )
    
    if len(workflows) > 10:
        embed.set_footer(text=f"Mostrando 10 de {len(workflows)} workflows")
    
    await ctx.send(embed=embed)


@bot.command(name="random")
async def random_workflow(ctx):
    """Mostra um workflow aleatório"""
    import random
    
    # Buscar todos (primeira página)
    data = await api_request("/workflows", {"per_page": 100})
    
    if not data or not data.get('workflows'):
        await ctx.send("❌ Erro ao buscar workflows")
        return
    
    wf = random.choice(data['workflows'])
    
    embed = discord.Embed(
        title=f"🎲 Workflow Aleatório: {wf['name']}",
        description=wf.get('description', 'Sem descrição'),
        color=discord.Color.gold()
    )
    
    embed.add_field(name="Arquivo", value=f"`{wf['filename']}`", inline=False)
    embed.add_field(name="Nós", value=wf.get('node_count', 'N/A'), inline=True)
    embed.add_field(name="Trigger", value=wf.get('trigger_type', 'N/A'), inline=True)
    
    integrations = ", ".join(wf.get('integrations', [])[:5])
    embed.add_field(name="Integrações", value=integrations, inline=False)
    
    download_url = f"{API_BASE_URL}/workflows/{wf['filename']}/download"
    embed.add_field(name="📥 Download", value=f"[Link]({download_url})", inline=False)
    
    await ctx.send(embed=embed)


@bot.command(name="help_workflows")
async def help_workflows(ctx):
    """Mostra ajuda dos comandos de workflows"""
    embed = discord.Embed(
        title="🤖 Comandos de Workflows N8N",
        description="Lista de comandos disponíveis",
        color=discord.Color.blue()
    )
    
    commands_list = [
        ("!stats", "Mostra estatísticas gerais"),
        ("!search <termo>", "Busca workflows por termo"),
        ("!download <arquivo>", "Baixa um workflow específico"),
        ("!categories", "Lista todas as categorias"),
        ("!category <nome>", "Busca workflows por categoria"),
        ("!random", "Mostra um workflow aleatório"),
        ("!help_workflows", "Mostra esta mensagem"),
    ]
    
    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.set_footer(text="Bot de Workflows N8N | 2057 workflows disponíveis")
    
    await ctx.send(embed=embed)


@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    print(f"🌐 API: {API_BASE_URL}")
    print(f"📊 Servidores: {len(bot.guilds)}")


# Iniciar bot
if __name__ == "__main__":
    bot.run(BOT_TOKEN)
```

---

## 📦 Parte 4: Instalação do Bot

### 1. Criar Bot no Discord

```bash
1. Acesse: https://discord.com/developers/applications
2. Click "New Application"
3. Vá em "Bot" → "Add Bot"
4. Copie o TOKEN
5. Em "OAuth2" → "URL Generator":
   - Selecione: bot
   - Permissions: Send Messages, Embed Links, Read Messages
   - Copie a URL e adicione o bot ao servidor
```

### 2. Instalar Dependências

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar discord.py
pip install discord.py aiohttp
```

### 3. Configurar e Executar

```python
# Editar discord_bot.py:
API_BASE_URL = "https://seu-dominio.railway.app/api"
BOT_TOKEN = "seu_token_aqui"

# Executar
python discord_bot.py
```

---

## 🎮 Parte 5: Uso no Discord

### Comandos Disponíveis:

```bash
!stats                          # Estatísticas gerais
!search telegram                # Buscar workflows
!download 0001_Telegram.json    # Baixar workflow
!categories                     # Listar categorias
!category Communication         # Workflows por categoria
!random                         # Workflow aleatório
!help_workflows                 # Ajuda
```

### Exemplos de Uso:

```
Usuário: !search openai
Bot: 🔍 Encontrados 8 workflows com "openai"
     [Lista com embeds bonitos]

Usuário: !download 0966_OpenAI_Data_Processing_Manual.json
Bot: 📥 OpenAI Data Processing Manual
     [Embed com detalhes + link de download]

Usuário: !random
Bot: 🎲 Workflow Aleatório: Telegram Bot Webhook
     [Detalhes + link]
```

---

## 🔒 Parte 6: Segurança e Otimização

### Rate Limiting (Adicionar ao api_server.py)

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

@app.get("/api/workflows")
@limiter.limit("30/minute")  # 30 requests por minuto
async def search_workflows(...):
    ...
```

### CORS para Discord (Já configurado)

```python
# Em api_server.py (linha 31-37)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite Discord
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Cache para Performance

```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache de 5 minutos
cache_time = {}
cache_data = {}

async def cached_api_request(endpoint):
    now = datetime.now()
    if endpoint in cache_time:
        if now - cache_time[endpoint] < timedelta(minutes=5):
            return cache_data[endpoint]
    
    data = await api_request(endpoint)
    cache_time[endpoint] = now
    cache_data[endpoint] = data
    return data
```

---

## 📊 Parte 7: Monitoramento

### Logs da API

```bash
# Ver logs no Railway
railway logs

# Ver logs no Docker
docker-compose logs -f

# Ver logs locais
tail -f logs/api.log
```

### Health Check

```python
# Adicionar ao bot
@bot.command(name="api_status")
async def api_status(ctx):
    """Verifica status da API"""
    try:
        data = await api_request("/stats")
        if data:
            await ctx.send("✅ API Online e funcionando!")
        else:
            await ctx.send("⚠️ API respondeu mas sem dados")
    except:
        await ctx.send("❌ API Offline ou com problemas")
```

---

## 🎯 Checklist de Deploy

- [ ] API subida online (Railway/Render/VPS)
- [ ] Domínio configurado e funcionando
- [ ] Testar endpoints manualmente (Postman/curl)
- [ ] Bot Discord criado e token copiado
- [ ] Bot adicionado ao servidor Discord
- [ ] Código do bot configurado com API_URL
- [ ] Bot executando e respondendo comandos
- [ ] Rate limiting configurado
- [ ] Logs e monitoramento ativos
- [ ] Backup do banco de dados configurado

---

## 🆘 Troubleshooting

### API não responde:
```bash
# Verificar se está rodando
curl https://seu-dominio.com/api/stats

# Ver logs
railway logs  # ou docker-compose logs
```

### Bot não conecta:
```python
# Verificar token
print(BOT_TOKEN)  # Deve começar com "MTE..."

# Verificar intents
intents = discord.Intents.default()
intents.message_content = True  # ← Importante!
```

### CORS errors:
```python
# Garantir que CORS está configurado
allow_origins=["*"]  # Permite todas as origens
```

---

## 🚀 Próximos Passos

1. **Slash Commands**: Migrar para comandos slash (/)
2. **Buttons**: Adicionar botões interativos
3. **Paginação**: Navegar entre resultados
4. **Favoritos**: Sistema de workflows favoritos por usuário
5. **Analytics**: Rastrear workflows mais baixados

---

## 📚 Recursos Adicionais

- **Discord.py Docs**: https://discordpy.readthedocs.io/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Railway Docs**: https://docs.railway.app/
- **N8N Docs**: https://docs.n8n.io/

---

**Pronto! Agora você tem tudo para criar um bot Discord incrível que busca e disponibiliza workflows N8N! 🎉**
