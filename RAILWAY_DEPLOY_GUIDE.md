# 🚂 Guia Rápido: Deploy no Railway

## 📋 Pré-requisitos
- ✅ Conta no GitHub
- ✅ Repositório com o código (este projeto)
- ✅ Dockerfile já configurado (✅ pronto!)

---

## 🚀 Passo 1: Preparar o Projeto

### Verificar arquivos necessários:
```bash
✅ Dockerfile              # Já existe
✅ requirements.txt        # Já existe
✅ run.py                  # Já existe
✅ api_server.py           # Já existe
✅ workflow_db.py          # Já existe
✅ workflows/ (2057 arquivos) # Já existe
```

**Status: Tudo pronto para deploy! ✅**

---

## 🚂 Passo 2: Deploy no Railway

### Opção A: Deploy Direto do GitHub (Recomendado)

1. **Acesse Railway:**
   - URL: https://railway.app
   - Click em "Login" → "Login with GitHub"

2. **Criar Novo Projeto:**
   - Click em "New Project"
   - Selecione "Deploy from GitHub repo"
   - Escolha o repositório: `n8n-workflows`
   - Railway detecta automaticamente o Dockerfile

3. **Configurar Deploy:**
   - Railway vai ler o Dockerfile automaticamente
   - Não precisa configurar nada!
   - Click em "Deploy"

4. **Aguardar Build:**
   ```
   ⏳ Building... (2-5 minutos)
   ✅ Build successful
   🚀 Deploying...
   ✅ Deployment live
   ```

5. **Gerar Domínio Público:**
   - No dashboard do projeto, click em "Settings"
   - Vá em "Networking" → "Generate Domain"
   - Você receberá: `https://seu-projeto.up.railway.app`

6. **Testar API:**
   ```bash
   # Testar endpoint de estatísticas
   curl https://seu-projeto.up.railway.app/api/stats
   
   # Ou abrir no navegador:
   https://seu-projeto.up.railway.app/api/stats
   ```

---

### Opção B: Deploy via Railway CLI

```bash
# 1. Instalar Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Inicializar projeto
railway init

# 4. Deploy
railway up

# 5. Abrir no navegador
railway open
```

---

## 🔧 Passo 3: Verificar Funcionamento

### Endpoints para testar:

1. **Estatísticas:**
   ```
   GET https://seu-projeto.up.railway.app/api/stats
   ```
   Deve retornar:
   ```json
   {
     "total": 2057,
     "active": 215,
     "triggers": {...},
     "unique_integrations": 365
   }
   ```

2. **Buscar workflows:**
   ```
   GET https://seu-projeto.up.railway.app/api/workflows?q=telegram&per_page=5
   ```

3. **Listar categorias:**
   ```
   GET https://seu-projeto.up.railway.app/api/categories
   ```

4. **Download de workflow:**
   ```
   GET https://seu-projeto.up.railway.app/api/workflows/0001_Telegram_Bot_Webhook.json/download
   ```

5. **Interface Web:**
   ```
   GET https://seu-projeto.up.railway.app/
   ```

---

## 🎯 Passo 4: Testar no n8n

### Criar Workflow de Teste no n8n:

1. **Adicionar nó HTTP Request:**
   - Method: `GET`
   - URL: `https://seu-projeto.up.railway.app/api/stats`
   - Authentication: None

2. **Executar e verificar resposta:**
   ```json
   {
     "total": 2057,
     "active": 215,
     ...
   }
   ```

3. **Teste de busca:**
   - Method: `GET`
   - URL: `https://seu-projeto.up.railway.app/api/workflows`
   - Query Parameters:
     - `q`: `telegram`
     - `per_page`: `10`

4. **Teste de download:**
   - Method: `GET`
   - URL: `https://seu-projeto.up.railway.app/api/workflows/{{$json["filename"]}}/download`
   - Isso vai baixar o JSON do workflow

---

## 📊 Exemplo de Workflow n8n Completo

### Workflow: "Buscar e Baixar Workflows da API"

```
┌─────────────────┐
│  Manual Trigger │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  HTTP Request   │ ← GET /api/stats
│  (Estatísticas) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  HTTP Request   │ ← GET /api/workflows?q=telegram
│  (Buscar)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Split Out      │ ← Separar workflows
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  HTTP Request   │ ← GET /api/workflows/{{filename}}/download
│  (Download)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Write File     │ ← Salvar JSON localmente
└─────────────────┘
```

