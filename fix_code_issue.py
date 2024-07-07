import requests

# Deep AI API endpoint and key (you can load these from environment variables or a config file)
DEEP_AI_API_KEY = "<your_deep_ai_api_key>"
DEEP_AI_API_ENDPOINT = "https://api.deepai.org"

# Function to fix code issues using Deep AI
def fix_code_issue(code_snippet, action):
    try:
        endpoint = f"{DEEP_AI_API_ENDPOINT}/{action}"
        headers = {
            "Authorization": f"Bearer {DEEP_AI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"code": code_snippet}
        response = requests.post(endpoint, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json().get("output", "No output received from Deep AI.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

# Example usage
if __name__ == "__main__":
    code_snippet = """
    def add_numbers(a, b):
        return a + b
    
    print(add_numbers(5, 10))
    """
    action = "optimize"  # Choose "debug" or "optimize"
    result = fix_code_issue(code_snippet, action)
    print("Fixed Code:")
    print(result)
