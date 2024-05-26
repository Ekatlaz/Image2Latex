import os
import requests
import telebot


base_url = "http://188.44.41.132:8000"
telegram_token = "7037592032:AAFttMfHRXjHxIxTJ3ElztOt1KK7XtEp7co"


class ServerInterface:
    def __init__(self, base_url):
        self.base_url = base_url
    def upload_image(self, image_path: str) -> dict:

        # Open the image file in binary mode
        with open(image_path, "rb") as image_file:
            # Prepare the files dictionary for the request
            files = {"file": ("img.png", image_file, "image/png")}

            # Make the POST request to upload the file
            response = requests.post(f"{self.base_url}/uploadFile", files=files)

        return {"status": response.status_code, "content": {"user_id": response.text.strip('"')}}

    def get_latex(self, user_id: str) -> dict:

        # Make the GET request to download the LaTeX code
        response = requests.get(f"{self.base_url}/tex/{user_id}/")

        return {
            "status": response.status_code,
            "content": {"latex_content": response.text.strip('"').replace('\\n', '\n').replace('\\\\', '\\')}
        }

    def get_pdf(self, user_id: str) -> dict:

        # Make the GET request to download the PDF file
        response = requests.get(f"{self.base_url}/pdf/{user_id}/")

        return {"status": response.status_code, "content": {"pdf_content": response.content}}

bot = telebot.TeleBot(telegram_token, parse_mode=None)
server_interface = ServerInterface(base_url)

# Handler for when a user sends an image
@bot.message_handler(content_types=['photo'])
def handle_image(message):

    # Get the file ID of the photo
    photo_file_id = message.photo[-1].file_id  # Get the highest resolution photo
    # Send a message to acknowledge the received image
    bot.send_message(message.chat.id, "Изображение получил, обрабатываю...")

    # You can also download the image if needed
    file_info = bot.get_file(photo_file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Save the photo locally
    with open('received_image.jpg', 'wb') as new_file:
        new_file.write(downloaded_file)

    server_response = server_interface.upload_image("received_image.jpg")
    if server_response["status"] == 200:
        user_id = server_response["content"]["user_id"]
        latex_response = server_interface.get_latex(user_id)
        if latex_response["status"] == 200:
            latex_content = latex_response["content"]["latex_content"]
            bot.send_message(message.chat.id, f'```latex\n{str(latex_content)}\n```', parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "Что-то пошло не так, повторите попытку.")

        pdf_response = server_interface.get_pdf(user_id)
        if pdf_response["status"] == 200:
            # Save the PDF to a file
            with open("output.pdf", "wb") as file:
                file.write(pdf_response['content']["pdf_content"])
            # Send the PDF file to the user
            with open("output.pdf", "rb") as file:
                bot.send_document(message.chat.id, file)
            os.remove("output.pdf")
        else:
            bot.send_message(message.chat.id, "Что-то пошло не так, повторите попытку.")

if __name__ == '__main__':
    print("bot started")
    bot.infinity_polling()
