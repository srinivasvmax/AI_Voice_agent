from llama_cpp import Llama

class LLMService:
    def __init__(self, model_path="models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"):
        print("Loading Llama model...")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=1024,
            n_threads=4
        )
        print("✅ Llama model loaded")
    
    def generate_response(self, user_input, language="en", max_tokens=256):
        """Generate response using Llama in the detected language
        
        Args:
            user_input: User's question/input
            language: Language code (en/hi/te)
            max_tokens: Maximum response length (default 512, ~300-400 words)
        """
        # Universal instruction for all languages
        universal_instruction = (
            "You are an intelligent multilingual voice assistant designed to handle customer queries "
            "related to the Government Electricity/Power Department. "
            "Your primary tasks are: "
            "1) Understand customer issues even if the speech-to-text transcription is noisy, incomplete, mixed-language, or misspelled. "
            "2) Identify the customer's intent accurately—such as bill issues, power outage, meter problems, complaints, payments, new connections, load increase, etc. "
            "3) Provide clear, correct, and helpful responses based on typical electricity department processes. "
            "4) Fill missing information logically when possible, and ask only necessary clarifying questions. "
            "5) Maintain a friendly, polite, and professional tone."
        )
        
        lang_instructions = {
            "en": (
                "Respond naturally in English. "
                "If the user's query is unclear because of transcription errors or mixed languages, "
                "infer the most likely meaning from context. "
                "Be concise but informative. "
                "Common customer intents include: power outage, electricity bill amount, high bill complaint, bill due date, "
                "meter reading issues, meter not working, new connection, service status, load change, and payment status. "
                "Guide the customer with typical electricity board procedures. "
                "If mandatory information is missing (e.g., consumer number), politely ask for it."
            ),
            "hi": (
                "हिंदी में स्पष्ट और स्वाभाविक तरीके से जवाब दें। "
                "अगर यूज़र की बात ट्रांसक्रिप्शन एरर या मिक्स्ड लैंग्वेज के कारण अधूरी हो, तो कॉन्टेक्स्ट के आधार पर सबसे संभव अर्थ समझें। "
                "सामान्य शिकायतों में बिजली गुल होना, बिल की राशि, ज़्यादा बिल आने की शिकायत, बिल की आख़िरी तारीख, "
                "मीटर रीडिंग समस्या, मीटर काम न करना, नया कनेक्शन, लोड बढ़ाना/घटाना, पेमेंट स्टेटस आदि शामिल होते हैं। "
                "यूज़र को बिजली विभाग की सामान्य प्रक्रिया के अनुसार गाइड करें। "
                "अगर ज़रूरी जानकारी (जैसे कंज़्यूमर नंबर) नहीं है, तो विनम्रता से पूछें।"
            ),
            "te": (
                "తెలుగులో సహజంగా మరియు స్పష్టంగా సమాధానం ఇవ్వండి. "
                "Speech-to-text లో తప్పులు వచ్చినా, మాటలు మిక్స్ అయ్యినా, సందర్భం ఆధారంగా యూజర్ అసలు ఉద్దేశ్యాన్ని అర్థం చేసుకోండి. "
                "సాధారణ సమస్యలు: పవర్ కట్, కరెంట్ బిల్లు మొత్తం, బిల్లు ఎక్కువగా రావడం, చివరి చెల్లింపు తేదీ, "
                "మీటర్ రీడింగ్ లో పొరపాట్లు, మీటర్ పని చేయకపోవడం, కొత్త కనెక్షన్, లోడ్ మార్పు, పేమెంట్ స్టేటస్ మొదలైనవి. "
                "వినియోగదారుడిని విద్యుత్ శాఖ యొక్క సాధారణ ప్రాసెస్ ప్రకారం మార్గనిర్దేశం చేయండి. "
                "అవసరమైన వివరాలు (ఉదా: Consumer Number) లేకపోతే, మర్యాదపూర్వకంగా అడగండి."
            )
        }
        
        # Combine universal instruction with language-specific instruction
        lang_specific = lang_instructions.get(language, lang_instructions["en"])
        system_msg = f"{universal_instruction}\n\n{lang_specific}"
        
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{system_msg}<|eot_id|>
<|start_header_id|>user<|end_header_id|>
{user_input}<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""
        
        response = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=0.6,
            stop=["<|eot_id|>"]
        )
        
        return response["choices"][0]["text"].strip()
