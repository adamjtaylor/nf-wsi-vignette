#!/usr/bin/env python

# This script takes a directory of npy coordinates and features files and concatonates them into a single parqurt file

import sys
import numpy as np
import hashlib
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

id = sys.argv[1]  # a string
coords_npy = sys.argv[3]  # a n x 4 npy file
features_npy = sys.argv[2]  # a n x m npy file
output_file = "features.parquet"


def generate_short_tile_hash(image_id, x1, y1, x2, y2, length=8):
    """Generate a short, unique hash for each tile using image ID and coordinates."""
    tile_string = f"{image_id}_{x1}_{y1}_{x2}_{y2}"
    short_hash = hashlib.shake_256(tile_string.encode()).hexdigest(4)
    return short_hash


### input
positions = np.load(coords_npy)
features = np.load(features_npy).astype(np.float32)
print(f"Features dtype: {features.dtype}")
print(f"Features shape: {features.shape}")


## output a csf file like this
# id, tile_hash, positions, features
# my_id, hash, [0, 0, 256, 256], [0.1, 0.2, 0.3, 0.4, 0.5]
# see that positions and features is a list

# Generate tile hashes
# We make tile hashes unique by including the image ID and coordinates
# These are useful for quickly identifying tiles by a unique identifier
tile_hashes = [generate_short_tile_hash(id, *pos) for pos in positions]

# Create a pandas dataframe
output = pd.DataFrame(
    {
        "slide_id": [id] * len(positions),
        "tile_hash": tile_hashes,
        "positions": positions.tolist(),
        "features": features.tolist()
    }
)

# Define schema with float32 array type
schema = pa.schema([
    ('slide_id', pa.dictionary(pa.int32(), pa.string())),  # Dictionary encoding for repeated slide_id
    ('tile_hash', pa.string()),  # Keep as string since it's unique
    ('positions', pa.list_(pa.int64(), list_size=4)),  # Fixed-size list for positions
    ('features', pa.list_(pa.float32(), list_size=features.shape[1]))  # Fixed-size list for features
])

# Convert to pyarrow table with schema
table = pa.Table.from_pandas(output, schema=schema)

# Write to parquet
pq.write_table(table, output_file)