
# test
This repository provides the code for automatic system to retrieve annotations of biomedical concepts such as genes and mutations in PubMed abstracts, PMC full-text articles or plain text.


<img
  src="https://github.com/gititub/test/blob/main/resources/workflow2.png"
  alt="Alt text"
  style="display: block; height:450px; width:800px">


## Installation

```
git clone https://github.com/gititub/test.git
cd test
```
Create a new environment with Conda. Supports Python 3.8, 3.9, and 3.10:
```
conda create -y --name env_app python=3.9
conda activate env_app
pip install -r requirements.txt
```

## Run from the Command Line on Linux:

$ ./ann.sh [input file or directory] [json/tsv]

This code first checks if the input is a directory and then process each file within the directory while applying the appropriate logic based on the file content, PubMed ID or PMC ID. Based on which function is being executed, the output files will have distinct names: "pmids", "PMC", "bern" and "ptc" will be appended to the output file name. Additionally, the script distinguishes between two output formats: 'biocjson' or 'dataframe' depending on whether the second argument is 'json' or 'tsv' respectively.

Results will be saved in a directory named "results_[datetime]".

Run example of a directory: 
```
chmod +x ann.sh
./ann.sh example tsv
```
Or of a single file:
```
./ann.sh example/pmids.tsv json
```

ℹ️ **Accepted file input extensions for all commands include .txt, .tsv, or .csv. The data must be organized into a single column of elements. The first row may also include a column name, which can be either 'pmid' or 'PMC'. If the output filename concludes with '.tsv', you will receive the results as a DataFrame. However, if it concludes with '.json', the results will be provided in the bioCjson format.**

## NER and NEN for PubMed abstracts with PubTator

$ python source/ptc_extract_pmids.py [file_path_pmids] [output_filename]

Run example: 
```
python source/ptc_extract_pmids.py example/pmids.tsv output.json
```
```
python source/ptc_extract_pmids.py example/pmids.tsv output.tsv
```
## NER and NEN for PubMed abstracts with BERN2

$ python source/bern_extract_pmids.py [file_path_pmids] [output_filename]

```
python source/bern_extract_pmids.py example/pmids2.csv output_bern.tsv
```
```
python source/bern_extract_pmids.py example/pmids.tsv output_bern.json
```
## NER and NEN for PMC full-text articles with PubTator

$ python source/ptc_extract_pmc.py [file_path_pmcs] [output_filename]

Run example:
```
python source/ptc_extract_pmc.py example/pmcs.txt output_pmc.json
```
```
python source/ptc_extract_pmc.py example/pmcs.txt output_pmc.tsv
```

## NER and NEN for plain text with BERN2

Plain text is limited to 5000 characters. To expedite the process, you can distribute the texts (each no longer than 5000 characters) into subdirectories within the designated input directory (with no more than 120 files per subdirectory). This process is parallelized to concurrently process the subdirectories. The outcome is acquired in a file bearing the same name as the subdirectory, following the specified format (JSON or TSV) – one result file per subdirectory. 

You can download the full text automatically divided into subdirectories yourself, from a PMC list or from a folder with pdf files.

From PMC list:

$ python source/download_pmc_fulltext.py [filepath_pmcs] [output_dir]

Run example: 
```
python source/download_pmc_fulltext.py example/pmcs.txt bern_ft
```
Or from a one or more PMCs:
```  
python source/download_pmc_fulltext.py PMC2907921,PMC2907921 bern_ft2
```

Additionally, you can use **Selenium** and **ChromeDriver**. ℹ️ The ChromeDriver’s primary function is to start Google Chrome. Without them, it is impossible to automate any website and run Selenium. To use ChromeDriver, you need to first download it from the Chromium website and then install it. https://chromedriver.chromium.org/downloads  

$ python source/download_fulltext_bern.py [filepath_pmcs] [output_dir]

```
python source/download_fulltext_bern.py example/pmcs.txt bern_ft
```
From **PDF files**:

$ python source/convert_pdf.py [pdf_directory] [output_directory]

Run example: 
```
python source/convert_pdf.py pdf_files bern_ft_pdf
```
Then, you can run **BERN2**. 

⚠️ This process might take several minutes. 


$ python source/bern_extract_ann.py [input_dir] [output_dir] [json/df]

Run example: 
```
python source/bern_extract_ann.py bern_ft_pdf bern_ft_pdf_results df
```

## NER and NEN from query