### Código do Workflow (JSON):

```json
{
  "nodes": [
    {
      "parameters": {},
      "name": "Manual Trigger",
      "type": "n8n-nodes-base.manualTrigger",
      "position": [250, 300]
    },
    {
      "parameters": {
        "url": "https://seu-projeto.up.railway.app/api/stats",
        "options": {}
      },
      "name": "Get Stats",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300]
    },
    {
      "parameters": {
        "url": "https://seu-projeto.up.railway.app/api/workflows",
        "qs": {
          "q": "telegram",
          "per_page": "10"
        }
      },
      "name": "Search Workflows",
      "type": "n8n-nodes-base.httpRequest",
      "position": [650, 300]
    },
    {
      "parameters": {
        "fieldToSplitOut": "workflows"
      },
      "name": "Split Out",
      "type": "n8n-nodes-base.splitOut",
      "position": [850, 300]
    },
    {
      "parameters": {
        "url": "=https://seu-projeto.up.railway.app/api/workflows/{{$json[\"filename\"]}}/download"
      },
      "name": "Download Workflow",
      "type": "n8n-nodes-base.httpRequest",
      "position": [1050, 300]
    }
  ],
  "connections": {
    "Manual Trigger": {
      "main": [[{"node": "Get Stats", "type": "main", "index": 0}]]
    },
    "Get Stats": {
      "main": [[{"node": "Search Workflows", "type": "main", "index": 0}]]
    },
    "Search Workflows": {
      "main": [[{"node": "Split Out", "type": "main", "index": 0}]]
    },
    "Split Out": {
      "main": [[{"node": "Download Workflow", "type": "main", "index": 0}]]
    }
  }
}
```

---

## 💰 Custos do Railway

### Plano Gratuito:
- ✅ **$5 de crédito grátis/mês**
- ✅ **500 horas de execução**
- ✅ **100GB de banda**
- ✅ **1GB de RAM**

### Estimativa de uso:
```
API simples como esta:
- ~10-20MB de RAM
- ~1-5% CPU
- Banda: depende do uso

Estimativa: $0.50 - $2.00/mês
(Cabe no plano gratuito!)
```

---

## 🔍 Monitoramento

### Ver logs no Railway:
```bash
# No dashboard:
1. Click no projeto
2. Aba "Deployments"
3. Click no deployment ativo
4. Ver "Logs" em tempo real
```

### Logs importantes:
```
✅ Database connected: 2057 workflows indexed
🌐 Starting server at http://0.0.0.0:8000
📊 API Documentation: http://0.0.0.0:8000/docs
```

---

## 🐛 Troubleshooting

### Problema: Build falhou
**Solução:**
```bash
# Verificar se requirements.txt está correto
cat requirements.txt

# Deve conter:
fastapi>=0.104.0,<1.0.0
uvicorn[standard]>=0.24.0,<1.0.0
pydantic>=2.4.0,<3.0.0
```

### Problema: Deploy OK mas API não responde
**Solução:**
```bash
# Verificar logs no Railway
# Procurar por erros como:
- "Port already in use"
- "Database connection failed"
- "Module not found"
```

### Problema: Workflows não aparecem
**Solução:**
```bash
# Verificar se pasta workflows/ foi incluída no build
# No Railway, ir em Settings → Check "Include workflows folder"
```

---

## 🎯 Checklist Final

Antes de considerar pronto:

- [ ] Deploy no Railway concluído
- [ ] Domínio público gerado
- [ ] Endpoint `/api/stats` respondendo
- [ ] Endpoint `/api/workflows` respondendo
- [ ] Endpoint `/api/categories` respondendo
- [ ] Download de workflow funcionando
- [ ] Testado no n8n com HTTP Request
- [ ] Logs sem erros
- [ ] Performance < 200ms

---

## 🔗 Links Úteis

- **Railway Dashboard:** https://railway.app/dashboard
- **Railway Docs:** https://docs.railway.app/
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **n8n HTTP Request Node:** https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/

---

## 🎉 Próximos Passos

Depois que validar que está tudo funcionando:

1. ✅ **API funcionando no Railway**
2. ✅ **Testado no n8n**
3. 🔜 **Integrar com Discord Bot**
4. 🔜 **Adicionar autenticação (opcional)**
5. 🔜 **Adicionar analytics (opcional)**

---

**Pronto para deploy! 🚀**
