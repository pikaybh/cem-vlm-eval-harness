from typing import Optional
import pandas as pd
import logging
import os

# Root logger setup
logger_name = 'make_data.format_converter'
logger = logging.getLogger(logger_name)
logger.setLevel(logging.DEBUG)

# File Handler
file_handler = logging.FileHandler(f'logs/{logger_name}.log', encoding='utf-8-sig')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(r'%(asctime)s [%(name)s, line %(lineno)d] %(levelname)s: %(message)s'))
logger.addHandler(file_handler)

# Stream Handler
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter(r'%(message)s'))
logger.addHandler(stream_handler)


class FileFormatConverter:
    """
    A class to read and save data in various file formats using pandas.

    Attributes:
        _df (pd.DataFrame): The dataframe to store and manipulate the data.
        _delimiter (str): Delimiter used when reading/writing text files.
        _html_index (int): Index to select which HTML table to read from a file.
        _orient (str): Orientation for JSON format when saving.
        _index (bool): Whether to write row indices in output files.
        _lines (bool): Whether to write JSON in line-delimited format.
    """

    def __init__(self, delimiter: Optional[str] = '\t', html_index: Optional[int] = 0, orient: Optional[str] = 'records', index: Optional[bool] = False, json_lines: Optional[bool] = True) -> None:
        """
        Initializes the FileFormatConverter class with default settings for file reading and writing.

        Args:
            delimiter (str, optional): The delimiter to use when reading/writing text files. Defaults to '\t'.
            html_index (int, optional): The index of the HTML table to read. Defaults to 0.
            orient (str, optional): The orientation for JSON output. Defaults to 'records'.
            index (bool, optional): Whether to write row indices when saving files. Defaults to False.
            json_lines (bool, optional): Whether to write JSON in line-delimited format. Defaults to True.
        """
        self._df: pd.DataFrame = pd.DataFrame()
        self._delimiter: str = delimiter
        self._html_index: int = html_index
        self._orient: str = orient
        self._index: bool = index
        self._lines: bool = json_lines
        self.force_ascii: bool = False

    @property
    def df(self) -> pd.DataFrame:
        """
        Returns the current dataframe.

        Returns:
            pd.DataFrame: The dataframe stored in the instance.
        """
        return self._df

    @df.setter
    def df(self, value: pd.DataFrame) -> None:
        """
        Sets the dataframe.

        Args:
            value (pd.DataFrame): The dataframe to be assigned to the instance.
        """
        self._df = value

    @property
    def delimiter(self) -> str:
        """
        Returns the delimiter used for text files.

        Returns:
            str: The delimiter.
        """
        return self._delimiter

    @delimiter.setter
    def delimiter(self, value: str) -> None:
        """
        Sets the delimiter for text files.

        Args:
            value (str): The delimiter to use.
        """
        self._delimiter = value

    @property
    def html_index(self) -> int:
        """
        Returns the index of the HTML table to read.

        Returns:
            int: The index of the HTML table.
        """
        return self._html_index

    @html_index.setter
    def html_index(self, value: int) -> None:
        """
        Sets the index of the HTML table to read.

        Args:
            value (int): The index of the HTML table.
        """
        self._html_index = value

    @property
    def json_orient(self) -> str:
        """
        Returns the JSON orientation format.

        Returns:
            str: The JSON orientation format.
        """
        return self._orient

    @json_orient.setter
    def json_orient(self, value: str) -> None:
        """
        Sets the JSON orientation format.

        Args:
            value (str): The orientation format for JSON.
        """
        self._orient = value

    @property
    def index(self) -> bool:
        """
        Returns whether row indices are written to the output file.

        Returns:
            bool: Whether to write row indices.
        """
        return self._index

    @index.setter
    def index(self, value: bool) -> None:
        """
        Sets whether to write row indices to the output file.

        Args:
            value (bool): Whether to write row indices.
        """
        self._index = value

    @property
    def json_lines(self) -> bool:
        """
        Returns whether JSON is written in line-delimited format.

        Returns:
            bool: Whether JSON is line-delimited.
        """
        return self._lines

    @json_lines.setter
    def json_lines(self, value: bool) -> None:
        """
        Sets whether to write JSON in line-delimited format.

        Args:
            value (bool): Whether JSON should be line-delimited.
        """
        self._lines = value

    def _read_file(self, input_path: str) -> None:
        """
        Reads a file and loads its content into the dataframe.

        Args:
            input_path (str): The file path to read from.

        Raises:
            ValueError: If the file format is unsupported.
        """
        _, ext = os.path.splitext(input_path)
        
        if ext in [".xlsx", ".xls"]:
            self.df = pd.read_excel(input_path)
        elif ext == ".csv":
            self.df = pd.read_csv(input_path)
        elif ext == ".txt":
            self.df = pd.read_csv(input_path, delimiter=self.delimiter)
        elif ext == ".json":
            self.df = pd.read_json(input_path)
        elif ext == ".html":
            self.df = pd.read_html(input_path)[self.html_index]
        elif ext == ".parquet":
            self.df = pd.read_parquet(input_path)
        elif ext == ".feather":
            self.df = pd.read_feather(input_path)
        elif ext == ".orc":
            self.df = pd.read_orc(input_path)
        elif ext == ".sas":
            self.df = pd.read_sas(input_path)
        elif ext == ".stata":
            self.df = pd.read_stata(input_path)
        elif ext == ".hdf":
            self.df = pd.read_hdf(input_path)
        elif ext == ".pkl":
            self.df = pd.read_pickle(input_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def _save_file(self, out_path: str) -> None:
        """
        Saves the dataframe to a file.

        Args:
            out_path (str): The file path to save to.
            index (bool): Whether to write row indices.
            lines (bool): Whether to write JSON in line-delimited format.

        Raises:
            ValueError: If saving to the specified format is unsupported.
        """
        _, ext = os.path.splitext(out_path)

        if ext in [".xlsx", ".xls"]:
            self.df.to_excel(out_path, index=self.index)
        elif ext == ".csv":
            self.df.to_csv(out_path, index=self.index)
        elif ext == ".txt":
            self.df.to_csv(out_path, sep=self.delimiter, index=self.index)
        elif ext == ".json":
            self.df.to_json(out_path, orient=self.json_orient, lines=self.json_lines, force_ascii=self.force_ascii)
        elif ext == ".jsonl":
            self.df.to_json(out_path, orient=self.json_orient, lines=self.json_lines, force_ascii=self.force_ascii)
        elif ext == ".html":
            self.df.to_html(out_path, index=self.index)
        elif ext == ".parquet":
            self.df.to_parquet(out_path, index=self.index)
        elif ext == ".feather":
            self.df.to_feather(out_path)
        elif ext == ".orc":
            raise ValueError(f"Saving to ORC is not supported natively by pandas.")
        elif ext == ".sas":
            raise ValueError(f"Saving to SAS format is not supported by pandas.")
        elif ext == ".stata":
            self.df.to_stata(out_path)
        elif ext == ".hdf":
            self.df.to_hdf(out_path, key='df', mode='w')
        elif ext == ".pkl":
            self.df.to_pickle(out_path)
        else:
            raise ValueError(f"Unsupported file format for saving: {ext}")

    def __call__(self, input_path: str, output_path: str) -> str:
        """
        Reads a file and saves it in a new format.

        Args:
            input_path (str): The path of the input file to read.
            output_path (str): The path of the output file to save.

        Returns:
            str: A success message indicating the file has been saved.
        """
        self._read_file(input_path)
        self._save_file(output_path)
        
        return f"File saved successfully at \"{output_path}\"."


