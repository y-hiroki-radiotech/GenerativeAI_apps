from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
import logging
from typing import Optional, Dict, List, Any
import json
from datetime import datetime
import re
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class RadiationData:
    def __init__(self):
        self.fluoroscopy_data = []
        self.radiography_data = []
        self.cumulative_data = []
        self.basic_info = {}
        self.total_stats = {}

    def to_dict(self) -> Dict:
        """データを辞書形式に変換"""
        return {
            "basic_info": self.basic_info,
            "total_stats": self.total_stats,
            "data": {
                "fluoroscopy_data": self.fluoroscopy_data,
                "radiography_data": self.radiography_data,
                "cumulative_data": self.cumulative_data
            }
        }

def format_radiation_data(data: Dict) -> Dict[str, str]:
    """放射線データを見やすく整形"""
    formatted = {}

    # 基本情報の整形
    if 'total_area_dose_cgy_cm2' in data['basic_info']:
        formatted['総面積線量'] = f"{data['basic_info']['total_area_dose_cgy_cm2']} cGy・cm²"
    if 'total_incident_dose_mgy' in data['basic_info']:
        formatted['総入射線量'] = f"{data['basic_info']['total_incident_dose_mgy']} mGy"
    if 'examination_start_time' in data['basic_info']:
        formatted['検査開始時間'] = data['basic_info']['examination_start_time']

    return formatted

class RadiationReportAnalyzer:
    def __init__(self):
        self.load_enviroment()
        self.model = self.initialize_gemini()
        self.setup_prompts()
        self.radiation_data = RadiationData()

    def load_enviroment(self) -> None:
        """環境変数の読み込みと検証"""
        try:
            load_dotenv()
            self.api_key = os.getenv("GOOGLE_API_KEY")
            if not self.api_key:
                raise ValueError("API key not found in environment variables")
        except Exception as e:
            logger.error(f"Environment loading error: {str(e)}")
            raise

    def initialize_gemini(self) -> None:
        """Geminiモデルの初期化"""
        try:
            genai.configure(api_key=self.api_key)
            return genai.GenerativeModel(model_name="gemini-1.5-pro")
        except Exception as e:
            logger.error(f"Gemini initialization error: {str(e)}")
            raise

    def setup_prompts(self) -> None:
        """分析プロンプトの設定"""
        self.prompt_templates = {
            "標準分析": """
        この画像はX線照射線量レポートです。人が読みやすい形式で回答してください：

        1. 基本情報:
           - 検査の総面積線量（cGy・cm²）
           - 検査の総入射線量（mGy）
           - 検査開始日時
           - 参照点の定義

        2. 合計統計:
           透視情報:
           - 総面積線量（cGy・cm²）
           - 総入射線量（mGy）
           - 積算時間（秒）

           撮影情報:
           - 総面積線量（cGy・cm²）
           - 総入射線量（mGy）
           - 積算時間（秒）

        """,

            "詳細分析": """
        この画像はX線照射線量レポートです。詳細な分析を行い、以下の情報を人が読みやすい形式で回答してください：

        1. 基本情報:
           - 検査の総面積線量（cGy・cm²）と意義
           - 検査の総入射線量（mGy）と臨床的意味
           - 検査開始日時
           - 参照点の定義と重要性
           - 撮影条件の詳細
           - 装置情報

        2. 詳細統計:
           透視分析:
           - 総面積線量（cGy・cm²）とその分布
           - 総入射線量（mGy）の特徴
           - 積算時間（秒）の分析
           - 平均線量率と変動
           - 最大線量率とその発生時点

           撮影分析:
           - 総面積線量（cGy・cm²）の詳細
           - 総入射線量（mGy）の特徴
           - 積算時間（秒）の分析
           - 平均線量と特徴
           - 最大線量とその意義

        3. 総合評価:
           - 被ばく管理の観点からの評価
           - 最適化の提案
           - 特記すべき所見
        """,

            "簡易分析": """
        この画像はX線照射線量レポートです。重要な情報を簡潔に抽出し、人が読みやすい形式で回答してください：

        1. 基本情報:
           - 検査の総面積線量（cGy・cm²）
           - 検査の総入射線量（mGy）
           - 検査開始日時

        2. 主要な数値:
           透視:
           - 総面積線量（cGy・cm²）
           - 総入射線量（mGy）

           撮影:
           - 総面積線量（cGy・cm²）
           - 総入射線量（mGy）

        3. 重要ポイント:
           - 最大線量値
           - 特記事項
        """
        }


    def process_image(self, uploaded_file) -> Optional[List[Dict[str, Any]]]:
        """画像ファイルの処理と検証"""
        try:
            if uploaded_file is None:
                raise FileNotFoundError("ファイルがアップロードされていません")
            if uploaded_file.size > 5 * 1024 * 1024:
                raise ValueError("ファイルサイズが大きすぎます（5MB以下にしてください）")

            bytes_data = uploaded_file.getvalue()
            return [{
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }]
        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
            raise

    def get_analysis(self, image_data: List[Dict[str, Any]], analysis_type: str = "標準分析", custom_prompt: str = "") -> str:
        """放射線レポートの分析実行"""
        try:
            prompt = custom_prompt if custom_prompt else self.prompt_templates[analysis_type]
            response = self.model.generate_content([prompt, image_data[0]])
            return response.text
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            raise

