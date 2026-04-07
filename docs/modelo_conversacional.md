# Modelo Conversacional - Agente de Tours

## Arquitectura General

La API de Claude es **stateless**: no recuerda nada entre llamadas.
Tu servidor es el responsable de mantener el historial y reenviarlo completo en cada request.

```
CLIENTE                    TU SERVIDOR                      CLAUDE API
  │                            │                                │
  │─── "Quiero Bariloche" ───→│                                │
  │                            │── messages: [user: "..."] ───→│
  │                            │←── tool_use: buscar_tours ────│
  │                            │   (ejecuta contra tu DB)       │
  │                            │── tool_result: [{tours}] ────→│
  │                            │←── text: "Encontré este..." ──│
  │←── "Encontré este..." ────│                                │
```

---

## Las 3 piezas de cada llamada

### 1. System Prompt (la personalidad)

Se envía en **cada llamada** pero NO forma parte del historial.
Es la instrucción fija que define quién es el agente.

```python
SYSTEM_PROMPT = """Sos el agente de atención al cliente de "Viajes Fantásticos"...
## Tu rol
...
## Reglas
- Siempre respondé en español
- Sé amable, profesional y entusiasta
..."""
```

El system prompt se pasa como parámetro aparte:

```python
response = client.messages.create(
    model=LLM_MODEL,
    system=SYSTEM_PROMPT,   # <-- acá
    tools=TOOLS,
    messages=conversation_history,
)
```

### 2. Conversation History (la memoria)

Es una lista que crece con cada mensaje. Se reenvía COMPLETA en cada llamada.

```
Llamada 1:
  messages: [
    {role: "user", content: "Hola"}
  ]

Llamada 2:
  messages: [
    {role: "user",      content: "Hola"},
    {role: "assistant", content: "¡Bienvenido a Viajes Fantásticos!"},
    {role: "user",      content: "Quiero ir a Bariloche"}
  ]

Llamada 3:
  messages: [
    {role: "user",      content: "Hola"},
    {role: "assistant", content: "¡Bienvenido a Viajes Fantásticos!"},
    {role: "user",      content: "Quiero ir a Bariloche"},
    {role: "assistant", content: "Encontré estos tours..."},
    {role: "user",      content: "Me interesa el primero"}
  ]
```

**Regla:** los mensajes siempre alternan `user` → `assistant` → `user` → `assistant`.

### 3. Tool Use Loop (las acciones)

Cuando Claude decide usar una herramienta, la conversación internamente se ve así:

```json
[
  {"role": "user", "content": "Quiero ir a Bariloche"},

  {"role": "assistant", "content": [
    {"type": "tool_use", "id": "toolu_xxx", "name": "buscar_tours",
     "input": {"destino": "Bariloche"}}
  ]},

  {"role": "user", "content": [
    {"type": "tool_result", "tool_use_id": "toolu_xxx",
     "content": "[{\"nombre\": \"Bariloche Nieve\", \"precio\": 850}]"}
  ]},

  {"role": "assistant", "content": [
    {"type": "text", "text": "¡Encontré este tour en Bariloche! ..."}
  ]}
]
```

El cliente nunca ve los pasos de tool_use. Solo ve la respuesta de texto final.

---

## Cómo funciona el loop en código

```python
def run_agent(user_message, db, conversation_history=None):
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    if conversation_history is None:
        conversation_history = []

    # 1. Agregar mensaje del usuario
    conversation_history.append({"role": "user", "content": user_message})

    # 2. Llamar a Claude
    response = client.messages.create(
        model=LLM_MODEL,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=conversation_history,
    )

    # 3. Loop: mientras Claude pida herramientas, ejecutarlas
    while response.stop_reason == "tool_use":
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                handler = HANDLER_MAP.get(block.name)
                result = handler(db, **block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        # Agregar al historial y volver a llamar
        conversation_history.append({"role": "assistant", "content": response.content})
        conversation_history.append({"role": "user", "content": tool_results})

        response = client.messages.create(
            model=LLM_MODEL,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=conversation_history,
        )

    # 4. Extraer texto final y retornar
    assistant_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            assistant_text += block.text

    conversation_history.append({"role": "assistant", "content": response.content})

    return {
        "response": assistant_text,
        "conversation_history": conversation_history,
    }
```

---

## Gestión de sesiones

El historial vive en memoria en el servidor, indexado por `session_id`:

```python
# chat.py
conversations: dict[str, list] = {}

@router.post("/")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    history = conversations.get(request.session_id, [])
    result = run_agent(request.message, db, history)
    conversations[request.session_id] = result["conversation_history"]
    return ChatResponse(response=result["response"], session_id=request.session_id)
```

- Cada `session_id` tiene su conversación aislada
- Si reiniciás el servidor, se pierden (están en memoria)
- `DELETE /chat/{session_id}` borra una sesión

### Uso desde un frontend o curl

```bash
# Mensaje 1
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, quiero un tour", "session_id": "usuario123"}'

# Mensaje 2 (misma sesión = recuerda lo anterior)
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Me interesa Bariloche", "session_id": "usuario123"}'

# Otra persona (sesión distinta = conversación independiente)
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola", "session_id": "otro_cliente456"}'
```

---

## Definición de herramientas

Las herramientas se definen como una lista de diccionarios con nombre, descripción y esquema de parámetros:

```python
TOOLS = [
    {
        "name": "buscar_tours",
        "description": "Busca tours disponibles...",
        "input_schema": {
            "type": "object",
            "properties": {
                "destino": {"type": "string", "description": "Destino del tour"},
                "categoria": {"type": "string"},
                "precio_maximo": {"type": "number"},
            },
            "required": []
        }
    },
    # ... más herramientas
]
```

Claude lee estas definiciones y decide cuándo y cómo usarlas.

---

## Modelos disponibles y costos

| Modelo | ID | Costo aprox (1M tokens) | Uso recomendado |
|---|---|---|---|
| Haiku | `claude-haiku-4-5-20251001` | ~$0.25 in / $1.25 out | Chatbot, agentes simples |
| Sonnet | `claude-sonnet-4-20250514` | ~$3 in / $15 out | Tareas complejas |
| Opus | `claude-opus-4-20250514` | ~$15 in / $75 out | Razonamiento avanzado |

Una conversación completa de reserva (~3000 tokens) con Haiku cuesta **menos de 1 centavo**.

Se configura con la variable de entorno `LLM_MODEL` en el archivo `.env`.

---

## Resumen

| Concepto | Qué hace | Dónde está |
|---|---|---|
| System prompt | Define personalidad y reglas | `tour_agent.py` |
| Historial | Memoria de la conversación | `chat.py` (en memoria) |
| Tools | Lo que el agente puede hacer | `tools.py` |
| Handlers | La lógica real de cada tool | `tool_handlers.py` |
| Loop | Ejecuta tools hasta tener respuesta | `tour_agent.py` |
| Sesiones | Aísla conversaciones por cliente | `chat.py` (`session_id`) |
