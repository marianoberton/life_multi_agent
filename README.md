# 🧠 Mariano's Life OS (Telegram + AI + Supabase)

## 📌 Descripción General
**Life OS** es un ecosistema de inteligencia personal diseñado para capturar, estructurar y visualizar tu vida sin fricción. Actúa como un "Segundo Cerebro" que procesa entradas de lenguaje natural (texto o audio) a través de Telegram, las convierte en datos estructurados mediante IA y las almacena en una base de datos vectorial para análisis futuro.

---

## 🤖 Arquitectura de Agentes

El sistema no es un simple bot; es una orquestación de múltiples agentes especializados gobernados por un "Cerebro Central". A continuación se detalla la lógica interna de cada uno:

### 1. 🔀 El Router (Dispatcher)
Es la puerta de entrada. Cada mensaje que envías pasa primero por aquí.
- **Modelo:** `gpt-4o-mini`
- **Función:** Analiza la intención semántica del mensaje y decide a qué especialista derivarlo.
- **Categorías:**
  - `FINANCE`: Gastos, ingresos, compras.
  - `HEALTH`: Entrenamientos, comidas, datos médicos.
  - `JOURNAL`: Reflexiones, diario íntimo, estado de ánimo.
  - `OTHER`: Mensajes no clasificables (charlas casuales).
- **Salida:** Retorna una `RoutingDecision` con la categoría y un nivel de confianza (0.0 - 1.0).

---

### 2. 💸 Agente Financiero (Finance Agent)
Especialista en estructurar el caos de tus gastos diarios.

- **Lógica de Extracción (`FinanceEntry`):**
  - **Fecha Inteligente:** El agente recibe la fecha actual del sistema en su prompt. Esto le permite resolver referencias temporales relativas como *"ayer"*, *"el viernes pasado"* o *"hace dos días"* y convertirlas a formato ISO (`YYYY-MM-DD`).
  - **Moneda:** Por defecto asume `ARS` si no se especifica otra (como `USD`).
  - **Categorización:** Infiere la categoría (ej: "Supermercado", "Transporte") basada en el contexto del gasto.
  - **Comercio:** Identifica entidades comerciales (ej: "Coto", "Shell", "Uber").

- **Ejemplo Real:**
  - *Input:* "Cargue 20 lucas de nafta en la shell de libertador ayer"
  - *Proceso:* Detecta "ayer" -> Calcula fecha. Detecta "20 lucas" -> 20000.
  - *Output:*
    ```json
    {
      "amount": 20000,
      "currency": "ARS",
      "category": "Transporte",
      "merchant": "Shell",
      "item": "nafta",
      "date": "2024-01-19"
    }
    ```

---

### 3. 🏋️ Agente de Salud (Health Agent)
Diseñado para ser flexible, ya que los entrenamientos y comidas tienen estructuras muy variadas.

- **Lógica de Extracción (`HealthEntry`):**
  - **Tipificación:** Clasifica la entrada en `workout`, `meal`, `medical`, etc.
  - **Detalles Flexibles (`details_json`):** A diferencia de las finanzas (que son rígidas), aquí guardamos los detalles en un objeto JSON libre. Esto permite guardar tanto *"4 series de 10 reps"* como *"una ensalada césar"*.
  - **Duración:** Extrae tiempos explícitos en minutos.

- **Ejemplo Real:**
  - *Input:* "Metí 4 series de banco plano con 80kg y después corrí 20 mins"
  - *Output:*
    ```json
    {
      "activity_type": "workout",
      "duration_minutes": 20,
      "details_json": {
        "exercises": [
          { "name": "banco plano", "sets": 4, "weight": "80kg" },
          { "name": "correr", "duration": "20 mins" }
        ]
      }
    }
    ```

---

### 4. 📓 Agente de Journaling (The Therapist)
El componente más empático y analítico del sistema.

- **Lógica de Extracción (`JournalEntry`):**
  - **Análisis de Sentimiento:** Evalúa el texto y asigna un `mood_score` del 1 al 10.
  - **Etiquetado:** Genera etiquetas automáticas (ej: `ansioso`, `productivo`, `nostálgico`).
  - **Resumen Reflexivo:** Reescribe tu entrada para capturar la esencia del pensamiento.
  - **Vectorización (Embeddings):** Utiliza el modelo `text-embedding-3-small` de OpenAI para convertir tu reflexión en un vector matemático. Esto permite que a futuro puedas hacer preguntas como *"¿Cómo me sentía en enero del año pasado?"* y el sistema busque por significado semántico, no por palabras clave.

- **Ejemplo Real:**
  - *Input:* "Hoy fue un día largo, me peleé con mi jefe pero al final pude cerrar el reporte."
  - *Output:*
    ```json
    {
      "mood_score": 6,
      "sentiment_tags": ["estrés", "logro", "trabajo"],
      "reflection_summary": "Día laboral difícil con conflictos interpersonales, pero con resolución exitosa de tareas pendientes."
    }
    ```

---

## 🛠️ Stack Tecnológico

### Backend (The Brain)
- **Lenguaje:** Python 3.10+
- **Framework:** `aiogram` 3.x (Bot de Telegram Asíncrono).
- **IA Orchestration:** LangChain.
- **Modelos:**
  - `gpt-4o-mini`: Para routing y extracción estructurada (rápido y económico).
  - `text-embedding-3-small`: Para memoria a largo plazo (vectores).
- **Base de Datos:** Supabase (PostgreSQL 15+).
  - Extension `vector` habilitada para búsquedas semánticas.

### Frontend (Dashboard)
- **Framework:** Next.js 15 (App Router).
- **UI:** Shadcn/UI + Tailwind CSS v4.
- **Gráficos:** Recharts (Donas, Áreas, Barras).
- **Tema:** Dark Mode nativo (Zinc/Slate palette).

---

## 📖 Guía de Uso Rápida

1.  **Abre Telegram** y busca tu bot.
2.  **Habla Naturalmente:** No necesitas comandos.
    *   *"Gaste 1500 en un alfajor"* (Finanzas)
    *   *"Me duele un poco la cabeza"* (Salud/Journal)
    *   *"Hoy entrené piernas"* (Salud)
3.  **Verificación:** El bot responderá con un resumen de lo que entendió.
4.  **Dashboard:** Visualiza todo en `http://localhost:3000`.

---

*Life OS v1.1 - Documentación generada automáticamente por Trae AI*
