import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Import schemas
from backend.core.schemas import (
    RoutingDecision,
    FinanceEntry,
    FinanceBatch,
    HealthEntry,
    JournalEntry
)

load_dotenv()

class LifeOSBrain:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        # Initialize the base LLM (gpt-4o-mini is efficient for this)
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=self.api_key
        )

        # Initialize Embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=self.api_key
        )

    def generate_embedding(self, text: str) -> List[float]:
        """Generates a vector embedding for the given text."""
        return self.embeddings.embed_query(text)

    def process_input(self, text: str) -> Dict[str, Any]:
        """
        Main entry point. Routes the input and extracts structured data.
        """
        # 1. Routing Step
        router_result = self._route_input(text)
        category = router_result.category
        confidence = router_result.confidence

        # If confidence is low, we might want to flag it (optional logic)
        # For now, we trust the category unless it's explicitly "OTHER"
        
        extracted_data = None
        
        if category == "FINANCE":
            extracted_data = self._extract_finance(text)
        elif category == "HEALTH":
            extracted_data = self._extract_health(text)
        elif category == "JOURNAL":
            extracted_data = self._extract_journal(text)
        else:
            # Category is OTHER
            category = "OTHER"
            extracted_data = {"raw_text": text, "message": "Could not categorize input."}

        # Prepare final data dict
        final_data = extracted_data.model_dump() if extracted_data and hasattr(extracted_data, 'model_dump') else extracted_data
        
        # Add embedding to data if it's a Journal entry
        if category == "JOURNAL" and final_data:
            final_data["embedding"] = self.generate_embedding(text)

        return {
            "category": category,
            "confidence": confidence,
            "data": final_data
        }

    def _route_input(self, text: str) -> RoutingDecision:
        """Decides the category of the input."""
        system_prompt = """You are the central router for a personal Life OS.
        Analyze the user's input and categorize it into one of the following:
        - FINANCE: Expense tracking, purchases, income.
        - HEALTH: Workouts, meals, medical info, grooming.
        - JOURNAL: Personal reflections, mood logs, diary entries.
        - OTHER: Anything that doesn't fit (e.g., questions, random chatter).
        
        Return a confidence score (0.0-1.0)."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])
        
        structured_llm = self.llm.with_structured_output(RoutingDecision)
        chain = prompt | structured_llm
        
        return chain.invoke({"input": text})

    def _extract_finance(self, text: str) -> FinanceBatch:
        """Extracts a LIST of finance transactions."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        system_prompt = f"""You are an expert accountant. Extract ALL financial transactions from the text.
        
        RULES:
        1. **Multiple Expenses**: The user might list multiple expenses in one sentence. Extract each as a separate entry.
        2. **Date**: Today is {today_str}. Use this to resolve relative dates (e.g., "ayer", "hoy").
        3. **Currency**: Default to 'ARS' unless specified otherwise.
        4. **Categories**: You MUST map each expense to one of these exact categories:
           - 'Supermercado' (Groceries, food shopping)
           - 'Servicios' (Utilities like electricity, gas, internet, phone)
           - 'Transporte' (Gas/Nafta, Uber, Taxi, Public transport, Tolls)
           - 'Ocio' (Restaurants, Movies, Going out)
           - 'Salud' (Pharmacy, Doctors, Gym, Sports)
           - 'Vivienda' (Rent, Condo fees/Expensas)
           - 'Educación' (Courses, Books, Tuition)
           - 'Otros' (Anything else)
        5. **Merchant Inference**: 
           - If the merchant is explicitly named (e.g. "Coto", "Shell"), use it.
           - If NOT named, INFER a generic entity based on context.
             - "luz" -> "Servicios Eléctricos"
             - "gas" -> "Distribuidora de Gas"
             - "nafta" -> "Estación de Servicio"
             - "alfajor" -> "Kiosco" or "Tienda"
           - NEVER use "Desconocido" or concatenate words randomly.
        
        Return a 'transactions' list containing all detected items.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])
        
        structured_llm = self.llm.with_structured_output(FinanceBatch)
        chain = prompt | structured_llm
        
        return chain.invoke({"input": text})

    def _extract_health(self, text: str) -> HealthEntry:
        """Extracts health, workout OR meal details."""
        system_prompt = """Extract health, workout, or nutrition details.
        
        IF IT IS A MEAL:
        - Set 'activity_type' to 'meal'.
        - In 'details_json', try to extract: 'food_items' (list), 'calories_est' (int), 'meal_time' (breakfast/lunch/dinner).
        
        IF IT IS A WORKOUT:
        - Set 'activity_type' to 'workout'.
        - In 'details_json', extract exercises, sets, reps, weight.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])
        
        structured_llm = self.llm.with_structured_output(HealthEntry)
        chain = prompt | structured_llm
        
        return chain.invoke({"input": text})

    def _extract_journal(self, text: str) -> JournalEntry:
        """Extracts journal and mood details."""
        system_prompt = """Analyze the text for a journal entry.
        - Estimate a 'mood_score' from 1 (terrible) to 10 (amazing) based on the sentiment.
        - Generate a list of 'sentiment_tags' (3-5 tags).
        - 'reflection_summary' should be the refined content of the user's thought.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])
        
        structured_llm = self.llm.with_structured_output(JournalEntry)
        chain = prompt | structured_llm
        
        return chain.invoke({"input": text})
