#!/usr/bin/env python3

# TODO: Implement logic to check if a given production is possible in a certain system given the planets in it
# TODO: Implement logic to only render the image of the production chain for the target product nad ignore everything irrelevant

from graphviz import Digraph
import json

# Load planet data
with open("planetary_data.json", "r") as file:
    data = json.load(file)

tiers = data["tiers"]
planetary_graph = data["dependencies"]
colors = data["colors"]

def visualise_graph(graph, tiers, colors):
    dot = Digraph(format="png")
    dot.attr(rankdir="LR")

    for tier, items in tiers.items():
        with dot.subgraph() as sub:
            sub.attr(rank="same")
            for item in items:
                sub.node(item, style="filled", fillcolor=colors[tier], shape="box")

    # Add edges
    for product, inputs in graph.items():
        for inp in inputs:
            dot.edge(inp, product)

    dot.render("pi_graph", view=True)

visualise_graph(planetary_graph, tiers, colors)
