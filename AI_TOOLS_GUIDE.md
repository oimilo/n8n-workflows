# 🤖 AI Agent Tools - N8N Workflows API

## 📋 Visão Geral

6 Tools HTTP Request prontas para seu AI Agent usar para buscar workflows!

---

## 🛠️ Tools Disponíveis

### 1️⃣ **search_workflows**
**Descrição:** Busca workflows por palavra-chave

**Parâmetros:**
- `query` (string): Termo de busca (ex: "telegram", "openai")
- `per_page` (number): Quantidade de resultados (padrão: 10, máx: 100)
- `trigger` (string): Filtro de trigger (Webhook, Manual, Scheduled, Complex, all)
- `complexity` (string): Filtro de complexidade (low, medium, high, all)

**Exemplo de uso pelo AI:**
```
User: "Find telegram workflows"
AI: Calls search_workflows(query="telegram", per_page=10)
```

---

### 2️⃣ **get_workflow_stats**
**Descrição:** Retorna estatísticas da coleção

**Parâmetros:** Nenhum

**Retorna:**
- Total de workflows
- Workflows ativos
- Distribuição de triggers
- Distribuição de complexidade
- Total de integrações únicas

**Exemplo:**
```
User: "How many workflows are available?"
AI: Calls get_workflow_stats()
AI: "There are 2,057 workflows available with 311 unique integrations!"
```

---

### 3️⃣ **list_categories**
**Descrição:** Lista todas as categorias disponíveis

**Parâmetros:** Nenhum

**Retorna:** Array de categorias

**Exemplo:**
```
User: "What categories are available?"
AI: Calls list_categories()
AI: Lists all 15 categories
```

---

### 4️⃣ **get_workflows_by_category**
**Descrição:** Busca workflows de uma categoria específica

**Parâmetros:**
- `category` (string): Nome da categoria

**Exemplo:**
```
User: "Show me AI workflows"
AI: Calls get_workflows_by_category(category="AI Agent Development")
```

---

### 5️⃣ **get_workflow_details**
**Descrição:** Detalhes completos de um workflow específico

**Parâmetros:**
- `filename` (string): Nome do arquivo do workflow

**Retorna:**
- Nome
- Descrição
- Nós
- Conexões
- Metadados

**Exemplo:**
```
User: "Tell me more about workflow 0001_Telegram_Bot_Webhook.json"
AI: Calls get_workflow_details(filename="0001_Telegram_Bot_Webhook.json")
```

---

### 6️⃣ **download_workflow**
**Descrição:** Baixa o JSON completo do workflow

**Parâmetros:**
- `filename` (string): Nome do arquivo

**Retorna:** JSON completo do workflow

**Exemplo:**
```
User: "Download the telegram bot workflow"
AI: Calls download_workflow(filename="0001_Telegram_Bot_Webhook.json")
```

---

## 🚀 Como Usar

### Passo 1: Importar Workflow
1. Abrir n8n
2. Menu → Import from File
3. Selecionar: `n8n_ai_tools_workflows.json`
4. Configurar credenciais OpenAI

### Passo 2: Testar
```
User: "Find workflows about Discord"
AI: Uses search_workflows tool
AI: Returns list of Discord workflows

User: "Show me statistics"
AI: Uses get_workflow_stats tool
AI: Shows collection stats

User: "What categories exist?"
AI: Uses list_categories tool
AI: Lists all categories
```

---

## 💡 Exemplos de Conversas

### Exemplo 1: Busca Simples
```
👤 User: "I need a telegram bot workflow"

🤖 AI: *calls search_workflows(query="telegram", per_page=5)*

🤖 AI: "I found 185 Telegram workflows! Here are the top 5:

1. **Telegram Bot Webhook** (0001_Telegram_Bot_Webhook.json)
   - 12 nodes | Medium complexity
   - Webhook trigger

2. **Telegram Message Handler** (0045_Telegram_Message_Handler.json)
   - 8 nodes | Low complexity
   - Manual trigger

Would you like more details on any of these?"
```

