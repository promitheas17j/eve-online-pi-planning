#!/usr/bin/env python3

# TODO: Implement logic to check if a given production is possible in a certain system given the planets in it
# TODO: Implement logic to only render the image of the production chain for the target product nad ignore everything irrelevant

from graphviz import Digraph
import json

# Load planet data
def load_pi_data():
    """
    Loads the adjacency graph data for the entire planetary interaction production chain and returns it in the form of 3 variables:
        tiers : What level of the production process each item is at
        planetary_graph : The adjacency graph itself, consisting of nodes (items) and edges (their production requirements)
        colors : The color that is assigned to each tier of item to be used later when generating the image
    """
    with open("planetary_data.json", "r") as file:
        data = json.load(file)
    tiers = data["tiers"]
    planetary_graph = data["dependencies"]
    colors = data["colors"]

    return tiers, planetary_graph, colors

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


def find_requirements(graph, product, visited=None):
    if visited is None:
        visited = set()
    if product in visited:
        return
    visited.add(product)

    requirements = set()

    for req in graph.get(product, []):
        if req in graph:
            requirements.add(req)
            requirements.update(find_requirements(graph, req, visited))

    return requirements

def extract_subgraph(graph, product):
    requirements = find_requirements(graph, product)
    subgraph = {k: [v for v in graph[k] if v in requirements] for k in requirements}
    return subgraph

def get_tier(item):
    for tier, items in data["tiers"].items():
        if item in items:
            return tier
    return None

def visualise_subgraph(graph, product):
    output_file = product + "_chain"
    subgraph = extract_subgraph(graph, product)

    dot = Digraph(format="png")
    dot.attr(rankdir="LR")

    tier_nodes = {"P0": [], "P1": [], "P2": [], "P3": [], "P4": []}

    for item in subgraph:
        tier = get_tier(item)
        color = colors.get(tier, "white")
        dot.node(item, style="filled", fillcolor=color)

        if tier:
            tier_nodes[tier].append(item)

    for item, requirements in subgraph.items():
        for req in requirements:
            dot.edge(req, item)

    for tier, items in tier_nodes.items():
        if items:
            dot.body.append('f{{rank=same; {" ".join(items)}}}')

    dot.body.append(f'{{rank=max; {product}}}')

    dot.render(output_file, view=True)

if __name__ == '__main__':
    tiers, planetary_graph, colors = load_pi_data()
    requirements = find_requirements(planetary_graph, "Robotics")
    print("Required materials: ", requirements)
    visualise_subgraph(planetary_graph, "Robotics")
    # visualise_graph(planetary_graph, tiers, colors)
