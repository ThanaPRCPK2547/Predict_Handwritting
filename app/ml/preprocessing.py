import numpy as np
from typing import List, Union


def normalize_canvas_pixels(
    pixels: Union[List[List[float]], List[float], List[int]],
) -> np.ndarray:
    """Convert canvas pixel data to normalized numpy array (0.0-1.0).
    
    Accepts either:
    - Flat 784-element array (28*28)
    - Nested 28x28 array
    
    If values are in 0-255 range, divides by 255 to normalize to 0.0-1.0.
    """
    arr = np.array(pixels, dtype=np.float64)
    if arr.ndim == 2:
        if arr.shape != (28, 28):
            raise ValueError(f"Expected 28x28 canvas, got shape {arr.shape}")
        arr = arr.flatten()
    else:
        if arr.shape != (784,):
            raise ValueError(f"Expected flat 784-element array, got shape {arr.shape}")
    # Normalize to 0.0-1.0 range if values are in 0-255
    if arr.max() > 1.0:
        arr = arr / 255.0
    return arr


def pixels_to_feature_dict(pixels: np.ndarray) -> dict:
    """Convert normalized pixel array to River-compatible feature dictionary."""
    return {f"p{i}": float(v) for i, v in enumerate(pixels)}
