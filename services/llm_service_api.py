import requests
import json

class LLMService:
    """LLM Service using llama.cpp server API"""
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        print(f"Using llama.cpp server at {base_url}")
        print("✅ LLM service configured (make sure llama.cpp server is running)")
    
    def generate_response(self, user_input, language="en", max_tokens=512):
        """Generate response using llama.cpp server
        
        Args:
            user_input: User's question/input
            language: Language code (en/hi/te)
            max_tokens: Maximum response length (default 512, ~300-400 words)
        """
        lang_instructions = {
            "en": "You are a helpful voice assistant. Give clear, natural responses in English. Be informative but conversational. You can use English words naturally when needed.",
            "hi": "आप एक सहायक वॉयस असिस्टेंट हैं। हिंदी में स्पष्ट, स्वाभाविक उत्तर दें। जानकारीपूर्ण लेकिन बातचीत के अंदाज में जवाब दें। अगर जरूरी हो तो English शब्द भी इस्तेमाल कर सकते हैं।",
            "te": "మీరు సహాయక వాయిస్ అసిస్టెంట్. తెలుగులో స్పష్టమైన, సహజ ప్రతిస్పందనలు ఇవ్వండి. సమాచారంతో కూడిన కానీ సంభాషణ శైలిలో సమాధానం ఇవ్వండి. అవసరమైతే English పదాలు కూడా వాడవచ్చు।"
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
                    "n_predict": max_tokens,  # Configurable token limit
                    "temperature": 0.7,
                    "stop": ["<|eot_id|>"],
                    "n_threads": 4  # Use 4 CPU threads for faster processing
                },
                timeout=300  # Increased to 5 minutes for slower CPUs
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
