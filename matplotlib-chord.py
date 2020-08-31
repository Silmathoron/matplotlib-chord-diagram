"""
Tools to draw a chord diagram in python
"""

from collections.abc import Sequence

import matplotlib.patches as patches

from matplotlib.colors import ColorConverter
from matplotlib.path import Path

import numpy as np

from gradient import gradient


LW = 0.3


def dist(points):
    x1, y1 = points[0]
    x2, y2 = points[1]

    return np.sqrt((x2 - x1)*(x2 - x1) + (y2 - y1)*(y2 - y1))


def polar2xy(r, theta):
    return np.array([r*np.cos(theta), r*np.sin(theta)])


def initial_path(start, end, radius, width):
    ''' First 16 vertices and 15 instructions are the same for everyone '''
    if start > end:
        start, end = end, start

    start *= np.pi/180.
    end   *= np.pi/180.

    # optimal distance to the control points
    # https://stackoverflow.com/questions/1734745/
    # how-to-create-circle-with-b%C3%A9zier-curves
    # use 16-vertex curves (4 quadratic Beziers which accounts for worst case
    # scenario of 360 degrees)
    inner = radius*(1-width)
    opt   = 4./3. * np.tan((end-start)/ 16.) * radius
    inter1 = start*(3./4.)+end*(1./4.)
    inter2 = start*(2./4.)+end*(2./4.)
    inter3 = start*(1./4.)+end*(3./4.)

    verts = [
        polar2xy(radius, start),
        polar2xy(radius, start) + polar2xy(opt, start+0.5*np.pi),
        polar2xy(radius, inter1) + polar2xy(opt, inter1-0.5*np.pi),
        polar2xy(radius, inter1),
        polar2xy(radius, inter1),
        polar2xy(radius, inter1) + polar2xy(opt, inter1+0.5*np.pi),
        polar2xy(radius, inter2) + polar2xy(opt, inter2-0.5*np.pi),
        polar2xy(radius, inter2),
        polar2xy(radius, inter2),
        polar2xy(radius, inter2) + polar2xy(opt, inter2+0.5*np.pi),
        polar2xy(radius, inter3) + polar2xy(opt, inter3-0.5*np.pi),
        polar2xy(radius, inter3),
        polar2xy(radius, inter3),
        polar2xy(radius, inter3) + polar2xy(opt, inter3+0.5*np.pi),
        polar2xy(radius, end) + polar2xy(opt, end-0.5*np.pi),
        polar2xy(radius, end)
    ]

    codes = [
        Path.MOVETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
    ]

    return start, end, verts, codes


def ideogram_arc(start, end, radius=1., width=0.2, color="r", alpha=0.7,
                 ax=None):
    '''
    Draw an arc symbolizing a region of the chord diagram.

    Parameters
    ----------
    start : float (degree in 0, 360)
        Starting degree.
    end : float (degree in 0, 360)
        Final degree.
    radius : float, optional (default: 1)
        External radius of the arc.
    width : float, optional (default: 0.2)
        Width of the arc.
    ax : matplotlib axis, optional (default: not plotted)
        Axis on which the arc should be plotted.
    color : valid matplotlib color, optional (default: "r")
        Color of the arc.

    Returns
    -------
    verts, codes : lists
        Vertices and path instructions to draw the shape.
    '''
    start, end, verts, codes = initial_path(start, end, radius, width)

    opt    = 4./3. * np.tan((end-start)/ 16.) * radius
    inner  = radius*(1-width)
    inter1 = start*(3./4.) + end*(1./4.)
    inter2 = start*(2./4.) + end*(2./4.)
    inter3 = start*(1./4.) + end*(3./4.)

    verts += [
        polar2xy(inner, end),
        polar2xy(inner, end) + polar2xy(opt*(1-width), end-0.5*np.pi),
        polar2xy(inner, inter3) + polar2xy(opt*(1-width), inter3+0.5*np.pi),
        polar2xy(inner, inter3),
        polar2xy(inner, inter3),
        polar2xy(inner, inter3) + polar2xy(opt*(1-width), inter3-0.5*np.pi),
        polar2xy(inner, inter2) + polar2xy(opt*(1-width), inter2+0.5*np.pi),
        polar2xy(inner, inter2),
        polar2xy(inner, inter2),
        polar2xy(inner, inter2) + polar2xy(opt*(1-width), inter2-0.5*np.pi),
        polar2xy(inner, inter1) + polar2xy(opt*(1-width), inter1+0.5*np.pi),
        polar2xy(inner, inter1),
        polar2xy(inner, inter1),
        polar2xy(inner, inter1) + polar2xy(opt*(1-width), inter1-0.5*np.pi),
        polar2xy(inner, start) + polar2xy(opt*(1-width), start+0.5*np.pi),
        polar2xy(inner, start),
        polar2xy(radius, start),
    ]

    codes += [
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.CLOSEPOLY,
    ]

    if ax is not None:
        path  = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor=tuple(color) + (alpha,),
                                  edgecolor=tuple(color) + (alpha,), lw=LW)
        ax.add_patch(patch)

    return verts, codes


