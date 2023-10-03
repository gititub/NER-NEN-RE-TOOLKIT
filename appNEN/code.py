import requests
import json
import pandas as pd
from bs4 import BeautifulSoup


def get_gene_info_by_gene_number(gene_numbers):
    data = []
    number_list = [num.strip() for num in gene_numbers.split(',') if num.strip()]
    for number in number_list:
        url = f"https://www.ncbi.nlm.nih.gov/gene/{number}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        word_element = soup.find('dd', class_='noline')
        word = word_element.contents[0] if word_element else "Not Found"
        sp_element = soup.find('dd', class_='tax')
        sp = sp_element.find('a').contents[0] if sp_element else "Not Found"
        data.append([number, word, sp, url])

    df = pd.DataFrame(data, columns=['gene', 'gene_name', 'sp', 'url'])
    df_cleaned = df.dropna(axis=1, how='all')
    return df_cleaned


def get_gene_info_by_gene_name(gene, species=None):
    data = []

    if species is None:
        url = f"https://www.ncbi.nlm.nih.gov/gene/?term={gene}"
    else:
        sp1, sp2 = species.split(' ')
        url = f"https://www.ncbi.nlm.nih.gov/gene/?term={sp1}+{sp2}+{gene}"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    gene_elements = soup.find_all('td', class_='gene-name-id')
    for gene_element in gene_elements:
        gene_name = gene_element.a.get_text()
        number_element = gene_element.find_next('span', class_='gene-id')
        gene_number = number_element.get_text() if number_element else "Not Found"
        species_element = gene_element.find_next('td').find_next('em')
        species_name = species_element.get_text() if species_element else "Not Found"

        if species is None:
            data.append([gene_name, species_name, gene_number, url])
        else:
            data.append([gene_name, species_name, gene_number, url])
            break  # Break the loop after finding the first entry for the specified species

    df = pd.DataFrame(data, columns=['gene_name', 'sp', 'id', 'url'])
    df_cleaned = df.dropna(axis=1, how='all')
    return df_cleaned


def get_gene_info_by_rsid(rsids):
    data = []
    rsid_list = [num.strip() for num in rsids.split(',') if num.strip()]
    for rsid in rsid_list:
        url = f"https://www.ncbi.nlm.nih.gov/snp/{rsid}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        sp_element = soup.select_one(
            "#main_content > main > div > div.summary-box.usa-grid-full > dl:nth-child(1) > dd.species_name")
        sp = sp_element.get_text() if sp_element else "Species Not Found"
        gene_element = soup.select_one(
            "#main_content > main > div > div.summary-box.usa-grid-full > dl:nth-child(2) > dd:nth-child(4) > span")
        gene = gene_element.get_text() if gene_element else "Gene Not Found"

        data.append([rsid, sp, gene, url])
    df = pd.DataFrame(data, columns=['rsid', 'sp', 'gene:variant type', 'link'])
    df_cleaned = df.dropna(axis=1, how='all')
    return df_cleaned
    

def get_pmc_ids_from_pmids(file, input):
    results = []
    if file is not None and not file.empty:
        pmids = file.iloc[:,0].drop_duplicates().tolist()
    else:
        pmids = [num.strip() for num in input.split(',') if num.strip()]
    for pmid in pmids:
        url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={pmid}&format=json"
        response = requests.get(url)
        if response.ok:
            data = response.json()
            records = data.get("records", [])
            if records:
                record = records[0]
                pmc_id = record.get("pmcid", None)
                results.append((pmid, pmc_id))
            else:
                results.append((pmid, None))
    df = pd.DataFrame(results, columns=["PMID", "PMCID"])
    return df


def get_pmids_from_pmc_ids(file, input):
    results = []
    if file is not None and not file.empty:
        pmc_ids = file.iloc[:, 0].drop_duplicates().tolist()
    else:
        pmc_ids = [num.strip() for num in input.split(',') if num.strip()]
    for pmc_id in pmc_ids:
        url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={pmc_id}&format=json"
        response = requests.get(url)
        if response.ok:
            data = response.json()
            records = data.get("records", [])
            if records:
                record = records[0]
                pmid = record.get("pmid", None)
                results.append((pmc_id, pmid))
            else:
                results.append((pmc_id, None))
    df = pd.DataFrame(results, columns=["PMCID", "PMID"])
    return df


def fetch_litvar_data(file, input):
    if file is not None and not file.empty:
        file['litvar'] = file['gene'] + " " + file['HGVS']
        query_list = file['litvar'].drop_duplicates().tolist()
    else:
        query_list = [num.strip() for num in input.split(',') if num.strip()]
    data_dict = {
        'Query': [],
        'rsid': [],
        'gene': [],
        'name': [],
        'hgvs': [],
        'pmids_count': [],
        'data_clinical_significance': []
    }
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

    litvar = pd.DataFrame(data_dict)
    litvar_cleaned = litvar.dropna(axis=1, how='all')
    return litvar_cleaned


def synvar(input):
    data_dict = {
        'pmid': [],
        'query': [],
        'gene': [],
        'variants_synonyms': [],
        'drugs': []
    }
    lines = input.split('\n')
    for line in lines:
        items = [item.strip() for item in line.split(',')]
        if len(items) != 2:
            continue  # Skip lines that do not have exactly two items
        ids = items[0]
        genvars = items[1]
        url = f"https://variomes.text-analytics.ch/api/fetchDoc?ids={ids}&genvars={genvars}"
        response = requests.get(url)
        if response.ok:
            result = response.json()

            data_dict['pmid'].append(ids)
            data_dict['query'].append(genvars)

            variants_data = result.get('normalized_query', {}).get('variants', [])
            data_dict['variants_synonyms'].append(variants_data[0].get('terms'))

            gene_data = result.get('publications', [])[0].get('details', {}).get('facet_details', {}).get('genes', [])
            gene_info = [f"{gene.get('preferred_term')}({gene.get('id')})" for gene in gene_data]
            data_dict['gene'].append(gene_info)

            drug_data = result.get('publications', [])[0].get('details', {}).get('facet_details', {}).get('drugs', [])
            drug_info = [f"{drug.get('preferred_term')}({drug.get('id')})" for drug in drug_data]
            data_dict['drugs'].append(drug_info)

    pd.set_option('display.max_colwidth', 30)
    synvar_df = pd.DataFrame(data_dict)
    synvar_df['gene'] = synvar_df['gene'].apply(lambda x: ', '.join(x))
    synvar_df['variants_synonyms'] = synvar_df['variants_synonyms'].apply(lambda x: ', '.join(x))
    synvar_cleaned = synvar_df.dropna(axis=1, how='all')
    return synvar_cleaned


def synvar_file(file):
    pd.set_option('display.max_colwidth', 30)
    file['query'] = file['gene'] + "(" + file['HGVS'] + ")"
    file['result'] = file.apply(fetch_data, axis=1)
    file['genes'] = file['result'].apply(extract_genes)
    file['genes'] = file['genes'].apply(lambda x: ', '.join(x))
    file['variants_synonyms'] = file['result'].apply(extract_variants_syn)
    file['variants_synonyms'] = file['variants_synonyms'].apply(lambda x: ', '.join(x))
    file['drugs'] = file['result'].apply(extract_drugs)
    return file[['pmid', 'query', 'genes', 'variants_synonyms', 'drugs']]


def fetch_data(row):
    ids = row['pmid']
    genvars = row['query']
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
