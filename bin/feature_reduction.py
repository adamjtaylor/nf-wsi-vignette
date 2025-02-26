#!/usr/bin/env python

import umap
import numpy as np
import sys
from tiatoolbox.wsicore.wsireader import WSIReader
from tiatoolbox.tools import patchextraction
from tiatoolbox.models.engine.patch_predictor import PatchPredictor
import matplotlib as mpl
import matplotlib.pyplot as plt
import igraph as ig
import leidenalg as la

wsi_path = sys.argv[1]
features_path = sys.argv[2]
positions_path = sys.argv[3]
model = sys.argv[4]
model = "H-optimus-0"

# if the model is prov-gigapath then patch shape is 256x256
if model == "Prov-GigaPath":
    patch_shape = [256, 256]
else:
    patch_shape = [224, 224]

# Configure matplotlib
mpl.rcParams["figure.dpi"] = 300  # for high resolution figure in notebook
mpl.rcParams["figure.facecolor"] = "white"  # To make sure text is visible in dark mode


# First we define a function to calculate the umap reduction
def umap_reducer(x: np.ndarray, dims: int = 3, nns: int = 10) -> np.ndarray:
    """UMAP reduction of the input data."""
    reducer = umap.UMAP(
        n_neighbors=nns,
        n_components=dims,
        metric="cosine",
        spread=0.5,
        random_state=2,
    )
    reduced = reducer.fit_transform(x)
    graph = reducer.graph_
    reduced -= reduced.min(axis=0)
    reduced /= reduced.max(axis=0)
    return reduced, graph


# load the features output by our feature extractor
pos = np.load(positions_path)
# add 122 to the x and y positions to center the patches
pos += 112


print(f"Positions: {pos.shape[0]}")
feats = np.load(features_path)
print(f"Features: {feats.shape}")
pos = pos / 8  # as we extracted at 0.5mpp, and we are overlaying on a thumbnail at 4mpp

# reduce the features into 3 dimensional (rgb) space
reduced, graph = umap_reducer(feats)

# save the reduced features and the graph
np.save("umap.npy", reduced)
np.save("knn_graph.npy", graph)

print(f"Reduced: {reduced.shape}")

overview_resolution = (
    4  # the resolution in which we desire to merge and visualize the patch predictions
)
# the unit of the `resolution` parameter. Can be "power", "level", "mpp", or "baseline"
overview_unit = "mpp"
wsi = WSIReader.open(wsi_path)
print("Generating overview")
wsi_overview = wsi.slide_thumbnail(resolution=overview_resolution, units=overview_unit)
print("Overview generated")
plt.figure()
plt.imshow(wsi_overview)
plt.axis("off")
plt.savefig("overview.png", bbox_inches="tight", pad_inches=0)

# plot the feature map reduction
plt.figure()
plt.imshow(wsi_overview)
plt.scatter(pos[:, 0], pos[:, 1], c=reduced, s=5, alpha=0.7)
plt.axis("off")
plt.savefig("umap_overlay.png", bbox_inches="tight", pad_inches=0)

reduced_2d, graph2d = umap_reducer(feats, dims=2)


def umap_to_igraph(graph):
    """Convert UMAP's graph to igraph format."""
    sources, targets = graph.nonzero()  # Extract edges
    weights = graph.data  # Extract edge weights
    g = ig.Graph(directed=False)
    g.add_vertices(graph.shape[0])  # Add nodes
    g.add_edges(list(zip(sources, targets)))  # Add edges
    g.es["weight"] = weights  # Assign edge weights
    return g


# Convert UMAP's graph
igraph_graph = umap_to_igraph(graph)


def leiden_clustering(igraph_graph, resolution=1.0):
    """Apply Leiden clustering on the given igraph Graph."""
    partition = la.find_partition(
        igraph_graph, la.RBConfigurationVertexPartition, resolution_parameter=resolution
    )
    return np.array(partition.membership)  # Return cluster labels


# Initial resolution
resolution = 0.5

# Run Leiden clustering
labels = leiden_clustering(igraph_graph, resolution=resolution)
num_clusters = len(np.unique(labels))

