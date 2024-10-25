from format_converter import FileFormatConverter
from quiz_generator import QuizGenerator, VisionQuizGenerator
from typing import List, Optional, Union
from tqdm import tqdm
import fire
import os

def quiz_gen(input_path: str = "src/2. Standard/한국물가정보_건설용어사전.xlsx",
         input_column: str = "해설",
         output_column: str = "단어",
         num_distractors: int = 4,
         template_path: str = "make_data/templates.yaml",
         yaml_key="standard_quize_gen", 
         change_keyword="STANDARD") -> None:
    # Create an instance of QuizGenerator
    generator = QuizGenerator(excel_path=input_path, foreign_word_column=input_column, korean_word_column=output_column)
    generator.config(yaml_path=template_path, yaml_key=yaml_key, change_keyword=change_keyword, num_distractors=num_distractors)
    # Save all quizzes to an Excel file
    generator.save_quizzes_to_excel(f"output/{input_path.split('/')[-1]}")

def vision_quiz_gen(input_dir: Optional[str] = "src/3. Domain",
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
         subject: str = "과목",
         yaml_path: Optional[str] = "templates.yaml", 
         sheet: Optional[Union[str, List[str]]] = "Sheet1",
         image_output_dir: Optional[str] = "output/img") -> None:
    for excelfile in tqdm([file for file in os.listdir(input_dir) if file.endswith(".xlsx")]):
        # Create an instance of QuizGenerator
        generator = VisionQuizGenerator(excel_path=os.path.join(input_dir, excelfile), question_num=question_num, question=question, image=image, query=query, answer=answer, explanation=explanation, 
                                  rate=rate, field=field, name=name, date=date, subject=subject)
        generator.config(yaml_path=yaml_path, sheet=sheet, image_output_dir=image_output_dir)
        # Save all quizzes to an Excel file
        generator.save_quizzes_to_excel(f"output/국가기술자격증시험_{excelfile}")

def data_convert(input_dir: str, output_dir: str, output_type: Optional[str] = "") -> None:
    file_converter = FileFormatConverter()
    for file in tqdm([file for file in os.listdir(input_dir) if '.' in file]):
        input_path: str = os.path.join(input_dir, file)
        output_path: str = os.path.join(output_dir, f"{os.path.splitext(file)[0]}.{output_type}" if output_type else f"{os.path.splitext(file)[0]}.{output_dir.split('/')[-1]}")

        file_converter(input_path, output_path)

def main(do: str, **kwargs) -> None:
    """
    Main function to execute quiz generation or data conversion based on the specified action.

    Args:
        do (str): Command specifying the action to perform:
            - "quiz" or "Q" or "gen" for general quiz generation.
            - "vision quiz" or "V" for vision quiz generation.
            - "convert" or "conv" or "C" for data conversion.
        **kwargs: Additional keyword arguments to pass to the functions.
    """
    if "quiz" in do or "Q" in do or "gen" in do:
        if "vision" in do or "V" in do:
            vision_quiz_gen(**kwargs)
        else:
            quiz_gen(**kwargs)

    elif "conv" in do or "C" in do:
        data_convert(**kwargs)

    else:
        raise ValueError(f"Unrecognized command: {do}")

if __name__ == "__main__":
    fire.Fire(main)