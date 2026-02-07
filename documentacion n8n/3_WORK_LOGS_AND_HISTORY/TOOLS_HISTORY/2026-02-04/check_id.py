
import json

def check_drive_id(file_id):
    # Google Drive IDs are typically ~33 chars (Alphanumeric + symbols)
    # or ~19 chars for older files.
    # Paths contain slashes.
    if "/" in file_id:
        return False, "Detected PATH instead of ID"
    
    if len(file_id) < 10:
        return False, "ID too short"
        
    return True, "Valid ID format"

# Mock Input from n8n
mock_input = "Documentos/Personal/cv.pdf" # Common hallucination
valid, reason = check_drive_id(mock_input)
print(f"Input: {mock_input} -> Valid: {valid} ({reason})")

mock_input_2 = "1B2M2Y8AsPTA9Tj_y3JqJzKe321" 
valid_2, reason_2 = check_drive_id(mock_input_2)
print(f"Input: {mock_input_2} -> Valid: {valid_2} ({reason_2})")
