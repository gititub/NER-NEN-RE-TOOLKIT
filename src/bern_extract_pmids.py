#python bern_extract_pmids.py list_of_pmids.txt output_file.tsv

import sys
import time
import json
import requests
import pandas as pd

def json_to_df(json_data):
    # Convert json_data to DataFrame and return
    pmid_list = []
    id_list = []
    is_neural_normalized_list = []
    prob_list = []
    mention_list = []
    obj_list = []
    begin_list = []
    end_list = []
    norm_list = []
    mut_type_list = []

    # Iterate over the JSON dictionaries and extract the information
    for item in json_data:
        if item['pmid'] is not None:
            pmid = item['pmid']
        else:
            pmid = item.get("pmid")
        annotations = item.get("annotations", [])
        for annotation in annotations:
            annotation_id = annotation["id"][0]
            is_neural_normalized = annotation["is_neural_normalized"]
            prob = annotation.get("prob")
            mention = annotation["mention"]
            mutation_type = annotation.get('mutationType')
            norm = annotation.get('normalizedName')
            obj = annotation["obj"]
            span = annotation.get("span", {})
            begin = span.get("begin")
            end = span.get("end")

            # Append the extracted information to the respective lists
            pmid_list.append(pmid)
            id_list.append(annotation_id)
            is_neural_normalized_list.append(is_neural_normalized)
            prob_list.append(prob)
            mention_list.append(mention)
            obj_list.append(obj)
            begin_list.append(begin)
            end_list.append(end)
            norm_list.append(norm)
            mut_type_list.append(mutation_type)

    # Create a DataFrame using the extracted information
    df = pd.DataFrame({
        "pmid": pmid_list,
        "id": id_list,
        "is_neural_normalized": is_neural_normalized_list,
        "prob": prob_list,
        "mention": mention_list,
        "normalized name": norm_list,
        "mutation type": mut_type_list,
        "obj": obj_list,
        "span_begin": begin_list,
        "span_end": end_list
    })

    return df


def process_pmid(pmid):
    print(f"Processing PMID {pmid} with BERN...")
    url = f"http://bern2.korea.ac.kr/pubmed/{pmid}"
    try:
        response = requests.get(url)

        if response.status_code == 200:
            json_data = response.json()
            df = json_to_df(json_data)
            return df
        else:
            print(f"Request for PMID {pmid} failed with status code:", response.status_code)
            return None
    except Exception as e:
        print(f"Error processing PMID {pmid}: {str(e)}")
        return None

def main():
    if len(sys.argv) != 3:
        print("Usage: python ann_pmids.py list_of_pmids.txt output_file")
        return

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, 'r') as f:
        pmids_total = [line.strip() for line in f]

    start_time = time.time()

    results = []

    for pmid in pmids_total:
        df = process_pmid(pmid)
        if df is not None:
            results.append(df)

    if results:
        bern = pd.concat(results)

        if output_file.endswith(".json"):
            bern.to_json(output_file, orient='records', lines=True)
        elif output_file.endswith(".tsv"):
            bern.to_csv(output_file, sep='\t', index=False)
        else:
            print("Invalid output file format. Please choose .json or .tsv.")

    end_time = time.time()
    total_time = end_time - start_time

    print(f"{len(pmids_total)} PMIDs annotated")
    print("Total time taken to extract annotations using BERN2:", total_time, "seconds")

if __name__ == "__main__":
    main()
