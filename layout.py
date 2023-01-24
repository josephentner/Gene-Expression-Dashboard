from dash import dcc, html
from helpers import get_genes, get_diseases, get_data

genes = get_genes()
diseases = get_diseases()
data = get_data()

def description_card():
    """
    Returns a Div containing dashboard title and description
    """

    return html.Div(
        id="description-card",
        children=[
            html.H1("Gene Expression Dashboard"),
            html.Div(
                id="intro",
                children="A computational tool to aid in understanding gene expression profiles across various tissues and cancer indications.",
            ),
            html.Br()
        ],
    )

def tab_card():
    """
    Returns a Div containing the tabs
    """

    return html.Div(
        id="tab-card",
        children=[
            dcc.Tabs(
                id="tabs",
                value="tab-1",
                children=[
                    dcc.Tab(
                        label="About"
                    ),
                    dcc.Tab(
                        label="Expression Analysis"
                    )
                ]
            )
        ]
    )

def about_tab():
    """
    Returns a Div containing the content for the "About" tab
    """

    return html.Div(
        children=[
            html.P(
                "This dashboard allows for a comparative analysis of \
                gene expression across both healthy and tumor tissue by \
                visualizing the distribution of expression results."
            ),
            html.B("THE DATA"),
            html.P(
                "This dashboard obtains gene expression data from \
                the UCSC Toil RNAseq dataset. This dataset combines \
                samples from three separate studies and harmonizes their  \
                expression results by ridding them of computational batch \
                effects making comparative analysis possible. The samples \
                are taken from the GTEx study for normal tissue, the TCGA \
                study for adult tumor tissue, and the TARGET study  \
                for child tumor tissue, creating a total of almost \
                20,000 samples."
            ),
            html.B("THE ANALYSIS"),
            html.P("The aim of this analysis is to help identify genes \
                that are overexpressed in cancer tissue compared to normal \
                tissue. Select a gene to view the distribution of expression \
                results across all normal tissues (taken from the GTEx \
                study). Then, select any number of cancer indications \
                (taken from the TCGA and TARGET studies) and compare these \
                results to the normal tissue results. To make the analysis \
                more specific, choose which tissue and sample types to \
                include. For example, you may want to exclude cell line \
                samples or focus solely on primary tumor samples." 
            ),
            html.B("DATA SOURCES"),
            html.P("If you are interested in further exploring the data \
                used in this dashboard, below are links to the original \
                datasets."
            ),
            html.P(),
            html.A(
                href="https://xenabrowser.net/datapages/?hub=https://toil.xenahubs.net:443",
                children="UCSC Toil RNAseq Recompute Compendium"
            ),
            html.P(),
            html.A(
                href="https://www.cancer.gov/about-nci/organization/ccg/research/structural-genomics/tcga",
                children="The Cancer Genome Atlas (TCGA)"
            ),
            html.P(),
            html.A(
                href="https://gtexportal.org/home/",
                children="Genotype-Tissue Expression (GTEx)"
            ),
            html.P(),
            html.A(
                href="https://ocg.cancer.gov/programs/target",
                children="Therapeutically Applicable Research To Generate Effective Treatments (TARGET)"
            )
        ]
    )

def analysis_tab():
    """
    Returns a Div containing content for the "Analysis" tab
    """

    return html.Div(
            children=[
                html.Div(
                    children="Determine genes overexpressed in tumors compared to healthy tissue."
                ),
                html.Br(),
                html.Div(
                    children=[
                        html.Div(
                            className="dropdown",
                            children=[
                                html.Div(
                                    children="Select gene"
                                ),
                                dcc.Dropdown(
                                    id="overexpression-gene",
                                    options=genes,
                                    value="ERBB2"
                                )
                            ],
                        ),
                        html.Div(
                            className="dropdown",
                            children=[
                                html.Div(
                                    children="Select indication(s)"
                                ),
                                dcc.Dropdown(
                                    id="overexpression-disease",
                                    options=diseases,
                                    value=["Breast Invasive Carcinoma"],
                                    multi=True
                                )
                            ],
                        ),
                    ]            
                ),
                html.Br(),
                html.Div(
                    children=[
                        html.Div(
                            className="checklist",
                            children=make_checklists(tissue=True)
                        ),
                        html.Div(
                            className="checklist",
                            children=make_checklists(tissue=False)
                        )
                    ]
                ),
                html.Br(),
                html.Button(
                    "Submit", 
                    id="submit-overexpression",
                    className="dropdown",
                    n_clicks=None
                )


            ]
        )

def make_checklists(tissue):
    """
    Returns the Divs for checklists (both tissue and sample type checklists)

    Parameters:
        tissue: True if returning tissue checklist, False if returning sample type checklist (Boolean)
    """
    
    if tissue: 
        tissue_options = sorted([x for x in set(data["Disease/Tissue"]) if x not in diseases if x is not None])

        tissue_checklist = html.Div(
            children=[
                html.Div("Select tissues to display"),
                dcc.Checklist(
                    options=["All"], 
                    value=["All"], 
                    id="all-checklist"),
                dcc.Checklist(
                    options=tissue_options,
                    value=tissue_options,
                    id="tissue-checklist",
                    inline=True,
                )
            ]
        )

        return tissue_checklist
    
    else:
        gtex_sample_types = sorted([x[6:] for x in set(data["Study/Sample Type"]) if x.startswith("GTEX")])
        tcga_sample_types = sorted([x[6:] for x in set(data["Study/Sample Type"]) if x.startswith("TCGA")], reverse=True)
        target_sample_types = sorted([x[8:] for x in set(data["Study/Sample Type"]) if x.startswith("TARGET")], reverse=True)
        sample_type_checklist = html.Div(
            children=[
                html.Div("Select sample types to include"),
                html.Div("GTEX:"),
                dcc.Checklist(
                    id="gtex-sample-type-checklist",
                    options=gtex_sample_types,
                    value=["Normal Tissue"],
                    labelStyle={'display': 'block'}
                ),
                html.Div("TCGA:"),
                dcc.Checklist(
                    id="tcga-sample-type-checklist",
                    className="sample-type-checklist",
                    options=tcga_sample_types,
                    value=["Primary Tumor"],
                    labelStyle={'display': 'block'}
                ),
                html.Div("TARGET:"),
                dcc.Checklist(
                    id="target-sample-type-checklist",
                    className="sample-type-checklist",
                    options=target_sample_types,
                    value=[],
                    labelStyle={'display': 'block'}
                ),
            ]
        )

        return sample_type_checklist
    
def make_layout():
    """
    Returns Div of entire app layout 
    """
    
    return html.Div(
        id="app-container",
        children=[
            html.Div(
                id="left-column",
                className="six columns",
                children=[
                    description_card(),
                    tab_card(),
                    dcc.Loading(
                        className="loading",
                        # color="dark",
                        # fullscreen=True,
                        # delay_show=10,
                        children=[
                            html.Div(
                                id="tabs-content",
                                className="tab-card",
                            )
                        ]
                    )
                ]
            ),
            html.Div(
                id="right-column",
                className="six columns",
                children=[
                    dcc.Loading(
                        className="loading",
                        # fullscreen=True,
                        # color="primary",
                        children=[
                            html.Div(
                                id="graph",
                                children="Submit analysis to view results.",
                                style={"margin-left": "15px", "margin-top": "15px"}
                            )
                        ]

                    )
                ],
            ),
        ]
    )