# ToDo: ここにグラフ専用の読み込みを作成する
class GraphDataExtractor:
    def __init__(self):
        self.prompt = """
        この画像は放射線レポートのグラフデータです。以下の基準で値を読み取り、JSON形式で返してください：

        1. グラフの読み取り基準:
           - 青色のバー: 透視線量（左軸の値を読み取る）
           - 黄色のバー: 撮影線量（左軸の値を読み取る）
           - 横軸: 回数

        2. データ形式:
           {
             "fluoroscopy": {
                透視線量データ（青色バー）
                "回数": 線量値
                線量が0の場合も含める
             },
             "radiography": {
               撮影線量データ（黄色バー）
               "回数": 線量値
               線量が0の場合も含める
             }
           }

        3. 読み取りの注意点:
           - 値は小数点第1位まで読み取る
           - バーが存在しない（線量が0）の場合も記録
           - 左軸（面積線量）の単位はcGy・cm2
           - 1から29までの全ての回数について記録

        回答は必ずJSONとして解析可能な形式で返してください。
        """

    def parse_response(self, response_text: str) -> Dict[str, Dict[str, float]]:
        """
        APIレスポンスをパースしてデータを整理する

        Args:
            response_text (str): APIからのレスポンステキスト

        Returns:
            Dict[str, Dict[str, float]]: 整理されたデータ
            {
                "fluoroscopy": {"1": 0.0, "2": 1.2, ...},
                "radiography": {"1": 0.0, "2": 0.0, ...}
            }
        """
        try:
            # JSONデータの抽出と解析
            data = json.loads(response_text)

            # データの検証
            required_keys = ["fluoroscopy", "radiography"]
            if not all(key in data for key in required_keys):
                raise ValueError("Required data categories not found in response")

            # データの整形
            result = {
                "fluoroscopy": {str(k): float(v) for k, v in data["fluoroscopy"].items()},
                "radiography": {str(k): float(v) for k, v in data["radiography"].items()}
            }

            return result

        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in response")
        except Exception as e:
            raise ValueError(f"Error parsing response: {str(e)}")

    def format_data_for_display(self, data: Dict[str, Dict[str, float]]) -> str:
        """
        データを表示用にフォーマットする

        Args:
            data (Dict[str, Dict[str, float]]): パースされたデータ

        Returns:
            str: フォーマットされたテキスト
        """
        output = []
        output.append("=== 透視線量データ ===")
        for point, value in sorted(data["fluoroscopy"].items(), key=lambda x: int(x[0])):
            output.append(f"回数 {point}: {value:.1f} cGy・cm2")

        output.append("\n=== 撮影線量データ ===")
        for point, value in sorted(data["radiography"].items(), key=lambda x: int(x[0])):
            output.append(f"回数 {point}: {value:.1f} cGy・cm2")

        return "\n".join(output)

    def get_prompt(self) -> str:
        """プロンプトを取得する"""
        return self.prompt


