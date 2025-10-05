#!/usr/bin/env python3
"""
Repair n8n workflow connections

Objetivo:
- Normalizar o objeto `connections` para o formato esperado pelo n8n
- Converter chaves/valores que estejam usando ID de nó para o NOME do nó
- Remover conexões para nós inexistentes
- Deduplicar conexões mantendo a estrutura [[{ node, type, index }]]
- (Opcional) Inferir uma cadeia simples de conexões por posição quando
  não houver nenhuma conexão (heurística segura)

Uso:
  python repair_n8n_connections.py --dry-run
  python repair_n8n_connections.py --apply

Parâmetros principais:
  --workflows-dir   Diretório raiz contendo subpastas com arquivos .json (default: workflows)
  --limit           Processar apenas N arquivos (para testes)
  --infer           Habilita heurística para criar cadeia simples quando não houver conexões
  --backup-dir      Diretório de backups (default: backups/repair_connections_<timestamp>)
  --dry-run         Não escreve alterações, apenas relata (default)
  --apply           Escreve alterações nos arquivos (cria backup antes)
"""

import argparse
import json
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


def ensure_array_of_arrays(connections_list: Any) -> List[List[Dict[str, Any]]]:
    """Garante o formato [[{...}], ...].
    Aceita variações comuns e converte com segurança.
    """
    if connections_list is None:
        return []

    # Caso já esteja no formato correto
    if (
        isinstance(connections_list, list)
        and all(isinstance(item, list) for item in connections_list)
    ):
        normalized: List[List[Dict[str, Any]]] = []
        for inner in connections_list:
            if isinstance(inner, list):
                normalized.append([c for c in inner if isinstance(c, dict)])
        return normalized

    # Caso seja uma lista plana de dicts -> embrulhar em uma camada
    if isinstance(connections_list, list) and all(
        isinstance(item, dict) for item in connections_list
    ):
        return [connections_list]

    # Caso seja um único dict -> embrulhar nas duas camadas
    if isinstance(connections_list, dict):
        return [[connections_list]]

    # Qualquer outro caso inesperado -> descartar com segurança
    return []


def normalize_connections(
    wf: Dict[str, Any], infer_chain: bool = False
) -> Tuple[Dict[str, Any], Dict[str, int]]:
    """Normaliza `connections` usando nomes de nós, deduplica e remove inválidas.

    Retorna o workflow modificado e métricas de alterações.
    """
    stats = defaultdict(int)

    nodes: List[Dict[str, Any]] = wf.get("nodes", []) or []
    if not isinstance(nodes, list):
        wf["nodes"] = []
        nodes = []

    # Mapas úteis
    id_to_name = {}
    name_set = set()
    for node in nodes:
        node_id = node.get("id")
        node_name = node.get("name")
        if node_id and node_name:
            id_to_name[str(node_id)] = str(node_name)
        if node_name:
            name_set.add(str(node_name))

    connections: Dict[str, Any] = wf.get("connections") or {}
    if not isinstance(connections, dict):
        connections = {}

    new_connections: Dict[str, Dict[str, List[List[Dict[str, Any]]]]] = {}

    for raw_source, outputs in connections.items():
        # Converter chave para NOME do nó (se vier ID)
        source_name = None
        if raw_source in name_set:
            source_name = raw_source
        elif str(raw_source) in id_to_name:
            source_name = id_to_name[str(raw_source)]
            stats["source_keys_converted_id_to_name"] += 1
        else:
            stats["source_keys_invalid_removed"] += 1
            continue  # nó origem inválido

        if not isinstance(outputs, dict):
            stats["output_blocks_invalid_removed"] += 1
            continue

        dest_by_type: Dict[str, List[List[Dict[str, Any]]]] = {}

        for out_type, conn_list in outputs.items():
            normalized_list = ensure_array_of_arrays(conn_list)

            dedup = set()
            cleaned_outer: List[List[Dict[str, Any]]] = []

            for inner in normalized_list:
                cleaned_inner: List[Dict[str, Any]] = []
                for conn in inner:
                    if not isinstance(conn, dict):
                        continue
                    dest_raw = conn.get("node")
                    if dest_raw is None:
                        continue

                    # Converter destino para NOME (se vier ID)
                    if dest_raw in name_set:
                        dest_name = dest_raw
                    elif str(dest_raw) in id_to_name:
                        dest_name = id_to_name[str(dest_raw)]
                        stats["target_nodes_converted_id_to_name"] += 1
                    else:
                        stats["target_nodes_invalid_removed"] += 1
                        continue

                    idx = int(conn.get("index", 0))
                    key = (out_type, dest_name, idx)
                    if key in dedup:
                        stats["connections_deduplicated"] += 1
                        continue
                    dedup.add(key)

                    cleaned_inner.append({
                        "node": dest_name,
                        "type": out_type,
                        "index": idx,
                    })

                if cleaned_inner:
                    cleaned_outer.append(cleaned_inner)

            if cleaned_outer:
                dest_by_type[out_type] = cleaned_outer

        if dest_by_type:
            new_connections[source_name] = dest_by_type

    # Heurística opcional: se não houver nenhuma conexão, criar cadeia simples
    if infer_chain and not new_connections and len(nodes) > 1:
        # Ordenar por posição X crescente; conectar main sequencialmente
        try:
            ordered = sorted(
                [
                    (n.get("name"), n.get("position", [0, 0])[0])
                    for n in nodes
                    if n.get("name")
                ],
                key=lambda x: (x[1], str(x[0])),
            )
            for i in range(len(ordered) - 1):
                a = ordered[i][0]
                b = ordered[i + 1][0]
                new_connections.setdefault(a, {}).setdefault("main", []).append([
                    {"node": b, "type": "main", "index": 0}
                ])
            stats["inferred_chain_created"] = len(ordered) - 1
        except Exception:
            # Ignorar falhas de inferência; manter sem conexões
            pass

    wf["connections"] = new_connections
    return wf, {k: int(v) for k, v in stats.items()}


