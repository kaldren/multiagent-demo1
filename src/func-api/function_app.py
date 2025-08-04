import azure.functions as func
import json
import requests

app = func.FunctionApp()

@app.function_name(name="message_discord")
@app.route(route="discord", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def message_discord(req: func.HttpRequest) -> func.HttpResponse:
    """
    Sends a message to a Discord channel using a webhook.
    :param message: The message to send to Discord.

    :return: A JSON string indicating success or failure.
    """
    webhook_url = "https://discord.com/api/webhooks/1398570122578497586/NV_BOPdY7yC2F7MNnpcc69pujq9cwUkUBWYX8ZpWul6FSJe_CrmlB5XNLa5y5Xqs59y9"
    message = req.params.get('message')
    data = {"content": message}

    response = requests.post(webhook_url, json=data, headers={"Content-Type": "application/json"})

    if response.status_code != 204:
        return json.dumps({"status": "error", "message": "Failed to send message to Discord"})
    else:
        return json.dumps({"status": "success", "message": "Message sent successfully to Discord"})