from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import google.generativeai as genai


load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# * Function to load Gemini Pro Vision
model = genai.GenerativeModel(model_name = "gemini-1.5-pro")
# model = genai.GenerativeModel("gemini-pro-vision")

def get_gemini_response(input, image, prompt):
    """_summary_

    Args:
        input (str): Modelに対するPromptを意味する
        image (jpg, png ): Image_file
        prompt (str): 画像からどのようなことを抜き出したいかを指示する
    """
    response = model.generate_content([input, image[0], prompt])
    return response.text

def input_image_details(uploaded_file):
    """
    Processes the uploaded file and prepares it for further use.
    Args:
        uploaded_file: The file uploaded by the user. It should be an object that has a `getvalue` method to read the file's bytes and a `type` attribute to get the MIME type.
    Returns:
        list: A list containing a dictionary with the MIME type and the file's byte data.
    Raises:
        FileNotFoundError: If no file is uploaded.
    """
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# *Initialize our streamlit app
st.set_page_config(page_title="MultiLanguage Invoice Extractor")
st.header("Gemini Application")

input = st.text_input("Input Prompt: ", key="input")
uploaded_file = st.file_uploader("Choose an image of the invoice...", type=["jpg", "jpeg", "png"])
image = ""

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True) # !画像の表示

submit = st.button("Tell me about the invoice")

input_prompt = """
You are an expert in understanding invoices. We will upload a image as invoice
and you will have to answer any questions based on the uploaded invoice image.
"""

# if submit button is clicked
if submit:
    image_data = input_image_details(uploaded_file)
    response = get_gemini_response(input_prompt, image_data, input)
    st.subheader("The Response is")
    st.write(response)
