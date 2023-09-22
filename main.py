from fastapi import FastAPI, Request, HTTPException, Depends, Body, Response
import httpx
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Any

class WebhookEvent(BaseModel):
    data: Any

load_dotenv()

app = FastAPI()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

@app.post("/webhook/")
async def webhook_endpoint(request: Request):
    body = await request.json()
    print(body)

    if body.get("object"):
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [{}])[0]

        if value and messages:
            phone_number_id = value.get("metadata", {}).get("phone_number_id")
            from_ = messages.get("from")
            msg_body = messages.get("text", {}).get("body")

            if phone_number_id and from_ and msg_body:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"https://graph.facebook.com/v12.0/{phone_number_id}/messages?access_token={WHATSAPP_TOKEN}",
                        json={
                            "messaging_product": "whatsapp",
                            "to": from_,
                            "text": {"body": "Ack: " + msg_body},
                        },
                        headers={"Content-Type": "application/json"},
                    )
                    response.raise_for_status()

        return {"status": "ok"}
    else:
        raise HTTPException(status_code=404, detail="Not from WhatsApp API")

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