# Reduce resolution incrementally until we get <= 5 clusters
while num_clusters > 5 and resolution > 0.1:
    resolution -= 0.1
    labels = leiden_clustering(igraph_graph, resolution=resolution)
    num_clusters = len(np.unique(labels))

# If we don't have enough clusters, increase resolution
while num_clusters < 5 and resolution < 1.0:
    resolution += 0.1
    labels = leiden_clustering(igraph_graph, resolution=resolution)
    num_clusters = len(np.unique(labels))

plt.figure()
plt.scatter(reduced_2d[:, 0], reduced_2d[:, 1], c=labels, cmap="tab10", s=1, alpha=0.9)
plt.savefig("leiden_clusters_umap.png")

# plot the feature map reduction
plt.figure()
plt.imshow(wsi_overview)
plt.scatter(pos[:, 0], pos[:, 1], c=labels, cmap="tab10", s=5, alpha=0.9)
plt.axis("off")
plt.savefig("leiden_clusters_overlay.png", bbox_inches="tight", pad_inches=0)


def select_representative_nodes(
    graph: ig.Graph, labels: np.ndarray, method="random", n_patches=5
):
    """
    Select representative nodes per cluster from the UMAP graph.

    Args:
        graph (igraph.Graph): Graph created from UMAP.
        labels (np.ndarray): Leiden cluster labels.
        method (str): Selection method ('degree', 'betweenness', 'medoid', 'random', 'random_walk').
        n_patches (int): Number of representative patches per cluster.

    Returns:
        dict: Cluster-wise selection of representative node indices.
    """
    unique_clusters = np.unique(labels)
    representative_patches = {}

    for cluster in unique_clusters:
        cluster_indices = np.where(labels == cluster)[0]
        subgraph = graph.subgraph(cluster_indices)  # Extract cluster subgraph

        if method == "random":
            # Randomly select `n_patches` nodes from the cluster
            selected_nodes = np.random.choice(
                cluster_indices,
                size=min(n_patches, len(cluster_indices)),
                replace=False,
            )

        elif method == "degree":
            # Select nodes with highest degree (most connections)
            degrees = subgraph.degree()
            selected_nodes = cluster_indices[np.argsort(degrees)[-n_patches:]]

        elif method == "betweenness":
            # Select nodes with highest betweenness centrality
            centrality = subgraph.betweenness()
            selected_nodes = cluster_indices[np.argsort(centrality)[-n_patches:]]

        elif method == "medoid":
            # Find the most central node (smallest avg. shortest path distance)
            distances = subgraph.shortest_paths()
            avg_distance = np.mean(distances, axis=1)
            selected_nodes = cluster_indices[np.argsort(avg_distance)[:n_patches]]

        elif method == "random_walk":
            # Perform a biased random walk and select visited nodes
            selected_nodes = set()
            node = np.random.choice(cluster_indices)
            while len(selected_nodes) < min(n_patches, len(cluster_indices)):
                neighbors = graph.neighbors(node)
                node = np.random.choice(neighbors)
                selected_nodes.add(node)
            selected_nodes = np.array(list(selected_nodes))

        # Convert back to global indices
        representative_patches[cluster] = selected_nodes

    return representative_patches


# Select randomly sampled patches from the graph
patch_indices = select_representative_nodes(
    igraph_graph, labels, method="degree", n_patches=5
)

# 1. Build flattened lists for both selected indices and annotation labels
selected_indices = []
annot_labels = []
for cluster_id, cluster_values in patch_indices.items():
    for i, idx in enumerate(cluster_values):
        selected_indices.append(idx)
        # Annotation format: "clusterID.indexWithinCluster"
        annot_labels.append(f"{cluster_id}.{i+1}")

selected_indices = np.array(selected_indices)
selected_indices = selected_indices.astype(int)

# 2. (Optional) Convert WSI overview to grayscale and dim it
wsi_greyscale = np.mean(wsi_overview, axis=-1)  # Convert to grayscale
# as rgb so it renders correcrly
wsi_greyscale = np.stack([wsi_greyscale] * 3, axis=-1)
wsi_dimmed = wsi_greyscale * 0.6  # Dim by reducing brightness

