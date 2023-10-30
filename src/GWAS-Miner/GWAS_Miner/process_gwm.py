import xml.etree.ElementTree as ET
import os
import json
import pandas as pd

directory1 = os.getcwd() + "/output/xml"
directory = os.getcwd() + "/output/json"

def process_xml_files(directory1):
    offsets = []
    lengths = []
    identifiers = []
    types = []
    texts = []
    file_names = []
    doc_ids = []
    section_list = []

    for filename in os.listdir(directory1):
        if filename.endswith('.xml'):
            filepath = os.path.join(directory1, filename)

            tree = ET.parse(filepath)
            root = tree.getroot()

            doc_id = root.find('.//id').text

            for passage in root.findall('.//passage'):
                #iao = passage.find('.//infon[@key="iao_name_1"]')
                iao = passage.find('.//infon[@key="iao_name_1"]')
                section = iao.text if iao is not None else None

                for annotation in passage.findall('.//annotation'):
                    offset = int(annotation.find('.//location').attrib['offset'])
                    length = int(annotation.find('.//location').attrib['length'])

                    offsets.append(offset)
                    lengths.append(offset + length)
                    infon = annotation.find('.//infon[@key="identifier"]')
                    identifier = infon.text if infon is not None else None
                    annotation_type = annotation.find('.//infon[@key="type"]')

                    section_list.append(section)
                    identifiers.append(identifier)
                    types.append(annotation_type.text)

                    text = annotation.find('text').text
                    texts.append(text)

                    file_names.append(filename)
                    doc_ids.append(doc_id)

        df = pd.DataFrame({
            #'file_name': file_names,
            'doc_id': doc_ids,
            'section': section_list,
            'offset': offsets,
            'end': lengths,
            'identifier': identifiers,
            'type': types,
            'text': texts
        })

    df.to_csv('data_GWASminer.tsv', sep='\t', index=False)


def process_json_files(directory):
    df_list =[]
    for filename in os.listdir(directory):
        if filename.endswith('_tables.json'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as json_file:
                data = json.load(json_file)

                PMC_list = []
                Id = []
                text_list = []
                type_list = []
                identifier_list = []
                offset_list = []
                table_elem_list =[]

                for doc in data['documents']:
                    PMC = doc['inputfile']
                    ids = doc['id']

                    for annotation in doc['annotations']:
                        text = annotation['text']
                        types = annotation['infons']['type']
                        identifier = annotation['infons']['identifier']
                        locations = annotation['locations'][0]['offset']
                        table_element = annotation['locations'][0]['table_element']

                        PMC_list.append(PMC)
                        Id.append(ids)
                        text_list.append(text)
                        type_list.append(types)
                        identifier_list.append(identifier)
                        offset_list.append(locations)
                        table_elem_list.append(table_element)

                df = pd.DataFrame({
                    'PMC': PMC_list,
                    'id': Id,
                    'type': type_list,
                    'text': text_list,
                    'table_element': table_elem_list,
                    'offset': offset_list,
                    'identifier': identifier_list})

                df_list.append(df)
    if df_list:
        df = pd.concat(df_list, ignore_index=True)
        df['PMC'] = df['PMC'].str.extract(r'PMC(\d+)\.html')
        df['PMC'] = "PMC" + df['PMC']
        df.to_csv('tables_GWASminer.tsv', sep='\t', index=False)
    else:
        print("No valid JSON files found in the directory.")

def main():
    process_xml_files(directory1)
    process_json_files(directory)

if __name__ == "__main__":
    main()
