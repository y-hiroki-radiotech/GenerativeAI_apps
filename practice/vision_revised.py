from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
import time
import io
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 環境設定の読み込みと初期化
def initialize_app():
    try:
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("API key not found in environment variables")
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(model_name="gemini-1.5-pro")
    except Exception as e:
        logger.error(f"Initialization error: {str(e)}")
        st.error("アプリケーションの初期化中にエラーが発生しました。")
        return None

# *画像の前処理
# 要するにチェックしたいことを書いていけばいい。try, exceptの構文はそんなものだから
def preprocess_image(uploaded_file):
    try:
        if uploaded_file is None:
            return None

        image = Image.open(uploaded_file)

        # 画像サイズの最適化
        max_size = 1600
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        # 画像フォーマットの確認と交換
        if image.format not in ["JPEG", "JPG", "PNG"]:
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            image = Image.open(buffer)

        return image
    except Exception as e:
        logger.error(f"Image preprocessing error: {str(e)}")
        return None

# Geminiからのreponseを取得
def get_gemini_response(model, input_text, image, retry_count=3):
    for attempt in range(retry_count):
        try:
            with st.spinner("分析中..."):
                # 空白文字を削除
                if input_text.strip():
                    response = model.generate_content([input_text, image])
                else:
                    response = model.generate_content(image)
                return response.text
        except Exception as e:
            logger.error(f"API call error (attempt {attempt + 1}): {str(e)}")
            if attempt == retry_count - 1:
                st.error("申し訳ありませんが、画像の分析中にエラーが発生しました。")
                return None
            time.sleep(1)

# *streamlitのアプリの設定
st.set_page_config(
    page_title="AI画像認識アプリ",
    page_icon="🔍",
    layout="wide"
)
# サイドバーの追加
with st.sidebar:
    st.header("設定")
    language = st.selectbox(
        "分析結果の言語を選択",
        options=["日本語", "English"],
        index=0
    )
    analysis_mode = st.radio(
        "分析モード",
        options=["一般分析", "詳細分析", "テキスト抽出", "物体検出"]
    )

# メインコンテンツ
st.title("AI画像認識アプリ 🔍")
st.markdown("---")

# モデルの初期化
model = initialize_app()

# 入力エリア
col1, col2 = st.columns([2, 1])
with col1:
    input_text = st.text_area(
        "分析の指示や質問を入力（オプション）:",
        help="画像に対する具体的な質問や分析の指示を入力できます",
        key="input"
    )
with col2:
    try:
        uploaded_file = st.file_uploader(
                "画像をアップロード",
                type=["jpg", "jpeg", "png"],
                help="JPG、JPEG、PNGファイルをサポートしています"
            )
        if uploaded_file:
            image = preprocess_image(uploaded_file)
            if image:
                st.image(image, caption="アップロードされた画像", use_container_width=True)
    except Exception as e:
        st.error(f"画像の処理中にエラーが発生しました。別の画像を試してください。{str(e)}")

# 分析実行ボタン
if st.button("画像を分析", type="primary"):
    # 分析モードに基づいて入力テキストを調整
    prompt_prefix = {
            "一般分析": "この画像を詳しく説明してください。",
            "詳細分析": "この画像の細かい詳細まで分析し、色、構図、要素間の関係性について説明してください。",
            "テキスト抽出": "この画像に含まれるすべてのテキストを抽出し、その内容を説明してください。",
            "物体検出": "この画像に写っているすべての物体を検出し、それらの位置関係を説明してください。"
        }
    final_prompt = f"{prompt_prefix[analysis_mode]}"
    if language != "日本語":
        final_prompt += f"Please respond in {language}."

    response = get_gemini_response(model, final_prompt, image)
    if response:
        st.markdown("### 分析結果")
        st.markdown("---")
        st.write(response)

        # 分析結果の保存オプション
        if st.button("分析結果を保存"):
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            with open(f"analysis_result_{timestamp}.txt", "w", encoding="utf-8") as f:
                f.write(response)
            st.success("分析結果を保存しました！")
