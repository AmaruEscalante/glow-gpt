from email.mime import image
from fastapi import FastAPI, Request, HTTPException, Depends, Body, Response
import httpx
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Any
from heyoo import WhatsApp
from open_ai import OpenAIChat
from utils.replicate_client import ImageEvaluator
from utils.ppt_client import generate_catalogue
import logging
from mvp import process_text_message_from_phone_number, retrieve_recommendations_for_catalogue, restart_recommendations_for_number


class WebhookEvent(BaseModel):
    data: Any

load_dotenv()

# Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI()

# Replicate
image_evaluator = ImageEvaluator()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
messenger = WhatsApp(WHATSAPP_TOKEN, phone_number_id=os.getenv("PHONE_NUMBER_ID"))

@app.post("/webhook/")
async def webhook_endpoint(request: Request):
    data = await request.json()
    logging.info("Received webhook data %s", data)
    changed_field = messenger.changed_field(data)
    if changed_field == "messages":
        new_message = messenger.is_message(data)
        if new_message:
            mobile = messenger.get_mobile(data)
            name = messenger.get_name(data)
            message_type = messenger.get_message_type(data)
            logging.info(
                f"New Message; sender:{mobile} name:{name} type:{message_type}"
            )
            if message_type == "text":
                message = messenger.get_message(data)
                name = messenger.get_name(data)
                logging.info("Message: %s", message)
                if "hola" in message.lower():
                    messenger.send_message(f"Hola {name}, soy GlowGPT, mándame una selfie para darte recomendaciones de productos!", mobile)
                else:
                    # Talk with the user about its preferences
                    response = process_text_message_from_phone_number(message, mobile)
                    logging.info(f"OpenAI Response: {response}")
                    messenger.send_message(response, mobile)
                    messenger.send_reply_button(
                        recipient_id=mobile,
                        button={
                            "type": "button",
                            "body": {
                                "text": "Recuerda que puedes descargar tu catálogo en cualquier momento."
                            },
                            "action": {
                                "buttons": [
                                    {
                                        "type": "reply",
                                        "reply": {
                                            "id": "generate_catalogue",
                                            "title": "Genera tu catálogo"
                                        }
                                    },
                                ]
                            }
                    },
                    )

            elif message_type == "interactive":
                message_response = messenger.get_interactive_response(data)
                interactive_type = message_response.get("type")
                message_id = message_response[interactive_type]["id"]
                message_text = message_response[interactive_type]["title"]
                logging.info(f"Interactive Message; {message_id}: {message_text}")
                # If interactive type id is "generate_catalogue"
                if message_id == "generate_catalogue":
                    # DO generate catalogue
                    messenger.send_message("Dame un momento...", mobile)
                    catalogue_body = retrieve_recommendations_for_catalogue(mobile)
                    if len(catalogue_body) > 0:
                        generate_catalogue(catalogue_body)
                        restart_recommendations_for_number(mobile)
                        messenger.send_message("Aquí está tu catálogo!", mobile)
                        # Send a pptx file
                        media_id = messenger.upload_media(media='catalogue.pptx')['id']
                        messenger.send_document(
                            document=media_id,
                            recipient_id=mobile,
                            link=False,
                        )
                    else:
                        messenger.send_message("No tienes recomendaciones, envíame una selfie o haz una pregunta para recomendarte productos!", mobile)

            elif message_type == "location":
                message_location = messenger.get_location(data)
                message_latitude = message_location["latitude"]
                message_longitude = message_location["longitude"]
                logging.info("Location: %s, %s", message_latitude, message_longitude)

            elif message_type == "image":
                image = messenger.get_image(data)
                image_id, mime_type = image["id"], image["mime_type"]
                image_url = messenger.query_media_url(image_id)
                image_filename = messenger.download_media(image_url, mime_type)
                
                awns = image_evaluator.evaluate_image(image_filename)
                if awns: # is a person
                    messenger.send_message("Gracias! por enviarnos tu foto, dame un momento para analizarla", mobile)
                    # analyze image
                    # hair_color = image_evaluator.ask_question(image_filename, "what is their hair color?")
                    skin_color = image_evaluator.ask_question(image_filename, "what is their skin color?")
                    # eye_color = image_evaluator.ask_question(image_filename, "what is their eye color?")
                    # messenger.send_message(f"El color de su cabello es: {hair_color}", mobile)
                    # messenger.send_message(f"El color de su piel: {skin_color}", mobile)
                    # messenger.send_message(f"El color de sus ojos es: {eye_color}", mobile)
                    msg = {"role": "user", "content": f"Translate this color to spanish: {skin_color}, just give me the name of the color in one word in lowercase without points"}
                    color = OpenAIChat.get_response([msg])
                    open_ai_resp = process_text_message_from_phone_number(f"Que me recomiendas para mi color de piel {color}?", mobile)
                    logging.info(f"OpenAI Response: {open_ai_resp}")
                    messenger.send_message(open_ai_resp, mobile)
                    messenger.send_reply_button(
                        recipient_id=mobile,
                        button={
                            "type": "button",
                            "body": {
                                "text": "Genial! Para ver tus recomendaciones descarga tu catálogo."
                            },
                            "action": {
                                "buttons": [
                                    {
                                        "type": "reply",
                                        "reply": {
                                            "id": "generate_catalogue",
                                            "title": "Genera tu catálogo"
                                        }
                                    },
                                ]
                            }
                    },
                    )
                else:
                    messenger.send_message("Por favor, intenta con otra imagen.", mobile)
                    
                logging.info(f"{mobile} sent image {image_filename}")

            elif message_type == "video":
                video = messenger.get_video(data)
                video_id, mime_type = video["id"], video["mime_type"]
                video_url = messenger.query_media_url(video_id)
                video_filename = messenger.download_media(video_url, mime_type)



                logging.info(f"{mobile} sent video {video_filename}")

            elif message_type == "audio":
                audio = messenger.get_audio(data)
                audio_id, mime_type = audio["id"], audio["mime_type"]
                audio_url = messenger.query_media_url(audio_id)
                audio_filename = messenger.download_media(audio_url, mime_type)
                logging.info(f"{mobile} sent audio {audio_filename}")

            elif message_type == "document":
                file = messenger.get_document(data)
                file_id, mime_type = file["id"], file["mime_type"]
                file_url = messenger.query_media_url(file_id)
                file_filename = messenger.download_media(file_url, mime_type)
                logging.info(f"{mobile} sent file {file_filename}")
            else:
                logging.info(f"{mobile} sent {message_type} ")
                logging.info(data)
        else:
            delivery = messenger.get_delivery(data)
            if delivery:
                logging.info(f"Message : {delivery}")
            else:
                logging.info("No new message")
    return "OK", 200

@app.get("/webhook/")
def verify_webhook(request: Request):

    query_params = request.query_params
    print("query_params", query_params)

    mode = query_params.get("hub.mode")
    verify_token = query_params.get("hub.verify_token")
    challenge = query_params.get("hub.challenge")
    if mode == "subscribe" and verify_token == VERIFY_TOKEN:
        print("WEBHOOK_VERIFIED", challenge)
        return Response(challenge, media_type="text/plain")
    else:
        raise HTTPException(status_code=403, detail="Tokens do not match")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
