# 🧪 Teste Local Antes do Deploy

## 📋 Passo a Passo para Testar Localmente

### 1️⃣ Instalar Dependências

```bash
# Verificar se tem Python 3.7+
python --version

# Instalar dependências
pip install -r requirements.txt

# Verificar instalação
pip list | findstr "fastapi uvicorn pydantic"
```

Deve mostrar:
```
fastapi         0.104.x
uvicorn         0.24.x
pydantic        2.4.x
```

---

### 2️⃣ Iniciar Servidor Local

```bash
# Opção 1: Comando simples
python run.py

# Opção 2: Com configurações customizadas
python run.py --host 127.0.0.1 --port 8000

# Opção 3: Modo desenvolvimento (auto-reload)
python run.py --dev
```

**Saída esperada:**
```
🚀 n8n-workflows Advanced Search Engine
==================================================
✅ Dependencies verified
✅ Directories verified
🔄 Setting up database: database/workflows.db
📚 Indexing workflows...
✅ Indexed 2057 workflows
📊 Database contains 2057 workflows
🌐 Starting server at http://127.0.0.1:8000
📊 API Documentation: http://127.0.0.1:8000/docs
🔍 Workflow Search: http://127.0.0.1:8000/api/workflows

Press Ctrl+C to stop the server
--------------------------------------------------
```

---

### 3️⃣ Testar Endpoints

#### Teste 1: Estatísticas
```bash
# PowerShell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/stats"

# Ou abrir no navegador:
http://127.0.0.1:8000/api/stats
```

**Resposta esperada:**
```json
{
  "total": 2057,
  "active": 215,
  "inactive": 1842,
  "triggers": {
    "Complex": 832,
    "Webhook": 521,
    "Manual": 478,
    "Scheduled": 226
  },
  "complexity": {
    "low": 720,
    "medium": 925,
    "high": 412
  },
  "total_nodes": 29528,
  "unique_integrations": 365,
  "last_indexed": "2025-01-27 12:00:00"
}
```

#### Teste 2: Buscar Workflows
```bash
# PowerShell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/workflows?q=telegram&per_page=3"

# Ou no navegador:
http://127.0.0.1:8000/api/workflows?q=telegram&per_page=3
```

#### Teste 3: Listar Categorias
```bash
http://127.0.0.1:8000/api/categories
```

#### Teste 4: Interface Web
```bash
# Abrir no navegador:
http://127.0.0.1:8000/
```

#### Teste 5: Documentação Interativa
```bash
# Swagger UI (OpenAPI):
http://127.0.0.1:8000/docs

# ReDoc:
http://127.0.0.1:8000/redoc
```

---

### 4️⃣ Testar no n8n

1. **Abrir n8n** (local ou cloud)

2. **Criar novo workflow**

3. **Adicionar nó "HTTP Request":**
   - **Method:** GET
   - **URL:** `http://127.0.0.1:8000/api/stats`
   - **Authentication:** None
   - **Response Format:** JSON

4. **Executar o nó**

5. **Verificar resposta:**
   - Deve retornar JSON com estatísticas
   - Status code: 200

6. **Testar busca:**
   - **URL:** `http://127.0.0.1:8000/api/workflows`
   - **Query Parameters:**
     - `q`: `telegram`
     - `per_page`: `5`

7. **Importar workflow de teste:**
   - Usar o arquivo: `test_n8n_workflow.json`
   - Substituir `SEU-PROJETO.up.railway.app` por `127.0.0.1:8000`
   - Executar e verificar resultados

---

## ✅ Checklist de Validação

Antes de fazer deploy no Railway, verificar:

- [ ] Servidor inicia sem erros
- [ ] Endpoint `/api/stats` responde
- [ ] Endpoint `/api/workflows` responde
- [ ] Busca por termo funciona (`?q=telegram`)
- [ ] Filtros funcionam (`?trigger=Webhook`)
- [ ] Paginação funciona (`?page=2&per_page=10`)
- [ ] Download de workflow funciona
- [ ] Interface web carrega (`/`)
- [ ] Documentação API carrega (`/docs`)
- [ ] Testado no n8n com HTTP Request
- [ ] Performance < 200ms

---

## 🐛 Problemas Comuns

### Erro: "Module not found"
```bash
# Solução: Instalar dependências
pip install -r requirements.txt
```

### Erro: "Port already in use"
```bash
# Solução: Usar outra porta
python run.py --port 8001

# Ou matar processo na porta 8000
# Windows:
netstat -ano | findstr :8000
taskkill /F /PID <PID>

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

### Erro: "No workflows found"
```bash
# Solução: Reindexar workflows
python run.py --reindex
```

### Erro: "Database locked"
```bash
# Solução: Remover banco e recriar
rm database/workflows.db
python run.py --reindex
```

---

## 📊 Performance Esperada

### Métricas locais:
- **Startup:** 5-10 segundos (primeira vez)
- **Startup:** 1-2 segundos (subsequentes)
- **GET /api/stats:** < 50ms
- **GET /api/workflows:** < 100ms
- **GET /api/workflows (com busca):** < 150ms
- **Download workflow:** < 200ms

### Uso de recursos:
- **RAM:** 50-100MB
- **CPU:** 1-5% (idle)
- **Disco:** ~100MB (database + workflows)

---

## 🎯 Próximo Passo

Quando tudo estiver funcionando localmente:

1. ✅ **Validado localmente**
2. 🔜 **Fazer commit das mudanças**
3. 🔜 **Push para GitHub**
4. 🔜 **Deploy no Railway**
5. 🔜 **Testar no Railway**
6. 🔜 **Integrar com n8n (produção)**

---

## 💡 Dicas

### Desenvolvimento:
```bash
# Usar modo dev para auto-reload
python run.py --dev

# Ver logs detalhados
python run.py --dev --log-level debug
```

### Teste de carga:
```bash
# Instalar Apache Bench
# Windows: baixar de https://www.apachelounge.com/

# Testar performance
ab -n 1000 -c 10 http://127.0.0.1:8000/api/stats
```

### Monitorar logs:
```bash
# Logs ficam em: logs/api.log (se configurado)
# Ou ver no terminal em tempo real
```

---

**Tudo pronto para testar! 🚀**

Execute `python run.py` e comece os testes!
