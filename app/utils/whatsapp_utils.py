import logging
from flask import current_app, jsonify
import json
import requests

from app.services.openai_service import generate_response_agent
from app.services.hubspot_service import (
    create_hubspot_contact,
    create_hubspot_note_on_contact,
)

import re

IMGS = {
    "Caja para Chilaquiles": "https://i.imgur.com/JbYKONs.png",
    "Tarjetas de Presentación": "https://i.imgur.com/1ivTDBl.png",
}

INITIATE_FLOW_DESCRIPTIONS = {
    "Caja para Chilaquiles": "Son ideales para contener chilaquiles o comida con salsa, con interior plastificado para resistir la humedad y grasa",
    "Tarjetas de Presentación": "Son para clientes exigentes que buscan tener una tarjeta de presentación fina y con un terminado distinto a las más comunes.",
}

PRODUCT_URLS = {
    "Caja para Chilaquiles": "https://www.pixz.com.mx/caja-para-chilaquiles/",
    "Tarjetas de Presentación": "https://www.pixz.com.mx/tarjetas/",
}

MOST_RECENT_PRODUCT_REQUEST = {"0": None}


def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_data(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )


def get_img_message_data(recipient, link):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "image",
            "image": {"link": link},
        }
    )


def get_list_message_data(
    recipient_waid, header_text, body_text, footer_text, sections
):
    """
    Create a list message payload for WhatsApp.

    :param recipient_waid: The WhatsApp ID of the recipient.
    :param header_text: The header text of the list message.
    :param body_text: The body text of the list message.
    :param footer_text: The footer text of the list message.
    :param sections: A list of sections, where each section is a dictionary with keys 'title' and 'rows'.
                     Each 'rows' is a list of dictionaries with keys 'id' and 'title'.
    :return: A JSON string payload to be sent to the WhatsApp API.
    """
    list_message_payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_waid,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": header_text},
            "body": {"text": body_text},
            "footer": {"text": footer_text},
            "action": {"button": "Select an option", "sections": sections},
        },
    }
    return json.dumps(list_message_payload)


def get_button_message_data(recipient, body_text, buttons):
    """
    Create a button message payload for WhatsApp.

    :param recipient: The WhatsApp ID of the recipient.
    :param body_text: The body text of the button message.
    :param buttons: A list of buttons, where each button is a dictionary with keys 'type' and 'reply'.
                    The 'reply' is a dictionary with keys 'id' and 'title'.
    :return: A JSON string payload to be sent to the WhatsApp API.
    """
    button_message_payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {"buttons": buttons},
        },
    }
    return json.dumps(button_message_payload)


def generate_response(response):
    # Return text in uppercase
    return response.upper()


def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def process_whatsapp_message(body):
    logging.info(f"BODY: {body}")
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    customer_name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"][
        "name"
    ]

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    if message["type"] == "interactive":
        # hardcoded assumption that this is a yes/no reply to request for order
        button_reply = message["interactive"]["button_reply"]
        if button_reply["id"] == "0":  # they said yes
            most_recent_product = MOST_RECENT_PRODUCT_REQUEST["0"]
            message = f"Perfecto! Puedes hacer el pedido en este link: {PRODUCT_URLS[most_recent_product]}"
        else:
            message = "Entendido! Te puedo ayudar con otra cosa?"
        response = process_text_for_whatsapp(message)
        text_data = get_text_message_data(
            current_app.config["RECIPIENT_WAID"], response
        )
        send_message(text_data)
        return
    else:
        message_body = message["text"]["body"]

    # TODO: implement custom function here
    # response = generate_response(message_body)

    # OpenAI Integration
    agent_output = generate_response_agent(message_body, wa_id, customer_name)
    # If the agent used tools to identify products then we need to go through a deterministic flow to initate an order
    products = agent_output.get("products")
    if len(products) > 0:
        product = products[0]
        # update this global variable which might get used for later responses
        MOST_RECENT_PRODUCT_REQUEST["0"] = product
        # Send text message about the product
        product_message = (
            f"Si, tenemos {product}!\n\n" f"{INITIATE_FLOW_DESCRIPTIONS[product]}"
        )
        response = process_text_for_whatsapp(product_message)
        text_data = get_text_message_data(
            current_app.config["RECIPIENT_WAID"], response
        )
        send_message(text_data)
        # Send image of product
        image_data = get_img_message_data(
            current_app.config["RECIPIENT_WAID"], IMGS[product]
        )
        send_message(image_data)
        # Send options for initiating order flow or not
        buttons = [
            {"type": "reply", "reply": {"title": "Si", "id": "0"}},
            {"type": "reply", "reply": {"title": "No", "id": "1"}},
        ]

        button_data = get_button_message_data(
            current_app.config["RECIPIENT_WAID"],
            "Te gustaría hacer un pedido?",
            buttons,
        )
        send_message(button_data)
        # Create Contact in Hubspot CRM
        contact_data = create_hubspot_contact(
            phone_number=wa_id, first_name=customer_name
        )
        contact_id = contact_data["id"]
        # Associate Note with Contact
        note = f"Cliente interesado en: {product}"
        response = create_hubspot_note_on_contact(contact_id, note)

    else:
        response = process_text_for_whatsapp(agent_output["new_message"])

        data = get_text_message_data(current_app.config["RECIPIENT_WAID"], response)
        send_message(data)


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )
