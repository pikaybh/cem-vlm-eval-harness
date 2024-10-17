from typing import List, Tuple, Dict, ClassVar, Optional, Union
from datetime import datetime
import pandas as pd
import logging
import base64
import random
import yaml
import os
import re

# Root 
logger_name = 'quiz_generator'
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


class QuizGenerator:
    """A class to generate quizzes from an Excel file using a YAML template.

    This class reads loanword-Korean word pairs from an Excel file and generates multiple-choice
    quizzes based on a template defined in a YAML file. The quizzes can be saved as an Excel file
    for further use. This class demonstrates the use of both class methods and instance methods.
    
    Attributes:
        _template_path (ClassVar[str]): Path to the YAML file containing the quiz template.
        _template_key (ClassVar[str]): Key in the YAML file to retrieve the quiz template.
        _change_keyword (ClassVar[Union[str, List[str]]]): Placeholder(s) to be replaced in the template.
    """

    _template_path: ClassVar[str] = "templates.yaml"
    _template_key: ClassVar[str] = "quiz_gen"
    _change_keyword: ClassVar[Union[str, List[str]]] = "LOANWORD"
    _sheet: ClassVar[Union[str, List[str]]] = "Sheet1"
    _num_distractors: ClassVar[int] = 3
    _output_dir: ClassVar[str] = ""

    def __init__(self, 
                 excel_path: str,
                 foreign_word_column: str = "외래어", 
                 korean_word_column: str = "우리말") -> None:
        """Initializes the QuizGenerator instance with configuration settings.

        Args:
            excel_path (str): Path to the Excel file containing loanword-Korean word pairs.
            foreign_word_column (str): Column name for loanwords. Default is '외래어'.
            korean_word_column (str): Column name for Korean words. Default is '우리말'.
        """
        self.excel_path = excel_path
        self.foreign_word_column = foreign_word_column
        self.korean_word_column = korean_word_column
        self._data = self.load_data()

    @property
    def data(self) -> List[Tuple[str, str]]:
        """Property to access the loaded data."""
        return self._data

    @data.setter
    def data(self, value: List[Tuple[str, str]]) -> None:
        """Setter for the data property."""
        self._data = value


    @classmethod
    def config(cls, 
               yaml_path: Optional[str] = "templates.yaml", 
               yaml_key: Optional[str] = "quiz_gen",
               change_keyword: Optional[Union[str, List[str]]] = "LOANWORD",
               sheet: Optional[Union[str, List[str]]] = "Sheet1",
               num_distractors: Optional[int] = 3,
               output_dir: Optional[str] = None) -> None:
        """Configures the class-level settings for the quiz generator.

        This method allows the user to set paths for the YAML template, configure the key used
        to retrieve templates, and specify placeholders for loanwords.

        Args:
            yaml_path (Optional[str]): Path to the YAML file containing the quiz template.
            yaml_key (Optional[str]): Key in the YAML file to retrieve the quiz template.
            change_keyword (Optional[Union[str, List[str]]]): Placeholder(s) to be replaced in the template.
            sheet (Optional[Union[str, List[str]]]): Sheet name(s) of the Excel file to load.
        """
        cls._template_path = yaml_path if yaml_path else cls._template_path
        cls._template_key = yaml_key if yaml_key else cls._template_key
        cls._change_keyword = change_keyword if change_keyword else cls._change_keyword
        cls._sheet = sheet if sheet else cls._sheet
        cls._num_distractors = num_distractors if num_distractors else cls._num_distractors
        cls._output_dir = output_dir if output_dir else cls._output_dir

    def load_data(self) -> List[Tuple[str, str]]:
        """Loads the word pairs from the configured Excel file.

        This method reads the loanword-Korean word pairs from the specified Excel file
        and stores them as a list of tuples, where each tuple contains a loanword and its
        corresponding Korean word.

        Returns:
            List[Tuple[str, str]]: A list of tuples representing loanword-Korean word pairs.
        """
        df = pd.read_excel(self.excel_path, sheet_name=self._sheet)
        return list(zip(df[self.foreign_word_column], df[self.korean_word_column]))

    @classmethod
    def load_template(cls) -> Dict[str, str]:
        """Loads the quiz template from the YAML file.

        This method reads the YAML file and extracts the quiz template using the configured key.

        Returns:
            Dict[str, str]: A dictionary containing the quiz template with placeholders.
        
        Example:
            {
                "question": "LOANWORD의 순화어로 알맞은 것은?"
            }
        """
        with open(cls._template_path, 'r', encoding='utf-8') as f:
            template = yaml.safe_load(f)
        return template[cls._template_key]

    @classmethod
    def generate_quiz(cls, loanword: str, correct_answer: str, all_data: List[Tuple[str, str]]) -> Dict[str, object]:
        """Generates a single quiz based on a loanword and its correct Korean equivalent.

        Args:
            loanword (str): The loanword to be included in the quiz question.
            correct_answer (str): The correct Korean word (answer) for the loanword.

        Returns:
            Dict[str, object]: A dictionary containing the quiz question, options, and answer.

        Example:
            {
                "question": "가꾸목의 순화어로 알맞은 것은?",
                "options": {
                    "text": ["각목", "철판", "수도꼭지", "토관"],
                    "label": ["A", "B", "C", "D"]
                },
                "answer": {
                    "text": "각목",
                    "key": "A"
                }
            }
        """
        distractors = cls._get_distractors(all_data, correct_answer, cls._num_distractors)
        options = distractors + [correct_answer]
        random.shuffle(options)

        labels = [chr(65 + i) for i in range(len(options))]
        labeled_options = dict(zip(labels, options))

        correct_label = [label for label, option in labeled_options.items() if option == correct_answer][0]
        question = cls.load_template()['question'].replace(str(cls._change_keyword), str(loanword))

        return {
            "question": question,
            "options": {
                "text": options,
                "label": labels
            },
            "answer": {
                "text": correct_answer,
                "key": correct_label
            }
        }

    @staticmethod
    def _get_distractors(data: List[Tuple[str, str]], correct_answer: str, num_distractors: int) -> List[str]:
        """Selects random incorrect Korean words as distractors for a quiz.

        Args:
            data (List[Tuple[str, str]]): List of loanword-Korean word pairs.
            correct_answer (str): The correct answer to exclude from the distractors.
            num_distractors (int): The number of distractors to generate.

        Returns:
            List[str]: A list of incorrect Korean words.
        """
        all_korean_words = [pair[1] for pair in data if pair[1] != correct_answer]
        return random.sample(all_korean_words, num_distractors)

    def generate_all_quizzes(self) -> List[Dict[str, object]]:
        """Generates quizzes for all word pairs in the Excel file.

        This method iterates over all rows in the Excel file and generates a quiz for
        each loanword-Korean word pair.

        Returns:
            List[Dict[str, object]]: A list of dictionaries, each representing a quiz.
        """
        return [self.generate_quiz(loanword, answer, self.data) for loanword, answer in self.data]

    def save_quizzes_to_excel(self, output_path: str) -> None:
        """Saves all generated quizzes to an Excel file.

        Args:
            output_path (str): The path where the Excel file will be saved.

        This method converts the generated quizzes into a DataFrame and saves it
        as an Excel file at the specified location.

        Example Excel Structure:
            | Question                  | Option A | Option B | Option C | Option D | Answer | Answer Key |
            |---------------------------|----------|----------|----------|----------|--------|------------|
            | 가꾸목의 순화어로 알맞은 것은? | 각목     | 철판     | 수도꼭지 | 토관     | 각목   | A          |
        """
        output_path = os.path.join(self._output_dir, output_path) if self._output_dir else output_path
        quizzes = self.generate_all_quizzes()
        rows = [
            {
                "Question": quiz["question"],
                "Answer": quiz["answer"]["text"],
                "Answer Key": quiz["answer"]["key"],
                **{chr(65 + idx): option for idx, option in enumerate(quiz["options"]["text"])}
            }
            for quiz in quizzes
        ]

        df = pd.DataFrame(rows)
        df.to_excel(output_path, index=False)
        logger.info(f"Quizzes saved to {output_path}")



