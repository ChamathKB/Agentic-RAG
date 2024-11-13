from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredFileLoader
import logging
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPreprocessor:
    """
    A class for preprocessing data from files in different formats.
    """

    def __init__(self, data_dir, data_file, chunk_size=1000, chunk_overlap=50):
        self.data_dir = data_dir
        self.data_file = data_file
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap


    def _process_files(self, file_path: str):
        """Processes files such as markdown, docx, and csv, extracting documents and metadata."""
        try:
            loader = UnstructuredFileLoader(file_path)
            docs = loader.load()

            if not docs:
                raise ValueError("No elements found in the file.")
            
            return docs
        except Exception as e:
            logger.error(f"Error processing file '{file_path}': {e}")
            return None


    def _split_documents(self, docs):
        """
        Splits documents into chunks using a text splitter.

        Args:
            docs (list): A list of documents to split.

        Returns:
            list: A list of chunked documents.
        """
        try:
            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
            )
            chunked_documents = text_splitter.split_documents(docs)
            return chunked_documents
        except Exception as e:
            logger.error(f"Error splitting documents for file '{self.data_file}': {e}")
            return None


    def preprocess(self):
        """
        Preprocesses a data file and returns extracted documents and metadata.

        Returns:
            list: A list of chunked documents.
        """
        file_path = os.path.join(self.data_dir, self.data_file)

        try:
            ext = os.path.splitext(self.data_file)[1].lower()

            if ext in [".md", ".docx", "csv"]:
                # Process files such as markdown, docx, and csv
                docs = self._process_files(file_path)
            else:
                raise ValueError(f"Unsupported file format: {ext}")
            
            doc_chunks = self._split_documents(docs)

            return doc_chunks

        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error processing data file '{self.data_file}': {e}")
            return None
