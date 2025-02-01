import os
import logging
import re
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any

import PyPDF2
import pytesseract
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from openai import OpenAI
from pdf2image import convert_from_path
from PIL import Image

import settings

load_dotenv()
logging.basicConfig(level=logging.INFO, force=True)


class PdfRename:
    """
    PDFファイルの名前を変更し、メタデータを更新するためのクラス。

    このクラスは以下の機能を提供します：
    - PDFファイルのテキスト抽出（OCR処理を含む）
    - OpenAIを使用したタイトル生成
    - PDFファイルの名前変更
    - メタデータの更新

    Attributes:
        llm (OpenAI): OpenAI APIクライアントインスタンス
        file_path (str): 処理対象のPDFファイルが存在するディレクトリパス
        pdf_files (List[str]): 処理対象のPDFファイルパスのリスト
    """

    def __init__(self, file_path: Optional[str] = None) -> None:
        """
        PdfRenameクラスの初期化。

        Args:
            file_path (Optional[str]): PDFファイルが存在するディレクトリパス。
                                     Noneの場合、デフォルトのパスが使用されます。

        Raises:
            FileNotFoundError: 指定されたディレクトリが存在しない場合
        """
        self.llm = OpenAI()
        self.file_path = file_path or self._get_default_file_path()
        self.pdf_files = self._get_pdf_files()

    def _get_default_file_path(self) -> str:
        """
        デフォルトのファイルパスを取得する。

        Returns:
            str: デフォルトのファイルパス（現在のディレクトリの'documents'フォルダ）

        Raises:
            FileNotFoundError: デフォルトのファイルパスが存在しない場合
        """
        current_dir = os.getcwd()
        default_path = os.path.join(current_dir, settings.DOCUMENTS)
        if not os.path.exists(default_path):
            raise FileNotFoundError(
                f"デフォルトのファイルパスが見つかりません: {default_path}・・・\
                settings.pyのsettingsDOCUMENTSを見直してください。"
            )
        return default_path

    def _generate_title(self, text: str) -> str:
        """
        テキストから会社名と報告書の種類を抽出してタイトルを生成する。

        Args:
            text (str): 解析対象のテキスト

        Returns:
            str: 生成されたタイトル（形式: 会社名-報告書の種類-年）
        """
        response = self.llm.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "あなたは優秀な日本の経済アナリストです。以下のテキストから会社名と報告書の種類を抽出してください。"},
                {"role": "user", "content": text},
                {"role": "system", "content": "以下の形式で出力してください: 会社名-報告書の種類-年"}
            ]
        )
        return response.choices[0].message.content.strip()

    def _clean_text(self, text: str) -> str:
        """
        抽出したテキストのクリーニングを行う。

        Args:
            text (str): クリーニング対象のテキスト

        Returns:
            str: クリーニング済みのテキスト
        """
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _extract_text_from_image(self, file_path: str) -> str:
        """
        PDFをOCR処理してテキストを抽出する。

        Args:
            file_path (str): 処理対象のPDFファイルパス

        Returns:
            str: 抽出されたテキスト（最初のページのみ）
        """
        images = convert_from_path(file_path)
        text_content = []
        # タイトルを抜き出すので、最初のページだけ処理する
        for image in images[:1]:
            text = pytesseract.image_to_string(image, lang="jpn")
            text_content.append(text)
            break
        return text_content[0]

    def _rename_pdf_file(self, file_path: str) -> None:
        """
        PDFファイルの名前を変更し、メタデータを更新する。

        Args:
            file_path (str): 処理対象のPDFファイルパス

        Note:
            この処理は元のファイルを削除し、新しいファイルを作成します。
        """
        reader = PyPDF2.PdfReader(file_path)
        writer = PyPDF2.PdfWriter()

        # メタデータを取得
        metadata = reader.metadata
        metadata.update({PyPDF2.generic.NameObject('/Title'): PyPDF2.generic.createStringObject(title)})

        # すべてのページをライターに追加
        for page_num in range(len(reader.pages)):
            writer.add_page(reader.pages[page_num])

        # メタデータを設定
        writer.add_metadata(metadata)

        first_page_text = self._extract_text_from_image(file_path)
        title = self._generate_title(first_page_text)

        # 新しいファイル名でPDFを保存
        output_path = f"{title}.pdf"

        shutil.copy2(file_path, output_path)
        original_path = Path(file_path)
        original_path.unlink()

    def _get_pdf_files(self) -> List[str]:
        """
        指定されたディレクトリからPDFファイルのリストを取得する。

        Returns:
            List[str]: PDFファイルパスのリスト
        """
        pdf_files = []
        for file in os.listdir(self.file_path):
            if file.endswith(".pdf"):
                pdf_files.append(os.path.join(self.file_path, file))
        return pdf_files

    def rename_pdfs(self) -> None:
        """
        すべてのPDFファイルの名前を変更する。

        Note:
            このメソッドは self.pdf_files 内のすべてのPDFファイルを処理します。
        """
        for pdf_file in self.pdf_files:
            self._rename_pdf_file(pdf_file)


if __name__ == "__main__":
    pdf_rename = PdfRename()
    pdf_rename.rename_pdfs()
