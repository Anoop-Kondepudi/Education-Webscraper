import requests

# Define the webhook URL and the message you want to send
webhook_url = "https://discord.com/api/webhooks/1290177580627922974/cDQLWsPzyHO55liHxAKC2zpZ9J7GTmv5snugwGhOCRnxa6LVVK0FgNrU3KLCdHAWBMOK"
message_content = "https://www.chegg.com/homework-help/questions-and-answers/two-shafts-ab-ef-fixed-ends-fixed-comnccied-s-mesh-common-gear-c-fixed-connected-shaft-cd--q25643059"

# Create a payload containing the message
payload = {
    "content": message_content
}

# Send a POST request to the webhook with the payload
response = requests.post(webhook_url, json=payload)

# Check if the request was successful
if response.status_code == 204:
    print("Message sent successfully!")
else:
    print(f"Failed to send message. Status code: {response.status_code}")
