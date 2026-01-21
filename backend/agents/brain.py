import os
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Import schemas
from backend.core.schemas import RoutingDecision

# Import Sub-Agents
from backend.agents.finance_agent import FinanceAgent
from backend.agents.health_agent import HealthAgent
from backend.agents.journal_agent import JournalAgent

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

        # Initialize Sub-Agents
        self.finance_agent = FinanceAgent(self.llm)
        self.health_agent = HealthAgent(self.llm)
        self.journal_agent = JournalAgent(self.llm)

    def generate_embedding(self, text: str) -> List[float]:
        """Generates a vector embedding for the given text."""
        return self.embeddings.embed_query(text)

    def process_input(self, text: str) -> Dict[str, Any]:
        """
        Main entry point. Routes the input and delegates to specialized agents.
        """
        # 1. Routing Step
        router_result = self._route_input(text)
        category = router_result.category
        confidence = router_result.confidence

        extracted_data = None
        
        # 2. Delegation Step
        if category == "FINANCE":
            extracted_data = self.finance_agent.process(text)
        elif category == "HEALTH":
            extracted_data = self.health_agent.process(text)
        elif category == "JOURNAL":
            extracted_data = self.journal_agent.process(text)
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
