from typing import Optional
from tqdm import tqdm
import pandas as pd
import logging
import fire
import os

# Root 
logger_name = 'make_data.functions'
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

def renamefiles(input_dir: Optional[str] = "output") -> None:
    for file in os.listdir(input_dir):
        file_path: str = os.path.join(input_dir, file)
        os.rename(file_path, file_path.replace("국자기술자격증시험", "국가기술자격증시험"))

def concat_excel(filestartswith: Optional[str] = "국가기술자격증시험", input_dir: Optional[str] = "output") -> None:
    final_df = None  # 초기화
    for file in tqdm([file for file in os.listdir(input_dir) if file.startswith(filestartswith)]):
        file_path = os.path.join(input_dir, file)
        try:
            # Read Excel file into a DataFrame
            df = pd.read_excel(file_path)
            logger.info(f"Loaded {file} with shape {df.shape}")
        except Exception as e:
            logger.error(f"Error reading {file}: {e}")
            continue

        # Concatenate all the loaded data into one DataFrame
        if final_df is None:
            final_df = df.copy()  # Initialize the final DataFrame
        else:
            final_df = pd.concat([final_df, df], ignore_index=True)

    # Check if final_df is not None before saving
    if final_df is not None:
        # Save the concatenated DataFrame to a new Excel file
        output_file = os.path.join(input_dir, f"3. Domain.xlsx")
        try:
            final_df.to_excel(output_file, index=False)
            logger.info(f"Successfully saved concatenated DataFrame to {output_file}")
        except Exception as e:
            logger.error(f"Error saving the concatenated DataFrame: {e}")
    else:
        logger.warning("No valid Excel files were found or concatenated. No output file was created.")

if __name__ == "__main__":
    fire.Fire(concat_excel)

