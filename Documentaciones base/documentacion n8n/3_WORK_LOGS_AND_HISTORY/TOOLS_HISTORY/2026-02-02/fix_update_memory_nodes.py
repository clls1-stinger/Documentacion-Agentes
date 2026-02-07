import json
import os

workflow_path = '/home/emky/n8n/debug_workflow.json'

new_js_code = """const chatHistory = $input.item.json.chat_history || [];
const userGoal = $input.item.json.user_goal;
const aiResponse = $input.item.json.response;

// Add new interaction
chatHistory.push({
  user: userGoal,
  ai: aiResponse,
  timestamp: new Date().toISOString()
});

const fileContent = JSON.stringify(chatHistory.slice(-20), null, 2);

// Return JSON for the chat output and Binary for the file writer
return [{
  json: { 
    response: aiResponse 
  },
  binary: {
    data: {
      data: Buffer.from(fileContent).toString('base64'),
      mimeType: 'application/json',
      fileName: 'history.json'
    }
  }
}];"""

with open(workflow_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes_updated = 0
for node in data['nodes']:
    if node['name'] in ['Update Memory', 'Update Memory1']:
        if node['type'] == 'n8n-nodes-base.code':
            print(f"Updating node: {node['name']}")
            node['parameters']['jsCode'] = new_js_code
            nodes_updated += 1

if nodes_updated > 0:
    with open(workflow_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Successfully updated {nodes_updated} nodes.")
else:
    print("No nodes found to update.")
