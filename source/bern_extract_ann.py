# python bern_extract_ann.py [input_dir] [output_dir] [json/df]

import os
import json
import requests
import pandas as pd
import argparse
import time
import re
from concurrent.futures import ThreadPoolExecutor

def process_file(file_path):
    results = []
    
    with open(file_path, 'r') as file:
        print(f"Processing file {file_path}")
        file_contents = file.read()
        text = file_contents.strip()
        url = "http://bern2.korea.ac.kr/plain"

        try:
            result = requests.post(url, json={'text': text}).json()
            pattern = r'\/([^\/]+)\.txt$'
            match = re.search(pattern, file_path)
            pmid = match.group(1)
            result['pmid'] = pmid
            results.append(result)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for file: {file_path}")
            print("Error message:", e)

    return results

def extract_annotations(subdirectory_path):
    file_paths = [os.path.join(subdirectory_path, filename) for filename in os.listdir(subdirectory_path) if filename.endswith(".txt")]
    try:
        with ThreadPoolExecutor() as pool:
            results = pool.map(process_file, file_paths)
    except KeyboardInterrupt:
        print("Interrupted. Stopping worker processes...")
        pool.shutdown(wait=False)
        print("Worker processes terminated.")
        raise

    extracted_data = []
    for result_list in results:
        for result in result_list:
            if result is None:
                continue
            annotations = result.get('annotations', [])            
            for annotation in annotations:
                pmid = result.get('pmid')
                annotation_id = annotation.get('id', [])
                is_neural_normalized = annotation.get('is_neural_normalized')
                prob = annotation.get('prob')
                mention = annotation.get('mention')
                normalized_name = annotation.get('normalizedName')
                mutation_type = annotation.get('mutationType')
                obj = annotation.get('obj')
                span_begin = annotation['span']['begin']
                span_end = annotation['span']['end']

                extracted_item = {
                    'PMC': pmid,
                    'id': annotation_id,
                    'is_neural_normalized': is_neural_normalized,
                    'prob': prob,
                    'mention': mention,
                    'normalized_name': normalized_name,
                    'mutation_type': mutation_type,
                    'obj': obj,
                    'span_begin': span_begin,
                    'span_end': span_end
                }

                extracted_data.append(extracted_item)

    return extracted_data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="Path to the input directory")
    parser.add_argument("output_dir", help="Path to the output directory")
    parser.add_argument("output_format", choices=["json", "df"], help="Output format: 'json' or 'df'")
    args = parser.parse_args()

    input_directory = args.input_dir
    output_directory = args.output_dir
    output_format = args.output_format
    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    start_time = time.time()

    with ThreadPoolExecutor() as executor:
        subdirectories = [subdir for subdir in os.listdir(input_directory) if os.path.isdir(os.path.join(input_directory, subdir))]
        results = executor.map(extract_annotations, [os.path.join(input_directory, subdir) for subdir in subdirectories])

    for subdir, result in zip(subdirectories, results):
        if output_format == "json":
            output_filename = f"{subdir}.ann.json"
            output_file_path = os.path.join(output_directory, output_filename)

            with open(output_file_path, 'w') as output_file:
                json.dump(result, output_file)
        elif output_format == "df":
            df = pd.DataFrame(result)
            df['PMC'] = df['PMC'].str.replace(r'\(.*\)', '', regex=True)
            df['dbSNP'] = df['normalized_name'].str.extract(r'(?:rs|RS#:)(\d+)', expand=False)
            df['dbSNP'] = 'rs' + df['dbSNP']
            
            output_filename = f"{subdir}.ann.tsv"
            output_file_path = os.path.join(output_directory, output_filename)

            df.to_csv(output_file_path, sep='\t', index=False)

    end_time = time.time()
    total_time = end_time - start_time

    print("Total time taken to extract annotations with BERN2:", total_time, "seconds")

if __name__ == "__main__":
    main()

