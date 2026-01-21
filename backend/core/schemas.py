from typing import List, Optional, Literal
from pydantic import BaseModel, Field

# --- Enums ---
class CategoryEnum(str):
    FINANCE = "FINANCE"
    HEALTH = "HEALTH"
    JOURNAL = "JOURNAL"
    OTHER = "OTHER"

# --- Extraction Models ---

class FinanceEntry(BaseModel):
    """Structured data for financial transactions."""
    amount: float = Field(description="The numeric amount of the transaction.")
    currency: str = Field(default="ARS", description="Currency code (e.g., ARS, USD). Defaults to ARS.")
    category: Literal["Supermercado", "Servicios", "Transporte", "Ocio", "Salud", "Vivienda", "Educación", "Otros"] = Field(
        description="Category of the expense. MUST be one of: Supermercado, Servicios, Transporte, Ocio, Salud, Vivienda, Educación, Otros."
    )
    merchant: Optional[str] = Field(None, description="Name of the merchant or entity (e.g., Coto, Shell, Edesur). If not explicit, infer a generic one (e.g., 'Estación de Servicio' for gas).")
    item: Optional[str] = Field(None, description="Description of the item or service purchased.")
    date: Optional[str] = Field(None, description="Date of the transaction (YYYY-MM-DD).")

class FinanceBatch(BaseModel):
    """List of financial transactions extracted from a document."""
    transactions: List[FinanceEntry] = Field(description="List of extracted finance entries.")

class HealthEntry(BaseModel):
    """Structured data for health and physical activities."""
    activity_type: str = Field(description="Type of activity (e.g., workout, meal, medical).")
    details_json: dict = Field(default_factory=dict, description="Detailed attributes (calories, sets, reps, etc.) as a dictionary.")
    duration_minutes: Optional[int] = Field(None, description="Duration of the activity in minutes.")

class JournalEntry(BaseModel):
    """Structured data for personal journal entries."""
    mood_score: int = Field(description="Mood score on a scale of 1-10.")
    sentiment_tags: List[str] = Field(description="List of sentiment tags (e.g., anxious, productive).")
    reflection_summary: str = Field(description="A refined summary or the main content of the reflection.")

# --- Routing Model ---

class RoutingDecision(BaseModel):
    """Decision on how to route the user input."""
    category: Literal["FINANCE", "HEALTH", "JOURNAL", "OTHER"] = Field(
        description="The category that best fits the input text."
    )
    confidence: float = Field(
        description="Confidence score between 0.0 and 1.0."
    )
