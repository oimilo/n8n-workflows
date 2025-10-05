# 🍴 Como Criar Fork e Fazer Deploy no Railway

## 📋 Passo a Passo Completo

### 1️⃣ Criar Fork no GitHub

1. **Acesse o repositório original:**
   ```
   https://github.com/Zie619/n8n-workflows
   ```

2. **Click no botão "Fork"** (canto superior direito)

3. **Configure o fork:**
   - ✅ Owner: Sua conta GitHub
   - ✅ Repository name: `n8n-workflows-api` (ou outro nome)
   - ✅ Description: "API de workflows N8N com integração Discord"
   - ⚠️ **DESMARQUE** "Copy the main branch only" (para manter histórico)
   - Click "Create fork"

4. **Aguardar criação** (10-30 segundos)

5. **Seu fork estará em:**
   ```
   https://github.com/SEU-USUARIO/n8n-workflows-api
   ```

---

### 2️⃣ Clonar Seu Fork Localmente

```bash
# Navegar para onde quer clonar
cd F:\Cursor\

# Clonar seu fork
git clone https://github.com/SEU-USUARIO/n8n-workflows-api.git

# Entrar na pasta
cd n8n-workflows-api

# Verificar remote
git remote -v
# Deve mostrar seu fork, não o original
```

---

### 3️⃣ Adicionar Arquivos Novos ao Fork

```bash
# Copiar os arquivos que criamos para o fork:
# - DISCORD_BOT_INTEGRATION.md
# - QUICK_START.md
# - RAILWAY_DEPLOY_GUIDE.md
# - START_LOCAL_TEST.md
# - discord_bot_example.py
# - requirements-discord-bot.txt
# - test_n8n_workflow.json

# Adicionar ao git
git add .

# Commit
git commit -m "Adiciona documentação e arquivos para deploy Railway + Discord Bot"

# Push para seu fork
git push origin main
```

---

### 4️⃣ Deploy no Railway com Seu Fork

1. **Acesse Railway:**
   ```
   https://railway.app
   ```

2. **Login com GitHub**

3. **New Project:**
   - Click "New Project"
   - Selecione "Deploy from GitHub repo"
   - **IMPORTANTE:** Selecione SEU fork: `SEU-USUARIO/n8n-workflows-api`
   - NÃO selecione o repositório original

4. **Railway detecta automaticamente:**
   - ✅ Dockerfile
   - ✅ requirements.txt
   - ✅ Estrutura do projeto

5. **Click "Deploy"**

6. **Aguardar build** (2-5 minutos):
   ```
   ⏳ Cloning repository...
   ⏳ Building Docker image...
   ⏳ Pushing to registry...
   ⏳ Deploying...
   ✅ Deployment successful!
   ```

7. **Gerar domínio público:**
   - Settings → Networking
   - Click "Generate Domain"
   - Copiar URL: `https://seu-projeto.up.railway.app`

---

### 5️⃣ Testar API em Produção

```bash
# Testar endpoint de estatísticas
curl https://seu-projeto.up.railway.app/api/stats

# Ou abrir no navegador:
https://seu-projeto.up.railway.app/api/stats
```

**Resposta esperada:**
```json
{
  "total": 2057,
  "active": 215,
  "unique_integrations": 311,
  ...
}
```

---

### 6️⃣ Testar no n8n (Produção)

1. **Abrir n8n**

2. **Criar workflow:**
   - Manual Trigger
   - HTTP Request:
     - URL: `https://seu-projeto.up.railway.app/api/stats`
     - Method: GET

3. **Executar e verificar resposta**

4. **Testar busca:**
   - URL: `https://seu-projeto.up.railway.app/api/workflows?q=telegram&per_page=5`

---

## 🔄 Workflow de Desenvolvimento

### Fazer mudanças no código:

```bash
# 1. Fazer alterações nos arquivos
# (editar api_server.py, workflow_db.py, etc.)

# 2. Testar localmente
python run.py

# 3. Commit
git add .
git commit -m "Descrição da mudança"

# 4. Push para seu fork
git push origin main

# 5. Railway faz deploy automático! 🚀
# (se configurado auto-deploy)
```

---

## 🎯 Vantagens do Fork

✅ **Controle total** - Você é dono do repositório
✅ **Mudanças livres** - Pode modificar o que quiser
✅ **Deploy automático** - Railway detecta commits e redeploy
✅ **Sem conflitos** - Não afeta o repositório original
✅ **Histórico limpo** - Suas mudanças separadas

---

## 🔧 Configurações Recomendadas no Railway

### Variáveis de Ambiente (opcional):
```
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=production
```

### Auto-Deploy:
- Settings → "Enable Auto-Deploy"
- Toda vez que fizer push, Railway redeploy automaticamente

### Health Check:
- Já configurado no Dockerfile
- Railway verifica: `http://localhost:8000/api/stats`

---

## 📊 Monitoramento

### Ver logs em tempo real:
```bash
# No Railway Dashboard:
1. Click no seu projeto
2. Aba "Deployments"
3. Click no deployment ativo
4. Ver "Logs"
```

### Métricas:
- CPU usage
- Memory usage
- Network traffic
- Request count

---

## 🆘 Troubleshooting

### Build falhou no Railway:
```bash
# Verificar logs no Railway
# Procurar por:
- "Module not found" → requirements.txt incompleto
- "Port already in use" → Configuração de porta
- "Database error" → Problema com workflows/
```

### Deploy OK mas API não responde:
```bash
# Verificar:
1. Health check está passando?
2. Porta 8000 está exposta?
3. Logs mostram "Uvicorn running"?
```

### Workflows não aparecem:
```bash
# Verificar se pasta workflows/ foi incluída no build
# Railway deve copiar todos os arquivos do repo
```

---

## 🚀 Próximos Passos

Depois do fork e deploy:

1. ✅ **Fork criado**
2. ✅ **Deploy no Railway**
3. ✅ **API funcionando em produção**
4. ✅ **Testado no n8n**
5. 🔜 **Integrar com Discord Bot**
6. 🔜 **Adicionar features customizadas**

---

## 💡 Dicas Importantes

### Manter fork atualizado com original:
```bash
# Adicionar remote do original
git remote add upstream https://github.com/Zie619/n8n-workflows.git

# Buscar atualizações
git fetch upstream

# Merge com seu fork (se quiser)
git merge upstream/main

# Push para seu fork
git push origin main
```

### Branches para features:
```bash
# Criar branch para nova feature
git checkout -b feature/discord-bot

# Fazer mudanças
# ...

# Commit e push
git push origin feature/discord-bot

# Railway pode fazer deploy de branches específicas
```

---

## 📝 Checklist Final

Antes de considerar pronto:

- [ ] Fork criado no GitHub
- [ ] Fork clonado localmente
- [ ] Arquivos novos adicionados ao fork
- [ ] Commit e push feitos
- [ ] Deploy no Railway configurado
- [ ] Domínio público gerado
- [ ] API respondendo em produção
- [ ] Testado no n8n com URL de produção
- [ ] Auto-deploy configurado (opcional)
- [ ] Documentação atualizada com nova URL

---

## 🎉 Resultado Final

Você terá:

```
GitHub (Seu Fork)
    ↓
Railway (Auto-Deploy)
    ↓
API Pública (https://seu-projeto.up.railway.app)
    ↓
n8n / Discord Bot (Consome a API)
```

---

**Pronto para criar o fork! 🍴**

Siga os passos acima e você terá sua própria versão da API rodando em produção!
