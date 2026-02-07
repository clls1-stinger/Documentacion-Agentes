#!/usr/bin/env python3
"""
🔥 N8N MASTER CONTROLLER - AUTONOMOUS AGENT INTERFACE
=====================================================
Version: 2.0.0 "God Mode"
Author: Vega Kernel

This script provides a High-Level API for Autonomous Agents to manipulate
the N8N SQLite database directly. It abstracts the SQL complexity.

COMMANDS:
    list                -> List all workflows (ID, Name, Active?)
    dump <id|name>      -> Dump full JSON of a workflow (for LLM analysis)
    push <id|name> <json_file> -> Overwrite workflow with new JSON logic
    search <keyword>    -> Find workflows containing specific nodes/code
    activate <id|name>  -> Turn workflow ON
    deactivate <id|name>-> Turn workflow OFF
    schema              -> Show database schema analysis

Usage:
    python3 n8n_master_controller.py [command] [args]
"""

import sqlite3
import json
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# CONFIGURATION
DB_PATH = Path.home() / ".n8n" / "database.sqlite"

def connect_db():
    if not DB_PATH.exists():
        print(f"❌ Error: Database not found at {DB_PATH}")
        sys.exit(1)
    return sqlite3.connect(f"file:{DB_PATH}?mode=rw", uri=True)

def find_workflow_id(cursor, identifier):
    """Resolves name OR ID to a UUID"""
    # Try exact ID match
    cursor.execute("SELECT id FROM workflow_entity WHERE id = ?", (identifier,))
    res = cursor.fetchone()
    if res: return res[0]
    
    # Try name match
    cursor.execute("SELECT id FROM workflow_entity WHERE name = ?", (identifier,))
    res = cursor.fetchone()
    if res: return res[0]
    
    # Try partial name match
    cursor.execute("SELECT id, name FROM workflow_entity WHERE name LIKE ?", (f"%{identifier}%",))
    res = cursor.fetchall()
    if len(res) == 1: return res[0][0]
    if len(res) > 1:
        print(f"⚠️ Ambiguous name '{identifier}'. Matches: {[r[1] for r in res]}")
        sys.exit(1)
        
    print(f"❌ Workflow '{identifier}' not found.")
    sys.exit(1)

# --- ACTIONS ---

def list_workflows(args):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, active, updatedAt FROM workflow_entity ORDER BY updatedAt DESC")
    print(f"{'ID':<24} | {'ACTIVE':<6} | {'UPDATED':<20} | {'NAME'}")
    print("-" * 80)
    for row in cursor.fetchall():
        active = "✅" if row[2] else "❌"
        print(f"{row[0][:22] + '..':<24} | {active:<6} | {row[3]:<20} | {row[1]}")
    conn.close()

def dump_workflow(args):
    conn = connect_db()
    cursor = conn.cursor()
    wid = find_workflow_id(cursor, args.identifier)
    
    cursor.execute("SELECT nodes, connections, settings, staticData, name FROM workflow_entity WHERE id = ?", (wid,))
    row = cursor.fetchone()
    
    full_data = {
        "meta": {
            "id": wid,
            "name": row[4],
            "exported_at": datetime.now().isoformat()
        },
        "nodes": json.loads(row[0]),
        "connections": json.loads(row[1]),
        "settings": json.loads(row[2]) if row[2] else {},
        "staticData": json.loads(row[3]) if row[3] else None
    }
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(full_data, f, indent=2)
        print(f"✅ Workflow exported to {args.output}")
    else:
        print(json.dumps(full_data, indent=2))
    conn.close()

def push_workflow(args):
    if not os.path.exists(args.json_file):
        print("❌ JSON file not found")
        sys.exit(1)
        
    with open(args.json_file, 'r') as f:
        data = json.load(f)
    
    # Validate critical keys
    if "nodes" not in data or "connections" not in data:
        print("❌ Invalid n8n JSON format. Must contain 'nodes' and 'connections'.")
        sys.exit(1)

    conn = connect_db()
    cursor = conn.cursor()
    wid = find_workflow_id(cursor, args.identifier)
    
    # Backup first!
    backup_file = f"/tmp/n8n_backup_{wid}_{int(datetime.now().timestamp())}.json"
    cursor.execute("SELECT nodes, connections FROM workflow_entity WHERE id = ?", (wid,))
    old_row = cursor.fetchone()
    with open(backup_file, 'w') as f:
        json.dump({"nodes": json.loads(old_row[0]), "connections": json.loads(old_row[1])}, f)
    print(f"🛡️ Backup created at {backup_file}")

    # Update
    cursor.execute("""
        UPDATE workflow_entity 
        SET nodes = ?, connections = ?, updatedAt = datetime('now')
        WHERE id = ?
    """, (json.dumps(data['nodes']), json.dumps(data['connections']), wid))
    
    conn.commit()
    print(f"✅ Workflow '{wid}' updated successfully in DB.")
    print("⚠️  REMINDER: Refresh n8n UI (F5) to see changes.")
    conn.close()

def set_active(args, state):
    conn = connect_db()
    cursor = conn.cursor()
    wid = find_workflow_id(cursor, args.identifier)
    
    cursor.execute("UPDATE workflow_entity SET active = ?, updatedAt = datetime('now') WHERE id = ?", (1 if state else 0, wid))
    conn.commit()
    status = "ACTIVATED" if state else "DEACTIVATED"
    print(f"✅ Workflow {status}. (Note: Triggers may need restart if n8n doesn't auto-detect DB change)")
    conn.close()

def search_code(args):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, nodes FROM workflow_entity")
    
    print(f"🔍 Searching for '{args.keyword}'...")
    found = False
    for row in cursor.fetchall():
        nodes = json.loads(row[2])
        for node in nodes:
            # Search in JS code, parameters, or node name
            node_str = json.dumps(node)
            if args.keyword in node_str:
                print(f"Found in: [{row[1]}] (ID: {row[0]}) -> Node: {node['name']}")
                found = True
    
    if not found: print("No matches found.")
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="N8N Master Controller")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # List
    subparsers.add_parser("list", help="List all workflows")
    
    # Dump
    dump_p = subparsers.add_parser("dump", help="Export workflow JSON")
    dump_p.add_argument("identifier", help="Workflow ID or Name")
    dump_p.add_argument("--output", "-o", help="Save to file instead of stdout")
    
    # Push
    push_p = subparsers.add_parser("push", help="Overwrite workflow logic")
    push_p.add_argument("identifier", help="Target Workflow ID or Name")
    push_p.add_argument("json_file", help="New JSON definition file")
    
    # Activate/Deactivate
    act_p = subparsers.add_parser("activate", help="Enable workflow")
    act_p.add_argument("identifier", help="Workflow ID or Name")
    
    deact_p = subparsers.add_parser("deactivate", help="Disable workflow")
    deact_p.add_argument("identifier", help="Workflow ID or Name")

    # Search
    search_p = subparsers.add_parser("search", help="Search code inside nodes")
    search_p.add_argument("keyword", help="Text/Code to find")

    args = parser.parse_args()
    
    if args.command == "list": list_workflows(args)
    elif args.command == "dump": dump_workflow(args)
    elif args.command == "push": push_workflow(args)
    elif args.command == "activate": set_active(args, True)
    elif args.command == "deactivate": set_active(args, False)
    elif args.command == "search": search_code(args)

if __name__ == "__main__":
    main()
