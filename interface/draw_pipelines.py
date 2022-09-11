import math
from typing import List
from itertools import chain
import networkx as nx
import plotly.graph_objs as go
import streamlit as st
import numpy as np


@st.cache(allow_output_mutation=True)
def get_pipeline_graph(pipeline):
    # Controls for how the graph is drawn
    nodeColor = "#ffbf00"
    nodeSize = 40
    lineWidth = 2
    lineColor = "#ffffff"

    G = pipeline.graph
    initial_coordinate = (0, len(G.nodes))
    fixed_pos = {
        node: np.array([initial_coordinate[0], initial_coordinate[1] - float(idx)])
        for idx, node in enumerate(G.nodes)
    }
    pos = nx.spring_layout(G, pos=fixed_pos, seed=42)

    for node in G.nodes:
        G.nodes[node]["pos"] = list(pos[node])

    # Make list of nodes for plotly
    node_x = []
    node_y = []
    node_name = []
    for node in G.nodes():
        node_name.append(G.nodes[node]["component"].name)
        x, y = G.nodes[node]["pos"]
        node_x.append(x)
        node_y.append(y)

    # Make a list of edges for plotly, including line segments that result in arrowheads
    edge_x = []
    edge_y = []
    for edge in G.edges():
        start = G.nodes[edge[0]]["pos"]
        end = G.nodes[edge[1]]["pos"]
        # addEdge(start, end, edge_x, edge_y, lengthFrac=1, arrowPos = None, arrowLength=0.025, arrowAngle = 30, dotSize=20)
        edge_x, edge_y = addEdge(
            start,
            end,
            edge_x,
            edge_y,
            lengthFrac=0.5,
            arrowPos="end",
            arrowLength=0.04,
            arrowAngle=40,
            dotSize=nodeSize,
        )

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=lineWidth, color=lineColor),
        hoverinfo="none",
        mode="lines",
    )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        textposition="middle right",
        hoverinfo="none",
        text=node_name,
        marker=dict(showscale=False, color=nodeColor, size=nodeSize),
        textfont=dict(size=18),
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )

    fig.update_layout(
        yaxis=dict(scaleanchor="x", scaleratio=1), plot_bgcolor="rgb(14,17,23)"
    )

    return fig


def addEdge(
    start,
    end,
    edge_x,
    edge_y,
    lengthFrac=1,
    arrowPos=None,
    arrowLength=0.025,
    arrowAngle=30,
    dotSize=20,
):

    # Get start and end cartesian coordinates
    x0, y0 = start
    x1, y1 = end

    # Incorporate the fraction of this segment covered by a dot into total reduction
    length = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
    dotSizeConversion = 0.0565 / 20  # length units per dot size
    convertedDotDiameter = dotSize * dotSizeConversion
    lengthFracReduction = convertedDotDiameter / length
    lengthFrac = lengthFrac - lengthFracReduction

    # If the line segment should not cover the entire distance, get actual start and end coords
    skipX = (x1 - x0) * (1 - lengthFrac)
    skipY = (y1 - y0) * (1 - lengthFrac)
    x0 = x0 + skipX / 2
    x1 = x1 - skipX / 2
    y0 = y0 + skipY / 2
    y1 = y1 - skipY / 2

    # Append line corresponding to the edge
    edge_x.append(x0)
    edge_x.append(x1)
    edge_x.append(
        None
    )  # Prevents a line being drawn from end of this edge to start of next edge
    edge_y.append(y0)
    edge_y.append(y1)
    edge_y.append(None)

    # Draw arrow
    if not arrowPos == None:

        # Find the point of the arrow; assume is at end unless told middle
        pointx = x1
        pointy = y1

        eta = math.degrees(math.atan((x1 - x0) / (y1 - y0))) if y1 != y0 else 90.0

        if arrowPos == "middle" or arrowPos == "mid":
            pointx = x0 + (x1 - x0) / 2
            pointy = y0 + (y1 - y0) / 2

        # Find the directions the arrows are pointing
        signx = (x1 - x0) / abs(x1 - x0) if x1 != x0 else +1  # verify this once
        signy = (y1 - y0) / abs(y1 - y0) if y1 != y0 else +1  # verified

        # Append first arrowhead
        dx = arrowLength * math.sin(math.radians(eta + arrowAngle))
        dy = arrowLength * math.cos(math.radians(eta + arrowAngle))
        edge_x.append(pointx)
        edge_x.append(pointx - signx**2 * signy * dx)
        edge_x.append(None)
        edge_y.append(pointy)
        edge_y.append(pointy - signx**2 * signy * dy)
        edge_y.append(None)

        # And second arrowhead
        dx = arrowLength * math.sin(math.radians(eta - arrowAngle))
        dy = arrowLength * math.cos(math.radians(eta - arrowAngle))
        edge_x.append(pointx)
        edge_x.append(pointx - signx**2 * signy * dx)
        edge_x.append(None)
        edge_y.append(pointy)
        edge_y.append(pointy - signx**2 * signy * dy)
        edge_y.append(None)

    return edge_x, edge_y


