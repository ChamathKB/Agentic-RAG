from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredFileLoader
from app.models.schema import Docs
from app.exceptions.preprocessor import DataPreprocessorError, FileProcessingError, DocumentSplittingError, UnsupportedFileFormatError
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPreprocessor:
    """
    A class for preprocessing data from files in different formats.
    """
    
    SUPPORTED_EXTENSIONS = [".md", ".docx", ".csv"]

    def __init__(self, data_dir: str, data_file: str, chunk_size: int = 1000, chunk_overlap: int = 50) -> None:
        self.data_dir = data_dir
        self.data_file = data_file
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _validate_file(self) -> str:
        """Validates the existence and extension of the file."""
        file_path = os.path.join(self.data_dir, self.data_file)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' does not exist.")
        if os.path.splitext(self.data_file)[1].lower() not in self.SUPPORTED_EXTENSIONS:
            raise UnsupportedFileFormatError(f"Unsupported file format: {self.data_file}")
        return file_path

    def _process_files(self, file_path: str) -> Docs:
        """Processes files such as markdown, docx, and csv, extracting documents and metadata."""
        try:
            loader = UnstructuredFileLoader(file_path)
            docs = loader.load()
            if not docs:
                raise FileProcessingError("No elements found in the file.")
            return docs
        except Exception as e:
            raise FileProcessingError(f"Error processing file '{file_path}': {e}")

    def _split_documents(self, docs: Docs) -> Docs:
        """Splits documents into smaller chunks."""
        try:
            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
            )
            return text_splitter.split_documents(docs)
        except Exception as e:
            raise DocumentSplittingError(f"Error splitting documents: {e}")

    def preprocess(self) -> Docs:
        """Preprocesses a data file and returns extracted documents and metadata."""
        try:
            file_path = self._validate_file()
            docs = self._process_files(file_path)
            return self._split_documents(docs)
        except DataPreprocessorError as e:
            logger.error(f"Preprocessing error: {e}")
            raise  # Re-raise the exception to let the caller handle it