# 3. Plot the WSI (dimmed grayscale or original RGB) and scatter the selected points
plt.figure(figsize=(5, 5))
# plt.imshow(wsi_greyscale, cmap="gray", alpha=0.9)  # Option: show dimmed grayscale
plt.imshow(wsi_overview, alpha=0.5)  # Showing the original WSI, semi-transparent

plt.scatter(
    pos[selected_indices, 0],
    pos[selected_indices, 1],
    c=labels[selected_indices],
    cmap="tab10",
    s=8,
)

import string

# Generate labels (A-Z, then 0-9 if needed)
num_points = len(selected_indices)
if num_points <= 26:
    labels_text = string.ascii_uppercase[:num_points]
else:
    labels_text = list(string.ascii_uppercase) + [
        str(i) for i in range(num_points - 26)
    ]


# Annotate each point inside the circle
for i, loc in enumerate(pos[selected_indices]):
    plt.text(
        loc[0],
        loc[1],
        labels_text[i],
        fontsize=3,
        ha="center",
        va="center",
        color="white",
        weight="bold",
    )

# 4. Annotate each point with its "clusterID.indexWithinCluster" label
#    (offset the text slightly so it's easier to read)
# texts = [
#    plt.text(
#        pos[idx, 0],
#        pos[idx, 1],
#        annot_labels[i],
#        ha="center",
#        va="center",
#        fontsize=2,
#        color="black",
#    )
#    for i, idx in enumerate(selected_indices)
# ]
# adjust_text(
#    texts, expand=(2, 2)
# )  # , # expand text bounding boxes by 1.2 fold in x direction and 2 fold in y direction
# arrowprops=dict(arrowstyle='->', color='black') # ensure the labeling is clear by adding arrows
# );

# 5. Final plot styling
plt.axis("off")
plt.savefig("selected_patches_overlay.png", bbox_inches="tight", pad_inches=0)

# Convert pos to full-resolution coordinates
scaling_factor = 4 / 0.5  # Calculate scaling factor based on mpp values
# subtract 122 to get the top left corner of the patch
pos8 = np.round(pos * scaling_factor).astype(int)

# Set number of patches per cluster
num_patches_per_cluster = 5

# Extract patches per cluster
patches_per_cluster = {}
clusters = list(patch_indices.keys())  # List of unique cluster IDs

for cluster in clusters:
    cluster_indices = patch_indices[cluster]

    # Ensure at least one patch exists
    if len(cluster_indices) == 0:
        print(f"Skipping cluster {cluster}: No patches available.")
        continue

    # Use pre-selected indices instead of random sampling
    selected_indices = np.array(patch_indices[cluster])  # Corrected variable name
    patch_centroids = pos8[selected_indices, :2]  # Ensure correct shape
    # add half of patch_shape to get the center of the patch
    patch_centroids += np.array(patch_shape) // 2

    # Use TIAToolbox patch extractor
    patch_extractor = patchextraction.get_patch_extractor(
        input_img=wsi,
        locations_list=patch_centroids,
        method_name="point",
        patch_size=patch_shape,
        resolution=0.5,
        units="mpp",
    )

    patches_per_cluster[cluster] = list(patch_extractor)  # Store extracted patches


def frame_image(img, pad_size, color=(255, 0, 0)):
    """Pads an image with a border of the given color.

    Args:
        img (np.ndarray): Input image (H, W, C).
        pad_size (int): Border width (in pixels).
        color (tuple): RGB color of the border.

    Returns:
        np.ndarray: Image with added border.
    """
    H, W, C = img.shape
    new_H, new_W = H + 2 * pad_size, W + 2 * pad_size
    # Create a new image filled with the border color
    framed_img = np.full((new_H, new_W, C), color, dtype=img.dtype)
    # Place the original image in the center
    framed_img[pad_size : pad_size + H, pad_size : pad_size + W, :] = img
    return framed_img


# Determine grid size dynamically
num_clusters = len(patches_per_cluster)
max_patches = max(
    len(patches) for patches in patches_per_cluster.values()
)  # Adjust column count

