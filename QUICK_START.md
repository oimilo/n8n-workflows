# 🚀 Quick Start - API de Workflows N8N

## ✅ Status Atual

**A API está funcionando localmente!** 🎉

```
✅ Servidor rodando em: http://127.0.0.1:8000
✅ Total de workflows: 2,057
✅ Integrações únicas: 311
✅ Total de nós: 76,618
```

---

## 🧪 Endpoints Testados e Funcionando

### 1. Estatísticas
```
GET http://127.0.0.1:8000/api/stats
```
✅ **Funcionando!** Retorna estatísticas completas.

### 2. Buscar Workflows
```
GET http://127.0.0.1:8000/api/workflows?q=telegram&per_page=5
```
✅ Pronto para testar

### 3. Categorias
```
GET http://127.0.0.1:8000/api/categories
```
✅ Pronto para testar

### 4. Download de Workflow
```
GET http://127.0.0.1:8000/api/workflows/{filename}/download
```
✅ Pronto para testar

### 5. Interface Web
```
GET http://127.0.0.1:8000/
```
✅ Disponível

### 6. Documentação Interativa
```
GET http://127.0.0.1:8000/docs
```
✅ Swagger UI disponível

---

## 🎯 Próximos Passos

### 1️⃣ Testar no n8n (AGORA)

**Criar workflow de teste:**

1. Abrir n8n
2. Criar novo workflow
3. Adicionar nó **HTTP Request**:
   - **Method:** GET
   - **URL:** `http://127.0.0.1:8000/api/stats`
   - **Authentication:** None
4. Executar e verificar resposta

**Resultado esperado:**
```json
{
  "total": 2057,
  "active": 215,
  "triggers": {...},
  "unique_integrations": 311
}
```

---

### 2️⃣ Testar Busca no n8n

**Workflow: Buscar workflows por termo**

1. Adicionar nó **HTTP Request**:
   - **Method:** GET
   - **URL:** `http://127.0.0.1:8000/api/workflows`
   - **Query Parameters:**
     - `q`: `telegram`
     - `per_page`: `5`

2. Executar

3. Adicionar nó **Split Out**:
   - **Field to Split Out:** `workflows`

4. Ver cada workflow separado

---

### 3️⃣ Testar Download no n8n

**Workflow: Baixar workflow específico**

1. Usar resultado do passo anterior

2. Adicionar nó **HTTP Request**:
   - **Method:** GET
   - **URL:** `http://127.0.0.1:8000/api/workflows/{{ $json.filename }}/download`

3. Executar

4. Ver o JSON completo do workflow

---

### 4️⃣ Importar Workflow de Teste Completo

Use o arquivo: **`test_n8n_workflow.json`**

1. Abrir n8n
2. Menu → Import from File
3. Selecionar `test_n8n_workflow.json`
4. **IMPORTANTE:** Substituir `SEU-PROJETO.up.railway.app` por `127.0.0.1:8000`
5. Executar workflow completo

**O workflow faz:**
- ✅ Busca estatísticas
- ✅ Busca workflows com termo "telegram"
- ✅ Separa cada workflow
- ✅ Baixa o JSON de cada um
- ✅ Formata a saída

---

## 🚂 Deploy no Railway (Depois de Validar)

Quando confirmar que está tudo funcionando no n8n:

### Passo 1: Commit e Push
```bash
git add .
git commit -m "API de workflows pronta para produção"
git push origin main
```

### Passo 2: Railway Deploy
1. Acesse: https://railway.app
2. Login com GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Selecione: `n8n-workflows`
5. Railway detecta Dockerfile automaticamente
6. Click "Deploy"
7. Aguardar build (2-5 minutos)

### Passo 3: Gerar Domínio
1. Settings → Networking
2. "Generate Domain"
3. Copiar URL: `https://seu-projeto.up.railway.app`

