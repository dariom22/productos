"""Agente principal de la agencia de tours usando Claude API."""

import os
import anthropic
from sqlalchemy.orm import Session

from app.agent.tools import TOOLS
from app.agent.tool_handlers import HANDLER_MAP

# Modelo conversacional - cambiá a "claude-sonnet-4-20250514" si necesitás más calidad
LLM_MODEL = os.environ.get("LLM_MODEL", "claude-haiku-4-5-20251001")

SYSTEM_PROMPT = """Sos el agente de atención al cliente de "Viajes Fantásticos", una agencia de tours.

## Tu rol
Guiás al cliente por todo el proceso de reserva de un tour:

1. **Consulta**: El cliente pregunta por tours. Vos buscás opciones y se las mostrás.
2. **Presupuesto**: Cuando el cliente se interesa, le armás un presupuesto (pedile nombre, email, WhatsApp y cantidad de personas).
3. **Aceptación**: Si acepta el presupuesto, contactás al proveedor por WhatsApp.
4. **Proveedor**: El proveedor confirma o propone cambios. Se lo comunicás al cliente.
5. **Confirmación**: El cliente confirma → generás link de pago por Stripe.
6. **Pago**: Una vez que paga, pedís el PAX al proveedor.
7. **PAX**: El proveedor envía el PAX y se lo pasás al cliente. ¡Listo!

## Reglas
- Siempre respondé en español
- Sé amable, profesional y entusiasta
- Pedí los datos necesarios antes de crear un presupuesto
- Siempre mostrá el resumen con precio total antes de confirmar
- Si no hay tours disponibles, sugerí alternativas
- Explicá cada paso al cliente para que sepa qué esperar
- Usá las herramientas disponibles para cada acción
"""


def run_agent(user_message: str, db: Session,
              conversation_history: list = None) -> dict:
    """Ejecuta el agente con un mensaje del usuario y retorna la respuesta."""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    if conversation_history is None:
        conversation_history = []

    conversation_history.append({"role": "user", "content": user_message})

    response = client.messages.create(
        model=LLM_MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=conversation_history,
    )

    # Loop de tool use
    while response.stop_reason == "tool_use":
        tool_results = []
        assistant_content = response.content

        for block in response.content:
            if block.type == "tool_use":
                handler = HANDLER_MAP.get(block.name)
                if handler:
                    result = handler(db, **block.input)
                else:
                    result = f"Herramienta '{block.name}' no disponible."

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        conversation_history.append({"role": "assistant", "content": assistant_content})
        conversation_history.append({"role": "user", "content": tool_results})

        response = client.messages.create(
            model=LLM_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=conversation_history,
        )

    assistant_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            assistant_text += block.text

    conversation_history.append({"role": "assistant", "content": response.content})

    return {
        "response": assistant_text,
        "conversation_history": conversation_history,
    }
