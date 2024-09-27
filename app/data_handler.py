from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
import json
import csv
import os


class DataPreprocessor:
    """
    A class for preprocess data from files different formats.
    """

    def __init__(self, data_dir, data_file, chunk_size=1000, chunk_overlap=50):
        """
        Initializes the preprocessor with the data directory path.

        Args:
            data_dir (str): The path to the directory containing data files.
            data_file (str): The name of the data file to process.
            chunk_size (int, optional): The size of each chunk. Defaults to 350.
            chunk_overlap (int, optional): The overlap between chunks. Defaults to 50.
        """
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
    

    def _load_documents(document):
        """
        Loads documents from a text file.

        Args:
            document (str): The path to the text file.

        Returns:
            list: A list of loaded documents.
        """

        loader = TextLoader(document)
        docs = loader.load()
        return docs


    def _split_documents(self, docs):
        """
        Splits documents into chunks using a text splitter.

        Args:
            docs (list): A list of documents to split.

        Returns:
            list: A list of chunked documents.
        """
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )
        chunked_documents = text_splitter.split_documents(docs)
        return chunked_documents
    

    def preprocess(self):
        """
        Preprocesses a data file and returns extracted documents and metadata.

        Args:
            data_file (str): The name of the data file to process.

        Returns:
            tuple or None:
                - A tuple containing two lists (documents, metadata) if successful.
                - None if there's an error during processing.
        """

        payload_path = os.path.join(self.data_dir, self.data_file)
        try:
            ext = os.path.splitext(self.data_file)[1].lower()

            if ext == ".json":
                docs = self._process_json(payload_path)
            elif ext == ".csv":
                docs = self._process_csv(payload_path)
            else:
                return None  # Handle unsupported file formats gracefully
            
            docs = self._load_documents(docs)
            docs = self._split_documents(docs)

            return docs

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error processing data file '{self.data_file}': {e}")
            return None