### Passo 4: Testar Produção
```bash
# Testar endpoint
curl https://seu-projeto.up.railway.app/api/stats

# Ou abrir no navegador
https://seu-projeto.up.railway.app/api/stats
```

### Passo 5: Atualizar n8n
- Substituir `127.0.0.1:8000` por `seu-projeto.up.railway.app`
- Testar todos os workflows novamente

---

## 📊 Endpoints Disponíveis para o Bot Discord

Quando estiver no Railway, estes endpoints estarão disponíveis:

### Base URL
```
https://seu-projeto.up.railway.app/api
```

### Endpoints Principais

| Endpoint | Descrição | Exemplo |
|----------|-----------|---------|
| `GET /stats` | Estatísticas gerais | `/stats` |
| `GET /workflows` | Buscar workflows | `/workflows?q=telegram&per_page=10` |
| `GET /workflows/{filename}` | Detalhes de workflow | `/workflows/0001_Telegram.json` |
| `GET /workflows/{filename}/download` | Download JSON | `/workflows/0001_Telegram.json/download` |
| `GET /categories` | Listar categorias | `/categories` |
| `GET /workflows/category/{cat}` | Por categoria | `/workflows/category/Communication` |

### Filtros Disponíveis

**Busca:**
- `q` - Termo de busca
- `trigger` - Tipo: Webhook, Manual, Scheduled, Complex
- `complexity` - Nível: low, medium, high
- `active_only` - Boolean: true/false
- `page` - Número da página
- `per_page` - Itens por página (máx: 100)

**Exemplo:**
```
/api/workflows?q=openai&trigger=Webhook&complexity=high&per_page=20
```

---

## 🤖 Integração com Discord Bot (Futuro)

Quando a API estiver no Railway, você poderá:

1. **Criar bot Discord** que consome a API
2. **Comandos sugeridos:**
   - `!search telegram` - Buscar workflows
   - `!download <filename>` - Baixar workflow
   - `!stats` - Ver estatísticas
   - `!categories` - Listar categorias
   - `!random` - Workflow aleatório

3. **O bot fará requests para:**
   ```
   https://seu-projeto.up.railway.app/api/workflows?q=...
   ```

---

## ✅ Checklist de Validação

### Local (Agora):
- [x] API rodando localmente
- [x] Endpoint `/api/stats` funcionando
- [ ] Testado no n8n com HTTP Request
- [ ] Busca funcionando no n8n
- [ ] Download funcionando no n8n
- [ ] Workflow de teste completo executado

### Produção (Depois):
- [ ] Deploy no Railway concluído
- [ ] Domínio público gerado
- [ ] API respondendo em produção
- [ ] Testado no n8n (produção)
- [ ] Performance validada
- [ ] Logs sem erros

---

## 🎯 Foco Atual

**AGORA: Testar no n8n localmente**

1. ✅ API funcionando (FEITO)
2. 🔄 Testar no n8n (PRÓXIMO PASSO)
3. ⏳ Deploy no Railway (DEPOIS)
4. ⏳ Integrar com Discord (FUTURO)

---

## 💡 Comandos Úteis

### Parar servidor:
```bash
# Pressionar Ctrl+C no terminal onde está rodando
```

### Reiniciar servidor:
```bash
python run.py
```

### Ver logs:
```bash
# Logs aparecem no terminal
```

### Testar endpoint rapidamente:
```bash
# Abrir no navegador:
http://127.0.0.1:8000/docs

# Testar todos os endpoints interativamente
```

---

## 🆘 Problemas?

### API não responde:
```bash
# Verificar se está rodando
netstat -ano | findstr :8000

# Reiniciar
python run.py
```

### Erro no n8n:
- Verificar URL: `http://127.0.0.1:8000` (não `localhost`)
- Verificar se API está rodando
- Verificar firewall

---

**Próximo passo: Testar no n8n! 🚀**

Abra o n8n e crie um workflow de teste com HTTP Request apontando para:
```
http://127.0.0.1:8000/api/stats
```
