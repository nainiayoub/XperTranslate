import streamlit as st
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
import xml.etree.ElementTree as ET
import networkx as nx
from pyvis.network import Network
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import tempfile
import base64
from htbuilder.units import percent, px
from htbuilder.funcs import rgba, rgb

def parse_xml(file_content):
    root = ET.fromstring(file_content)
    species_data = {}

    for coded_description in root.findall('.//CodedDescription'):
        species_id = coded_description.get('id')
        label = coded_description.find('.//Label').text
        detail = coded_description.find('.//Detail').text
        characteristics = []

        for categorical in coded_description.findall('.//Categorical'):
            for state in categorical.findall('.//State'):
                characteristics.append(state.get('ref'))

        species_data[species_id] = {
            'label': label,
            'detail': detail,
            'characteristics': characteristics
        }

    return species_data

def calculate_similarity(species_data):
    species_ids = list(species_data.keys())
    characteristics_matrix = [' '.join(species_data[species_id]['characteristics']) for species_id in species_ids]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(characteristics_matrix)
    similarity_matrix = cosine_similarity(tfidf_matrix)

    return species_ids, similarity_matrix

def create_graph(species_ids, similarity_matrix, species_data, threshold):
    G = nx.Graph()

    for i, species_id in enumerate(species_ids):
        G.add_node(species_id, label=species_data[species_id]['label'], title=species_data[species_id]['detail'])

    for i in range(len(species_ids)):
        for j in range(i + 1, len(species_ids)):
            if similarity_matrix[i][j] > threshold:
                G.add_edge(species_ids[i], species_ids[j], weight=round(similarity_matrix[i][j], 2))

    return G

def plot_interactive_graph(G):
    net = Network(notebook=True, height="600px", width="100%", bgcolor="#ffffff", font_color="black")  # Changed background to white

    # Add nodes
    for node, node_attrs in G.nodes(data=True):
        net.add_node(node, label=node_attrs['label'], title=node_attrs['title'])

    # Add edges
    for source, target, edge_attrs in G.edges(data=True):
        weight = edge_attrs['weight']
        net.add_edge(source, target, value=weight, title=f"Similarity: {weight}")

    net.toggle_physics(True)
    net.show_buttons(filter_=['physics'])

    for node in net.nodes:
        node['size'] = 20
        node['color'] = '#6EAECF'

    # Save and read the file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmpfile:
        net.save_graph(tmpfile.name)
        with open(tmpfile.name, 'r', encoding='utf-8') as f:
            html_string = f.read()

    return html_string


def layout(*args):

    style = """
    <style>
      MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
     
     img{
        background-color: #ddd;
     }
     img:hover{
        background-color: rgba(59,130,246,.5);
        margin: 0 auto;
     }
    </style>
    """

    style_div = styles(
        position="fixed",
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        color="black",
        text_align="center",
        height="auto",
        opacity=1
    )

    style_hr = styles(
        # display="block",
        # margin=px(8, 8, "auto", "auto"),
        # border_style="inset",
        # border_width=px(2)
    )

    body = p()
    foot = div(
        style=style_div
    )(
        hr(
            style=style_hr
        ),
        body
    )

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)

        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)

def image(src_as_string, **style):
    return img(src=src_as_string, style=styles(**style), width=150)

def link(link, text, **style):
    return a(_href=link, _target="_blank", style=styles(**style))(text)

def footer():
    myargs = [
        # "Made by ",
        # link("https://twitter.com/nainia_ayoub", "@nainia_ayoub"),
        # br(),
        # link("https://xper3.fr/en/", image('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ-KAmBjq2oHr29bytRvh_1s1HlxWI9Oi0_Wg&s')),
    ]
    layout(*myargs)
