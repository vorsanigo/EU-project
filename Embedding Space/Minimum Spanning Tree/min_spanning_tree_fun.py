import networkx as nx
from scipy.spatial.distance import pdist, squareform
from sklearn.neighbors import NearestNeighbors, kneighbors_graph
from scipy.sparse.csgraph import connected_components
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.spatial import Delaunay
from scipy.spatial import Delaunay
from itertools import combinations
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import ConvexHull

from shapely.geometry import Point, Polygon


def compute_mst(points):

    if len(points) < 2:
        return None, 0
    
    # pairwise distance matrix
    D = squareform(pdist(points))
    
    # build graph
    G = nx.Graph()
    n = len(points)
    for i in range(n):
        for j in range(i+1, n):
            G.add_edge(i, j, weight=D[i, j])
    
    # MST
    mst = nx.minimum_spanning_tree(G)

    # MST length
    mst_length = sum(edge[2]["weight"] for edge in mst.edges(data=True))
    
    return mst, mst_length

def find_min_k_for_connectivity(points, k_candidates=None, metric="euclidean", n_jobs=-1):
    """
    Try candidate k values and return the smallest k that yields a single connected component.
    points: (n, d) numpy array
    k_candidates: list of ints to try (will be sorted). If None, uses a sensible default.
    Returns: chosen_k, components_dict where components_dict[k] = n_components
    """
    
    n = len(points)
    if k_candidates is None:
        # sensible default: geometric progression around log(n)
        k0 = max(2, int(np.log(n)))
        k_candidates = sorted({2, 3, 5, k0, k0*2, 10, 15, 20, 30, 50, 75, 100})
    # ensure valid ks and <= n-1
    k_candidates = [int(k) for k in k_candidates if 1 < k < n]

    comp_results = {}
    chosen_k = None

    for k in k_candidates:
        #print(f"Testing k={k} ...")
        # build kneighbors graph (distance mode)
        A = kneighbors_graph(points, n_neighbors=k, mode="distance", include_self=False, n_jobs=n_jobs)
        n_components, labels = connected_components(A, directed=False, return_labels=True)
        comp_results[k] = n_components
        #print(f"  -> components: {n_components}")
        if n_components == 1:
            chosen_k = k
            break

    return chosen_k, comp_results



def delaunay_mst(points, plot=False):
    """
    Compute the Minimum Spanning Tree (MST) from a set of 2D points
    using the Delaunay triangulation to limit edge computation.

    Parameters
    ----------
    points : np.ndarray
        Array of shape (n_points, 2) with coordinates.
    plot : bool, optional
        If True, plot the points and the MST.

    Returns
    -------
    mst : networkx.Graph
        The minimum spanning tree graph.
    total_length : float
        Total length (sum of edge weights) of the MST.
    """

    if len(points) < 4:
        mst, total_length = compute_mst(points)
    
    else:
        # --- Delaunay triangulation ---
        tri = Delaunay(points)

        # --- Collect unique edges ---
        edges = set()
        for simplex in tri.simplices:
            for i, j in combinations(simplex, 2):
                edges.add(tuple(sorted((i, j))))

        # --- Build weighted graph ---
        G = nx.Graph()
        for i, j in edges:
            dist = np.linalg.norm(points[i] - points[j])
            G.add_edge(i, j, weight=dist)
        

        # --- Compute MST ---
        mst = nx.minimum_spanning_tree(G)#algorithm='kruskal'

        # --- Compute total MST length ---
        total_length = sum(d['weight'] for _, _, d in mst.edges(data=True))

        # --- Optional plot ---
        if plot:
            plt.figure(figsize=(8, 8))
            plt.scatter(points[:, 0], points[:, 1], s=2, color='gray', alpha=0.6, label='Points')
            for u, v in mst.edges():
                plt.plot([points[u, 0], points[v, 0]],
                        [points[u, 1], points[v, 1]],
                        c='red', lw=0.5, alpha=0.7)
            plt.title(f"MST (Total length = {total_length:.2f})")
            plt.axis('equal')
            plt.legend()
            plt.show()

    return mst, total_length


def random_points_in_hull(n, hull_test):
    points = []
    while len(points) < n:
        p = np.random.rand(2)  # sample in [0,1]^2 bounding box
        if hull_test.find_simplex(p) >= 0:
            points.append(p)
    return np.array(points)



