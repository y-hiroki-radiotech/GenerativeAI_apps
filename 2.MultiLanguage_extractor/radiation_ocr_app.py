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
st.set_page_config(page_title="Radiation Report Extractor")
st.header("Gemini Application")

input = st.text_input("Input Prompt: ", key="input")
uploaded_file = st.file_uploader("Choose an image of the radiation...", type=["jpg", "jpeg", "png"])
image = ""

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True) # !画像の表示

submit = st.button("Tell me about the radiation")

input_prompt = """
この画像はX線照射線量レポートを示しています。以下の点について分析をお願いします：

検査の基本情報（総面積線量、総入射線量、検査日時）の詳細な読み取り
透視と撮影それぞれの：

総面積線量
総入射線量
積算時間
の比較分析


グラフの解釈：

青色のバーで示される透視の面積線量の変動パターン
黄色のバーで示される撮影の面積線量の分布
グレーの折れ線で示される累積値の推移


特に顕著な値を示している時点（ピーク値）の特定
全体的な放射線被ばく量の評価
"""

# if submit button is clicked
if submit:
    image_data = input_image_details(uploaded_file)
    response = get_gemini_response(input_prompt, image_data, input)
    st.subheader("The Response is")
    st.write(response)