class VisionQuizGenerator(QuizGenerator):
    def __init__(self, 
                 excel_path: str, 
                 question_num: str = "문제번호",
                 question: str = "문제",
                 image: str = "그림",
                 query: str = "문항",
                 answer: str = "정답", 
                 explanation: str = "문제해설",
                 rate: str = "정답률",
                 field: str = "CBT",
                 name: str = "시험",
                 date: str = "출제일자",
                 subject: str = "과목") -> None:
        """
        Initializes the VisionQuizGenerator instance with configuration settings.

        This method extends the initialization of the `QuizGenerator` class by adding additional 
        columns for vision-based quizzes, such as images, explanations, and quiz-related metadata.

        Args:
            excel_path (str): The path to the Excel file containing quiz data.
            question (str): The column name for quiz questions. Default is "문제".
            image (str): The column name for images. Default is "그림".
            query (str): The column name for query statements. Default is "문항".
            answer (str): The column name for answers. Default is "정답".
            explanation (str): The column name for explanations. Default is "문제해설".
            rate (str): The column name for answer rates. Default is "정답률".
            field (str): The column name for field. Default is "CBT".
            name (str): The column name for the quiz name. Default is "시험".
            date (str): The column name for the quiz date. Default is "출제일자".
            subject (str): The column name for the quiz subject. Default is "과목".
        """
        self.num_column = question_num
        self.question_column = question
        self.query_column = query
        self.image_column = image
        self.answer_column = answer
        self.explanation_column = explanation
        self.rate_column = rate
        self.field_column = field
        self.name_column = name
        self.date_column = date
        self.subject_column = subject
        super().__init__(excel_path)

    @property
    def data(self) -> List[Tuple[str, str, str, str, str, str, str, str, str, str, str]]:
        """Property to access the loaded data."""
        return self._data

    @data.setter
    def data(self, value: List[Tuple[str, str, str, str, str, str, str, str, str, str, str]]) -> None:
        """Setter for the data property."""
        self._data = value

    @classmethod
    def config(cls, 
               yaml_path: Optional[str] = "templates.yaml", 
               sheet: Optional[Union[str, List[str]]] = "Sheet1",
               output_dir: Optional[str] = None,
               image_output_dir: Optional[str] = "img") -> None:
        """
        Configures the class-level settings for the quiz generator.

        This method allows the user to set the path for the YAML template, configure the Excel sheet 
        to be loaded, and optionally specify the output directory for saving generated quizzes.

        Args:
            yaml_path (Optional[str]): The path to the YAML file containing the quiz template. Defaults to "templates.yaml".
            sheet (Optional[Union[str, List[str]]]): The name(s) of the Excel sheet(s) to load. Defaults to "Sheet1".
            output_dir (Optional[str]): The directory where output files will be saved. If None, the current working directory is used.
        
        Returns:
            None
        """
        super().config(yaml_path=yaml_path, sheet=sheet, output_dir=output_dir)
        cls._image_dir = image_output_dir

    def load_data(self) -> List[Tuple[str, str, str, str, str, str, str, str, str, str, str]]:
        """
        Loads the word pairs from the configured Excel file.

        This method reads the quiz data from the specified Excel file and returns
        them as a list of tuples, where each tuple contains values for the specified columns.

        Returns:
            List[Tuple[str, str, str, str, str, str, str, str, str, str]]: A list of tuples 
            representing the quiz data, including questions, images, answers, and explanations.
        """
        df = pd.read_excel(self.excel_path, sheet_name=self._sheet)
        return list(zip(df[self.num_column],
                        df[self.question_column], 
                        df[self.query_column], 
                        df[self.image_column], 
                        df[self.answer_column], 
                        df[self.explanation_column], 
                        df[self.rate_column], 
                        df[self.field_column], 
                        df[self.name_column], 
                        df[self.date_column], 
                        df[self.subject_column]))

    @classmethod
    def generate_quiz(cls, 
                    number: float,
                    question: str, 
                    queries: str, 
                    image: Optional[bytes], 
                    correct_answer: str, 
                    explanation: Optional[Union[str, float]],  # Allow both str and float types
                    rate: str, 
                    field: str, 
                    name: str, 
                    date: str, 
                    subject: str) -> Optional[Dict[str, object]]:
        """
        Generates a single quiz entry, including the question, options, answer, and additional metadata.

        Args:
            number (float): The quiz number, used for ordering or identification.
            question (str): The quiz question text.
            queries (str): The query string containing multiple options.
            image (Optional[bytes]): Base64-encoded image data.
            correct_answer (str): The correct answer text.
            explanation (Optional[Union[str, float]]): Explanation or commentary for the question. Can be None or float.
            rate (str): The accuracy rate of the question in percentage format.
            field (str): The field or category the question belongs to.
            name (str): The name of the test or quiz.
            date (str): The date when the quiz was created.
            subject (str): The subject or topic of the quiz.

        Returns:
            Optional[Dict[str, object]]: A dictionary containing all quiz information if no error occurs.
            Returns None if an exception occurs.
        """
        correct_answer = correct_answer.replace("1. ", "").replace("2. ", "").replace("3. ", "").replace("4. ", "").replace("[포인트 모으기 및 사용법]", "").strip().lower()
        options = [option.strip().lower() for option in cls._split_queries(queries)]

        labels = [chr(65 + i) for i in range(len(options))]
        labeled_options = dict(zip(labels, options))

        try:
            correct_label = [label for label, option in labeled_options.items() if option == correct_answer][0]
        except IndexError:
            logger.warning(f"[{field}-{name}-{date}-{number}] Correct answer '{correct_answer}' not found in options: {options}. Skipping this quiz.")
            return None

        # Handle image decoding
        decoded_image = ""
        if image and isinstance(image, (str, bytes)):
            decoded_image = cls._decode_img(image, cls._image_dir, field, name, date, number)

        # Ensure explanation is a string, otherwise set it to an empty string
        if not isinstance(explanation, str):
            explanation = ""

        return {
            "question": question,
            "image": decoded_image,
            "options": {
                "text": options,
                "label": labels
            },
            "answer": {
                "text": correct_answer,
                "key": correct_label
            },
            "explanation": explanation.replace("<문제 해설>", "").strip() if "<문제 해설>" in explanation else explanation,
            "rate": cls._percent2float(rate),
            "field": field, 
            "name": name, 
            "date": cls._convert_time(date), 
            "subject": subject,
            "vision": int(bool(decoded_image))
        }

    @staticmethod
    def _decode_img(img_byte: bytes, output_dir: str, field: str, name: str, date: str, number: float) -> str:
        """
        Decodes a base64-encoded image string and saves it to a directory.

        Args:
            img_byte (Union[str, bytes]): Base64-encoded image string.
            output_dir (str): The directory where the image will be saved.
            field (str): The field name to be used in the file name.
            name (str): The name to be used in the file name.
            date (str): The date to be used in the file name, formatted as YYYYMMDD.
            number (float): A number to be included in the file name, zero-padded to 3 digits.

        Returns:
            str: The path to the saved image file. If img_byte is falsy, returns img_byte as is.
        """
        if not img_byte:
            return img_byte

        # Ensure Base64 string has correct padding
        if isinstance(img_byte, str):
            # If img_byte is a string, calculate the missing padding and add it
            missing_padding = len(img_byte) % 4
            if missing_padding:
                img_byte += '=' * (4 - missing_padding)
            img_byte = img_byte.encode('utf-8')  # Convert string to bytes for decoding
        elif isinstance(img_byte, bytes):
            # If img_byte is bytes, calculate the missing padding and add it
            missing_padding = len(img_byte) % 4
            if missing_padding:
                img_byte += b'=' * (4 - missing_padding)

        # Ensure the directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Create file path with padded number
        image_path = os.path.join(output_dir, f"{field}-{name}-{date}-{str(int(number)).zfill(3)}.png")

        # Decode base64 and save as image
        with open(image_path, "wb") as img_file:
            img_file.write(base64.b64decode(img_byte))

        return image_path

    @staticmethod
    def _split_queries(queries: str) -> List[str]:
        """
        Splits the queries string into individual options.

        Args:
            queries (str): The string containing quiz options, separated by numbers (e.g., "1. option1\n2. option2").

        Returns:
            List[str]: A list of stripped quiz options.
        """
        TARGET = "해설이 아직 작성되지 않았습니다.해설을 알고 계시다면 오른쪽 해설추가 기능을 이용하여 해설을 작성하여 다른분들과 함께 해설을 나누었으면 합니다.로그인 후 오류 신고 및 해설 작성 하시면 포인트가 제공됩니다.[포인트 모으기 및 사용법]"
        return [line.strip() for line in re.split(r'\d+\.\n', queries.replace(TARGET, "")) if line.strip()]

    @staticmethod
    def _convert_time(date: str) -> str:
        """
        Converts a Korean formatted date string (e.g., "2022년04월24일") to "YYYY-MM-DD" format.

        Args:
            date (str): A string containing a date in the format "YYYY년MM월DD일".

        Returns:
            str: A string representing the date in the format "YYYY-MM-DD".
        """
        # 한글 제거하고 날짜 객체로 변환
        date_obj = datetime.strptime(date, "%Y년%m월%d일")

        # 원하는 형식으로 변환
        return date_obj.strftime("%Y-%m-%d")

    @staticmethod
    def _percent2float(percent: str) -> float:
        """
        Converts a percentage string to a float value. If no valid percentage is found, returns 0.0.

        Args:
            percent (str): A string containing a percentage (e.g., "82%").

        Returns:
            float: The equivalent float value of the percentage (e.g., "82%" -> 0.82).
        """
        match = re.search(r'\d+', percent)
        if match:
            return float(match.group()) / 100
        else:
            # If no percentage is found, return 0.0 or handle it accordingly
            logger.warning(f"No valid percentage found in '{percent}', defaulting to 0.0.")
            return 0.0

    def generate_all_quizzes(self) -> List[Dict[str, object]]:
        """
        Generates quizzes for all word pairs in the Excel file.

        This method iterates over all rows in the Excel file and generates a quiz for each entry.
        Skips entries where a quiz cannot be generated (returns None).

        Returns:
            List[Dict[str, object]]: A list of dictionaries, each representing a quiz.
        """
        return [quiz for quiz in (self.generate_quiz(*entry) for entry in self.data) if quiz is not None]

    def save_quizzes_to_excel(self, output_path: str) -> None:
        """
        Saves all generated quizzes to an Excel file.

        This method collects all generated quizzes, converts them into a structured DataFrame, 
        and saves them as an Excel file at the specified location.

        Args:
            output_path (str): The path where the Excel file will be saved.

        The structure of the output Excel file is as follows:
            | Question                  | Option A | Option B | Option C | Option D | Answer | Answer Key |
            |---------------------------|----------|----------|----------|----------|--------|------------|
            | 가꾸목의 순화어로 알맞은 것은? | 각목     | 철판     | 수도꼭지 | 토관     | 각목   | A          |

        The columns included in the Excel sheet are:
            - "Question": The quiz question.
            - "Figure": The image associated with the quiz.
            - "Explanation": The explanation or commentary for the question.
            - "Human Accuracy": The accuracy rate in percentage form.
            - "Field": The field or category of the quiz.
            - "Test": The test or quiz name.
            - "Date": The date of the quiz.
            - "Answer": The correct answer text.
            - "Answer Key": The correct answer label (e.g., "A").

        Example:
            save_quizzes_to_excel("quizzes.xlsx")
        """
        output_path = os.path.join(self._output_dir, output_path) if self._output_dir else output_path
        quizzes = self.generate_all_quizzes()
        rows = [
            {
                "Vision Encoder": quiz["vision"],
                "Question": quiz["question"],
                "Figure": quiz["image"],
                "Explanation": quiz["explanation"],
                "Human Accuracy": quiz["rate"],
                "Field": quiz["field"],
                "Test": quiz["name"],
                "Date": quiz["date"],
                "Answer": quiz["answer"]["text"],
                "Answer Key": quiz["answer"]["key"],
                **{chr(65 + idx): option for idx, option in enumerate(quiz["options"]["text"])}
            }
            for quiz in quizzes
        ]

        df = pd.DataFrame(rows)
        df.to_excel(output_path, index=False)
        logger.info(f"Quizzes saved to {output_path}")