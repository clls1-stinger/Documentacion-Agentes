import json

INPUT_FILE = "workflow_yes_patched_v41.json"
OUTPUT_FILE = "workflow_yes_patched_v42.json"

def patch_workflow():
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            workflow = json.load(f)

        nodes = workflow.get('nodes', [])
        
        for node in nodes:
            # 1. Patch Clean Actor
            if node.get('name') == 'Clean Actor':
                print("Found Clean Actor. Applying patch...")
                js_code = node['parameters']['jsCode']
                
                # Check if patch is already applied to avoid double patching if re-run
                if "datos.fileId = datos.file_id" not in js_code:
                    # Insert the file_id normalization logic before the return
                    patch_code = """
    // --- ID NORMALIZATION FIX ---
    if (datos.file_id && !datos.fileId) {
        datos.fileId = datos.file_id;
    }
"""
                    # Insert before the last return
                    last_return_idx = js_code.rfind("return { json: { ...item")
                    if last_return_idx != -1:
                         new_js_code = js_code[:last_return_idx] + patch_code + js_code[last_return_idx:]
                         node['parameters']['jsCode'] = new_js_code
                         print("Clean Actor patched successfully.")
                    else:
                        print("WARNING: Could not find insertion point in Clean Actor.")
                else:
                    print("Clean Actor already has the patch.")

            # 2. Patch Drive Download
            if node.get('name') == 'Drive Download':
                print("Found Drive Download. Applying patch...")
                # Force the correct expression
                node['parameters']['fileId'] = "={{ $json.datos.fileId }}"
                print("Drive Download patched successfully.")

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2)
            
        print(f"Successfully created {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"Error patching workflow: {e}")

if __name__ == "__main__":
    patch_workflow()
