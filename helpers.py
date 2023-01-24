import pandas as pd
import plotly.express as px
import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import xenaPython as xena

cohort = "TCGA TARGET GTEx"
host = xena.PUBLIC_HUBS["toilHub"]

def get_field(dataset, samples, probe):
    """
    Returns all values for a specific field for a list of samples

    Parameters:
        dataset: name of Xena dataset to query (string)
        samples: list of sample ID"s (list)
        probe: name of field to get values for (string)
    
    Returns:
        field_values: list of values for specified samples (list)
    """

    # get dictionary to map result code to actual results
    field_codes = xena.field_codes(host, dataset, [probe])[0]["code"]
    codes_dict = dict(enumerate(field_codes.split("\t")))
    
    # get field value codes and map to results
    raw_values = xena.dataset_fetch(host, dataset, samples, [probe])[0]
    field_values = list(map(codes_dict.get, raw_values))

    return field_values

def get_data(gene="ERBB2"):
    """
    Gets expression results and relevant metadata for all samples for a specific gene

    Parameters:
        gene: name of gene to query (string)
    
    Returns: 
        data: dataframe that contains all samples, expression results, and metadata (pd.DataFrame)
    """

    # get expression results
    dataset = "TcgaTargetGtex_RSEM_Hugo_norm_count"
    samples = xena.dataset_samples(host, dataset, None)
    expression = xena.dataset_gene_probes_values(host, dataset, samples, gene)[1][0]

    # get relevant metadata (sample type and disease/tissue)
    dataset = "TcgaTargetGTEX_phenotype.txt"
    sample_type = get_field(dataset, samples, "_sample_type")
    disease_tissue = get_field(dataset, samples, "primary disease or tissue")

    # create DataFrame, clean data results, and store data
    data = pd.DataFrame()
    data["Sample"] = samples
    data["Study"] = data["Sample"].apply(lambda x: x.split("-")[0])
    data["Expression"] = expression
    data["Sample Type"] = sample_type
    data["Disease/Tissue"] = disease_tissue
    data["Study/Sample Type"] = data.apply(lambda x: x["Study"] + ": " + x["Sample Type"], axis=1)
    data["Disease/Tissue"] = data["Disease/Tissue"].apply(lambda x : x.split(" - ")[0] if x is not None else x )
    
    return data


def get_genes():
    """
    Grabs all genes from the dataset

    Parameters: None

    Returns: 
        genes: list of all genes (list)
    """
    
    dataset = "TcgaTargetGtex_RSEM_Hugo_norm_count"
    genes = xena.dataset_field(host, dataset)

    return genes

def get_diseases():
    """
    Grabs all diseases from the dataset

    Parameters: None

    Returns: TCGA diseases and TARGET diseases (list)
    """
    
    host = xena.PUBLIC_HUBS["toilHub"]
    dataset = "TcgaTargetGTEX_phenotype.txt"
    probe = "primary disease or tissue"

    # create dictionary that stores all diseases as values
    field_codes = xena.field_codes(host, dataset, [probe])[0]["code"]
    codes_dict = dict(enumerate(field_codes.split("\t")))

    # keep only the diseases that are in the TCGA and TARGET datasets
    tcga_diseases = list(codes_dict.values())[:33]
    target_diseases = list(codes_dict.values())[88:]

    return tcga_diseases + target_diseases

def make_figure(gene, disease, tissues, sample_types):
    """
    Creates the graph (boxplots) based on data and filters

    Parameters:
        gene: name of gene to visualize expression levels (string)
        disease: list of diseases to visualize alongside normal tissue (list)
        tissues: list of normal tissues to include in visualization (list)
        sample_types: list of sample types to include in data (list)

    Returns:
        fig: boxplots visualizing expression distribution for normal amd 
            tumor tissue for a gene (px.box)
    """
    data = get_data(gene)
    
    # filter data
    normal_data = data[(data["Study"] == "GTEX") & (data["Sample Type"].isin(sample_types)) & data["Disease/Tissue"].isin(tissues)]
    cancer_data = data[(data["Disease/Tissue"].isin(list(disease))) & data["Sample Type"].isin(sample_types)]
    graph_data = pd.concat([cancer_data, normal_data], axis=0)

    # visualize data
    color_map = {x: ("#4589ff" if x not in disease else "#fa4d56") for x in list(set(graph_data["Disease/Tissue"]))}
    fig = px.box(
        graph_data, 
        y="Disease/Tissue", 
        x="Expression", 
        color="Disease/Tissue", 
        color_discrete_map=color_map, 
        title=f"{gene} Expression in Healthy vs Tumor Tissue", 
        hover_data=["Sample"],
        width=700,
        height=800
    )
    fig.update_layout(
        showlegend=False,
        # font_family="Arial",
    )

    
    return fig