import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as hr
from scipy.spatial.distance import squareform
import riskfolio.AuxFunctions as af
import riskfolio.DBHT as db

def plot_dendrogram(
    returns,
    custom_cov=None,
    codependence="pearson",
    linkage="ward",
    k=None,
    max_k=10,
    bins_info="KN",
    alpha_tail=0.05,
    leaf_order=True,
    title="",
    height=5,
    width=12,
    ax=None,
):
    if not isinstance(returns, pd.DataFrame):
        raise ValueError("returns must be a DataFrame")

    if ax is None:
        fig = plt.gcf()
        ax = fig.gca()
        fig.set_figwidth(width)
        fig.set_figheight(height)
    else:
        fig = ax.get_figure()

    labels = np.array(returns.columns.tolist())

    # Calculating codependence matrix and distance metric
    if codependence in {"pearson", "spearman"}:
        codep = returns.corr(method=codependence)
        dist = np.sqrt(np.clip((1 - codep) / 2, a_min=0.0, a_max=1.0))
    elif codependence in {"abs_pearson", "abs_spearman"}:
        codep = np.abs(returns.corr(method=codependence[4:]))
        dist = np.sqrt(np.clip((1 - codep), a_min=0.0, a_max=1.0))
    elif codependence in {"distance"}:
        codep = af.dcorr_matrix(returns).astype(float)
        dist = np.sqrt(np.clip((1 - codep), a_min=0.0, a_max=1.0))
    elif codependence in {"mutual_info"}:
        codep = af.mutual_info_matrix(returns, bins_info).astype(float)
        dist = af.var_info_matrix(returns, bins_info).astype(float)
    elif codependence in {"tail"}:
        codep = af.ltdi_matrix(returns, alpha_tail).astype(float)
        dist = -np.log(codep)
    elif codependence in {"custom_cov"}:
        codep = af.cov2corr(custom_cov).astype(float)
        dist = np.sqrt(np.clip((1 - codep) / 2, a_min=0.0, a_max=1.0))

    # Hierarchical clustering
    dist = dist.to_numpy()
    dist = pd.DataFrame(dist, columns=codep.columns, index=codep.index)
    if linkage == "DBHT":
        # different choices for D, S give different outputs!
        D = dist.to_numpy()  # dissimilarity matrix
        if codependence in {"pearson", "spearman", "custom_cov"}:
            S = (1 - dist**2).to_numpy()
        else:
            S = codep.copy().to_numpy()  # similarity matrix
        (_, _, _, _, _, clustering) = db.DBHTs(
            D, S, leaf_order=leaf_order
        )  # DBHT clustering
    else:
        p_dist = squareform(dist, checks=False)
        clustering = hr.linkage(p_dist, method=linkage, optimal_ordering=leaf_order)

    # Ordering clusterings
    permutation = hr.leaves_list(clustering)
    permutation = permutation.tolist()

    # optimal number of clusters
    if k is None:
        k = af.two_diff_gap_stat(codep, dist, clustering, max_k)

    root, nodes = hr.to_tree(clustering, rd=True)
    nodes = [i.dist for i in nodes]
    nodes.sort()
    nodes = nodes[::-1][: k - 1]
    color_threshold = np.min(nodes)

    colors = af.color_list(k)  # color list

    hr.set_link_color_palette(colors)
    hr.dendrogram(
        clustering, color_threshold=color_threshold, above_threshold_color="grey", ax=ax
    )
    an = hr.dendrogram(
        clustering, color_threshold=color_threshold, above_threshold_color="grey", ax=ax
    )
    hr.set_link_color_palette(None)

    ax.set_xticklabels(labels[permutation], rotation=90, ha="center")

    i = 0
    for coll in ax.collections[:-1]:  # the last collection is the ungrouped level
        xmin, xmax = np.inf, -np.inf
        ymax = -np.inf
        for p in coll.get_paths():
            (x0, _), (x1, y1) = p.get_extents().get_points()
            xmin = min(xmin, x0)
            xmax = max(xmax, x1)
            ymax = max(ymax, y1)
        rec = plt.Rectangle(
            (xmin - 4, 0),
            xmax - xmin + 8,
            ymax * 1.05,
            coll.get_color()[0],  # coll.get_color()[0],facecolor=colors[i]
            alpha=0.2,
            edgecolor="none",
        )
        ax.add_patch(rec)
        i += 1

    ax.set_yticks([])
    ax.set_yticklabels([])
    for i in {"right", "left", "top", "bottom"}:
        side = ax.spines[i]
        side.set_visible(False)

    if title == "":
        title = (
            "Assets Dendrogram ("
            + codependence.capitalize()
            + " & "
            + linkage
            + " linkage)"
        )

    ax.set_title(title)

    try:
        fig.tight_layout()
    except:
        pass

    return ax, an
