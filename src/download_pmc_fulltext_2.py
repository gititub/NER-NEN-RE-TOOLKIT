import os
import argparse
import time
import warnings
from bs4 import BeautifulSoup
import requests
import shutil
import uuid
<<<<<<< HEAD:src/download_pmc_fulltext_2.py
from requests_html import HTMLSession
from requests.exceptions import ConnectionError

=======
>>>>>>> cea8f23f47f9d63900117a22370c0f32c7ca3930:source/download_pmc_fulltext.py
warnings.filterwarnings("ignore")


def save_text_to_files(pmc_list, max_length, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    s = HTMLSession()
    headers = {'user-agent': 'Mozilla/5.0'}
    for pmc in pmc_list:
        pmc = pmc.strip()
        try:
            url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc}/"
            response = s.get(url, headers=headers)
            response.raise_for_status()
            print(f'Response status for PMC {pmc}: {response.status_code}')
            if response.status_code == 200:
<<<<<<< HEAD:src/download_pmc_fulltext_2.py
                soup = BeautifulSoup(response.content, 'html.parser')
                content = soup.get_text()
=======
                content = response.content.decode()
>>>>>>> cea8f23f47f9d63900117a22370c0f32c7ca3930:source/download_pmc_fulltext.py
                chunks = []
                while content:
                    last_period_index = content.rfind('.', 0, max_length)
                    if last_period_index == -1:
                        last_period_index = max_length
                    chunk = content[:last_period_index + 1]  # Include the last period in the chunk
                    content = content[last_period_index + 1:].strip()
                    chunks.append(chunk)

                for chunk_number, chunk in enumerate(chunks, start=1):
                    output_file_path = os.path.join(output_directory, f"{pmc}({chunk_number}).txt")
                    with open(output_file_path, 'w', encoding='utf-8') as output_file:
                        output_file.write(chunk)

        except Exception as e:
            print("Error occurred while processing PMC {}: {}".format(pmc, e))
            continue
            
    file_list = os.listdir(output_directory)
    num_subdirectories = len(file_list) // 120 + 1
    for i in range(num_subdirectories):
         subdirectory_name = f'subdirectory_{uuid.uuid4()}'
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

    print("Text extraction and saving completed.")

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("input_file", help="Path to the input list of pmcs")
parser.add_argument("output_directory", help="Path to the output directory")
args = parser.parse_args()

# Set input arguments
input_file = args.input_file
output_directory = args.output_directory

# Read PMCs from the input file
if input_file.startswith('PMC'):
    pmc_list = [num.strip() for num in input_file.split(',') if num.strip()]
else:
    with open(input_file, 'r') as f:
        pmc_list = [line.strip() for line in f]

start_time = time.time()
max_length = 4900

save_text_to_files(pmc_list, max_length, output_directory)

end_time = time.time()
total_time = end_time - start_time
print("Total time taken:", total_time, "seconds")