def main():
    st.set_page_config(
        page_title="放射線レポート分析",
        page_icon="📊",
    )

    st.title("放射線レポート分析システム")
    st.markdown("""
                このアプリケーションは、X線照射線量レポートを分析し、わかりやすい形式で情報を提供します。
                """)

    try:
        analyzer = RadiationReportAnalyzer()

        with st.sidebar:
            st.header("分析オプション")
            analysis_type = st.radio(
                "分析タイプの選択",
                ["標準分析", "詳細分析", "簡易分析"]
            )

        uploaded_file = st.file_uploader(
            "X線照射線量レポートをアップロード",
            type=["jpg", "jpeg", "png"],
            help="対応フォーマット: JPG, JPEG, PNG"
        )

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="アップロードされたレポート", use_container_width=True)

            if st.button("レポートを分析", type="primary"):
                with st.spinner("分析中..."):
                    image_data = analyzer.process_image(uploaded_file)
                    analysis_result = analyzer.get_analysis(image_data, analysis_type)

                    st.markdown("### 分析結果")
                    st.markdown("---")

                    # タブで結果を分けて表示
                    tab1, tab2 = st.tabs(["テキスト分析", "グラフデータ"])

                    with tab1:
                        # テキストベースの分析結果を表示
                        st.markdown(analysis_result)

                    with tab2:
                        try:
                            # 透視データと撮影データを並べて表示するための列を作成
                            col1, col2 = st.columns(2)

                            with col1:
                                st.subheader("透視線量データ (青色バー)")
                                print(analysis_result)
                                if "fluoroscopy_data" in analysis_result.get("data", {}):
                                    fluoroscopy_data = analysis_result["data"]["fluoroscopy_data"]
                                    fluoroscopy_df = pd.DataFrame(fluoroscopy_data)
                                    if not fluoroscopy_df.empty:
                                        # データの表示
                                        st.dataframe(
                                            fluoroscopy_df.rename(columns={
                                                'point': 'ポイント',
                                                'area_dose': '面積線量 (cGy・cm²)'
                                            })
                                        )

                                        # 統計情報
                                        st.metric(
                                            "最大面積線量",
                                            f"{fluoroscopy_df['area_dose'].max():.2f} cGy・cm²"
                                        )
                                        st.metric(
                                            "平均面積線量",
                                            f"{fluoroscopy_df['area_dose'].mean():.2f} cGy・cm²"
                                        )
                                    else:
                                        st.info("透視データが見つかりませんでした")
                                else:
                                    st.info("透視データが見つかりませんでした")

                            with col2:
                                st.subheader("撮影線量データ (黄色バー)")
                                if "radiography_data" in analysis_result.get("data", {}):
                                    radiography_data = analysis_result["data"]["radiography_data"]
                                    radiography_df = pd.DataFrame(radiography_data)
                                    if not radiography_df.empty:
                                        # データの表示
                                        st.dataframe(
                                            radiography_df.rename(columns={
                                                'point': 'ポイント',
                                                'area_dose': '面積線量 (cGy・cm²)'
                                            })
                                        )

                                        # 統計情報
                                        st.metric(
                                            "最大面積線量",
                                            f"{radiography_df['area_dose'].max():.2f} cGy・cm²"
                                        )
                                        st.metric(
                                            "平均面積線量",
                                            f"{radiography_df['area_dose'].mean():.2f} cGy・cm²"
                                        )
                                    else:
                                        st.info("撮影データが見つかりませんでした")
                                else:
                                    st.info("撮影データが見つかりませんでした")

                            # 累積データの表示（オプション）
                            if "cumulative_data" in analysis_result.get("data", {}):
                                st.subheader("累積線量データ（折れ線）")
                                cumulative_data = analysis_result["data"]["cumulative_data"]
                                cumulative_df = pd.DataFrame(cumulative_data)
                                if not cumulative_df.empty:
                                    st.dataframe(
                                        cumulative_df.rename(columns={
                                            'point': 'ポイント',
                                            'cumulative_dose': '累積線量 (cGy・cm²)'
                                        })
                                    )

                        except Exception as e:
                            st.warning("グラフデータの解析に失敗しました。テキスト分析結果をご確認ください。")
                            logger.error(f"Graph data processing error: {str(e)}")
                            st.error(f"エラーの詳細: {str(e)}")


                    # テキストファイルとしての保存オプション
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button(
                        "分析結果をテキストファイルでダウンロード",
                        data=analysis_result,
                        file_name=f"radiation_analysis_{timestamp}.txt",
                        mime="text/plain"
                    )

    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
        logger.error(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()
