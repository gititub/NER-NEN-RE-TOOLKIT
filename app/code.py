import requests
import json
import pandas as pd
from Bio import Entrez
from drug_named_entity_recognition import find_drugs
import spacy
from bs4 import BeautifulSoup

def extract_pubtator(ids, output):
    id_list = [num.strip() for num in ids.split(',') if num.strip()]
    results_json = []
    results = []

    for id in id_list:
        print(f"Processing ID: {id}")
        url = "https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/biocjson?pmids=" + str(id)
        try:
            response = requests.get(url)
            response.raise_for_status()
            json_data = response.json()
            results_json.append(json_data)
        except requests.exceptions.RequestException as e:
            print(f"Error for {id}: {e}")
        except ValueError as e:
            print("Error parsing JSON data:", e)
            print("URL:", url)
            print("Response:", response.content)
            continue

    for pubtator in results_json:
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

        PMID = id  # pubtator['id']
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

        results.append(df)

    if len(results) == 0:
        print("No dataframes to concatenate.")

    if output == 'biocjson':
        return json.dumps(results_json, indent=4)
    elif output == 'df':
        combined_df = pd.concat(results, ignore_index=True)
        return combined_df
    else:
        print("Invalid output format. Please choose 'biocjson' or 'df'.")


def extract_pubtator_from_pmcs(ids, output):
    id_list = [num.strip() for num in ids.split(',') if num.strip()]
    list_of_pubtators = []
    error_ids = []
    results = []

    for id in id_list:
        print(f"Processing ID: {id}")
        url = "https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/biocjson?pmcids=" + str(id)
        try:
            response = requests.get(url)
            response.raise_for_status()
            json_data = response.json()
            list_of_pubtators.append(json_data)
        except requests.exceptions.RequestException as e:
            error_ids.append(id)
            continue  # Skip to the next ID if an error occurs
        except ValueError as e:
            print("Error parsing JSON data:", e)
            print("URL:", url)
            print("Response:", response.content)
            continue  # Skip to the next ID if an error occurs

        print(f"Total number of errors extracting Pubtator data from PMCs: {error_ids}")

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
        results.append(df)

    if len(results) == 0:
        print("No dataframes to concatenate.")

    if output == 'biocjson':
        return json.dumps(list_of_pubtators, indent=4)
    elif output == 'df':
        combined_df = pd.concat(results, ignore_index=True)
        return combined_df
    else:
        print("Invalid output format. Please choose 'biocjson' or 'df'.")

def bern_extract_pmids(pmids, output):
    results = []
    pmid_list = [num.strip() for num in pmids.split(',') if num.strip()]
    for pmid in pmid_list:
        json_data, df = process_pmid(pmid)  # Capture both JSON data and DataFrame
        if df is not None:
            results.append(df)
    if results:
        bern = pd.concat(results)
    if output == 'biocjson':
        return json.dumps(json_data, indent=4)
    elif output == 'df':
        return bern  # Return the DataFrame
    else:
        print("Invalid output format. Please choose 'biocjson' or 'df'.")


def process_pmid(pmid):
    print(f"Processing PMID {pmid} with BERN2...")
    url = f"http://bern2.korea.ac.kr/pubmed/{pmid}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            json_data = response.json()
            df = json_to_df(json_data)
            return json_data, df
        else:
            print(f"Request for PMID {pmid} failed with status code:", response.status_code)
            return None
    except Exception as e:
        print(f"Error processing PMID {pmid}: {str(e)}")
        return None


def json_to_df(json_data):
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
        #"is_neural_normalized": is_neural_normalized_list,
        "prob": prob_list,
        "mention": mention_list,
        "normalized name": norm_list,
        "mutation type": mut_type_list,
        "obj": obj_list,
        "span_begin": begin_list,
        "span_end": end_list
    })
    df['Wikipedia URL'] = df['mention'].apply(lambda x: 'https://en.wikipedia.org/wiki/' + x)
    df['PubChem'], df['chEBI'], df['DrugBank'] = zip(*df['mention'].apply(db_from_wikipedia))

    return df


def query_plain(text, output):
    url = "http://bern2.korea.ac.kr/plain"
    result = requests.post(url, json={'text': text}).json()

    extracted_data = []
    annotations = result.get('annotations', [])
    for annotation in annotations:
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

    if len(extracted_data) == 0:
        print("No dataframes to concatenate.")
    df = pd.DataFrame(extracted_data)
    df['dbSNP'] = df['normalized_name'].str.extract(r'(?:rs|RS#:)(\d+)', expand=False)
    df['dbSNP'] = 'rs' + df['dbSNP']
    df['Wikipedia URL'] = df['mention'].apply(lambda x: 'https://en.wikipedia.org/wiki/' + x)
    df['PubChem'], df['chEBI'], df['DrugBank'] = zip(*df['mention'].apply(db_from_wikipedia))

    if output == 'biocjson':
        return json.dumps(result, indent=4)
    elif output == 'df':
        return df
    else:
        print("Invalid output format. Please choose 'biocjson' or 'df'.")


