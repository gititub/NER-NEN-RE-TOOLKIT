import requests
import pandas as pd
import os
import sys

def get_pmids_from_pmc_ids(pmc_ids, output_dir, file_name):
    """Returns a Pandas DataFrame stored in the output_dir with columns PMC and PMID,
    where column PMC contains the input PMC IDs, and column PMID contains the corresponding PMIDs (if available),
    or "none" otherwise.
    """
    results = []
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
    df = pd.DataFrame(results, columns=["PMC", "PMID"])
    output_file = os.path.join(output_dir, file_name)
    df.to_csv(output_file, sep="\t", index=False)

def main():
    if len(sys.argv) != 4:
        print("Usage: python script_name.py [input pmc_ids file(tsv, csv or txt)] [output dir] [file name suffix]")
        sys.exit(1)
    
    input_pmc_ids_file = sys.argv[1]
    output_dir = sys.argv[2]
    file_name_suffix = sys.argv[3]
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read PMC IDs from the input file
    with open(input_pmc_ids_file, 'r') as f:
        pmc_ids = [line.strip() for line in f]
    
    file_name = os.path.splitext(os.path.basename(input_pmc_ids_file))[0] + file_name_suffix + ".tsv"
    get_pmids_from_pmc_ids(pmc_ids, output_dir, file_name)

if __name__ == "__main__":
    main()
  
