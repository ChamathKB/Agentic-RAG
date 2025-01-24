class DataPreprocessorError(Exception):
    """Base class for all preprocessing errors."""
    pass

class FileNotFoundError(DataPreprocessorError):
    """Raised when the specified file does not exist."""
    pass

class UnsupportedFileFormatError(DataPreprocessorError):
    """Raised when the file format is unsupported."""
    pass

class FileProcessingError(DataPreprocessorError):
    """Raised when there is an error in processing the file."""
    pass

class DocumentSplittingError(DataPreprocessorError):
    """Raised when there is an error in splitting documents."""
    pass
