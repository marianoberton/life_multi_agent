from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from backend.core.schemas import HealthEntry

class HealthAgent:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def process(self, text: str) -> HealthEntry:
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