def backup_file(src: Path, backup_root: Path) -> Path:
    backup_root.mkdir(parents=True, exist_ok=True)
    dst = backup_root / src.relative_to(src.parents[1])
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def process_repository(
    workflows_dir: Path, dry_run: bool, limit: int, infer_chain: bool, backup_dir: Path
) -> Dict[str, int]:
    counters = defaultdict(int)
    files: List[Path] = []
    for category in workflows_dir.iterdir():
        if category.is_dir():
            files.extend(sorted(category.glob("*.json")))

    if limit:
        files = files[:limit]

    for wf_file in files:
        try:
            with wf_file.open("r", encoding="utf-8") as f:
                data = json.load(f)

            before = json.dumps(data.get("connections", {}), sort_keys=True)
            data, stats = normalize_connections(data, infer_chain=infer_chain)
            after = json.dumps(data.get("connections", {}), sort_keys=True)

            if before != after:
                counters["files_modified"] += 1
                for k, v in stats.items():
                    counters[k] += v

                if not dry_run:
                    # Backup antes de escrever
                    backup_file(wf_file, backup_dir)
                    with wf_file.open("w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                counters["files_unchanged"] += 1

        except Exception as e:
            counters["files_failed"] += 1
            print(f"❌ Erro em {wf_file.name}: {e}")

    counters["total_files"] = len(files)
    return {k: int(v) for k, v in counters.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair n8n workflow connections")
    parser.add_argument(
        "--workflows-dir",
        default="workflows",
        help="Diretório com subpastas de workflows .json",
    )
    parser.add_argument("--limit", type=int, default=0, help="Limitar número de arquivos")
    parser.add_argument(
        "--infer",
        action="store_true",
        help="Inferir cadeia simples quando não houver conexões",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Apenas relatar mudanças")
    mode.add_argument("--apply", action="store_true", help="Aplicar mudanças nos arquivos")
    parser.add_argument(
        "--backup-dir",
        default=None,
        help="Diretório para backups; padrão cria pasta com timestamp em backups/",
    )

    args = parser.parse_args()

    workflows_dir = Path(args.workflows_dir)
    if not workflows_dir.exists():
        raise SystemExit(f"Workflows dir não encontrado: {workflows_dir}")

    dry_run = True if args.dry_run or not args.apply else False

    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_root = (
        Path(args.backup_dir)
        if args.backup_dir
        else Path("backups") / f"repair_connections_{ts}"
    )

    print(
        f"START repair | dir={workflows_dir} | dry_run={dry_run} | infer={args.infer} | limit={args.limit or 'all'}"
    )

    summary = process_repository(
        workflows_dir=workflows_dir,
        dry_run=dry_run,
        limit=args.limit,
        infer_chain=args.infer,
        backup_dir=backup_root,
    )

    print("\nRESULT:")
    for k, v in sorted(summary.items()):
        print(f"  - {k}: {v}")

    if not dry_run:
        print(f"\nBackups em: {backup_root}")


if __name__ == "__main__":
    main()


