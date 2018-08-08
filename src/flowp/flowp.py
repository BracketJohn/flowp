"""Approximate flowpipes of an LHA for n steps."""
from itertools import product
from typing import Any, Dict, List, Optional

import numpy as np
import plotly.graph_objs as go
from plotly.offline import plot
import scipy.linalg
import scipy.spatial


def approx(initial_location: List[np.ndarray], flow: np.ndarray,
           bloating: List[np.ndarray], step_size: float=1, plot: bool=True):
    """Approximate flowpipes of an LHA.

    Parameters
    ----------
    initial_location: List[np.ndarray]
        Initial starting valuation, expecting this to be a 2D V-representation.

    flow: np.ndarray
        Flow in current location, used to calculate flow pipe.

    bloating: List[np.ndarray]
        Bloating factor for over approximation. Expecting this to be a
        2D V-representation, it will be added to the flowpipe by calculating
        the minkowski sum.

    step_size: float
        Delta used for matrix exponential calculation. Larger delta results in
        larger and fewer flowpipes, which reduces computational complexity.
        This however also reduces precision.

    plot: bool
        Whether to plot resulting V-representation or just return it.

    Returns
    -------
    polytopes: List[Dict[str, Any]]
        Polytope dicts, each representing a polytope like:
        ```
            {
                'name': name,
                'vertices': [
                    [x1, y1],
                    ...,
                ],
            }
        ```
        The V-representation of each polytope is minimal.

    """
    matrix_exp = scipy.linalg.expm(step_size * flow)
    flowpipe = [matrix_exp @ v for v in initial_location]
    if bloating:
        bloated_flowpipe = [v1 + v2 for v1, v2 in product(flowpipe, bloating)]
    else:
        bloated_flowpipe = flowpipe

    bloated_flowpipe_with_init = bloated_flowpipe + initial_location

    polytopes = [
            {
                'name': 'Initial Valuation I',
                'vertices': initial_location
            },
            {
                'name': 'mat_exp(flow) * I',
                'vertices': flowpipe
            },
            {
                'name': 'Omega_1: convHull(mink_sum(mat_exp(flow) * I, bloat), I)',
                'vertices': bloated_flowpipe_with_init
            },
        ]

    if bloating:
        polytopes.append({
            'name': 'Bloating',
            'vertices': bloating
        })

    for polytope in polytopes:
        conv_hull = scipy.spatial.ConvexHull(polytope['vertices'])
        polytope['vertices'] = [conv_hull.points[vert]
                                for vert in conv_hull.vertices]

    if plot:
        return plot_polytopes(polytopes)

    return polytopes


def plot_polytopes(polytopes: List[Dict[str, Any]]) -> None:
    """Plot result of flowpipe construction.

    Parameters
    ----------
    polytopes: List[Dict[str, Any]]
        Polytope dicts, each representing a polytope like:
        ```
            {
                'name': name,
                'vertices': [
                    [x1, y1],
                    ...,
                ],
            }
        ```

    """
    centers = np.empty((0, 2))
    for polytope in polytopes:
        poly = np.array(polytope['vertices'])
        centers = np.append(centers, [poly[0] - [0, 0.1]], axis=0)

    labels_x = centers[:, 0]
    labels_y = centers[:, 1]

    label_trace = go.Scatter(
        x=labels_x,
        y=labels_y,
        text=[polytope['name'] for polytope in polytopes],
        mode='text',
    )
    data = [label_trace]
    layout = {
        'shapes': [{
                'type': 'path',
                'path': _plot_path(polytope['vertices']),
                'fillcolor': f'rgba({", ".join(str(n) for n in np.random.randint(0, 240, 3))}, 0.2)',
            } for polytope in polytopes
        ],
        'xaxis': {
            'zerolinecolor': 'rgba(0, 0, 0, 0.15)',
        },
        'yaxis': {
            'zerolinecolor': 'rgba(0, 0, 0, 0.15)',
        },
    }
    fig = {
        'data': data,
        'layout': layout,
    }
    plot(fig)


def _plot_path(v_repr: List[np.ndarray]) -> Optional[str]:
    """Generate plotly path from a convex hull represenation.

    Parameters
    ----------
    v_repr: List[np.ndarray]
        Coordinates of all vertices belonging to a polytope.

    Returns
    -------
    path: str
        Path usable by plotly to plot polygon.

    """
    if not v_repr:
        return None

    start = _strip_brackets(v_repr[0])
    return (f'M {start} ' +
            ' '.join(f'L {_strip_brackets(v)}' for v in v_repr[1:]) +
            f' L {start}')


def _strip_brackets(v: np.ndarray) -> str:
    """Strip brackets from np coordinate to use for string concat.

    Parameters
    ----------
    v: np.ndarray
        Vertex to strip.

    Returns
    -------
    v_repr: str
        Comma seperated coordinates of v.

    """
    return ', '.join(str(coord) for coord in v)