def chord_arc(start1, end1, start2, end2, radius=1.0, chordwidth=0.7,
              ax=None, color="r", cend="r", alpha=0.7, use_gradient=False):
    '''
    Draw a chord between two regions (arcs) of the chord diagram.

    Parameters
    ----------
    start1 : float (degree in 0, 360)
        Starting degree.
    end1 : float (degree in 0, 360)
        Final degree.
    start2 : float (degree in 0, 360)
        Starting degree.
    end2 : float (degree in 0, 360)
        Final degree.
    radius : float, optional (default: 1)
        External radius of the arc.
    chordwidth : float, optional (default: 0.2)
        Width of the chord.
    ax : matplotlib axis, optional (default: not plotted)
        Axis on which the chord should be plotted.
    color : valid matplotlib color, optional (default: "r")
        Color of the chord or of its beginning if `use_gradient` is True.
    cend : valid matplotlib color, optional (default: "r")
        Color of the end of the chord if `use_gradient` is True.
    alpha : float, optional (default: 0.7)
        Opacity of the chord.
    use_gradient : bool, optional (default: False)
        Whether a gradient should be use so that chord extremities have the
        same color as the arc they belong to.

    Returns
    -------
    verts, codes : lists
        Vertices and path instructions to draw the shape.
    '''
    start1, end1, verts, codes = initial_path(start1, end1, radius, chordwidth)

    start2, end2, verts2, _ = initial_path(start2, end2, radius, chordwidth)

    rchord = radius * (1-chordwidth)

    verts += [polar2xy(rchord, end1), polar2xy(rchord, start2)] + verts2

    verts += [
        polar2xy(rchord, end2),
        polar2xy(rchord, start1),
        polar2xy(radius, start1),
    ]

    codes += [
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
    ]

    if ax is not None:
        path = Path(verts, codes)

        if use_gradient:
            # find the start and end points of the gradient
            p0 = np.array([verts[0], verts[-4]])
            p1 = np.array([verts[15], verts[18]])

            points = p0 if dist(p0) < dist(p1) else p1

            # make the patch
            patch = patches.PathPatch(path, facecolor="none",
                                      edgecolor="none", lw=LW)
            ax.add_patch(patch)  # this is required to clip the gradient

            # make the grid
            x = y = np.linspace(-1, 1, 50)
            meshgrid = np.meshgrid(x, y)

            gradient(points[0], points[1], color, cend, meshgrid, patch, ax,
                     alpha)
        else:
            patch = patches.PathPatch(path, facecolor=tuple(color)+(alpha,),
                                      edgecolor=tuple(color)+(alpha,), lw=LW)

            ax.add_patch(patch)

    return verts, codes


def self_chord_arc(start, end, radius=1.0, chordwidth=0.7, ax=None,
                   color=(1,0,0), alpha=0.7):
    start, end, verts, codes = initial_path(start, end, radius, chordwidth)
    
    rchord = radius * (1-chordwidth)

    verts += [
        polar2xy(rchord, end),
        polar2xy(rchord, start),
        polar2xy(radius, start),
    ]

    codes += [
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
    ]

    if ax is not None:
        path  = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor=tuple(color)+(alpha,),
                                  edgecolor=tuple(color)+(alpha,), lw=LW)
        ax.add_patch(patch)

    return verts, codes


