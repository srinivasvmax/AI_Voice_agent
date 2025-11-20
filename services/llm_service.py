from llama_cpp import Llama

class LLMService:
    def __init__(self, model_path="models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"):
        print("Loading Llama model...")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=4
        )
        print("✅ Llama model loaded")
    
    def generate_response(self, user_input, language="en"):
        """Generate response using Llama in the detected language"""
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
        
        response = self.llm(
            prompt,
            max_tokens=256,
            temperature=0.7,
            stop=["<|eot_id|>"]
        )
        
        return response["choices"][0]["text"].strip()
