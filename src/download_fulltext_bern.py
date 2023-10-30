#python download_fulltext_bern.py [filepath_pmcs] [output_dir]
#example: python download_fulltext_bern.py pmcs.txt bern_ft

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import shutil
import argparse
import time
import warnings
warnings.filterwarnings("ignore")


def save_text_to_files(pmc_list, max_length, output_directory):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for pmc in pmc_list:
        pmc = pmc.strip()
        url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc}/"
        driver.get(url)
        driver.implicitly_wait(10)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        paragraphs = soup.find_all("div", class_="tsec sec")
        filtered_paragraphs = []

        for paragraph in paragraphs:
            if not any(tag in paragraph.get("id", []) for tag in ["ref-list", "glossary",
                                                                  "fn-group", "ack"]):
                filtered_paragraphs.append(paragraph)

        file_number = 1

        for paragraph in filtered_paragraphs:
            paragraph_text = paragraph.get_text().strip()
            while len(paragraph_text) > max_length:
                last_period_index = paragraph_text.rfind('.', 0, max_length)
                if last_period_index == -1:
                    last_period_index = max_length

                split_text = paragraph_text[:last_period_index + 1]  # Include the last period in the chunk
                paragraph_text = paragraph_text[last_period_index + 1:].strip()

                output_file_path = os.path.join(output_directory, f"{pmc}({file_number}).txt")
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(split_text)
                    file_number += 1
            if len(paragraph_text) > 0:
                output_file_path = os.path.join(output_directory, f"{pmc}({file_number}).txt")
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(paragraph_text)
                file_number += 1

    driver.quit()
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

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("input_file", help="Path to the input list of pmcs")
parser.add_argument("output_directory", help="Path to the output directory")
args = parser.parse_args()

# Set input arguments
input_file = args.input_file
output_directory = args.output_directory

# Read PMIDs from the input file
with open(input_file, 'r') as f:
    pmc_list = [line.strip() for line in f]

start_time = time.time()
max_length = 4900

save_text_to_files(pmc_list, max_length, output_directory)

end_time = time.time()
total_time = end_time - start_time
print("Total time taken:", total_time, "seconds")
