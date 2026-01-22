import asyncio
import logging
import os
import sys
import tempfile
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import Message, ContentType

# Add project root to path so we can import from backend.core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.brain import LifeOSBrain
from backend.agents.doc_parser import DocumentProcessor
from backend.core.setup import supabase

from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Load env vars
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
USER_ID = os.getenv("TELEGRAM_USER_ID")  # Needs to be set in .env

# Initialize Bot and Dispatcher
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Initialize Scheduler
scheduler = AsyncIOScheduler()

async def send_daily_checkin():
    """Sends a daily check-in message to the user."""
    if not USER_ID:
        logging.warning("USER_ID not set in .env, skipping daily check-in.")
        return
        
    try:
        await bot.send_message(
            chat_id=USER_ID, 
            text="🌙 Buenas noches Mariano. Es hora de tu check-in diario.\n¿Cómo te sentiste hoy? (Del 1 al 10) ¿Qué tal estuvo tu día?"
        )
    except Exception as e:
        logging.error(f"Failed to send daily check-in: {e}")

# Initialize Agents
brain = LifeOSBrain()
doc_processor = DocumentProcessor()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Hola Mariano! Soy tu Life OS Bot. Envíame tus gastos, entrenamientos, pensamientos o documentos (PDF/Imágenes).")

@dp.message(F.document | F.photo)
async def handle_files(message: Message, bot: Bot):
    """
    Handles Document (PDF) and Photo ingestion for Finance parsing.
    """
    await message.answer("📄 Recibí un archivo. Analizando...")

    try:
        # 1. Determine file type and get file_id
        file_id = None
        is_image = False
        file_name = "unknown"

        if message.document:
            file_id = message.document.file_id
            file_name = message.document.file_name
            if message.document.mime_type == 'application/pdf':
                is_image = False
            elif message.document.mime_type.startswith('image/'):
                is_image = True
            else:
                await message.answer("⚠️ Formato no soportado. Solo acepto PDF o Imágenes.")
                return
        elif message.photo:
            # Photos come in array of sizes, take the largest
            file_id = message.photo[-1].file_id
            file_name = "photo.jpg"
            is_image = True

        # 2. Download File
        file_info = await bot.get_file(file_id)
        
        # Create a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file_name}") as tmp_file:
            await bot.download_file(file_info.file_path, destination=tmp_file.name)
            local_path = tmp_file.name

        try:
            # 3. Process File
            transactions = []
            
            if is_image:
                # Pass image path directly to Vision model
                transactions = doc_processor.analyze_finance_document(local_path, is_image=True)
            else:
                # Extract text from PDF first
                try:
                    text_content = doc_processor.extract_text_from_pdf(local_path)
                    transactions = doc_processor.analyze_finance_document(text_content, is_image=False)
                except ValueError as ve:
                    await message.answer(f"⚠️ Error leyendo PDF: {ve}")
                    return

            # 4. Insert into Supabase
            if not transactions:
                await message.answer("⚠️ No encontré transacciones válidas en el documento.")
                return

            total_amount = 0
            count = 0

            for t in transactions:
                if supabase:
                    supabase.table("finance_transactions").insert({
                        "date_transaction": t.date,
                        "amount": t.amount,
                        "currency": t.currency,
                        "category": t.category,
                        "merchant": t.merchant,
                        "is_fixed": False,
                        "source": f"doc_parser_{file_name}"
                    }).execute()
                    total_amount += t.amount
                    count += 1
            
            # 5. Summary Response
            await message.answer(
                f"✅ Procesamiento completado.\n"
                f"📄 Transacciones extraídas: {count}\n"
                f"💰 Total detectado: ${total_amount:,.2f}\n\n"
                f"Guardado en Base de Datos."
            )

        finally:
            # Cleanup temp file
            if os.path.exists(local_path):
                os.remove(local_path)

    except Exception as e:
        logging.error(f"Error processing file: {e}")
        await message.answer(f"❌ Error procesando el archivo:\n{str(e)}")

