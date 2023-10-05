# app.py
import os
import json
import pandas as pd
import shinyswatch
from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui
from shiny.types import ImgData
from code import count_characters, extract_pubtator, query_plain, \
    extract_pubtator_from_pmcs_query, plain_drugs, download_from_PMC, download_from_PubMed, \
    bern_extract_pmids, synvar_ann, download_data, apply_db_from_wikipedia


app_ui = ui.page_fluid(
    shinyswatch.theme.superhero(),
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
            4,
            ui.h2("Biomedical Entity Recognition"),
        ),
         ui.column(
            2,
            ui.output_image("imagen2", height="90px"),
            ui.tags.a("About & FAQ",
                  href="https://github.com/gititub/NEN-NER-TOOLKIT"),
        ),
    ),
    ui.row(
        ui.column(
            4,
            ui.input_select(
                "input_type",
                "Query Type",
                {
                    "PTC": "PMC or PubMed ID (PubTator)",
                    "query": "Word in PubMed Central (PubTator)",
                    "plain_text": "Plain Text (BERN2)",
                    "pmid_bern": "PubMed ID (BERN2)",
                    "plain_drugs": "Plain Text (Drug NER)",
                    "id_drugs":  "PMC or PubMed ID (Drug NER)",
                    "pmid_synvar": "PubMed ID (Variomes)",
                },
                selected='Plain Text',
            ),
        ),
        ui.column(
            4,
            ui.input_select(
                "output_type",
                "Output Type",
                {
                    "df": "Dataframe",
                    "biocjson": "BioCjson"
                },
                selected="BioCjson",
            ),

        ),
    ),
    ui.input_text_area("id",
                       "PMC or pmid (one or more, comma separated), word or plain text (less than 5000 characters for BERN2)",
                       placeholder='eg.PMC2882923 or 34216518 or Hardy&Weinberg for query',
                       width='800px', height='200px'),
    ui.output_text('ch'),
    ui.br(),
    ui.input_date('x', 'Date From (Only For Query):', value='2022-01-01'),
    ui.input_numeric('retmax', 'Max. Retrievals (Only For Query):', value=25),
    ui.input_switch("all_results", "Show All", True),
    ui.input_action_button(
        "action", "Submit", class_="btn-primary"
    ),
    ui.download_button("download", "Download results"),
    ui.output_text_verbatim("txt"),
    ui.output_data_frame("table"),
)


def server(input, output, session):
    @output
    @render.image
    def imagen():
        return {
            "src": 'literatura.png',
            "style": "width: 100px; max-height: 100px;",
        }

    @output
    @render.image
    def imagen2():
        return {
            "src": '5907623.png',
            "style": "width: 80px; max-height: 80px;",
        }

    @output
    @render.text
    def ch():
        return f"Character counter: {count_characters(input.id())}"

    @reactive.Calc
    def result():
        if input.input_type() == "PTC":
            result = extract_pubtator(input.id(), input.output_type())
        elif input.input_type() == 'plain_text':
            result = query_plain(input.id(), input.output_type())
        elif input.input_type() == 'pmid_bern':
            result = bern_extract_pmids(input.id(), input.output_type())
        elif input.input_type() == 'query':
            result = extract_pubtator_from_pmcs_query(input.id(), input.x(),
                                                      input.retmax(),
                                                      input.output_type())
        elif input.input_type() == 'plain_drugs':
            result = plain_drugs(input.id(), input.output_type())
        elif input.input_type() == 'pmid_synvar':
            result = synvar_ann(input.id(), input.output_type())
        else:
            input_text = download_data(input.id())
            result = plain_drugs(input_text, input.output_type())
        return result

    @output
    @render.data_frame
    @reactive.event(input.action)
    def table():
        height = 450 if input.all_results() else None
        if isinstance(result(), pd.DataFrame):
            if input.all_results():
                return render.DataGrid(
                    result(),
                    width="100%",
                    height=height,
                    filters=True,
                )
            else:
                return render.DataGrid(
                    result().head(12),
                    width="100%",
                    height="100%",
                    filters=True,
                )

    @output
    @render.text
    @reactive.event(input.action)
    def txt():
        if input.output_type() == 'biocjson':
            if result():
                return result()
            else:
                return f"No results found. Try again."
        else:
            if not isinstance(result(), pd.DataFrame):
                return f"No results found. Try again."


    @session.download()
    def download():
        if input.output_type() == 'df':
            result().to_csv('results.tsv', sep='\t', index=False)
            path = os.path.join(os.path.dirname(__file__), "results.tsv")
            return path

        elif input.output_type() == 'biocjson':
            with open('results.json', 'w') as json_file:
                json.dump(result(), json_file, indent=4)
                path = os.path.join(os.path.dirname(__file__), "results.json")
                return path

    @reactive.Effect
    def _():
        req(input.action())
        ui.notification_show("Retrieving Entities!", duration=5, type="message")


app = App(app_ui, server)
