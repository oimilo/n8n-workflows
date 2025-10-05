#!/usr/bin/env python3
"""
Startup Workflow Cleaner
Automatically cleans and organizes workflows on startup
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import re
from collections import defaultdict

class WorkflowStartupCleaner:
    def __init__(self, workflows_dir="workflows"):
        self.workflows_dir = Path(workflows_dir)
        self.cleaned_count = 0
        self.errors = 0
        
    def clean_workflow_file(self, file_path: Path) -> bool:
        """Clean a single workflow file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            
            original_nodes = len(workflow_data.get('nodes', []))
            cleaned = False
            
            # Remove duplicate documentation nodes
            if self.remove_duplicate_documentation(workflow_data):
                cleaned = True
            
            # Remove duplicate error handlers
            if self.remove_duplicate_error_handlers(workflow_data):
                cleaned = True
            
            # Clean connections
            if self.clean_connections(workflow_data):
                cleaned = True
            
            # Remove empty nodes
            if self.remove_empty_nodes(workflow_data):
                cleaned = True
            
            if cleaned:
                # Write cleaned workflow back
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(workflow_data, f, indent=2, ensure_ascii=False)
                
                self.cleaned_count += 1
                print(f"✅ Cleaned: {file_path.name}")
                return True
                
        except Exception as e:
            print(f"❌ Error cleaning {file_path.name}: {e}")
            self.errors += 1
            return False
    
    def remove_duplicate_documentation(self, workflow_data: Dict) -> bool:
        """Remove duplicate documentation nodes."""
        nodes = workflow_data.get('nodes', [])
        if not nodes:
            return False
        
        # Find documentation nodes
        doc_nodes = []
        other_nodes = []
        
        for node in nodes:
            if (node.get('type') == 'n8n-nodes-base.stickyNote' and 
                'documentation' in node.get('name', '').lower()):
                doc_nodes.append(node)
            else:
                other_nodes.append(node)
        
        # Keep only the first documentation node if any
        if len(doc_nodes) > 1:
            # Keep the first one, remove the rest
            other_nodes.append(doc_nodes[0])
            workflow_data['nodes'] = other_nodes
            return True
        
        return False
    
    def remove_duplicate_error_handlers(self, workflow_data: Dict) -> bool:
        """Remove duplicate error handlers for the same node."""
        nodes = workflow_data.get('nodes', [])
        connections = workflow_data.get('connections', {})
        
        if not nodes or not connections:
            return False
        
        # Find error handler nodes
        error_handlers = []
        other_nodes = []
        
        for node in nodes:
            if ('error' in node.get('name', '').lower() and 
                'stopAndError' in node.get('type', '')):
                error_handlers.append(node)
            else:
                other_nodes.append(node)
        
        # Group error handlers by target node
        error_groups = defaultdict(list)
        for handler in error_handlers:
            # Extract target node ID from handler name
            handler_name = handler.get('name', '')
            if 'error-handler-' in handler_name:
                # Extract the target node ID
                parts = handler_name.split('-')
                if len(parts) >= 3:
                    target_id = '-'.join(parts[2:])
                    error_groups[target_id].append(handler)
        
        # Keep only one error handler per target node
        cleaned_handlers = []
        for target_id, handlers in error_groups.items():
            if len(handlers) > 1:
                # Keep the first one, remove the rest
                cleaned_handlers.append(handlers[0])
            else:
                cleaned_handlers.extend(handlers)
        
        # Update nodes
        if len(cleaned_handlers) < len(error_handlers):
            other_nodes.extend(cleaned_handlers)
            workflow_data['nodes'] = other_nodes
            return True
        
        return False
    
    def clean_connections(self, workflow_data: Dict) -> bool:
        """Clean and validate connections, or create them if missing."""
        connections = workflow_data.get('connections', {})
        nodes = workflow_data.get('nodes', [])
        
        if not nodes:
            return False
        
        # Get valid node IDs
        valid_node_ids = {node.get('id') for node in nodes}
        
        # If no connections exist, try to create logical connections
        if not connections:
            return self.create_logical_connections(workflow_data, nodes)
        
        cleaned_connections = {}
        cleaned = False
        
        for source_id, source_connections in connections.items():
            if source_id not in valid_node_ids:
                cleaned = True
                continue
            
            if isinstance(source_connections, dict):
                cleaned_source = {}
                for output_name, output_connections in source_connections.items():
                    if isinstance(output_connections, list):
                        # Filter valid connections
                        valid_connections = []
                        for connection in output_connections:
                            if (isinstance(connection, dict) and 
                                'node' in connection and 
                                connection['node'] in valid_node_ids):
                                valid_connections.append(connection)
                        
                        if valid_connections:
                            cleaned_source[output_name] = valid_connections
                        elif output_connections:  # Had connections but none were valid
                            cleaned = True
                    else:
                        cleaned_source[output_name] = output_connections
                
                if cleaned_source:
                    cleaned_connections[source_id] = cleaned_source
                else:
                    cleaned = True
        
        if cleaned:
            workflow_data['connections'] = cleaned_connections
            return True
        
        return False
    
    def create_logical_connections(self, workflow_data: Dict, nodes: List[Dict]) -> bool:
        """Create logical connections between nodes based on their order and type."""
        if len(nodes) < 2:
            return False
        
        # Sort nodes by position (x-coordinate) to determine logical flow
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
                # Create main connection
                if current_id not in connections:
                    connections[current_id] = {}
                
                connections[current_id]['main'] = [[{
                    'node': next_id,
                    'type': 'main',
                    'index': 0
                }]]
        
        if connections:
            workflow_data['connections'] = connections
            return True
        
        return False
    
    def remove_empty_nodes(self, workflow_data: Dict) -> bool:
        """Remove nodes with no meaningful content."""
        nodes = workflow_data.get('nodes', [])
        if not nodes:
            return False
        
        cleaned_nodes = []
        cleaned = False
        
        for node in nodes:
            # Keep nodes that have meaningful content
            if (node.get('name') and 
                node.get('type') and 
                node.get('name').strip() and
                not node.get('name').startswith('Unnamed')):
                cleaned_nodes.append(node)
            else:
                cleaned = True
        
        if cleaned:
            workflow_data['nodes'] = cleaned_nodes
            return True
        
        return False
    
    def clean_all_workflows(self) -> Dict[str, int]:
        """Clean all workflow files."""
        print("🧹 Starting workflow cleanup...")
        
        if not self.workflows_dir.exists():
            print(f"❌ Workflows directory not found: {self.workflows_dir}")
            return {'cleaned': 0, 'errors': 0, 'total': 0}
        
        json_files = list(self.workflows_dir.rglob("*.json"))
        total_files = len(json_files)
        
        print(f"📁 Found {total_files} workflow files")
        
        for file_path in json_files:
            self.clean_workflow_file(file_path)
        
        print(f"\n🎉 Cleanup complete!")
        print(f"   ✅ Cleaned: {self.cleaned_count} workflows")
        print(f"   ❌ Errors: {self.errors} workflows")
        print(f"   📊 Total: {total_files} workflows")
        
        return {
            'cleaned': self.cleaned_count,
            'errors': self.errors,
            'total': total_files
        }

def main():
    """Main cleanup function."""
    print("🚀 N8N Workflow Startup Cleaner")
    print("=" * 50)
    
    cleaner = WorkflowStartupCleaner()
    stats = cleaner.clean_all_workflows()
    
    if stats['cleaned'] > 0:
        print(f"\n✨ {stats['cleaned']} workflows have been cleaned and organized!")
    else:
        print("\n✨ All workflows are already clean!")
    
    return stats

if __name__ == "__main__":
    main()
