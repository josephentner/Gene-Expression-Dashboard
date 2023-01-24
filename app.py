from dash import dash, Dash, dcc, Input, Output, State, callback_context

from helpers import make_figure
from layout import make_layout, about_tab, analysis_tab


# create app
app = Dash(__name__)
app.title = "Gene Expression Dashboard"

server = app.server
app.config.suppress_callback_exceptions = True

# create layout for app 
app.layout = make_layout()

@app.callback(
    Output("tabs-content", "children"),
    Input("tabs", "value")
)
def render_tab(tab):
    """
    Callback function to display content of clicked tab
    
    Parameters:
        tab: value of currently clicked tab (string)
    Returns: 
        html.Div of tab content
    """
    if tab == "tab-1":
        return about_tab()
    if tab == "tab-2":
        return analysis_tab()

@app.callback(
    Output("graph", "children"),
    Output("graph", "style"),
    Input("submit-overexpression", "n_clicks"),
    [
    State("overexpression-gene", "value"),
    State("overexpression-disease", "value"),
    State("tissue-checklist", "value"),
    State("gtex-sample-type-checklist", "value"),
    State("tcga-sample-type-checklist", "value"),
    State("target-sample-type-checklist", "value")
    ]
)
def render_graph(n_clicks, gene, disease, tissues, gtex_sample_types, tcga_sample_types, target_sample_types):
    """
    Callback function to render graph based on input filters

    Parameters: 
        n_clicks: number of times submit button has been pressed (int|None)
        gene: gene user selects (string)
        disease: disease or multiple disease user selects to display (list)
        tissues: tissues to user selects to display (list)
        gtex_sample_types: GTEx sample types to include (list)
        tcga_sample_types: TCGA sample types to include (list)
        target_sample_types: TARGET sample types to include (list)
    
    Returns:
        graph: dcc.Graph of graph to display or string prompting user to submit graph (dcc.Graph|string)
        style: determines position of graph (dict)
    """

    if n_clicks != None:
        sample_types = gtex_sample_types + tcga_sample_types + target_sample_types
        figure = make_figure(gene, disease, tissues, sample_types)
        graph = dcc.Graph(
            figure=figure
        ) 

        # graph positioned top-left of parent Div
        style = {"margin-left": "0px", "margin-top": "0px"}

        return graph, style
    
    else:
        return dash.no_update, dash.no_update

    
@app.callback(
    Output("tissue-checklist", "value"),
    Output("all-checklist", "value"),
    Input("tissue-checklist", "value"),
    Input("all-checklist", "value"),
    [
    State("tissue-checklist", "options")
    ]
)
def sync_checklists(tissues_selected, all_selected, options):
    """
    Callback function to two sync checklists 
    i.e. when "all" option is checked, rest of other checklist becomes checked
    taken from https://dash.plotly.com/advanced-callbacks

    Parameters: 
        tissues_selected: tissues user has selected (list)
        all_selected: if "all" is selected (list)
        options: all possible options of tissue checklist (list)
    
    Returns:
        tissues_selected: tissues user has selected (list)
        all_selected: if "all" is selected (list)
    """

    ctx = callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id == "tissue-checklist":
        all_selected = ["All"] if set(tissues_selected) == set(options) else []
    else:
        tissues_selected = options if all_selected else []
    
    return tissues_selected, all_selected

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)

