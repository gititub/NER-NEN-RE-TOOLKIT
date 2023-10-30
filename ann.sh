#!/bin/bash

if [ $# -ne 2 ]; then
  echo "Usage: $0 input_file_or_directory output_type"
  exit 1
fi

input="$1"
output_type="$2"
current_date=$(date +'%Y-%m-%d_%H-%M-%S')
output_directory="results_${current_date}"

# Create the output directory if it doesn't exist
mkdir -p "$output_directory"
current_dir=$(pwd)
# Function to process a single file
process_file() {
  file="$1"
  file_content=$(head -n 1 "$file")
  file_name_without_extension=$(basename -- "$file" | sed 's/\.[^.]*$//')
  output_file="${file_name_without_extension}.${output_type}"

  if [[ $file_content =~ ^[0-9]+$ ]] || [[ $file_content == "pmid" ]]; then
    python src/bern_extract_pmids.py "$file" "${output_directory}/bern_pmid_${output_file}"
    python src/ptc_extract_pmids.py "$file" "${output_directory}/ptc_pmid_${output_file}"
  elif [[ $file_content =~ ^PMC[0-9]+$ ]] || [[ $file_content == "PMC" ]]; then
    python src/ptc_extract_pmc.py "$file" "${output_directory}/ptc_pmc_${output_file}"
    cp "$file" src/GWAS-Miner/GWAS_Miner/"$file"
    cd src/GWAS-Miner/GWAS_Miner/
    ./gwasminer.sh "$file"
    cp tables_GWASminer.tsv "${current_dir}/${output_directory}/tables_GWASminer.tsv"
    cp data_GWASminer.tsv "${current_dir}/${output_directory}/data_GWASminer.tsv"
  fi
}

# Check if the input is a directory
if [ -d "$input" ]; then
  # Input is a directory, process each file within it
  for file in "$input"/*; do
    # Check if the file is a regular file
    if [ -f "$file" ]; then
      process_file "$file"
    fi
  done
else
  # Input is not a directory, treat it as a single file
  process_file "$input"
fi

