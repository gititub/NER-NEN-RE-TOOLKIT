#python ptc_extract_pmc_query.py [query] [output_filename] [retmax]
#example: python ptc_extract_pmc_query.py biotin output_pmc2.json 30

import os
import requests
import json
import pandas as pd
import time
import argparse
from Bio import Entrez

email = "weliw001@hotmail.com"

def extract_pubtator_from_pmcs(pmcs, output):
    """Python function to extract Pubtator results from a list of PMCIDs.
    Returns results in biocjson format if output = "biocjson" and returns results
    in pandas DataFrame format if output = "df".
    """
    print("Extracting Pubtator results from PMCs...")
    list_of_pubtators = []
    error_pmc_ids = []
    error_sum = 0
    pmc_sum = 0

    for pmc in pmcs:
        print(f"Processing PMC: PMC{pmc}")
        url = "https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/biocjson?pmcids=PMC" + str(pmc)
        try:
            response = requests.get(url)
            response.raise_for_status()
            json_data = response.json()
            if not json_data.get('passages'):
                print(f"No Pubtator results found for PMC: PMC{pmc}")
                continue
        except requests.exceptions.RequestException as e:
            error_pmc_ids.append(pmc)
            error_sum += 1
        except ValueError as e:
            print("Error parsing JSON data:", e)
            print("URL:", url)
            print("Response:", response.content)
            error_sum += 1
        else:
            list_of_pubtators.append(json_data)
            pmc_sum += 1

    print(f"Total number of errors extracting Pubtator data from PMCs: {error_sum}")
    print(f"Total number of PMC articles annotated: {pmc_sum}")

    df_list = []

    for pubtator in list_of_pubtators:
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

        if pubtator['_id'].split('|')[0] is not None:
            PMID = pubtator['_id'].split('|')[0]
        else:
            PMID = pubtator['passages'][0]['infons'].get('article-id_pmid')

        if pubtator['_id'].split('|')[1] is not None:
            PMC = pubtator['_id'].split('|')[1]
        else:
            PMC = pubtator['passages'][0]['infons'].get('article-id_pmc')

        for d in pubtator['passages']:
            section_type = d['infons']['section_type']

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
        return list_of_pubtators
    elif output == 'df':
        if not df_list:
            print("No articles with annotations found.")
            return pd.DataFrame()
        else:
            merged_df = pd.concat(df_list, ignore_index=True)
            return merged_df
    else:
        print("Invalid output format. Please choose 'biocjson' or 'df'.")

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("query", help="PubMed query")
parser.add_argument("output_filename", help="Output filename")
parser.add_argument("retmax", type=int, help="Maximum number of PMIDs to retrieve")
parser.add_argument("--pub_date", help="Publication date (YYYY/MM/DD)")
args = parser.parse_args()

# Set input arguments
query = args.query
output_filename = args.output_filename
retmax = args.retmax
pub_date = args.pub_date

# Perform PMC search to get PMC IDs based on the query
Entrez.email = email
if pub_date:
    query += f" AND {pub_date}[Date - Publication]"
handle = Entrez.esearch(db="pmc", term=query, retmax=retmax)
record = Entrez.read(handle)
handle.close()

pmc_ids = record["IdList"]

start_time = time.time()

if output_filename.endswith(".json"):
    # Save the output_data to a file with output_filename
    output_data = extract_pubtator_from_pmcs(pmc_ids, 'biocjson')
    with open(output_filename, 'w') as output_file:
        json.dump(output_data, output_file, indent=2)
    print(f"Biocjson data saved to {output_filename}")
elif output_filename.endswith(".tsv"):
    # Save the merged DataFrame to a CSV file with output_filename
    merged_df = extract_pubtator_from_pmcs(pmc_ids, 'df')
    merged_df.to_csv(output_filename, sep='\t', index=False)
    print(f"DataFrame saved to {output_filename}")
else:
    print("Invalid output format. Please choose 'biocjson' or 'df'.")

end_time = time.time()
total_time = end_time - start_time

print("Total time taken to extract annotations with PTC:", total_time, "seconds")
print("Maximum number of PMCIDs retrieved:", retmax)
