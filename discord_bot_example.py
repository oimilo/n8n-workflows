#!/usr/bin/env python3
"""
🤖 Bot Discord para N8N Workflows
Busca e disponibiliza workflows através de comandos Discord
"""

import discord
from discord.ext import commands
import aiohttp
import json
from typing import Optional, Dict, Any
from urllib.parse import quote
import random

# ==================== CONFIGURAÇÃO ====================
API_BASE_URL = "https://seu-dominio.railway.app/api"  # ← ALTERE AQUI
BOT_TOKEN = "seu_token_discord_aqui"  # ← ALTERE AQUI

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True

# Criar bot
bot = commands.Bot(command_prefix="!", intents=intents)

# ==================== FUNÇÕES AUXILIARES ====================

async def api_request(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
    """Faz request para a API de workflows"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{API_BASE_URL}{endpoint}"
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    return await response.json()
                print(f"❌ API Error: {response.status}")
                return None
    except Exception as e:
        print(f"❌ Request Error: {e}")
        return None


def create_workflow_embed(workflow: Dict, color: discord.Color = discord.Color.blue()) -> discord.Embed:
    """Cria um embed formatado para um workflow"""
    embed = discord.Embed(
        title=f"📋 {workflow.get('name', 'Sem nome')}",
        description=workflow.get('description', 'Sem descrição disponível')[:200],
        color=color
    )
    
    # Informações básicas
    embed.add_field(
        name="📁 Arquivo",
        value=f"`{workflow.get('filename', 'N/A')}`",
        inline=False
    )
    
    # Estatísticas
    stats_text = (
        f"📊 **Nós:** {workflow.get('node_count', 0)}\n"
        f"🔧 **Complexidade:** {workflow.get('complexity', 'N/A').title()}\n"
        f"🎯 **Trigger:** {workflow.get('trigger_type', 'N/A')}\n"
        f"{'✅' if workflow.get('active') else '⭕'} **Status:** {'Ativo' if workflow.get('active') else 'Inativo'}"
    )
    embed.add_field(name="📈 Estatísticas", value=stats_text, inline=True)
    
    # Integrações
    integrations = workflow.get('integrations', [])
    if integrations:
        integrations_text = ", ".join(integrations[:5])
        if len(integrations) > 5:
            integrations_text += f" +{len(integrations) - 5} mais"
        embed.add_field(name="🔌 Integrações", value=integrations_text, inline=True)
    
    # Link de download
    filename = workflow.get('filename', '')
    if filename:
        download_url = f"{API_BASE_URL}/workflows/{filename}/download"
        embed.add_field(
            name="📥 Download",
            value=f"[Clique aqui para baixar]({download_url})",
            inline=False
        )
    
    return embed


# ==================== COMANDOS DO BOT ====================

@bot.event
async def on_ready():
    """Evento quando o bot está pronto"""
    print("=" * 50)
    print(f"✅ Bot conectado como: {bot.user}")
    print(f"🌐 API Base URL: {API_BASE_URL}")
    print(f"📊 Servidores conectados: {len(bot.guilds)}")
    print(f"👥 Usuários alcançados: {sum(guild.member_count for guild in bot.guilds)}")
    print("=" * 50)
    
    # Testar conexão com API
    stats = await api_request("/stats")
    if stats:
        print(f"✅ API Online - {stats.get('total', 0)} workflows disponíveis")
    else:
        print("⚠️ API não respondeu - verifique a configuração")


@bot.command(name="stats")
async def stats(ctx):
    """📊 Mostra estatísticas dos workflows disponíveis"""
    async with ctx.typing():
        data = await api_request("/stats")
        
        if not data:
            await ctx.send("❌ Erro ao buscar estatísticas da API")
            return
        
        embed = discord.Embed(
            title="📊 Estatísticas de Workflows N8N",
            description="Biblioteca completa de automações",
            color=discord.Color.blue()
        )
        
        # Estatísticas principais
        embed.add_field(
            name="📚 Workflows",
            value=f"**Total:** {data.get('total', 0)}\n"
                  f"**Ativos:** {data.get('active', 0)}\n"
                  f"**Inativos:** {data.get('inactive', 0)}",
            inline=True
        )
        
        embed.add_field(
            name="🔧 Recursos",
            value=f"**Integrações:** {data.get('unique_integrations', 0)}\n"
                  f"**Total de Nós:** {data.get('total_nodes', 0):,}",
            inline=True
        )
        
        # Triggers
        triggers = data.get('triggers', {})
        if triggers:
            trigger_text = "\n".join([
                f"**{key}:** {value}" for key, value in triggers.items()
            ])
            embed.add_field(name="🎯 Tipos de Trigger", value=trigger_text, inline=False)
        
        # Complexidade
        complexity = data.get('complexity', {})
        if complexity:
            complexity_text = "\n".join([
                f"**{key.title()}:** {value}" for key, value in complexity.items()
            ])
            embed.add_field(name="📈 Complexidade", value=complexity_text, inline=False)
        
        # Última indexação
        last_indexed = data.get('last_indexed', 'N/A')
        embed.set_footer(text=f"Última atualização: {last_indexed}")
        
        await ctx.send(embed=embed)


@bot.command(name="search", aliases=["buscar", "find"])
async def search(ctx, *, query: str):
    """🔍 Busca workflows por termo
    
    Uso: !search telegram
         !search openai bot
    """
    async with ctx.typing():
        data = await api_request("/workflows", {"q": query, "per_page": 10})
        
        if not data or not data.get('workflows'):
            await ctx.send(f"❌ Nenhum workflow encontrado para: **{query}**")
            return
        
        workflows = data['workflows']
        total = data['total']
        
        embed = discord.Embed(
            title=f"🔍 Resultados para: {query}",
            description=f"Encontrados **{total}** workflows (mostrando até 10)",
            color=discord.Color.green()
        )
        
        for i, wf in enumerate(workflows[:10], 1):
            integrations = ", ".join(wf.get('integrations', [])[:3])
            if not integrations:
                integrations = "N/A"
            
            embed.add_field(
                name=f"{i}. {wf.get('name', 'Sem nome')}",
                value=f"📁 `{wf.get('filename', 'N/A')}`\n"
                      f"🔧 {integrations}\n"
                      f"📊 {wf.get('node_count', 0)} nós | {wf.get('complexity', 'N/A')} complexity",
                inline=False
            )
        
        if total > 10:
            embed.set_footer(text=f"💡 Use !download <arquivo> para baixar um workflow específico")
        
        await ctx.send(embed=embed)


@bot.command(name="download", aliases=["baixar", "get"])
async def download(ctx, *, filename: str):
    """📥 Baixa um workflow específico
    
    Uso: !download 0001_Telegram_Bot_Webhook.json
    """
    # Remover backticks se o usuário copiou do comando search
    filename = filename.strip('`')
    
    async with ctx.typing():
        data = await api_request(f"/workflows/{filename}")
        
        if not data:
            await ctx.send(f"❌ Workflow não encontrado: **{filename}**\n"
                          f"💡 Use `!search <termo>` para encontrar workflows")
            return
        
        embed = create_workflow_embed(data, discord.Color.purple())
        await ctx.send(embed=embed)


@bot.command(name="categories", aliases=["categorias", "cats"])
async def categories(ctx):
    """📂 Lista todas as categorias disponíveis"""
    async with ctx.typing():
        data = await api_request("/categories")
        
        if not data:
            await ctx.send("❌ Erro ao buscar categorias")
            return
        
        cats = data.get('categories', [])
        
        embed = discord.Embed(
            title="📂 Categorias Disponíveis",
            description=f"Total: **{len(cats)}** categorias",
            color=discord.Color.orange()
        )
        
        # Dividir em duas colunas
        half = (len(cats) + 1) // 2
        
        if cats:
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
        
        embed.set_footer(text="💡 Use !category <nome> para buscar workflows dessa categoria")
        
        await ctx.send(embed=embed)


@bot.command(name="category", aliases=["cat", "categoria"])
async def category(ctx, *, category_name: str):
    """🏷️ Busca workflows por categoria
    
    Uso: !category Communication & Messaging
         !category AI Agent Development
    """
    async with ctx.typing():
        # URL encode da categoria
        encoded_cat = quote(category_name)
        data = await api_request(f"/workflows/category/{encoded_cat}")
        
        if not data or not data.get('workflows'):
            await ctx.send(f"❌ Nenhum workflow na categoria: **{category_name}**\n"
                          f"💡 Use `!categories` para ver categorias disponíveis")
            return
        
        workflows = data['workflows']
        
        embed = discord.Embed(
            title=f"📂 Categoria: {category_name}",
            description=f"**{len(workflows)}** workflows encontrados",
            color=discord.Color.blue()
        )
        
        for i, wf in enumerate(workflows[:10], 1):
            embed.add_field(
                name=f"{i}. {wf.get('name', 'Sem nome')}",
                value=f"📁 `{wf.get('filename', 'N/A')}`\n"
                      f"📊 {wf.get('node_count', 0)} nós | {wf.get('trigger_type', 'N/A')}",
                inline=False
            )
        
        if len(workflows) > 10:
            embed.set_footer(text=f"Mostrando 10 de {len(workflows)} workflows")
        
        await ctx.send(embed=embed)


@bot.command(name="random", aliases=["aleatorio", "rand"])
async def random_workflow(ctx):
    """🎲 Mostra um workflow aleatório"""
    async with ctx.typing():
        # Buscar workflows (primeira página com 100 itens)
        data = await api_request("/workflows", {"per_page": 100})
        
        if not data or not data.get('workflows'):
            await ctx.send("❌ Erro ao buscar workflows")
            return
        
        wf = random.choice(data['workflows'])
        
        embed = create_workflow_embed(wf, discord.Color.gold())
        embed.title = f"🎲 Workflow Aleatório: {wf.get('name', 'Sem nome')}"
        
        await ctx.send(embed=embed)


@bot.command(name="filter", aliases=["filtrar"])
async def filter_workflows(ctx, trigger: str = "all", complexity: str = "all"):
    """🔎 Filtra workflows por trigger e complexidade
    
    Uso: !filter Webhook medium
         !filter Scheduled high
         !filter Manual all
    
    Triggers: Webhook, Scheduled, Manual, Complex, all
    Complexity: low, medium, high, all
    """
    async with ctx.typing():
        data = await api_request("/workflows", {
            "trigger": trigger,
            "complexity": complexity,
            "per_page": 10
        })
        
        if not data or not data.get('workflows'):
            await ctx.send(f"❌ Nenhum workflow encontrado com os filtros:\n"
                          f"**Trigger:** {trigger} | **Complexidade:** {complexity}")
            return
        
        workflows = data['workflows']
        total = data['total']
        
        embed = discord.Embed(
            title=f"🔎 Workflows Filtrados",
            description=f"**Trigger:** {trigger} | **Complexidade:** {complexity}\n"
                       f"Encontrados: **{total}** workflows (mostrando 10)",
            color=discord.Color.teal()
        )
        
        for i, wf in enumerate(workflows[:10], 1):
            embed.add_field(
                name=f"{i}. {wf.get('name', 'Sem nome')}",
                value=f"📁 `{wf.get('filename', 'N/A')}`\n"
                      f"📊 {wf.get('node_count', 0)} nós",
                inline=False
            )
        
        await ctx.send(embed=embed)


@bot.command(name="api_status", aliases=["status", "ping"])
async def api_status(ctx):
    """🏥 Verifica o status da API"""
    async with ctx.typing():
        try:
            data = await api_request("/stats")
            
            if data:
                embed = discord.Embed(
                    title="✅ API Online",
                    description="A API está funcionando normalmente",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="📊 Workflows Disponíveis",
                    value=f"{data.get('total', 0)} workflows",
                    inline=True
                )
                embed.add_field(
                    name="🔌 Integrações",
                    value=f"{data.get('unique_integrations', 0)} serviços",
                    inline=True
                )
                embed.add_field(
                    name="🌐 URL",
                    value=f"[{API_BASE_URL}]({API_BASE_URL})",
                    inline=False
                )
            else:
                embed = discord.Embed(
                    title="⚠️ API com Problemas",
                    description="A API respondeu mas sem dados válidos",
                    color=discord.Color.orange()
                )
        except Exception as e:
            embed = discord.Embed(
                title="❌ API Offline",
                description=f"Não foi possível conectar à API\n\n**Erro:** {str(e)}",
                color=discord.Color.red()
            )
        
        await ctx.send(embed=embed)


@bot.command(name="help_workflows", aliases=["ajuda", "comandos"])
async def help_workflows(ctx):
    """❓ Mostra ajuda dos comandos de workflows"""
    embed = discord.Embed(
        title="🤖 Comandos de Workflows N8N",
        description="Lista completa de comandos disponíveis",
        color=discord.Color.blue()
    )
    
    commands_list = [
        ("!stats", "📊 Mostra estatísticas gerais dos workflows"),
        ("!search <termo>", "🔍 Busca workflows por palavra-chave"),
        ("!download <arquivo>", "📥 Baixa um workflow específico"),
        ("!categories", "📂 Lista todas as categorias disponíveis"),
        ("!category <nome>", "🏷️ Busca workflows por categoria"),
        ("!filter <trigger> <complexity>", "🔎 Filtra workflows por critérios"),
        ("!random", "🎲 Mostra um workflow aleatório"),
        ("!api_status", "🏥 Verifica status da API"),
        ("!help_workflows", "❓ Mostra esta mensagem de ajuda"),
    ]
    
    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.set_footer(text="Bot de Workflows N8N | 2057+ workflows disponíveis")
    
    await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    """Tratamento de erros"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Comando não encontrado. Use `!help_workflows` para ver comandos disponíveis.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Parâmetro faltando. Use `!help_workflows` para ver como usar o comando.")
    else:
        print(f"Erro: {error}")
        await ctx.send(f"❌ Ocorreu um erro ao executar o comando.")


# ==================== INICIAR BOT ====================

if __name__ == "__main__":
    print("🚀 Iniciando Bot Discord...")
    print(f"📡 API: {API_BASE_URL}")
    print("-" * 50)
    
    try:
        bot.run(BOT_TOKEN)
    except discord.LoginFailure:
        print("❌ Token inválido! Verifique o BOT_TOKEN no código.")
    except Exception as e:
        print(f"❌ Erro ao iniciar bot: {e}")
