from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import os
import json

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for hackathon simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration ---
# User provided Gemini API Key
GEMINI_API_KEY = "AIzaSyDve36j4qx0x8NIf1zC_JQU0-PBnMLnKwc"

# --- Models (Must be defined before use) ---

class PatientSummary(BaseModel):
    age: str = Field(..., description="Patient age if provided, else 'Unknown'")
    symptoms: List[str] = Field(..., description="List of identified symptoms")
    duration: str = Field(..., description="Duration of symptoms")
    severity: str = Field(..., description="mild, moderate, or severe")

class TriageResponse(BaseModel):
    patient_summary: PatientSummary
    red_flags_detected: List[str] = Field(..., description="List of red flag symptoms")
    risk_score: int = Field(..., ge=0, le=10, description="Risk score 0-10")
    recommended_care: Literal["Self Care", "Tele-Consult", "Emergency"]
    care_reasoning: str
    next_steps: List[str]
    medical_disclaimer: str = "This AI provides preliminary guidance only and does not replace professional medical advice."
    
    # We add this field to carry the conversation, as a purely JSON output 
    # without a message field makes a chat impossible.
    message_to_patient: str = Field(..., description="The conversational response to the patient")

class ChatRequest(BaseModel):
    message: str
    history: List[dict] # [{"role": "user", "content": "..."}, ...]

# --- System Prompt ---

SYSTEM_PROMPT = """
You are an AI-powered medical conversational triage assistant.
Your goal is to assess symptoms, assign risk (0-10), and recommend care (Self Care, Tele-Consult, Emergency).

RULES:
1. Conduct a calm, empathetic conversation.
2. Ask one clear follow-up question at a time to gather info (Age, Symptoms, Duration, Severity, Red flags).
3. Calculate Risk Score based on input (Mild: 1-2, Mod: 3-5, Severe: 6-10).
4. Output JSON ONLY. No markdown outside JSON.

JSON FORMAT:
{
  "patient_summary": { "age": "...", "symptoms": [], "duration": "...", "severity": "..." },
  "red_flags_detected": [],
  "risk_score": 0,
  "recommended_care": "Self Care | Tele-Consult | Emergency",
  "care_reasoning": "...",
  "next_steps": ["..."],
  "medical_disclaimer": "...",
  "message_to_patient": "Your conversational reply here..."
}
"""

# --- External Tools (Mock/Real) ---

SERPAPI_KEY = os.getenv("SERPAPI_KEY") # Get from env or set here

def search_web(query: str):
    """
    Performs a web search using SerpApi if available, otherwise returns a mock result.
    """
    print(f"Searching web for: {query}")
    
    if SERPAPI_KEY:
        try:
            from serpapi import GoogleSearch
            search = GoogleSearch({
                "q": query,
                "api_key": SERPAPI_KEY
            })
            results = search.get_dict()
            if "organic_results" in results:
                snippets = [r.get("snippet", "") for r in results["organic_results"][:3]]
                return "\n".join(snippets)
        except Exception as e:
            print(f"Search API Error: {e}")
            
    return "Simulated search result: Standard medical guidance advises consulting a healthcare professional for specific symptoms."

def get_ai_response(messages: List[dict]):
    """
    Calls Google Gemini API using the provided key.
    """
    error_msg = None
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=GEMINI_API_KEY)
            
            # Using 'gemini-flash-latest' (1.5 Flash) which is stable and often has better free tier limits
            model = genai.GenerativeModel("models/gemini-flash-latest")
            
            # Convert OpenAI-style messages to Gemini history
            
            formatted_history = []
            system_instruction = ""
            
            for m in messages:
                if m["role"] == "system":
                    system_instruction += m["content"] + "\n"
                elif m["role"] == "user":
                    formatted_history.append({"role": "user", "parts": [m["content"]]})
                elif m["role"] == "assistant":
                    formatted_history.append({"role": "model", "parts": [m["content"]]})
            
            current_message = formatted_history.pop() if formatted_history and formatted_history[-1]["role"] == "user" else {"parts": [""]}
            
            chat = model.start_chat(history=formatted_history)
            
            final_prompt = f"{system_instruction}\n\nUser Request: {current_message['parts'][0]}"
            
            response = chat.send_message(
                final_prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            content = response.text
            if content:
                # Remove markdown guards if present
                clean_content = content.strip().lstrip("```json").rstrip("```").strip()
                return json.loads(clean_content)
                
        except Exception as e:
            if "429" in str(e):
                error_msg = "Rate limit exceeded (Too many requests). Please wait 30-60 seconds and try again."
                print(f"Gemini Rate Limit: {e}")
            else:
                print(f"Gemini API Error: {e}")
                error_msg = str(e)
            
            # --- Auto-Diagnosis: List available models ---
            try:
                available_models = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        available_models.append(m.name)
                
                if available_models:
                    model_list_str = "\\n".join(available_models)
                    error_msg += f"\\n\\n[DEBUG] AVAILABLE MODELS FOUND:\\n{model_list_str}"
            except Exception as debug_e:
                error_msg += f" (Could not list models: {debug_e})"
            
            pass
            
    # --- Fallback Mock Logic ---
    print(f"Using Mock AI Logic. Error was: {error_msg}")
    user_msg = messages[-1]["content"].lower()
    
    # Simple keyword detection
    risk = 0
    symptoms = []
    care = "Self Care"
    msg = "Could you describe your symptoms in more detail?"
    
    if "pain" in user_msg:
        symptoms.append("Pain")
        risk += 2
    if "fever" in user_msg:
        symptoms.append("Fever")
        risk += 3
        msg = "How high is the fever and how long have you had it?"
    if "chest" in user_msg and "pain" in user_msg:
        symptoms.append("Chest Pain")
        risk = 9
        care = "Emergency"
        msg = "Chest pain is a serious medical emergency. Please call emergency services immediately."
    
    # Simulate a "Search" if user asks specifically
    if "search" in user_msg or "google" in user_msg:
        search_result = search_web(user_msg)
        msg += f"\n\n(I also found this online: {search_result})"

    # Prepend error for debugging
    if error_msg:
        msg = f"[SYSTEM ERROR: {error_msg}] \n\n" + msg

    return {
        "patient_summary": {
            "age": "Unknown",
            "symptoms": symptoms,
            "duration": "Unknown",
            "severity": "Moderate" if risk > 4 else "Mild"
        },
        "red_flags_detected": ["Chest Pain"] if risk > 7 else [],
        "risk_score": risk,
        "recommended_care": care,
        "care_reasoning": "Based on initial assessment of keywords.",
        "next_steps": ["Monitor symptoms", "Seek professional advice"],
        "medical_disclaimer": "This AI provides preliminary guidance only.",
        "message_to_patient": msg
    }

@app.get("/")
def read_root():
    return {"status": "Medical Triage API is running"}

@app.post("/chat", response_model=TriageResponse)
def chat_endpoint(request: ChatRequest):
    # Construct the message history for the AI
    # System prompt + History + New Message
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + request.history + [{"role": "user", "content": request.message}]
    
    response_data = get_ai_response(messages)
    
    return TriageResponse(**response_data)
