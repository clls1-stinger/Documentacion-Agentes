#!/usr/bin/env python3
import sqlite3, json, os

conn = sqlite3.connect(os.path.expanduser('~/.n8n/database.sqlite'))
cursor = conn.cursor()
cursor.execute('SELECT connections FROM workflow_entity WHERE id=?', ('Urf7HpECFvfQooAv',))
conns = json.loads(cursor.fetchone()[0])
switch_conns = conns.get('Is Done Switch', {})

print('SWITCH CONNECTIONS:')
print(json.dumps(switch_conns, indent=2))
print()
print('INTERPRETACIÓN:')
print('Puerto 0 (cuando regla coincide)   →', switch_conns['main'][0])
print('Puerto 1 (fallback/extra)          →', switch_conns['main'][1])
print()
print('PROBLEMA SOSPECHADO:')
print('Si la regla es "is_done_string === TRUE" pero está yendo a Final Response con FALSE,')
print('entonces las conexiones están INVERTIDAS o el Switch tiene un bug.')
