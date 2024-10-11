from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from unstructured.partition.auto import partition
import json
import csv
import os


class DataPreprocessor:
    """
    A class for preprocessing data from files in different formats.
    """

    def __init__(self, data_dir, data_file, chunk_size=1000, chunk_overlap=50):
        self.data_dir = data_dir
        self.data_file = data_file
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _process_json(self, file_path: str):
        """Processes a JSON file, extracting documents and metadata."""
        with open(file_path, "r") as f:
            docs = json.load(f)
        return docs

    def _process_csv(self, file_path: str):
        """Processes a CSV file, extracting documents and metadata."""
        docs = []
        with open(file_path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                docs.append(dict(row))
        return docs

    def _process_files(self, file_path: str):
        """Processes files such as markdown, docx, and csv, extracting documents and metadata."""
        elements = partition(filename=file_path)
        docs = [str(el) for el in elements]

        if not docs:
            raise ValueError("No elements found in the file.")
        
        return docs

    def _load_documents(self, file_path: str):
        """
        Loads documents from a text file.

        Args:
            file_path (str): The path to the text file.

        Returns:
            list: A list of loaded documents.
        """
        try:
            loader = TextLoader(file_path)
            docs = loader.load()
            return docs
        except Exception as e:
            print(f"Error loading document from {file_path}: {e}")
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
            print(f"Error splitting documents: {e}")
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

            if ext == ".json":
                docs = self._process_json(file_path)
            elif ext == ".csv":
                docs = self._process_csv(file_path)
            else:
                docs = self._process_files(file_path)

            if not docs:
                print(f"No documents extracted from {self.data_file}.")
                return None

            documents = []
            for doc in docs:
                # Skip loading for JSON/CSV, use as-is
                if isinstance(doc, dict) or isinstance(doc, str):
                    doc_chunks = self._split_documents([doc])
                else:
                    loaded_doc = self._load_documents(doc)
                    if loaded_doc:
                        doc_chunks = self._split_documents(loaded_doc)
                    else:
                        continue

                if doc_chunks:
                    documents.extend(doc_chunks)

            return documents

        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            print(f"Error processing data file '{self.data_file}': {e}")
            return None
