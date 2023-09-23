from email.mime import image
from fastapi import FastAPI, Request, HTTPException, Depends, Body, Response
import httpx
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Any
from heyoo import WhatsApp
from utils.replicate_client import ImageEvaluator
import logging

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
                messenger.send_message(f"Hi {name}, nice to connect with you", mobile)

            elif message_type == "interactive":
                message_response = messenger.get_interactive_response(data)
                interactive_type = message_response.get("type")
                message_id = message_response[interactive_type]["id"]
                message_text = message_response[interactive_type]["title"]
                logging.info(f"Interactive Message; {message_id}: {message_text}")

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
                    hair_color = image_evaluator.ask_question(image_filename, "what is his hair color?")
                    race = image_evaluator.ask_question(image_filename, "what is his race?")
                    eye_color = image_evaluator.ask_question(image_filename, "what is his eye color?")
                    messenger.send_message(f"El color de su cabello es: {hair_color}", mobile)
                    messenger.send_message(f"Su raza es: {race}", mobile)
                    messenger.send_message(f"El color de sus ojos es: {eye_color}", mobile)
                    
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

    # if body.get("object"):
    #     entry = body.get("entry", [{}])[0]
    #     changes = entry.get("changes", [{}])[0]
    #     value = changes.get("value", {})
    #     messages = value.get("messages", [{}])[0]

    #     if value and messages:
    #         phone_number_id = value.get("metadata", {}).get("phone_number_id")
    #         from_ = messages.get("from")
    #         msg_body = messages.get("text", {}).get("body")

    #         if phone_number_id and from_ and msg_body:
    #             async with httpx.AsyncClient() as client:
    #                 response = await client.post(
    #                     f"https://graph.facebook.com/v12.0/{phone_number_id}/messages?access_token={WHATSAPP_TOKEN}",
    #                     json={
    #                         "messaging_product": "whatsapp",
    #                         "to": from_,
    #                         "text": {"body": "Ack: " + msg_body},
    #                     },
    #                     headers={"Content-Type": "application/json"},
    #                 )
    #                 response.raise_for_status()

    #     return {"status": "ok"}
    # else:
    #     raise HTTPException(status_code=404, detail="Not from WhatsApp API")

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