@dp.message()
async def process_message_handler(message: Message) -> None:
    """
    Main handler: Processes text via LifeOSBrain and saves to Supabase.
    """
    user_id = str(message.from_user.id)
    text = message.text
    
    if not text:
        return

    # 0. Log raw message
    try:
        if supabase:
            supabase.table("raw_logs").insert({
                "user_id": user_id,
                "message_content": text,
                "media_type": "text"
            }).execute()
    except Exception as e:
        logging.error(f"Failed to insert raw log: {e}")

    await message.answer("🧠 Procesando...")

    try:
        # 1. Process Input
        result = brain.process_input(text)
        category = result["category"]
        data = result["data"]
        confidence = result["confidence"]

        if category == "OTHER" or category == "UNCLEAR":
             await message.answer(f"⚠️ No estoy seguro de qué hacer con esto (Categoría: {category}).\nIntenta ser más específico.")
             return

        # 2. Insert into Supabase based on Category
        if not supabase:
             await message.answer("❌ Error: Base de datos no configurada.")
             return

        if category == "FINANCE":
            # Handle FinanceBatch (list of transactions)
            transactions_data = data.get("transactions", [])
            
            if not transactions_data:
                 await message.answer("⚠️ Entendí que es finanzas, pero no pude extraer los detalles.")
                 return

            count = 0
            total_amount = 0
            
            for tx in transactions_data:
                # Use extracted date or default to today
                tx_date = tx.get("date")
                if not tx_date or str(tx_date).lower() in ["none", "null"]:
                    tx_date = datetime.now().strftime("%Y-%m-%d")

                installments = tx.get("installments") or {}

                supabase.table("finance_transactions").insert({
                    "amount": tx.get("amount"),
                    "currency": tx.get("currency", "ARS"),
                    "category": tx.get("category"),
                    "subcategory": tx.get("subcategory"),
                    "merchant": tx.get("merchant"),
                    "date_transaction": tx_date,
                    "payment_method": tx.get("payment_method"),
                    "is_fixed": tx.get("is_fixed", False),
                    "is_client_expense": tx.get("is_client_expense", False),
                    "installment_current": installments.get("current"),
                    "installment_total": installments.get("total"),
                    "original_desc": tx.get("item"),
                    "source": "telegram_manual",
                }).execute()
                
                count += 1
                total_amount += float(tx.get("amount", 0))
            
            response_msg = f"✅ Se guardaron {count} gastos.\n💰 Total: ${total_amount:,.2f}"

        elif category == "HEALTH":
            supabase.table("activities").insert({
                "type": data.get("activity_type"),
                "details": data.get("details_json")
            }).execute()
            
            response_msg = f"✅ Actividad guardada:\n🏃 {data.get('activity_type')}\n📋 {data.get('details_json')}"

        elif category == "JOURNAL":
            # Embedding is already generated by Brain
            supabase.table("journal_entries").insert({
                "content": data.get("reflection_summary"),
                "mood_score": data.get("mood_score"),
                "sentiment_tags": data.get("sentiment_tags"),
                "embedding": data.get("embedding")
            }).execute()
            
            response_msg = f"✅ Journal guardado:\n📝 {data.get('reflection_summary')}\nmood: {data.get('mood_score')}/10"

        else:
            response_msg = f"❓ Categoría reconocida ({category}) pero no implementada en DB."

        # 3. Confirm to User
        await message.answer(response_msg)

    except Exception as e:
        logging.error(f"Error processing message: {e}")
        await message.answer(f"❌ Ocurrió un error procesando tu mensaje:\n{str(e)}")

async def main() -> None:
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_TOKEN not found in environment variables.")
        return

    # Start polling
    scheduler.add_job(send_daily_checkin, 'cron', hour=21, minute=0)
    scheduler.start()
    logging.info("🤖 Scheduler started (Daily Check-in at 21:00)")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