fig, axes = plt.subplots(
    num_clusters, max_patches, figsize=(max_patches * 0.9, num_clusters * 0.9)
)
plt.subplots_adjust(wspace=0.01, hspace=0.01)  # Reduce whitespace
# Convert axes to a list if there’s only one row
if num_clusters == 1:
    axes = [axes]

# Define colormap
cmap = plt.get_cmap("tab20", num_clusters)

patch_counter = 0

print("Plotting extracted patches...")

# Plot extracted patches per cluster and add labels
for row, (cluster, patches) in enumerate(patches_per_cluster.items()):
    cluster_color = cmap(row)[:3]  # Extract RGB color from colormap
    cluster_color = tuple(int(c * 255) for c in cluster_color)  # Convert to 0-255 scale

    for col, patch in enumerate(patches):
        if col >= max_patches:  # Avoid IndexError if fewer patches exist
            break

        ax = axes[row, col] if num_clusters > 1 else axes[col]

        # Apply border to patch
        framed_patch = frame_image(
            patch.astype(np.uint8), pad_size=20, color=cluster_color
        )

        ax.imshow(framed_patch)
        # Add a patch label to the patch based on labels_text
        # label_text is the number of patches wide
        # label should be top left corner on  the patch
        ax.text(
            0, -15, labels_text[patch_counter], fontsize=6, color="black", weight="bold"
        )
        if col == 0:
            ax.text(
                -50,
                250,
                f"Cluster {cluster}",
                fontsize=6,
                rotation=90,
                weight="bold",
            )
        ax.axis("off")
        patch_counter += 1

    # Add cluster label on the leftmost image in each row
    axes[row, 0].set_ylabel(
        f"Cluster {cluster}", fontsize=12, rotation=90, labelpad=20, weight="bold"
    )


plt.tight_layout()
plt.savefig("extracted_patches.png", bbox_inches="tight", pad_inches=0.2)


# Try merging predictions
print("Merging predictions...")
output = {
    "resolution": 1,
    "units": "baseline",
    "predictions": labels + 1,
    "coordinates": pos,
}

merged = PatchPredictor.merge_predictions(
    wsi_overview, output, resolution=4, units="baseline"
)
merged -= 1
# in merged set zero to be null
merged[merged == -1] = np.nan

cmap = plt.get_cmap("tab10").copy()  # Copy to modify safely
cmap.set_bad(color=(0, 0, 0, 0))  # RGBA: fully transparent

# plot the feature map reduction
plt.figure()
plt.imshow(wsi_overview)
plt.imshow(merged, alpha=0.7, cmap=cmap)
plt.axis("off")
plt.savefig("cluster_overlay_merged.png", bbox_inches="tight", pad_inches=0)

output = {
    "resolution": 1,
    "units": "baseline",
    "predictions": list(range(1, len(labels) + 1)),
    "coordinates": pos,
}

merged = PatchPredictor.merge_predictions(
    wsi_overview, output, resolution=4, units="baseline"
)

# Ensure merged is an integer array
merged_int = np.nan_to_num(merged, nan=0).astype(int)

# Create a semi-transparent RGBA image (float32 to match reduced's 0-1 scale)
filled = np.zeros((*merged_int.shape, 4), dtype=np.float32)  # Default fully transparent

# Mask valid indices (ignore background values)
valid_mask = merged_int > 0

# Convert to 0-based indexing
valid_indices = merged_int[valid_mask] - 1
valid_indices = np.clip(
    valid_indices, 0, len(reduced) - 1
)  # Prevent out-of-bounds errors

# Assign RGB values from reduced (already 0-1 scaled)
filled[valid_mask, :3] = reduced[valid_indices]  # No need for scaling

# Set alpha to 0.5 (semi-transparent) for valid pixels
filled[valid_mask, 3] = 0.7  # 50% transparency


plt.figure()
plt.imshow(wsi_overview)  # Base image
plt.imshow(filled)  # Overlay with 50% transparency
plt.axis("off")
plt.savefig("umap_overlay_merged.png", bbox_inches="tight", pad_inches=0)
