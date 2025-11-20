import requests
import json

class LLMService:
    """LLM Service using llama.cpp server API"""
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        print(f"Using llama.cpp server at {base_url}")
        print("✅ LLM service configured (make sure llama.cpp server is running)")
    
    def generate_response(self, user_input, language="en"):
        """Generate response using llama.cpp server"""
        lang_instructions = {
            "en": "You are a helpful voice assistant. Give concise, natural responses in English.",
            "hi": "आप एक सहायक वॉयस असिस्टेंट हैं। हिंदी में संक्षिप्त, स्वाभाविक उत्तर दें।",
            "te": "మీరు సహాయక వాయిస్ అసిస్టెంట్. తెలుగులో సంక్షిప్త, సహజ ప్రతిస్పందనలు ఇవ్వండి।"
        }
        
        system_msg = lang_instructions.get(language, lang_instructions["en"])
        
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{system_msg}<|eot_id|>
<|start_header_id|>user<|end_header_id|>
{user_input}<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""
        
        try:
            response = requests.post(
                f"{self.base_url}/completion",
                json={
                    "prompt": prompt,
                    "n_predict": 256,
                    "temperature": 0.7,
                    "stop": ["<|eot_id|>"]
                },
                timeout=120  # Increased to 2 minutes for slower systems
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["content"].strip()
            else:
                return f"Error: Server returned {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to llama.cpp server. Make sure it's running on port 8080."
        except Exception as e:
            return f"Error: {str(e)}"
