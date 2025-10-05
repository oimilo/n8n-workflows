#!/usr/bin/env python3
"""
Force Connection Fixer
More aggressive script to fix ALL workflow connections
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

def force_fix_workflow_connections(file_path: Path) -> bool:
    """Force fix connections in a single workflow file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        nodes = workflow_data.get('nodes', [])
        
        if len(nodes) < 2:
            return False
        
        # Always create connections, even if they exist
        print(f"🔗 Force creating connections for {file_path.name}")
        connections = create_connections(nodes)
        workflow_data['connections'] = connections
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(workflow_data, f, indent=2, ensure_ascii=False)
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {file_path.name}: {e}")
        return False

def create_connections(nodes: List[Dict]) -> Dict:
    """Create logical connections between nodes."""
    # Sort nodes by position (x-coordinate)
    positioned_nodes = []
    for node in nodes:
        position = node.get('position', [0, 0])
        positioned_nodes.append((position[0], node))
    
    # Sort by x-coordinate (left to right)
    positioned_nodes.sort(key=lambda x: x[0])
    
    # Create connections between adjacent nodes
    connections = {}
    for i in range(len(positioned_nodes) - 1):
        current_node = positioned_nodes[i][1]
        next_node = positioned_nodes[i + 1][1]
        
        current_id = current_node.get('id')
        next_id = next_node.get('id')
        
        if current_id and next_id:
            connections[current_id] = {
                'main': [[{
                    'node': next_id,
                    'type': 'main',
                    'index': 0
                }]]
            }
    
    return connections

def force_fix_all_workflows():
    """Force fix connections in ALL workflow files."""
    workflows_dir = Path("workflows")
    if not workflows_dir.exists():
        print("❌ Workflows directory not found")
        return
    
    json_files = list(workflows_dir.rglob("*.json"))
    fixed_count = 0
    
    print(f"🔧 Force fixing connections in {len(json_files)} workflows...")
    
    for file_path in json_files:
        if force_fix_workflow_connections(file_path):
            fixed_count += 1
    
    print(f"✅ Force fixed connections in {fixed_count} workflows")

if __name__ == "__main__":
    force_fix_all_workflows()
