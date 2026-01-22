from typing import List, Optional, Literal, Dict
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
    
    category: Literal[
        "Ingreso: Sueldo", "Ingreso: Alquiler", "Ingreso: Freelance",
        "Vivienda: Depto", "Vehículo: Auto", "Vehículo: Moto", "Educación: Data Science", "Servicios",
        "Supermercado", "Salidas/Ocio", "Suscripciones", "Salud", "Otros"
    ] = Field(description="Category of the transaction. Must match exactly one of the provided options.")
    
    subcategory: Optional[str] = Field(None, description="Specific subcategory (e.g., Nafta, Expensas, Cena, Seguro).")

    payment_method: Literal[
        "Efectivo", "Débito", "Crédito: Visa", "Crédito: Master", "Crédito: Amex", "Transferencia"
    ] = Field(default="Efectivo", description="Payment method used. Defaults to 'Efectivo' if unclear, or 'Crédito: Visa' if 'tarjeta' is mentioned.")
    
    merchant: Optional[str] = Field(None, description="Name of the merchant or entity (e.g., Coto, Shell). Infer generic if needed.")
    item: Optional[str] = Field(None, description="Description of the item or service purchased.")
    date: Optional[str] = Field(None, description="Date of the transaction (YYYY-MM-DD).")
    
    is_fixed: bool = Field(default=False, description="True if this is a recurring fixed expense (e.g. rent, subscription).")
    is_client_expense: bool = Field(default=False, description="True if this expense is on behalf of a client.")

    # Installment support
    installments: Optional[Dict[str, int]] = Field(
        None, 
        description="If it's an installment plan, provide {'current': int, 'total': int}. Example: {'current': 1, 'total': 12}"
    )

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
