import sqlite3
import json
import os

DB_PATH = '/home/emky/n8n/database_copy.sqlite'

def get_last_execution():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get the latest execution
        # Common table is 'execution_entity'
        query = """
        SELECT id, mode, startedAt, stoppedAt, status, data 
        FROM execution_entity 
        ORDER BY id DESC 
        LIMIT 1
        """
        
        cursor.execute(query)
        row = cursor.fetchone()
        
        if row:
            print(f"Execution ID: {row['id']}")
            print(f"Mode: {row['mode']}")
            print(f"Started At: {row['startedAt']}")
            print(f"Stopped At: {row['stoppedAt']}")
            print(f"Status: {row['status']}")
            
            # The 'data' column usually contains the detailed execution data including node errors
            try:
                data_json = json.loads(row['data'])
                # Look for errors in resultData
                if 'resultData' in data_json and 'error' in data_json['resultData']:
                     print("\nError Details:")
                     print(json.dumps(data_json['resultData']['error'], indent=2))
                elif 'resultData' in data_json and 'runData' in data_json['resultData']:
                    # Check for nodes with errors
                    run_data = data_json['resultData']['runData']
                    found_error = False
                    for node_name, node_runs in run_data.items():
                        for run in node_runs:
                             if 'error' in run:
                                 print(f"\nError in Node '{node_name}':")
                                 print(json.dumps(run['error'], indent=2))
                                 found_error = True
                    
                    if not found_error and row['status'] == 'error':
                        print("\nStatus is 'error' but no specific node error found in runData structure checked.")
                    elif not found_error:
                         print("\nNo errors found in execution data.")

            except json.JSONDecodeError:
                print("\nCould not decode execution data JSON.")
        else:
            print("No executions found.")
            
        conn.close()
    except Exception as e:
        print(f"Error accessing database: {e}")

if __name__ == "__main__":
    get_last_execution()
