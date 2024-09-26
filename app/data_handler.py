import json
import csv
import os


class DataPreprocessor:
    """
    A class for embedd data from files in JSON and CSV formats.
    """

    def __init__(self, data_dir):
        """
        Initializes the preprocessor with the data directory path.

        Args:
            data_dir (str): The path to the directory containing data files.
        """
        self.data_dir = data_dir

    def preprocess(self, data_file: str):
        """
        Preprocesses a data file and returns extracted documents and metadata.

        Args:
            data_file (str): The name of the data file to process.

        Returns:
            tuple or None:
                - A tuple containing two lists (documents, metadata) if successful.
                - None if there's an error during processing.
        """

        payload_path = os.path.join(self.data_dir, data_file)
        try:
            ext = os.path.splitext(data_file)[1].lower()

            if ext == ".json":
                return self._process_json(payload_path)

            elif ext == ".csv":
                return self._process_csv(payload_path)

            else:
                return None  # Handle unsupported file formats gracefully

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error processing data file '{data_file}': {e}")
            return None

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