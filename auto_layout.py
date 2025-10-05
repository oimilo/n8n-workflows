#!/usr/bin/env python3
"""
Auto layout for n8n workflows

Reposiciona nós para evitar sobreposição e organizar em grade por camadas
(da esquerda para a direita) com base nas conexões. Funciona mesmo quando
as conexões usam IDs ou nomes como chaves.

Uso:
  python auto_layout.py --dry-run --limit 50
  python auto_layout.py --apply

Parâmetros:
  --workflows-dir  Diretório raiz dos workflows (default: workflows)
  --limit          Limitar número de arquivos processados (para teste)
  --dry-run        Não escreve no disco
  --apply          Escreve alterações

Layout:
  - Espaçamento padrão: X=280, Y=180
  - Margem: (100, 100)
  - Camada calculada via BFS a partir de triggers (webhook/cron/manual/...)
  - Se não houver triggers, começa por nós sem entradas
"""

from __future__ import annotations

import argparse
import json
from collections import deque, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple, Set


SPACING_X = 280
SPACING_Y = 180
MARGIN_X = 100
MARGIN_Y = 100


def normalize_conn_lists(conn_value: Any) -> List[List[Dict[str, Any]]]:
    if conn_value is None:
        return []
    if isinstance(conn_value, list):
        # [[{...}], ...] OR [{...}, ...]
        if all(isinstance(item, list) for item in conn_value):
            return [ [c for c in inner if isinstance(c, dict)] for inner in conn_value ]
        if all(isinstance(item, dict) for item in conn_value):
            return [conn_value]
    if isinstance(conn_value, dict):
        return [[conn_value]]
    return []


def build_graph(wf: Dict[str, Any]) -> Tuple[Dict[str, Set[str]], Dict[str, int]]:
    """Constroi grafo direcionado (adjacência por id) e indegrees.
    Aceita conexões com chaves por id ou por nome.
    """
    nodes: List[Dict[str, Any]] = wf.get("nodes", []) or []
    id_to_name = {}
    name_to_id = {}
    for n in nodes:
        nid = str(n.get("id")) if n.get("id") is not None else None
        nm = str(n.get("name")) if n.get("name") is not None else None
        if nid and nm:
            id_to_name[nid] = nm
            name_to_id[nm] = nid

    adj: Dict[str, Set[str]] = defaultdict(set)
    indeg: Dict[str, int] = {nid: 0 for nid in id_to_name}

    connections: Dict[str, Any] = wf.get("connections") or {}
    for raw_source, by_output in connections.items():
        src_id = raw_source
        if src_id not in id_to_name and raw_source in name_to_id:
            src_id = name_to_id[raw_source]
        if src_id not in id_to_name:
            continue
        if not isinstance(by_output, dict):
            continue
        for _out_name, raw_list in by_output.items():
            for inner in normalize_conn_lists(raw_list):
                for edge in inner:
                    tgt_raw = edge.get("node")
                    if tgt_raw is None:
                        continue
                    tgt_id = tgt_raw
                    if tgt_id not in id_to_name and tgt_raw in name_to_id:
                        tgt_id = name_to_id[tgt_raw]
                    if tgt_id in id_to_name:
                        if tgt_id not in adj[src_id]:
                            adj[src_id].add(tgt_id)
                            indeg[tgt_id] = indeg.get(tgt_id, 0) + 1

    # Certificar todos os nós no dicionário
    for nid in id_to_name:
        adj.setdefault(nid, set())
        indeg.setdefault(nid, 0)

    return adj, indeg


def find_triggers(nodes: List[Dict[str, Any]]) -> List[str]:
    triggers: List[str] = []
    for n in nodes:
        nid = n.get("id")
        t = (n.get("type") or "").lower()
        if nid and any(key in t for key in ["trigger", "webhook", "schedule", "cron", "manual"]):
            triggers.append(nid)
    return triggers


def auto_layout_workflow(wf: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
    nodes: List[Dict[str, Any]] = wf.get("nodes", []) or []
    if len(nodes) <= 1:
        return wf, False

    id_to_node = {str(n.get("id")): n for n in nodes if n.get("id")}

    adj, indeg = build_graph(wf)

    # Seeds: triggers -> senão, nós com indegree==0 -> senão, todos
    seeds = find_triggers(nodes)
    if not seeds:
        seeds = [nid for nid, d in indeg.items() if d == 0]
    if not seeds:
        seeds = list(id_to_node.keys())

    # BFS multi-source para camadas
    layer: Dict[str, int] = {}
    q = deque()
    for s in seeds:
        layer[s] = 0
        q.append(s)

    while q:
        u = q.popleft()
        for v in adj.get(u, ()): 
            cand = layer[u] + 1
            if v not in layer or cand < layer[v]:
                layer[v] = cand
                q.append(v)

    # Nós eventualmente desconectados ficam na camada 0 após triggers
    for nid in id_to_node:
        layer.setdefault(nid, 0)

    # Agregar por camada e ordenar por nome para espaçar verticalmente
    layer_to_nodes: Dict[int, List[str]] = defaultdict(list)
    for nid, lvl in layer.items():
        layer_to_nodes[lvl].append(nid)

    changed = False
    for lvl, nids in layer_to_nodes.items():
        nids.sort(key=lambda x: (id_to_node[x].get("name") or ""))
        for row, nid in enumerate(nids):
            target_pos = [MARGIN_X + lvl * SPACING_X, MARGIN_Y + row * SPACING_Y]
            node = id_to_node[nid]
            if node.get("position") != target_pos:
                node["position"] = target_pos
                changed = True

    wf["nodes"] = list(id_to_node.values())
    return wf, changed


def process_repo(workflows_dir: Path, dry_run: bool, limit: int) -> Dict[str, int]:
    files = list(workflows_dir.rglob("*.json"))
    if limit:
        files = files[:limit]
    stats = defaultdict(int)

    for fp in files:
        try:
            data = json.loads(Path(fp).read_text(encoding="utf-8"))
            data, changed = auto_layout_workflow(data)
            if changed:
                stats["files_changed"] += 1
                if not dry_run:
                    Path(fp).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            else:
                stats["files_unchanged"] += 1
        except Exception as e:
            stats["files_failed"] += 1
            print(f"❌ {fp}: {e}")

    stats["total"] = len(files)
    return {k: int(v) for k, v in stats.items()}


def main() -> None:
    ap = argparse.ArgumentParser(description="Auto layout n8n workflows")
    ap.add_argument("--workflows-dir", default="workflows")
    ap.add_argument("--limit", type=int, default=0)
    me = ap.add_mutually_exclusive_group()
    me.add_argument("--dry-run", action="store_true")
    me.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    wd = Path(args.workflows_dir)
    if not wd.exists():
        raise SystemExit(f"Workflows dir não encontrado: {wd}")

    dry_run = True if args.dry_run or not args.apply else False
    print(f"AUTO-LAYOUT | dir={wd} | dry_run={dry_run} | limit={args.limit or 'all'}")
    res = process_repo(wd, dry_run, args.limit)
    print("RESULT:")
    for k, v in sorted(res.items()):
        print(f"  - {k}: {v}")


if __name__ == "__main__":
    main()


