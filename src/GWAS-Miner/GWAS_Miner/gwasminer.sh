#!/bin/bash

PYTHON_SCRIPT="download_html.py"

if [ "$#" -lt 1 ]; then
    echo "Error: Please provide PMC ID(s) or a file as argument"
    exit 1
fi

if [ -f "$1" ]; then
    # Read PMC IDs from file and process them
    if [[ "$1" =~ \.txt$ ]]; then
        pmc_ids=$(cat "$1")
    elif [[ "$1" =~ \.csv$ ]]; then
        pmc_ids=$(tail -n +2 "$1" | cut -d',' -f1)
    elif [[ "$1" =~ \.tsv$ ]]; then
        pmc_ids=$(tail -n +2 "$1" | cut -d$'\t' -f1)
    else
        echo "Unsupported file format. Please provide a TXT, CSV, or TSV file."
        exit 1
    fi

    python3 "$PYTHON_SCRIPT" $pmc_ids
else
    python3 "$PYTHON_SCRIPT" "$@"
fi

#conda deactivate
#conda activate env3.7

cd Auto-CORPus/ || exit 1
python run_app.py -c "configs/config_pmc.json" -t "output" -f "./html_files" -o JSON

# Copy json files from Auto-CORPus/output/ to input/ directory

current_dir=$(pwd)
dir1="$current_dir/output/"

#conda deactivate

cd .. || exit 1
current_dir=$(pwd)
dir2="$current_dir/input/"

files=$(ls "$dir1"*_bioc.json "$dir1"*_tables.json)

for file in $files; do
    if [ -e "$file" ]; then
        cp "$file" "$dir2"
    fi
done

# Install required Python packages
pip install .
pip install --upgrade pip
pip install .

python GWASMiner.py -d input

python process_gwm.py

exit 0