def db_from_wikipedia(mention):
    url = f"https://en.wikipedia.org/wiki/{mention}"
    response = requests.get(url)
    pubchem = ""
    chebi = ""
    drugbank = ""

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        infobox = soup.find('table', class_='infobox')
        if infobox:
            id_elements = infobox.find_all('a', href=True)
            for id_element in id_elements:
                if 'pubchem.ncbi.nlm.nih.gov' in id_element['href']:
                    pubchem = id_element.contents[0]
                elif 'www.drugbank.ca' in id_element['href']:
                    drugbank = id_element.contents[0]
                elif 'www.ebi.ac.uk' in id_element['href']:
                    chebi = id_element.contents[0]

    return pubchem, chebi, drugbank


def extract_pubtator_from_pmcs_query(query, pub_date, retmax, output):
    email = "weliw001@hotmail.com"
    Entrez.email = email
    if pub_date:
        pub_date_formatted = pub_date.strftime("%Y/%m/%d")
        query += f" AND {pub_date_formatted}[Date - Publication]"
    handle = Entrez.esearch(db="pmc", term=query, retmax=retmax)
    record = Entrez.read(handle)
    handle.close()
    pmcs = record["IdList"]

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

    if len(df_list) == 0:
        print("No dataframes to concatenate.")

    merged_df = pd.concat(df_list, ignore_index=True)

    if output == 'biocjson':
        return json.dumps(list_of_pubtators, indent=4)
    elif output == 'df':
        return merged_df
    else:
        print("Invalid output format. Please choose 'biocjson' or 'df'.")


def count_characters(input_text):
    character_count = len(input_text)
    if character_count > 4990:
        return "You exceeded the character limit"
    else:
        return character_count


def plain_drugs(txt, output):
    nlp = spacy.blank("en")
    doc = nlp(txt)
    json_data2 = find_drugs([t.text for t in doc], is_ignore_case=True)
    json_data = find_drugs(txt.split(" "), is_ignore_case=True)

    if json_data:
        names = []
        synonyms = []
        mesh_ids = []
        drugbank_ids = []
        medline_ids = []
        nhs_urls = []
        wikipedia_urls = []
        positions = []

        for data in json_data:
            if 'name' in data[0]:
                names.append(data[0]['name'])
            else:
                names.append(None)
            if 'synonyms' in data[0]:
                synonyms.append(data[0]['synonyms'])
            else:
                synonyms.append(None)
            if 'mesh_id' in data[0]:
                mesh_ids.append(data[0]['mesh_id'])
            else:
                mesh_ids.append(None)
            if 'drugbank_id' in data[0]:
                drugbank_ids.append(data[0]['drugbank_id'])
            else:
                drugbank_ids.append(None)
            if 'medline_plus_id' in data[0]:
                medline_ids.append(data[0]['medline_plus_id'])
            else:
                medline_ids.append(None)
            if 'nhs_url' in data[0]:
                nhs_urls.append(data[0]['nhs_url'])
            else:
                nhs_urls.append(None)
            if 'wikipedia_url' in data[0]:
                wikipedia_urls.append(data[0]['wikipedia_url'])
            else:
                wikipedia_urls.append(None)

            positions.append(data[1])

        df = pd.DataFrame({'Name': names,
                           'Synonyms': synonyms,
                           'MESH id': mesh_ids,
                           'Drugbank_ID': drugbank_ids,
                           'MedlinePlus id': medline_ids,
                           'NHS URL': nhs_urls,
                           'Wikipedia URL': wikipedia_urls,
                           'Position': positions})
        if df:
            df['PubChem'], df['chEBI'], df['DrugBank'] = zip(*df['Name'].apply(db_from_wikipedia))

        if output == 'biocjson':
            result = []
            for item in json_data:
                # Convert set of synonyms to a list
                item[0]['synonyms'] = list(item[0]['synonyms'])
                json_str = json.dumps(item[0], separators=(',', ':'))
                result.append(json_str)
            return result
        elif output == 'df':
            return df


def download_from_PMC(pmcids):
    pmcid_list = [num.strip() for num in pmcids.split(',') if num.strip()]
    text = []
    for pmcid in pmcid_list:
        print(f"Downloading {pmcid}...")
        URL = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/{pmcid}/unicode"
        response = requests.get(URL)
        data = response.text
        text.append(data)
    joined_text = '.'.join(text)  # Join the text data with '.'
    return joined_text

def download_from_PubMed(pmids):
    pmid_list = [num.strip() for num in pmids.split(',') if num.strip()]
    text = []
    for pmid in pmid_list:
        print(f"Downloading PMID {pmid}...")
        URL = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pubmed.cgi/BioC_json/{pmid}/unicode"
        response = requests.get(URL)
        data = response.text
        text.append(data)
    joined_text = '.'.join(text)  # Join the text data with '.'
    return joined_text
