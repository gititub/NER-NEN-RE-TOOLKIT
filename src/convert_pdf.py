import os
import argparse
import time
import warnings
import shutil
from PyPDF2 import PdfReader
from tqdm import tqdm
warnings.filterwarnings("ignore")


def convert_pdf_to_text(pdf_file_path):
    pdf_reader = PdfReader(pdf_file_path)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text.strip()


def convert_directory_to_text(input_directory, output_directory, max_length):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    pdf_files = [file for file in os.listdir(input_directory) if file.endswith(".pdf")]
    file_number = 1

    for pdf_file in tqdm(pdf_files, desc="Converting PDFs"):
        pdf_file_path = os.path.join(input_directory, pdf_file)
        pdf_text = convert_pdf_to_text(pdf_file_path)

        while len(pdf_text) > max_length:
            last_period_index = pdf_text.rfind('.', 0, max_length)  # Find the last period within max_length
            if last_period_index == -1:  # If no period is found, split at max_length
                split_index = max_length
            else:
                split_index = last_period_index + 1  # Include the last period in the chunk

            split_text = pdf_text[:split_index]
            pdf_text = pdf_text[split_index:]

            output_file_path = os.path.join(output_directory, f"{pdf_file}({file_number}).txt")
            with open(output_file_path, "w") as output_file:
                output_file.write(split_text)
            file_number += 1

        if len(pdf_text) > 0:
            output_file_path = os.path.join(output_directory, f"{pdf_file}({file_number}).txt")
            with open(output_file_path, "w") as output_file:
                output_file.write(pdf_text)
            file_number += 1

    file_list = os.listdir(output_directory)
    num_subdirectories = len(file_list) // 120 + 1
    for i in range(num_subdirectories):
         subdirectory_name = f'subdirectory_{i+1}'
         subdirectory_path = os.path.join(output_directory, subdirectory_name)
         os.makedirs(subdirectory_path)
         start_index = i * 120
         end_index = min((i + 1) * 120, len(file_list))
         files_to_move = file_list[start_index:end_index]
         # Move the files to the subdirectory
         for file_name in files_to_move:
             source_path = os.path.join(output_directory, file_name)
             destination_path = os.path.join(subdirectory_path, file_name)
             shutil.move(source_path, destination_path)

    print(f'Subdirectory "{subdirectory_name}" created with {len(files_to_move)} files.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_directory", help="Path to the input directory containing PDF files")
    parser.add_argument("output_directory", help="Path to the output directory for plain text files")
    args = parser.parse_args()

    input_directory = args.input_directory
    output_directory = args.output_directory
    max_length = 4900

    start_time = time.time()

    convert_directory_to_text(input_directory, output_directory, max_length)

    end_time = time.time()
    total_time = end_time - start_time
    print("Total time taken:", total_time, "seconds")