This command will search for PMC articles related to a query, for example *biotin* or *Hodgkin+Lymphoma* (it is not case sensitive), using Bio.Entrez (Spaces may be replaced by '+' sign). Retrieves and processes PubTator annotations and save the results in the specified output file in biocjson or tsv format.

Entrez.ESearch searches and retrieves primary IDs and term translations, and optionally retains results for future use in the user’s environment. The fourth command-line argument is the number of IDs to retrieve.

The last command-line argument is the oldest publication date. If you don't want to filter by date, simply omit the --pub_date argument. This argument is not mandatory but it is recommended to use it.

**Pubmed abstracts**

$ python source/ptc_extract_pmids_query.py [query] [output_filename] [max retrievals] --pub_date ["YYYY/MM/DD"]

Run example: published after January 1, 2023
```
python source/ptc_extract_pmids_query.py biotin output_biotin.tsv 50 --pub_date "2022/01/01"
```

**PMC articles**

$ python source/ptc_extract_pmc_query.py [query] [output_filename] [max retrievals] --pub_date ["YYYY/MM/DD"]

Run example: 
```
python source/ptc_extract_pmc_query.py BRAF output_braf.json 35 --pub_date "2021/01/01"
```
```
python source/ptc_extract_pmc_query.py Hodgkin+Lymphoma output_lymphoma.tsv 25 
```
## ID converter

**Convert PubMed ids to PMC ids**  
Here, pmids is your input file containing the list of pmids (tsv, csv and txt format allowed), output_directory is the directory where you want to save the output file, and _pmc is the suffix you want to add to the output file's name. This script will read the input pmids, retrieve PMC IDs, and save the output file in the specified directory with the desired name.

$ python source/pmc_from_pmid.py [pmids] [output_directory] [_pmc]
 
Run example: 
```
python source/pmc_from_pmid.py example/pmids.tsv '.' _pmc
```
**Convert PMC ids to pmids**  
Run example: 
```
python source/pmid_from_pmc.py example/pmcs.txt '.' _pmid
```

# NER&NEN-App 

## NerVerseToolkit 

https://nerversetoolkit.shinyapps.io/nerversetoolkit/

<img
  src="https://github.com/gititub/test/blob/main/resources/app.png"
  alt="Alt text"
  style="display: block; width:400px">

**Run NER-App in Linux:**
```
cd app;shiny run --reload
```
You can also run NER-App in Windows.  
1. Make a query:  
- PMC or PubMed id to **PubTator** (One or more, comma separated).
  For example, "36064841, PMC9797458" (They can be mixed together).
- Query to **PubTator**: Word (replace space with ‘&’) + Publication Date + max. Retrievals
- Plain Text to **BERN2** (max. 5000 characters)
- PubMed id to **BERN2** (one or more, comma separated)
- Plain Text to **Drug Named Entity Recognition**
- PMC or PubMed id to **Drug Named Entity Recognition** (one or more, comma separated. They can be mixed together)
- PubMed id to **Variomes**

2. Select output type: DataFrame or BioCjson.  
3. Download results


<img
  src="https://github.com/gititub/test/blob/main/resources/Captura.png"
  alt="Alt text"
  style="display: block; width:400px">
  
## NormaMed Toolbox

https://nerversetoolkit.shinyapps.io/normamedtoolbox/

**Run NEN-App in Linux:**
```
cd appNEN;shiny run --reload
```
<img
  src="https://github.com/gititub/test/blob/main/resources/appNEN.png"
  alt="Alt text"
  style="display: block; width: 400px">

1.	Make a query
- SynVar Normalization : e.g. 19915144, MEK1(p.Q56P) or upload CSV file with three mandatory columns: 'pmid', gene' and 'HGVS'.
- LitVar Normalization: e.g. BRAFp.V600E  (one or more, comma separated) or upload CSV file with two mandatory columns,'gene' and 'HGVS. → dbSNP rs ID  
- Gene Normalization to gene ID (one by one, only a gene name or gene + specie)  
- Gene ID → Gene Name (one or more, comma separated)  
- Rs id → Gene Info (one or more, comma separated)   
2.	Download results  
   
## NER with SynVar and LitVar

To run example use test.tsv or test2.csv as input file, or use your own data with 3 columns: pmid, gene, HGVS. Returns two files in the specified output directory, one with LitVar normalization and the second one with SynVar normalization and gene+drug NER.

$ python source/normalize.py [input_file] [output_directory] 

```
python source/normalize.py example/test2.csv '.'
```
