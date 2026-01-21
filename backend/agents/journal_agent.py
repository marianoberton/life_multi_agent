from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from backend.core.schemas import JournalEntry

class JournalAgent:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def process(self, text: str) -> JournalEntry:
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
