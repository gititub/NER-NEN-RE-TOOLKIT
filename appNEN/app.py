# app.py
import json
import pandas as pd
import shinyswatch
import os
from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui
from shiny.types import FileInfo
from code import fetch_litvar_data, get_gene_info_by_gene_number, get_gene_info_by_gene_name, \
    get_gene_info_by_rsid, synvar_file, synvar, fetch_data, extract_variants_syn, extract_drugs, \
    extract_genes, get_pmc_ids_from_pmids, get_pmids_from_pmc_ids

app_ui = ui.page_fluid(
    shinyswatch.theme.minty(),
    # shinyswatch.theme.darkly(),
    # shinyswatch.theme.sketchy(),
    # ui.include_css("style.css"),
    ui.br(),
    ui.row(
        ui.column(
            1,
            ui.br(),
        ),
        ui.column(
            2,
            ui.output_image("imagen", height="90px"),
        ),
        ui.column(
            6,
            ui.h2("Biomedical Entity Normalization"),
        ),
    ),
    ui.br(),
    ui.input_select(
        "input_type",
        "Select function:",
        {
            "norm": "LitVar Variant Normalization",
            "norm2": "SynVar Variant Normalization",
            "gene": "Gene Normalization",
            "gene_name": "Gene Name",
            "gene_info": "rs ID Gene Info",
            "pmid_to_pmc": "PubMed ID to PMC ID",
            "pmc_to_pmid": "PMC ID to PubMed ID",
        },
        selected="Variant Normalization",
    ),
    ui.output_text_verbatim("txt"),
    ui.input_text_area("id", "Write query:",
                       placeholder='e.g.rs5030858 or BRAF',
                       width='800px', height='200px'),
    ui.row(
        ui.column(
            4,
            ui.input_file("file", "Choose CSV or TSV File",
                          accept=[".csv", ".tsv", ".txt"],
                          multiple=False),
        ),
        ui.column(
            2,
            ui.br(),
            ui.input_action_button(
                "clear", "Clear", class_="btn-primary"
            ),
        ),
    ),
    ui.br(),
    ui.input_switch("all_results", "View all results", True),
    ui.input_action_button(
        "action", "Submit", class_="btn-primary"
    ),
    ui.download_button("download", "Download results"),
    ui.output_data_frame("table"),
)


def server(input, output, session):
    @output
    @render.image
    def imagen():
        return {
            "src": 'aprender.png',
            "style": "width: 80px; max-height: 80px;",
        }

    @output
    @render.text
    def txt():
        if input.input_type() == "gene":
            return "e.g. BRAF or braf homo sapiens"
        elif input.input_type() == 'gene_name':
            return "e.g. 7157,657,4234"
        elif input.input_type() == 'gene_info':
            return "e.g. rs5030858"
        elif input.input_type() == 'pmid_to_pmc':
            return "e.g. 27432226, 22383897 or upload CSV/TSV/TXT file "
        elif input.input_type() == 'pmc_to_pmid':
            return "e.g. PMC9797458, PMC3285588  or upload CSV/TSV/TXT file"
        elif input.input_type() == 'norm2':
            return "e.g. 19915144, MEK1(p.Q56P) or upload CSV file with three mandatory columns: 'pmid', gene' and 'HGVS'."
        else:
            return "e.g. BRAF p.V600E (or upload CSV file with two mandatory columns,'gene' and 'HGVS)"

    @reactive.Calc
    def result():
        if input.file():
            f: list[FileInfo] = input.file()
            file = pd.read_csv(f[0]["datapath"], header=0, sep='\t')
            if input.input_type() == 'pmc_to_pmid':
                result = get_pmids_from_pmc_ids(file, None)
            elif input.input_type() == 'pmid_to_pmc':
                result = get_pmc_ids_from_pmids(file, None)
            elif input.input_type() == 'norm2':
                result = synvar_file(file)
            elif input.input_type() == 'norm':
                result = fetch_litvar_data(file, None)

        else:
            if input.input_type() == "gene":
                result = get_gene_info_by_gene_name(input.id())
            elif input.input_type() == 'gene_name':
                result = get_gene_info_by_gene_number(input.id())
            elif input.input_type() == 'gene_info':
                result = get_gene_info_by_rsid(input.id())
            elif input.input_type() == 'pmid_to_pmc':
                result = get_pmc_ids_from_pmids(file=None, input=input.id())
            elif input.input_type() == 'pmc_to_pmid':
                result = get_pmids_from_pmc_ids(file=None, input=input.id())
            elif input.input_type() == 'norm2':
                result = synvar(input.id())
            elif input.input_type() == 'norm':
                result = fetch_litvar_data(None, input.id())

        return result

    @output
    @render.ui
    @reactive.event(input.clear)
    def _():
        return None

    @output
    @render.data_frame
    @reactive.event(input.action)
    def table():
        if isinstance(result(), pd.DataFrame):
            if input.all_results():
                return render.DataGrid(
                    result(),
                    width="100%",
                    height="100%",
                    filters=True,
                )
            else:
                return result().head(15)

    @session.download()
    def download():
        result().to_csv('results.tsv', sep='\t', index=False)
        path = os.path.join(os.path.dirname(__file__), "results.tsv")
        return path

    @reactive.Effect
    def _():
        req(input.action())
        ui.notification_show("Go!!", duration=5, type="message")


app = App(app_ui, server)
