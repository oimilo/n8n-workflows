#!/usr/bin/env python3
"""
Fix Workflow Connections
Direct script to fix broken workflow connections
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

def fix_workflow_connections(file_path: Path) -> bool:
    """Fix connections in a single workflow file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        nodes = workflow_data.get('nodes', [])
        connections = workflow_data.get('connections', {})
        
        if len(nodes) < 2:
            return False
        
        # If no connections exist, create them
        if not connections:
            print(f"🔗 Creating connections for {file_path.name}")
            connections = create_connections(nodes)
            workflow_data['connections'] = connections
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=2, ensure_ascii=False)
            return True
        
        return False
        
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

def fix_all_workflows():
    """Fix connections in all workflow files."""
    workflows_dir = Path("workflows")
    if not workflows_dir.exists():
        print("❌ Workflows directory not found")
        return
    
    json_files = list(workflows_dir.rglob("*.json"))
    fixed_count = 0
    
    print(f"🔧 Fixing connections in {len(json_files)} workflows...")
    
    for file_path in json_files:
        if fix_workflow_connections(file_path):
            fixed_count += 1
    
    print(f"✅ Fixed connections in {fixed_count} workflows")

if __name__ == "__main__":
    fix_all_workflows()
