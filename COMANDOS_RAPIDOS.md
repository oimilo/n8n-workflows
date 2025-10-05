# ⚡ Comandos Rápidos - Cheat Sheet

## 🍴 Criar Fork e Deploy

### Passo 1: Fork no GitHub (Web)
```
1. Ir em: https://github.com/Zie619/n8n-workflows
2. Click "Fork" (canto superior direito)
3. Configurar nome: n8n-workflows-api
4. Click "Create fork"
```

### Passo 2: Clonar Seu Fork
```bash
cd F:\Cursor\
git clone https://github.com/SEU-USUARIO/n8n-workflows-api.git
cd n8n-workflows-api
```

### Passo 3: Copiar Arquivos Novos
```bash
# Copiar da pasta atual para o fork:
# - DISCORD_BOT_INTEGRATION.md
# - QUICK_START.md
# - RAILWAY_DEPLOY_GUIDE.md
# - START_LOCAL_TEST.md
# - discord_bot_example.py
# - requirements-discord-bot.txt
# - test_n8n_workflow.json
# - COMO_CRIAR_FORK_E_DEPLOY.md (este arquivo)
```

### Passo 4: Commit e Push
```bash
git add .
git commit -m "Adiciona docs e arquivos para Railway + Discord"
git push origin main
```

### Passo 5: Deploy no Railway (Web)
```
1. https://railway.app
2. Login com GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Selecionar: SEU-USUARIO/n8n-workflows-api
5. Click "Deploy"
6. Aguardar build (2-5 min)
7. Settings → Networking → "Generate Domain"
8. Copiar URL: https://seu-projeto.up.railway.app
```

---

## 🧪 Testar API

### Local:
```bash
# Iniciar servidor
python run.py

# Testar
curl http://127.0.0.1:8000/api/stats
```

### Produção:
```bash
# Testar
curl https://seu-projeto.up.railway.app/api/stats

# Ou abrir no navegador:
https://seu-projeto.up.railway.app/api/stats
https://seu-projeto.up.railway.app/docs
```

---

## 🔄 Fazer Mudanças

```bash
# 1. Editar arquivos
# ...

# 2. Testar localmente
python run.py

# 3. Commit
git add .
git commit -m "Descrição da mudança"

# 4. Push
git push origin main

# 5. Railway faz redeploy automático! 🚀
```

---

## 🎯 Endpoints Principais

```bash
# Base URL (produção)
BASE_URL="https://seu-projeto.up.railway.app/api"

# Estatísticas
curl $BASE_URL/stats

# Buscar workflows
curl "$BASE_URL/workflows?q=telegram&per_page=5"

# Categorias
curl $BASE_URL/categories

# Download workflow
curl "$BASE_URL/workflows/0001_Telegram.json/download"
```

---

## 🐛 Debug Rápido

### Ver logs Railway:
```
Dashboard → Deployments → Click deployment → Logs
```

### Verificar porta local:
```bash
netstat -ano | findstr :8000
```

### Matar processo:
```bash
taskkill /F /PID <PID>
```

### Reinstalar dependências:
```bash
pip install -r requirements.txt
```

---

## 📝 Checklist Rápido

Deploy completo:
- [ ] Fork criado
- [ ] Clonado localmente
- [ ] Arquivos copiados
- [ ] Push feito
- [ ] Railway deploy OK
- [ ] Domínio gerado
- [ ] API testada
- [ ] n8n testado

---

## 🚀 URLs Importantes

```bash
# Seu fork
https://github.com/SEU-USUARIO/n8n-workflows-api

# Railway dashboard
https://railway.app/dashboard

# Sua API (após deploy)
https://seu-projeto.up.railway.app

# Documentação interativa
https://seu-projeto.up.railway.app/docs
```

---

**Salve este arquivo para referência rápida! 📌**
