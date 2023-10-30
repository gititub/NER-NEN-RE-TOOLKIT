#python ptc_extract_pmids.py [file_path_pmids] [output_filename]
#example: python ptc_extract_ann.py pmids.tsv output_df.tsv

import os
import requests
import json
import pandas as pd
import time
import argparse

def extract_pubtator(pmids, output):
    """Python function that, given a list of pmids, returns Pubtator results
    in biocjson format if output = "biocjson" and returns Pubtator results
    in pandas DataFrame format if output = "df".
    """
    print("Extracting PubTator results from PMIDs...")
    list_of_abstracts_pubtator = []
    error_count = 0 

    for pmid in pmids:
        print(f"Processing PMID: {pmid}")
        url = "https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/biocjson?pmids=" + str(pmid)
        try:
            response = requests.get(url)
            response.raise_for_status()
            json_data = response.json()
            if not json_data.get('passages'):
                print(f"No Pubtator results found for PMID: {pmid}")
                continue
        except requests.exceptions.RequestException as e:
            print(f"Error for {pmid}: {e}")
            error_count += 1
        except ValueError as e:
            print("Error parsing JSON data:", e)
            print("URL:", url)
            print("Response:", response.content)
            error_count += 1
        else:
            list_of_abstracts_pubtator.append(json_data)

    df_list = []

    for pubtator in list_of_abstracts_pubtator:
        PMID_list = []
        PMC_list = []
        section_type_list = []
        sentences_list = []
        entity_type_list = []
        offset_list = []
        end_list = []
        identifier_list = []
        string_text_list = []
        subtype_list = []
        tmvar_list = []
        identifiers_list = []
        homologene_list = []

        PMID = pubtator['id']
        PMC = pubtator['passages'][0]['infons'].get('article-id_pmc')

        for d in pubtator['passages']:
            section_type = d['infons']['type']

            for annotation in d['annotations']:
                entity_type = annotation['infons']['type']
                subtype = annotation['infons'].get('subtype')
                tmVar = annotation['infons'].get('originalIdentifier')
                identifiers = annotation['infons'].get('identifiers')
                offset = annotation['locations'][0]['offset']
                end = offset + annotation['locations'][0]['length']
                identifier = annotation['infons']['identifier']
                string_text = annotation['text']
                ncbi_homologene = annotation['infons'].get('ncbi_homologene')

                PMID_list.append(PMID)
                PMC_list.append(PMC)
                section_type_list.append(section_type)
                entity_type_list.append(entity_type)
                offset_list.append(offset)
                end_list.append(end)
                identifier_list.append(identifier)
                identifiers_list.append(identifiers)
                string_text_list.append(string_text)
                subtype_list.append(subtype)
                tmvar_list.append(tmVar)
                homologene_list.append(ncbi_homologene)

        df = pd.DataFrame({
            'PMID': PMID_list,
            'PMC': PMC_list,
            'section_type': section_type_list,
            'string_text': string_text_list,
            'offset': offset_list,
            'end': end_list,
            'entity_type': entity_type_list,
            'entity_subtype': subtype_list,
            'ncbi_homologene': homologene_list,
            'tmVar': tmvar_list,
            'identifiers_list': identifiers_list,
            'identifier': identifier_list
        })

        df = df[df['identifier'].notna()]
        df_list.append(df)

    if output == 'biocjson':
        return list_of_abstracts_pubtator, error_count
    elif output == 'df':
        if not df_list:
            print("No abstracts with annotations found.")
            return pd.DataFrame(), error_count
        else:
            merged_df = pd.concat(df_list, ignore_index=True)
            return merged_df, error_count
    else:
        print("Invalid output format. Please choose 'biocjson' or 'df'.")
        return None, error_count

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("input_file", help="Path to the input file containing PMIDs")
parser.add_argument("output_filename", help="Output filename")
args = parser.parse_args()

# Set input arguments
input_file = args.input_file
output_filename = args.output_filename

# Read PMIDs from the input file
with open(input_file, 'r') as f:
    pmids = [line.strip() for line in f]

start_time = time.time()

if output_filename.endswith(".json"):
    output_data, error_count = extract_pubtator(pmids,'biocjson')
    # Save the output_data to a file with output_filename
    with open(output_filename, 'w') as output_file:
        json.dump(output_data, output_file, indent=2)
    print(f"Biocjson data saved to {output_filename}")
elif output_filename.endswith(".tsv"):
    # Extract PubTator data once and store in merged_df
    merged_df, error_count = extract_pubtator(pmids, 'df')
    # Save the merged DataFrame to a CSV file with output_filename
    merged_df.to_csv(output_filename, sep='\t', index=False)
    print(f"DataFrame saved to {output_filename}")
else:
    print("Invalid output format. Please choose 'biocjson' or 'df'.")

end_time = time.time()
total_time = end_time - start_time

print("Total time taken to extract annotations with PTC:", total_time, "seconds")
print("Total PMIDs annotated:", len(pmids))
print("Total errors encountered:", error_count)
