import logging
import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredFileLoader

from app.exceptions.preprocessor import (
    DataPreprocessorError,
    DocumentSplittingError,
    FileProcessingError,
    UnsupportedFileFormatError,
)
from app.models.schema import Docs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """
    A class for preprocessing data from files in different formats.
    """

    SUPPORTED_EXTENSIONS = [".md", ".docx", ".csv"]

    def __init__(
        self,
        data_dir: str,
        data_file: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 50,
    ) -> None:
        """Initializes the DataPreprocessor with the specified parameters.
        Args:
            data_dir (str): The directory where the data file is located.
            data_file (str): The name of the data file.
            chunk_size (int, optional): The size of the chunks to split the documents into.
                                        Defaults to 1000.
            chunk_overlap (int, optional): The overlap between chunks. Defaults to 50.
        Raises:
            DataPreprocessorError: If the file does not exist or is not supported.
            FileProcessingError: If there is an error processing the file.
            DocumentSplittingError: If there is an error splitting the documents.
            UnsupportedFileFormatError: If the file format is not supported.
            Exception: For any other unexpected errors during preprocessing.
        """

        self.data_dir = data_dir
        self.data_file = data_file
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _validate_file(self) -> str:
        """Validates the existence and extension of the file.
        Returns:
            str: The full path of the validated file.
        Raises:
            DataPreprocessorError: If the file does not exist or the file format is not supported.
            UnsupportedFileFormatError: If the file format is not supported.
        Raises:
            FileNotFoundError: If the file does not exist.
            UnsupportedFileFormatError: If the file format is not supported.
        """
        file_path = os.path.join(self.data_dir, self.data_file)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' does not exist.")
        if os.path.splitext(self.data_file)[1].lower() not in self.SUPPORTED_EXTENSIONS:
            raise UnsupportedFileFormatError(f"Unsupported file format: {self.data_file}")
        return file_path

    def _process_files(self, file_path: str) -> Docs:
        """Processes files such as markdown, docx, and csv, extracting documents and metadata.
        Args:
            file_path (str): The path of the file to process.
        Returns:
            Docs: A list of documents extracted from the file.
        Raises:
            FileProcessingError: If there is an error processing the file.
            Exception: For any other unexpected errors during file processing.
        Raises:
            FileProcessingError: If there is an error processing the file.
            Exception: For any other unexpected errors during file processing.
        """
        try:
            loader = UnstructuredFileLoader(file_path)
            docs = loader.load()
            if not docs:
                raise FileProcessingError("No elements found in the file.")
            return docs
        except Exception as e:
            raise FileProcessingError(f"Error processing file '{file_path}': {e}")

    def _split_documents(self, docs: Docs) -> Docs:
        """Splits documents into smaller chunks.
        Args:
            docs (Docs): A list of documents to split.
        Returns:
            Docs: A list of split documents.
        Raises:
            DocumentSplittingError: If there is an error splitting the documents.
            Exception: For any other unexpected errors during document splitting.
        Raises:
            DocumentSplittingError: If there is an error splitting the documents.
            Exception: For any other unexpected errors during document splitting.
        """
        try:
            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
            return text_splitter.split_documents(docs)
        except Exception as e:
            raise DocumentSplittingError(f"Error splitting documents: {e}")

    def preprocess(self) -> Docs:
        """Preprocesses a data file and returns extracted documents and metadata.
        Returns:
            Docs: A list of documents extracted from the file.
        Raises:
            DataPreprocessorError: If any error occurs during preprocessing.
            Exception: For any other unexpected errors during preprocessing.
        """
        try:
            file_path = self._validate_file()
            docs = self._process_files(file_path)
            return self._split_documents(docs)
        except DataPreprocessorError as e:
            logger.error(f"Preprocessing error: {e}")
            raise  # Re-raise the exception to let the caller handle it
