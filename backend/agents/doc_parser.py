import os
import base64
import pdfplumber
from typing import List, Union
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

from backend.core.schemas import FinanceBatch, FinanceEntry

load_dotenv()

class DocumentProcessor:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Initialize LLM with gpt-4o for robust vision/text handling
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=self.api_key
        )

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extracts raw text from a PDF file using pdfplumber."""
        text_content = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text_content += page.extract_text() + "\n"
        except Exception as e:
            raise ValueError(f"Error reading PDF: {str(e)}")
        
        if not text_content.strip():
            raise ValueError("No text extracted from PDF. It might be scanned or encrypted.")
            
        return text_content

    def _encode_image(self, image_path: str) -> str:
        """Encodes an image to base64."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def analyze_finance_document(self, content: str, is_image: bool = False) -> List[FinanceEntry]:
        """
        Analyzes a financial document (text or image) and returns a list of transactions.
        
        Args:
            content: Raw text content OR file path to image if is_image=True
            is_image: Boolean flag indicating if content is an image path
        """
        
        system_prompt = """Eres un analista contable experto.
        Analiza este documento (resumen de cuenta, ticket o factura).
        Extrae UNA lista de transacciones financieras.
        
        Reglas:
        1. Ignora pagos de la propia tarjeta, saldos anteriores o intereses de financiación si no son compras nuevas.
        2. Para cada transacción extrae: fecha (YYYY-MM-DD), item/descripcion, monto, moneda (ARS/USD) y categoría.
        3. Categoriza inteligentemente (Supermercado, Ocio, Servicios, Transporte, etc).
        4. Si la moneda no es explícita, asume ARS.
        """

        if is_image:
            # Handle Image with Vision
            base64_image = self._encode_image(content)
            
            messages = [
                HumanMessage(
                    content=[
                        {"type": "text", "text": system_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ]
                )
            ]
            
            # Using with_structured_output directly on the LLM with the message list
            structured_llm = self.llm.with_structured_output(FinanceBatch)
            result = structured_llm.invoke(messages)
            
        else:
            # Handle Text
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}")
            ])
            
            structured_llm = self.llm.with_structured_output(FinanceBatch)
            chain = prompt | structured_llm
            result = chain.invoke({"input": content})

        return result.transactions
