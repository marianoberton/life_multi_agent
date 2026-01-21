from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from backend.core.schemas import FinanceBatch

class FinanceAgent:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def process(self, text: str) -> FinanceBatch:
        """Extracts a LIST of finance transactions based on Mariano's specific context."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        system_prompt = f"""Eres el contador personal de Mariano. 
        - ACTIVOS: Tiene un Departamento, un Auto y una Moto. 
        - INGRESOS: Sueldo fijo, Alquileres (variable) y Freelance (variable). 
        - EDUCACIÓN: Estudia Data Science (gastos académicos). 
        - CLIENTES: A veces paga suscripciones para clientes (detectar contexto y marcar `is_client_expense=True`). 
        - PAGOS: Usa Visa, Master y Amex. Si dice 'tarjeta' sin especificar, asume 'Crédito: Visa'. 
        - REGLA: Extrae TODAS las transacciones del texto (pueden ser varias). Si menciona USD, usa moneda 'USD'.
        - FECHA: Hoy es {today_str}. Úsalo para resolver fechas relativas.

        Categorías válidas (Strict):
        - Ingresos: "Ingreso: Sueldo", "Ingreso: Alquiler", "Ingreso: Freelance".
        - Estructurales: "Vivienda: Depto", "Vehículo: Auto", "Vehículo: Moto", "Educación: Data Science", "Servicios".
        - Consumo: "Supermercado", "Salidas/Ocio", "Suscripciones", "Salud", "Otros".
        
        Métodos de pago válidos (Strict):
        - "Efectivo", "Débito", "Crédito: Visa", "Crédito: Master", "Crédito: Amex", "Transferencia".
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])
        
        structured_llm = self.llm.with_structured_output(FinanceBatch)
        chain = prompt | structured_llm
        
        return chain.invoke({"input": text})