### Exemplo 2: Busca com Filtros
```
👤 User: "Show me complex OpenAI workflows"

🤖 AI: *calls search_workflows(query="openai", complexity="high", per_page=10)*

🤖 AI: "Found 12 complex OpenAI workflows:

1. **OpenAI Advanced Agent** - 25 nodes
2. **OpenAI Data Processing Pipeline** - 32 nodes
3. **OpenAI Multi-Model Comparison** - 28 nodes

These are advanced workflows with sophisticated logic. Would you like to see details or download any?"
```

### Exemplo 3: Exploração por Categoria
```
👤 User: "What AI-related workflows do you have?"

🤖 AI: *calls list_categories()*
🤖 AI: *calls get_workflows_by_category(category="AI Agent Development")*

🤖 AI: "I found 45 workflows in the 'AI Agent Development' category:

- OpenAI integrations: 15 workflows
- Anthropic Claude: 8 workflows
- Hugging Face: 12 workflows
- Custom AI agents: 10 workflows

Which type interests you?"
```

### Exemplo 4: Estatísticas
```
👤 User: "Give me an overview of the collection"

🤖 AI: *calls get_workflow_stats()*

🤖 AI: "Here's an overview of the workflow collection:

📊 **Total**: 2,057 workflows
✅ **Active**: 215 workflows
🔌 **Integrations**: 311 unique services

**By Trigger Type:**
- Webhook: 543 workflows
- Manual: 565 workflows
- Scheduled: 227 workflows
- Complex: 722 workflows

**By Complexity:**
- Low: 35 workflows
- Medium: 451 workflows
- High: 1,571 workflows

What would you like to explore?"
```

---

## 🎯 System Prompt (Já Incluído)

```
You are a helpful AI assistant that helps users find and explore n8n workflows.

You have access to a collection of 2,057 n8n workflows with 311 unique integrations.

Available tools:
- search_workflows: Search workflows by keyword
- get_workflow_stats: Get collection statistics
- list_categories: List all categories
- get_workflows_by_category: Get workflows in a category
- get_workflow_details: Get detailed info about a workflow
- download_workflow: Download workflow JSON

When users ask about workflows:
1. Use search_workflows to find relevant workflows
2. Present results in a clear, organized way
3. Include filename, description, complexity, and node count
4. Offer to provide more details or download links

Be helpful, concise, and always provide actionable information.
```

---

## 🔧 Customização

### Trocar Modelo AI:
- OpenAI GPT-4
- Anthropic Claude
- Google Gemini
- Ollama (local)

### Adicionar Mais Tools:
```json
{
  "name": "get_integrations",
  "description": "List all available integrations",
  "url": "https://n8n-workflows-production-fb1e.up.railway.app/api/integrations"
}
```

### Melhorar System Prompt:
- Adicionar personalidade
- Incluir exemplos específicos
- Definir formato de resposta

---

## 📊 Endpoints Usados

| Tool | Endpoint | Método |
|------|----------|--------|
| search_workflows | `/api/workflows` | GET |
| get_workflow_stats | `/api/stats` | GET |
| list_categories | `/api/categories` | GET |
| get_workflows_by_category | `/api/workflows/category/{cat}` | GET |
| get_workflow_details | `/api/workflows/{filename}` | GET |
| download_workflow | `/api/workflows/{filename}/download` | GET |

---

## ✅ Checklist

- [ ] Workflow importado no n8n
- [ ] Credenciais OpenAI configuradas
- [ ] Tools testadas individualmente
- [ ] AI Agent respondendo corretamente
- [ ] System prompt ajustado
- [ ] Memória funcionando (conversa contextual)

---

## 🎉 Resultado Final

Você terá um AI Agent que pode:
- ✅ Buscar workflows por termo
- ✅ Filtrar por categoria, trigger, complexidade
- ✅ Fornecer estatísticas
- ✅ Detalhar workflows específicos
- ✅ Disponibilizar downloads
- ✅ Manter contexto da conversa

**Pronto para usar! 🚀**
