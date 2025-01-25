from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
import logging
from typing import Optional, Dict, List, Any, Tuple
import json
from datetime import datetime
import pandas as pd
import re

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class RadiationAnalyzer:
    def __init__(self):
        self._setup_environment()
        self._setup_prompts()

    def _setup_environment(self) -> None:
        """環境設定とGeminiモデルの初期化"""
        try:
            load_dotenv()
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("API key not found in environment variables")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        except Exception as e:
            logger.error(f"Setup error: {str(e)}")
            raise

    def _setup_prompts(self) -> None:
        """プロンプトテンプレートの設定"""
        self.prompts = {
            "basic_info": """
            X線照射線量レポートから以下の基本情報を抽出して回答してください：
            1. 検査の総面積線量（cGy・cm²）
            2. 検査の総入射線量（mGy）
            3. 検査開始日時
            4. 参照点の定義
            5. 透視の総面積線量、総入射線量、積算時間
            6. 撮影の総面積線量、総入射線量、積算時間
            """,

            "graph_data": """
            グラフから以下のデータを抽出してJSON形式で返してください：

            1. データ形式:
            {
              "metadata": {
                "max_point": グラフの最後の回数
              },
              "fluoroscopy": {
                // 青色バーの値（key: 回数, value: 左軸の値）
                // 全ての回数を含める（値が0の場合も）
              },
              "radiography": {
                // 黄色バーの値（key: 回数, value: 左軸の値）
                // 全ての回数を含める（値が0の場合も）
              }
            }

            2. 注意点:
            - 値は小数点第1位まで記録
            - 左軸の単位はcGy・cm2
            - 1から最後の回数まで全て記録
            - 必ず有効なJSONとして解析可能な形式で返すこと
            """
        }

    def process_image(self, image_file) -> Dict:
        """画像ファイルの処理"""
        try:
            if image_file.size > 5 * 1024 * 1024:
                raise ValueError("File size too large (max 5MB)")

            return [{
                "mime_type": image_file.type,
                "data": image_file.getvalue()
            }]
        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
            raise

    def analyze_report(self, image_data: List[Dict]) -> Tuple[str, Dict]:
        """レポートの分析実行"""
        try:
            # 基本情報の取得
            basic_info = self.model.generate_content(
                [self.prompts["basic_info"], image_data[0]]
            ).text

            # グラフデータの取得と解析
            graph_response = self.model.generate_content(
                [self.prompts["graph_data"], image_data[0]]
            ).text
            graph_data = self._parse_graph_data(graph_response)

            return basic_info, graph_data

        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            raise

    def _parse_graph_data(self, response: str) -> Dict:
        """グラフデータの解析"""
        try:
            # JSONデータの抽出（余分なテキストがある場合に対応）
            json_match = re.search(r'\{[\s\S]*\}', response)
            if not json_match:
                raise ValueError("No valid JSON found in response")

            data = json.loads(json_match.group())

            # データの検証
            required_keys = ["metadata", "fluoroscopy", "radiography"]
            if not all(key in data for key in required_keys):
                raise ValueError("Missing required data categories")

            max_point = int(data["metadata"]["max_point"])

            # データの検証と整形
            result = {
                "metadata": {"max_point": max_point},
                "fluoroscopy": {},
                "radiography": {}
            }

            # 各データセットの処理
            for key in ["fluoroscopy", "radiography"]:
                values = {str(k): float(v) for k, v in data[key].items()}
                # すべての回数のデータが存在することを確認
                expected_points = set(str(i) for i in range(1, max_point + 1))
                if set(values.keys()) != expected_points:
                    raise ValueError(f"Missing points in {key} data")
                result[key] = values

            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            raise ValueError("Invalid JSON format in response")
        except Exception as e:
            logger.error(f"Graph data parsing error: {str(e)}")
            raise

def create_dataframe(data: Dict, data_type: str) -> pd.DataFrame:
    """データフレームの作成"""
    try:
        if data_type not in ["fluoroscopy", "radiography"]:
            raise ValueError("Invalid data type")

        df = pd.DataFrame([
            {"回数": k, "面積線量 (cGy・cm²)": v}
            for k, v in data[data_type].items()
        ])
        df["回数"] = df["回数"].astype(int)
        return df.sort_values("回数")
    except Exception as e:
        logger.error(f"DataFrame creation error: {str(e)}")
        raise

def main():
    st.set_page_config(page_title="放射線レポート分析", page_icon="📊")
    st.title("放射線レポート分析システム")

    try:
        analyzer = RadiationAnalyzer()

        uploaded_file = st.file_uploader(
            "X線照射線量レポートをアップロード",
            type=["jpg", "jpeg", "png"],
            help="対応フォーマット: JPG, JPEG, PNG（最大5MB）"
        )

        if uploaded_file:
            # 画像の表示
            image = Image.open(uploaded_file)
            st.image(image, caption="アップロードされたレポート", use_container_width=True)

            if st.button("レポートを分析", type="primary"):
                with st.spinner("分析中..."):
                    # 画像の処理と分析
                    image_data = analyzer.process_image(uploaded_file)
                    basic_info, graph_data = analyzer.analyze_report(image_data)

                    # 結果の表示
                    tab1, tab2 = st.tabs(["基本情報", "グラフデータ"])

                    with tab1:
                        st.markdown("### 基本情報")
                        st.markdown(basic_info)

                    with tab2:
                        st.markdown("### グラフデータ")
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("透視線量データ")
                            fluoro_df = create_dataframe(graph_data, "fluoroscopy")
                            non_zero_fluoro = fluoro_df[fluoro_df["面積線量 (cGy・cm²)"] > 0]
                            st.dataframe(non_zero_fluoro)

                            if not non_zero_fluoro.empty:
                                st.metric("最大面積線量",
                                        f"{non_zero_fluoro['面積線量 (cGy・cm²)'].max():.1f} cGy・cm²")
                                st.metric("平均面積線量",
                                        f"{non_zero_fluoro['面積線量 (cGy・cm²)'].mean():.1f} cGy・cm²")

                        with col2:
                            st.subheader("撮影線量データ")
                            radio_df = create_dataframe(graph_data, "radiography")
                            non_zero_radio = radio_df[radio_df["面積線量 (cGy・cm²)"] > 0]
                            st.dataframe(non_zero_radio)

                            if not non_zero_radio.empty:
                                st.metric("最大面積線量",
                                        f"{non_zero_radio['面積線量 (cGy・cm²)'].max():.1f} cGy・cm²")
                                st.metric("平均面積線量",
                                        f"{non_zero_radio['面積線量 (cGy・cm²)'].mean():.1f} cGy・cm²")

                    # 結果の保存
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                    # 基本情報の保存
                    st.download_button(
                        "分析結果をテキストファイルでダウンロード",
                        data=basic_info,
                        file_name=f"radiation_analysis_{timestamp}.txt",
                        mime="text/plain"
                    )

                    # グラフデータの保存
                    st.download_button(
                        "グラフデータをJSONでダウンロード",
                        data=json.dumps(graph_data, ensure_ascii=False, indent=2),
                        file_name=f"radiation_graph_data_{timestamp}.json",
                        mime="application/json"
                    )

    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
        logger.error(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()
