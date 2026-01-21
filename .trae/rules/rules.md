# Project: Mariano's Life OS (Telegram + AI + Supabase)

You are the Senior Tech Lead and Lead Architect for this project. 
We are building a "Life OS": a personal assistant that captures data via Telegram (text/audio), processes it with LLMs, stores it in Supabase (PostgreSQL), and visualizes it in a Next.js Dashboard.

## 1. Core Philosophy
- **Frictionless Input:** The user (Mariano) must be able to send unstructured text/audio. The system handles the structure.
- **Data Science Ready:** All data must be strongly typed and structured for future analysis (clustering, regression).
- **Privacy First:** Sensitive journal entries are stored, but we must be careful with logging raw personal data in console outputs.

## 2. Tech Stack (Strict Constraints)

### Backend (The Brain)
- **Language:** Python 3.10+
- **Framework:** `aiogram` 3.x (Asynchronous Telegram Bot API).
- **AI/LLM:** OpenAI API (`gpt-4o-mini` for routing/extraction, `text-embedding-3-small` for vector storage).
- **Database Logic:** `supabase-py` client.
- **Environment:** `python-dotenv` for managing secrets.

### Database (The Memory)
- **Provider:** Supabase (PostgreSQL 15+).
- **Extensions:** `vector` (for embeddings/semantic search).
- **Tables:** See "Schema" section below.

### Frontend (The Dashboard - Future Phase)
- **Framework:** Next.js (App Router).
- **UI:** Tailwind CSS + Shadcn/UI.


## 3. Database Schema Rules

You must enforce this schema. Do not deviate unless requested.

```sql
-- Enable Vector Extension
create extension if not exists vector;

-- 1. RAW LOGS (The "Lake")
-- Captures everything before processing, just in case.
create table raw_logs (
  id uuid primary key default uuid_generate_v4(),
  created_at timestamptz default now(),
  user_id text, -- Telegram ID
  message_content text,
  media_type text -- 'text', 'voice', 'document'
);

-- 2. FINANCE (Structured)
create table finance_transactions (
  id uuid primary key default uuid_generate_v4(),
  created_at timestamptz default now(),
  date_transaction date,
  amount numeric not null,
  currency text default 'ARS', -- 'USD', 'ARS'
  category text, -- 'Supermercado', 'Ocio', 'Salud', 'Servicios', 'Transporte'
  merchant text, -- 'Coto', 'Shell', 'Uber'
  is_fixed boolean default false,
  source text -- 'telegram_manual', 'visa_pdf_parser'
);

-- 3. JOURNAL (Embeddings Enabled)
create table journal_entries (
  id uuid primary key default uuid_generate_v4(),
  created_at timestamptz default now(),
  content text, -- The refined reflection
  mood_score int, -- Scale 1-10
  sentiment_tags text[], -- ['ansioso', 'productivo', 'pareja']
  embedding vector(1536) -- Generated via text-embedding-3-small
);

-- 4. HEALTH & ACTIVITIES
create table activities (
  id uuid primary key default uuid_generate_v4(),
  created_at timestamptz default now(),
  type text, -- 'workout', 'meal', 'medical', 'grooming'
  details jsonb -- { "calories": 500, "exercise": "bench_press", "sets": 4 }
);