import requests
import os

name = 'ram'  # Replace with your name
esp32_url = 'http://192.168.152.155/capture'  # Update with your ESP32's IP

img_counter = 0
output_folder = f"dataset/{name}"  # Specify the folder where images will be saved

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

while True:
    try:
        response = requests.get(esp32_url)
        print("Response status code:", response.status_code)
        if response.status_code == 200:
            image_data = response.content

            # Check if the received image data is not empty
            if len(image_data) > 0:
                # Generate an image file name
                img_name = f"{output_folder}/image_{img_counter}.jpg"

                # Save the image to the specified folder
                with open(img_name, 'wb') as f:
                    f.write(image_data)

                print(f"Saved: {img_name}")
                img_counter += 1
            else:
                print("Received image data is empty")
        else:
            print(f"Failed to retrieve image. Response content: {response.content}")

    except Exception as e:
        print("Error:", e)
