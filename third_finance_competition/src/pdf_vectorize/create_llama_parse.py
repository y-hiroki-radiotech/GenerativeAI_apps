import os
from copy import deepcopy
from glob import glob

from dotenv import load_dotenv
from llama_index.core import (
    Settings,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.core.schema import TextNode
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.llms.openai import OpenAI
from llama_index.postprocessor.cohere_rerank import CohereRerank
from llama_parse import LlamaParse

import settings


load_dotenv()


class LlamaParserVectorStore:
    def __init__(self, model="OpenAI"):
        self.llm = self._initialize_llm(model)
        self.embed_model = self._initialize_embed(model)
        self.file_paths = self._file_paths()
        self.reranker = CohereRerank(top_n=5)
        self.save_and_load_path = f"./{model}_storage"

    def _initialize_llm(self, model):
        if model == "OpenAI":
            return OpenAI(model=settings.OPENAI_MODEL)
        elif model == "Gemini":
            return Gemini(model=settings.GEMINI_MODEL)
        else:
            raise ValueError("Unsupported model type. Use 'OpenAI' or 'Gemini'.")

    def _initialize_embed(self, model):
        if model == "OpenAI":
            return OpenAIEmbedding(model=settings.OPENAI_EMBEDDING_MODEL)
        elif model == "Gemini":
            return GeminiEmbedding(model=settings.GEMINI_EMBEDDING_MODEL)
        else:
            raise ValueError("Unsupported model type. Use 'OpenAI' or 'Gemini'.")

    def _file_paths(self, file_path=None):
        try:
            if file_path is None:
                file_paths = glob(settings.pdf_file_path + "/*")
            else:
                file_paths = glob(file_path + "/*")
        except Exception as e:
            print(e)
        return file_paths

    def _get_page_nodes(self, docs, separator="\n---\n"):
        """Split each document into page node, by separator."""
        nodes = []
        for doc in docs:
            doc_chunks = doc.text.split(separator)
            for doc_chunk in doc_chunks:
                node = TextNode(text=doc_chunk, metadata=deepcopy(doc.metadata))
                nodes.append(node)
        return nodes

    def _save_index(self, index):
        index.storage_context.persist(persist_dir=self.save_and_load_path)

    def _index_load(self):
        # ストレージコンテキストの作成
        storage_context = StorageContext.from_defaults(
            persist_dir=self.save_and_load_path
        )
        # インデックスのロード
        index_pages = load_index_from_storage(storage_context)
        return index_pages

    def create_vector_engine(self, save=False):
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model

        parser = LlamaParse(
            result_type="markdown", verbose=True, num_workers=len(self.file_paths)
        )
        documents = parser.load_data(self.file_paths)

        node_parser = MarkdownElementNodeParser(
            llm=self.llm, num_worker=len(self.file_paths)
        )

        nodes = node_parser.get_nodes_from_documents(documents)
        base_nodes, objects = node_parser.get_nodes_and_objects(nodes)
        page_nodes = self._get_page_nodes(documents)

        recursive_index = VectorStoreIndex(nodes=base_nodes + objects + page_nodes)
        recursive_pages_query_engine = recursive_index.as_query_engine(
            similarity_top_k=5, node_postprocessor=[self.reranker], verbose=True
        )

        if save:
            self._save_index(recursive_index)

        return recursive_pages_query_engine

    def load_vector_engine(self):
        if os.path.exists(self.save_and_load_path):
            index = self._index_load()
            return index.as_query_engine(
                similarity_top_k=5, node_postprocessor=[self.reranker], verbose=True
            )
        else:
            raise FileNotFoundError(
                f"No saved index found at {self.save_and_load_path}"
            )
