import requests
import pandas as pd
import time
import sys


def fetch_litvar_data(query_list):
    data_dict = {
        'Query': [],
        'rsid': [],
        'gene': [],
        'name': [],
        'hgvs': [],
        'pmids_count': [],
        'data_clinical_significance': []
    }

    start_time = time.time()
    queries_done = 0

    for query in query_list:
        url = f'https://www.ncbi.nlm.nih.gov/research/litvar2-api/variant/autocomplete/?query={query}'
        response = requests.get(url)
        data = response.json()

        if data:
            for result in data:
                data_dict['Query'].append(query)
                data_dict['rsid'].append(result.get('rsid', 'N/A'))
                data_dict['gene'].append(result.get('gene', 'N/A'))
                data_dict['name'].append(result.get('name', 'N/A'))
                data_dict['hgvs'].append(result.get('hgvs', 'N/A'))
                data_dict['pmids_count'].append(result.get('pmids_count', 'N/A'))
                data_dict['data_clinical_significance'].append(result.get('data_clinical_significance', 'N/A'))

        queries_done += 1

    total_time = time.time() - start_time

    litvar = pd.DataFrame(data_dict)
    return litvar, queries_done, total_time


def fetch_data(row):
    ids = row['pmid']
    genvars = row['synvar']
    url = f"https://variomes.text-analytics.ch/api/fetchDoc?ids={ids}&genvars={genvars}"
    response = requests.get(url)
    if response.ok:
        data = response.json()
        return data
    else:
        return None


def extract_variants_syn(result):
    if result is None:
        return None
    else:
        variants_data = result.get('normalized_query', {}).get('variants', [])
        return variants_data[0].get('terms')


def extract_genes(result):
    if result is None:
        return None
    else:
        gene_data = result.get('publications', [])[0].get('details', {}).get('facet_details', {}).get('genes', [])
        gene_info = [f"{gene.get('preferred_term')}({gene.get('id')})" for gene in gene_data]
        if gene_data:
            return gene_info
        else:
            return None


def extract_drugs(result):
    if result is None:
        return None
    else:
        drug_data = result.get('publications', [])[0].get('details', {}).get('facet_details', {}).get('drugs', [])
        drug_info = [f"{drug.get('preferred_term')}({drug.get('id')})" for drug in drug_data]
        if drug_data:
            return drug_info
        else:
            return None

def main():
    if len(sys.argv) != 3:
        print("Usage: python normalize.py file.tsv output_dir")
        return

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    start_time = time.time()

    file = pd.read_csv(input_file, sep='\t')
    file['litvar'] = file['gene'] + " "+ file['HGVS']
    file['synvar'] = file['gene'] + "("+ file['HGVS']+")"

    # Generate litvar data
    litvar, queries_done, litvar_total_time = fetch_litvar_data(file['litvar'].drop_duplicates().tolist())
    litvar.to_csv(f'{output_dir}/litvar_result.tsv', sep='\t', index=False)
    print(f"Total time for {queries_done} queries to LitVar API: {litvar_total_time:.2f} seconds")

    # Fetch and process data
    file['result'] = file.apply(fetch_data, axis=1)
    file['genes'] = file['result'].apply(extract_genes)
    file['variants_syn'] = file['result'].apply(extract_variants_syn)
    file['drugs'] = file['result'].apply(extract_drugs)

    end_time = time.time()
    total_time = end_time - start_time - litvar_total_time
    print(f"Total time taken for SynVar processing: {total_time:.2f} seconds")

    file.to_csv(f'{output_dir}/synvar_results.tsv', sep='\t', index=False)


if __name__ == "__main__":
    main()