def sample_points_in_bounding_box(X, size_sample):
    """
    Uniformly sample n_samples points inside the convex hull
    of 'points' (shape: [n_points, n_dims]) using Dirichlet weights.
    """
    '''hull = ConvexHull(points)
    vertices = points[hull.vertices]  # get hull vertices (subset)
    m, d = vertices.shape

    # Draw random weights from a Dirichlet distribution
    weights = np.random.dirichlet(alpha=np.ones(m), size=n_samples)

    # Compute convex combinations
    samples = weights @ vertices'''
    mins = X.min(axis=0)
    maxs = X.max(axis=0)
    X_null = np.random.uniform(mins, maxs, size=size_sample)#X.shape

    return X_null



def sample_in_hull_rejection(points, n_samples, random_state=None):
    rng = np.random.default_rng(random_state)
    
    # Compute convex hull polygon
    hull = ConvexHull(points)
    poly = Polygon(points[hull.vertices])
    
    # Bounding box
    min_x, min_y, max_x, max_y = poly.bounds
    
    samples = []
    while len(samples) < n_samples:
        xs = rng.uniform(min_x, max_x, size=n_samples)
        ys = rng.uniform(min_y, max_y, size=n_samples)
        for x, y in zip(xs, ys):
            if poly.contains(Point(x, y)):
                samples.append((x, y))
            if len(samples) >= n_samples:
                break
    return np.array(samples)



def in_hull(points, n_samples):
    
    # build convex hull
    hull = ConvexHull(points)
    A = hull.equations[:, :-1]
    b = -hull.equations[:, -1]

    #in_hull_points = np.all(A @ points.T <= b[:, None], axis=0)

    # bounding box of the data
    mins, maxs = points.min(axis=0), points.max(axis=0)

    # sample uniformly in bounding box and keep points inside
    #n_samples = 1000
    samples = []
    while len(samples) < n_samples:
        # sample candidates in the box
        cand = np.random.uniform(mins, maxs, size=(n_samples, points.shape[1]))
        mask = np.all(A @ points.T <= b[:, None], axis=0) #in_hull(cand, A, b)
        samples.extend(cand[mask])
        samples = samples[:n_samples]  # keep only needed amount

    samples = np.array(samples)

    return samples


def sample_points_in_convex_hull(X, n_samples, method="auto", random_state=None):
    """
    Sample points inside the convex hull defined by the real data points X.

    Parameters
    ----------
    X : array-like, shape (n_points, n_dims)
        Real data points defining the convex hull.
    n_samples : int, optional
        Number of points to sample inside the convex hull.
    method : {"auto", "rejection", "convex"}, optional
        Sampling method:
          - "rejection": uniform sampling with rejection
          - "convex": random convex combinations of hull vertices
          - "auto": use rejection if dim <= 10, else convex
    random_state : int, optional
        Random seed for reproducibility.

    Returns
    -------
    samples : ndarray, shape (n_samples, n_dims)
        Points inside the convex hull.
    """

    rng = np.random.default_rng(random_state)
    X = np.asarray(X)
    n_points, n_dims = X.shape

    # Compute convex hull
    hull = ConvexHull(X)
    A = hull.equations[:, :-1]
    b = hull.equations[:, -1]

    def in_hull(points):
        """Check if points are inside convex hull."""
        return np.all(A @ points.T + b[:, None] <= 1e-12, axis=0)

    # Select sampling method
    if method == "auto":
        method = "rejection" if n_dims <= 10 else "convex"

    print(method)

    # --- 1️⃣ Rejection sampling (approximately uniform)
    if method == "rejection":
        mins, maxs = X.min(axis=0), X.max(axis=0)
        samples = []
        while len(samples) < n_samples:
            candidates = rng.uniform(mins, maxs, size=(n_samples, n_dims))
            mask = in_hull(candidates)
            samples.extend(candidates[mask])
        samples = np.array(samples[:n_samples])

    # --- 2️⃣ Convex combination sampling (always inside)
    elif method == "convex":
        n_vertices = len(hull.vertices)
        vertices = X[hull.vertices]
        w = rng.random(size=(n_samples, n_vertices))
        w /= w.sum(axis=1, keepdims=True)
        samples = w @ vertices

    else:
        raise ValueError("method must be one of {'auto', 'rejection', 'convex'}")

    return samples

# Example
'''np.random.seed(0)
pts = np.random.rand(20, 2)
samples = sample_in_hull_rejection(pts, n_samples=1000)

plt.figure(figsize=(6, 6))

# Plot all initial points
plt.scatter(pts[:, 0], pts[:, 1], color="blue", label="Original points")
plt.savefig('prova1.png')


plt.figure(figsize=(6, 6))
plt.scatter(pts[:, 0], pts[:, 1], color="red", label="Hull points")
plt.scatter(samples[:, 0], samples[:, 1], s=5, alpha=0.5, label="Samples")
plt.legend()
plt.show()

plt.savefig('prova.png')
'''