def chord_diagram(mat, names=None, width=0.1, pad=2., gap=0., chordwidth=0.7,
                  ax=None, colors=None, cmap=None, alpha=0.7,
                  use_gradient=False, show=False, **kwargs):
    """
    Plot a chord diagram.

    Parameters
    ----------
    mat : square matrix
        Flux data, mat[i, j] is the flux from i to j
    names : list of str, optional (default: no names)
        Names of the nodes that will be displayed.
    width : float, optional (default: 0.1)
        Width/thickness of the ideogram arc.
    pad : float, optional (default: 2)
        Distance between two neighboring ideogram arcs. Unit: degree.
    gap : float, optional (default: 0)
        Distance between the arc and the beginning of the cord.
    chordwidth : float, optional (default: 0.7)
        Position of the control points for the chords, controlling their shape.
    ax : matplotlib axis, optional (default: new axis)
        Matplotlib axis where the plot should be drawn.
    colors : list, optional (default: from `cmap`)
        List of user defined colors or floats.
    cmap : str or colormap object (default: viridis)
        Colormap to use.
    alpha : float in [0, 1], optional (default: 0.7)
        Opacity of the chord diagram.
    use_gradient : bool, optional (default: False)
        Whether a gradient should be use so that chord extremities have the
        same color as the arc they belong to.
    **kwargs : keyword arguments
        Available kwargs are "fontsize".
    """
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots()

    # mat[i, j]:  i -> j
    num_nodes = len(mat)

    x = mat.sum(axis = 1) # sum over rows

    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    
    # First, set default to viridis color list
    if colors is None:
        colors = np.linspace(0, 1, num_nodes)

    if cmap is None:
        cmap = "viridis"

    if isinstance(colors, (Sequence, np.ndarray)):
        assert len(colors) == num_nodes, "One color per node is required."

        # check color type
        first_color = colors[0]

        if isinstance(first_color, (int, float, np.integer)):
            cm = plt.get_cmap(cmap)
            colors = cm(colors)[:, :3]
        else:
            colors = [ColorConverter.to_rgb(c) for c in colors]
    else:
        raise ValueError("`colors` should be a list.")

    # find position for each start and end
    y = x / np.sum(x).astype(float) * (360 - pad*len(x))

    pos = {}
    arc = []
    nodePos = []
    start = 0

    for i in range(len(x)):
        end = start + y[i]
        arc.append((start, end))
        angle = 0.5*(start+end)

        if -30 <= angle <= 210:
            angle -= 90
        else:
            angle -= 270

        nodePos.append(
            tuple(polar2xy(1.1, 0.5*(start + end)*np.pi/180.)) + (angle,))

        z = (mat[i, :] / x[i].astype(float)) * (end - start)

        ids = np.argsort(z)

        z0 = start

        for j in ids:
            pos[(i, j)] = (z0, z0+z[j])
            z0 += z[j]

        start = end + pad

    for i in range(len(x)):
        start, end = arc[i]

        ideogram_arc(start=start, end=end, radius=1.0, color=colors[i],
                     width=width, alpha=alpha, ax=ax)

        start, end = pos[(i,i)]

        self_chord_arc(start, end, radius=1 - width - gap,
                       chordwidth=0.7*chordwidth, color=colors[i],
                       alpha=alpha, ax=ax)

        color = colors[i]

        for j in range(i):
            cend = colors[j]

            start1, end1 = pos[(i,j)]
            start2, end2 = pos[(j,i)]

            chord_arc(start1, end1, start2, end2, radius=1 - width - gap,
                      chordwidth=chordwidth, color=colors[i], cend=cend,
                      alpha=alpha, ax=ax, use_gradient=use_gradient)

    # add names if necessary
    if names is not None:
        assert len(names) == num_nodes, "One name per node is required."

        prop = {
            "fontsize": kwargs.get("fontsize", 16*0.8),
            "ha": "center",
            "va": "center"
        }

        for pos, name in zip(nodePos, names):
            ax.text(pos[0], pos[1], name, rotation=pos[2], **prop)

    # configure axis
    ax.set_aspect(1)
    ax.axis('off')
    plt.tight_layout()

    if show:
        plt.show()

    return nodePos


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    flux = np.array([[11975,  5871, 8916, 2868],
      [ 1951, 10048, 2060, 6171],
      [ 8010, 16145, 81090, 8045],
      [ 1013,   990,  940, 6907]
    ])

    names = ['non-crystal', 'FCC', 'HCP', 'BCC']

    for grd in (True, False):
        
        chord_diagram(flux, names, use_gradient=grd)

        plt.savefig("example{}.png".format("_gradient" if grd else ""),
                    dpi=600, transparent=True, bbox_inches='tight',
                    pad_inches=0.02)

    plt.show()
