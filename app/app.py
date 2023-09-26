# app.py
import json
import shinyswatch
import os
from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui
from shiny.types import ImgData
from code import count_characters, extract_pubtator, extract_pubtator_from_pmcs, query_plain, \
    extract_pubtator_from_pmcs_query, plain_drugs, download_from_PMC, download_from_PubMed, bern_extract_pmids

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
            6,
            ui.h2("Biomedical Entity Recognition"),
        ),
    ),
    ui.row(
        ui.column(
            4,
            ui.input_select(
                "input_type",
                "Query Type",
                {
                    "PMC": "PMC (PubTator)",
                    "pmid": "PubMed ID (PubTator)",
                    "plain_text": "Plain Text (BERN2)",
                    "pmid_bern": "PubMed ID (BERN2)",
                    "plain_drugs": "Plain Text (Drug NER)",
                    "pmc_drugs": "PMC (Drug NER)",
                    "pmid_drugs": "PubMed ID (Drug NER)",
                    "query": "Word in PubMed Central (PubTator)",
                },
                selected='Plain Text',
            ),
        ),
        ui.column(
            4,
            ui.input_select(
                "output_type",
                "Output type",
                {
                    "df": "Dataframe",
                    "biocjson": "BioCjson"
                },
                selected="BioCjson",
            ),

        ),
    ),
    ui.input_text_area("id",
                       "PMC or pmid (one or more, comma separated), word or plain text (less than 5000 characters)",
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
            "style": "width: 80px; max-height: 80px;",
        }

    @output
    @render.text
    def ch():
        return f"Character counter: {count_characters(input.id())}"

    @reactive.Calc
    def result():
        if input.input_type() == "PMC":
            result = extract_pubtator_from_pmcs(input.id(), input.output_type())
        elif input.input_type() == 'plain_text':
            result = query_plain(input.id(), input.output_type())
        elif input.input_type() == 'pmid':
            result = extract_pubtator(input.id(), input.output_type())
        elif input.input_type() == 'pmid_bern':
            result = bern_extract_pmids(input.id(), input.output_type())
        elif input.input_type() == 'query':
            result = extract_pubtator_from_pmcs_query(input.id(), input.x(),
                                                      input.retmax(),
                                                      input.output_type())
        elif input.input_type() == 'plain_drugs':
            result = plain_drugs(input.id(), input.output_type())
        elif input.input_type() == 'pmid_drugs':
            input_text = download_from_PubMed(input.id())
            result = plain_drugs(input_text, input.output_type())
        else:
            input_text = download_from_PMC(input.id())
            result = plain_drugs(input_text, input.output_type())
        return result

    @output
    @render.data_frame
    @reactive.event(input.action)
    def table():
        if result():
            if input.output_type() == 'df':
                if input.all_results():
                    return render.DataGrid(
                        result(),
                        width="100%",
                        height="100%",
                        filters=True,
                    )
                else:
                    return render.DataGrid(
                        result().head(15),
                        width="100%",
                        height="100%",
                        filters=True,
                    )
        else:
            return txt()

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
