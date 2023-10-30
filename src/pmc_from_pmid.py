import requests
import pandas as pd
import os
import sys

def get_pmc_ids_from_pmids(pmids, output_dir, file_name):
    """Returns a Pandas DataFrame stored in the output_dir with columns PMID and PMC,
    where column PMID contains
    the input pmids, and column PMC contains the PMC IDs for each pmid (if available),
    or "none" otherwise.
    """
    results = []
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
    df = pd.DataFrame(results, columns=["PMID", "PMC"])
    output_file = os.path.join(output_dir, file_name)
    df.to_csv(output_file, sep="\t", index=False)


def main():
    if len(sys.argv) != 4:
        print("Usage: python script_name.py [input pmids file(tsv, csv or txt)] [output dir] [file name suffix]")
        sys.exit(1)
    
    input_pmids_file = sys.argv[1]
    output_dir = sys.argv[2]
    file_name_suffix = sys.argv[3]
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read PMIDs from the input file
    with open(input_pmids_file, 'r') as f:
        pmids = [line.strip() for line in f]
    
   
    file_name = os.path.splitext(os.path.basename(input_pmids_file))[0] + file_name_suffix + ".tsv"
    get_pmc_ids_from_pmids(pmids, output_dir, file_name)


if __name__ == "__main__":
    main()
