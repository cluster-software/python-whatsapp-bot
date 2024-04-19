# INTRO_MESSAGE = {
#     "type": "button",
#     "buttons": [
#         {"type": "reply", "reply": {"title": "Seguimiento para un pedido", "id": "0"}},
#         {"type": "reply", "reply": {"title": "Pedir Cotizacion", "id": "1"}},
#         {"type": "reply", "reply": {"title": "Otra Pregunta", "id": "2"}},
#     ],
#     "body_text": "Que estas buscando?",
# }

INTRO_MESSAGE = {
    "type": "list",
    "header_text": "Que estas buscando?",
    "body_text": "Escoge una opcion",
    "sections": [
        {
            "title": "Products",
            "rows": [
                {"id": "quote", "title": "Pedir Cotizacion"},
                {"id": "order_status", "title": "Seguimiento de un pedido"},
                {"id": "other", "title": "Otra Pregunta"},
            ],
        }
    ],
}

# button_message_payload = {
#     "messaging_product": "whatsapp",
#     "recipient_type": "individual",
#     "to": recipient,
#     "type": "interactive",
#     "interactive": {
#         "type": "button",
#         "body": {"text": body_text},
#         "action": {"buttons": buttons},
#     },
# }
