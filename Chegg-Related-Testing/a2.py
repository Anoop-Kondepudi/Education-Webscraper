import requests

# Define webhooks
webhooks = [
    "https://discord.com/api/webhooks/1290503546105626656/zv1jOu4BBP6j5m-Z408KTdw3AJMg_Lr8wb3sgkGNFzBdooqN-T7qhoLQ6rmy0Nzn-nrQ",
    "https://discord.com/api/webhooks/1290503567823867958/dRmWQa7oF_aDTBBaI08Lqq4dX43aN4YqvJaCZB5fPBwLP2E-NmAZDjOY5gw8F0XbT4bl",
    "https://discord.com/api/webhooks/1290503594843308055/3L65ag0gLKjwehGtkADRjrcjNq065iz-ClWzpr38GlZ4fWNmIL_X9LA2otinhVLHW72j",
    "https://discord.com/api/webhooks/1290503619380248627/xyEQW6ic8nYSu_jiWifAWzMQdKIacGqO7Oo4N2oQFDAqroV5A3j7J1rS8optDMrwuYPk",  
    "https://discord.com/api/webhooks/1290503651651223563/kL8smR0Fq2gLMjjptLMK-vvuuc2L9LiYaf4IGMTUiEiKuGGrNIbaxxLB0kupA9a3jNRw"
]

# Path to the file
file_path = "C:/Users/MCBat/OneDrive/Desktop/Education-Webscraper/chegg_links.txt"

# Function to read all links from the file
def get_all_links(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

# Function to write the remaining links back to the file
def write_remaining_links(file_path, remaining_links):
    with open(file_path, 'w') as file:
        file.writelines(remaining_links)

# Function to send a link to a webhook
def send_link(webhook_url, link):
    payload = {"content": link.strip()}  # .strip() to remove any trailing newlines or spaces
    response = requests.post(webhook_url, json=payload)
    if response.status_code == 204:
        print(f"Link sent successfully to {webhook_url}")
    else:
        print(f"Failed to send link to {webhook_url}, Status code: {response.status_code}")

def main():
    links = get_all_links(file_path)
    webhook_count = len(webhooks)

    for i, link in enumerate(links):
        # Send the link to the appropriate webhook in a round-robin fashion
        webhook = webhooks[i % webhook_count]
        send_link(webhook, link)

        # Remove the sent link from the list
        remaining_links = links[i + 1:]
        write_remaining_links(file_path, remaining_links)

    print("All links sent and removed successfully.")

if __name__ == "__main__":
    main()