def add_arrows(
    source_x: List[float],
    target_x: List[float],
    source_y: List[float],
    target_y: List[float],
    arrowLength=0.025,
    arrowAngle=30,
):
    pointx = list(map(lambda x: x[0] + (x[1] - x[0]) / 2, zip(source_x, target_x)))
    pointy = list(map(lambda x: x[0] + (x[1] - x[0]) / 2, zip(source_y, target_y)))
    etas = list(
        map(
            lambda x: math.degrees(math.atan((x[1] - x[0]) / (x[3] - x[2]))),
            zip(source_x, target_x, source_y, target_y),
        )
    )

    signx = list(
        map(lambda x: (x[1] - x[0]) / abs(x[1] - x[0]), zip(source_x, target_x))
    )
    signy = list(
        map(lambda x: (x[1] - x[0]) / abs(x[1] - x[0]), zip(source_y, target_y))
    )

    dx = list(map(lambda x: arrowLength * math.sin(math.radians(x + arrowAngle)), etas))
    dy = list(map(lambda x: arrowLength * math.cos(math.radians(x + arrowAngle)), etas))
    none_spacer = [None for _ in range(len(pointx))]
    arrow_line_x = list(
        map(lambda x: x[0] - x[1] ** 2 * x[2] * x[3], zip(pointx, signx, signy, dx))
    )
    arrow_line_y = list(
        map(lambda x: x[0] - x[1] ** 2 * x[2] * x[3], zip(pointy, signx, signy, dy))
    )

    arrow_line_1x_coords = list(chain(*zip(pointx, arrow_line_x, none_spacer)))
    arrow_line_1y_coords = list(chain(*zip(pointy, arrow_line_y, none_spacer)))

    dx = list(map(lambda x: arrowLength * math.sin(math.radians(x - arrowAngle)), etas))
    dy = list(map(lambda x: arrowLength * math.cos(math.radians(x - arrowAngle)), etas))
    none_spacer = [None for _ in range(len(pointx))]
    arrow_line_x = list(
        map(lambda x: x[0] - x[1] ** 2 * x[2] * x[3], zip(pointx, signx, signy, dx))
    )
    arrow_line_y = list(
        map(lambda x: x[0] - x[1] ** 2 * x[2] * x[3], zip(pointy, signx, signy, dy))
    )

    arrow_line_2x_coords = list(chain(*zip(pointx, arrow_line_x, none_spacer)))
    arrow_line_2y_coords = list(chain(*zip(pointy, arrow_line_y, none_spacer)))

    x_arrows = arrow_line_1x_coords + arrow_line_2x_coords
    y_arrows = arrow_line_1y_coords + arrow_line_2y_coords

    return x_arrows, y_arrows
