# Usage Guide: `09_ROI_plot`

This script creates glass brain plots to visualize the stability of selected ROIs based on their selection frequency across multiple runs. It uses nilearn's plotting functionality to display ROIs as colored markers on a brain template, with the top 3 most frequently selected ROIs highlighted with larger markers and numbered annotations.

- **Location:** Analysis/
- **Tested with:** Python 3.13.2

## Overview
`09_ROI_plot.py` visualizes ROI selection stability by creating publication-quality glass brain plots. The script:
1. Loads ROI data including selection counts, 3D coordinates, and network assignments
2. Identifies the top 3 most frequently selected ROIs
3. Creates a glass brain plot with ROIs colored by functional network
4. Highlights top 3 ROIs with larger markers and numerical annotations
5. Adds a legend and text box with top ROI details
6. Saves the plot as PNG and SVG files

## 1. Inputs
- **ROI data**: Hardcoded list of ROI information including:
  - Region name (string)
  - Selection count (integer)
  - 3D coordinates (x, y, z in MNI space)
  - Network assignment (string)

The script contains multiple predefined datasets (commented out) for different scenarios. The active dataset is selected by uncommenting the appropriate `data = [...]` block.

## 2. Outputs
Visualization files saved to `ELAGAopt/Analysis_result/ROI_plot/`:
- `color_coded_brain_map_numbered_s4.png` — Static glass brain plot (300 DPI)
- `color_coded_brain_map_numbered_s4.svg` — Vector format glass brain plot

### Plot Features:
- **Glass brain display**: Orthogonal views (sagittal, coronal, axial) using nilearn
- **Color coding**: ROIs colored by functional network (e.g., Visual=red, Sensory=blue)
- **Marker sizing**: Marker size proportional to selection count
- **Top 3 highlighting**: Largest markers for most selected ROIs with white numerical labels (1, 2, 3)
- **Legend**: Network color legend in upper left
- **Text box**: Details of top 3 ROIs with names and counts

## 3. Configuration (script-level variables)

Located in the script's data sections and plotting parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | list | Various hardcoded datasets | ROI data list with [name, count, x, y, z, network] |
| `network_colors` | dict | Varies by dataset | Color mapping for functional networks |
| `marker_size` | expression | `Count * 10` | Marker size scaling factor |
| `top_n` | int | `3` | Number of top ROIs to highlight and number |
| Output paths | string | `ELAGAopt//Analysis_result//ROI_plot//color_coded_brain_map_numbered_s4.png` | Save paths for plots |

## 4. Behavior / Workflow

### Main Workflow:
1. Define ROI dataset (uncomment desired data block)
2. Create DataFrame from ROI data
3. Identify top 3 ROIs by selection count
4. Set up network color scheme
5. Create glass brain plot using nilearn:
   - Initialize orthogonal display
   - Plot normal ROIs (smaller markers, by network)
   - Plot top 3 ROIs (larger markers, same network colors)
   - Add numerical labels to top 3 ROIs
6. Add legend and text box with top ROI details
7. Save plot as PNG and SVG files

### Key Operations:
- **Data structure**: Each ROI has [name, count, x, y, z, network] format
- **Top ROI identification**: Uses `df.nlargest(3, 'Count')` to find most selected ROIs
- **Marker scaling**: Size = count * 10, with top 3 getting additional emphasis
- **Numerical annotation**: Uses matplotlib TeX markers (`$1$`, `$2$`, `$3$`) for numbering

## 5. Usage examples

### Basic usage (use current active dataset):
```bash
python Analysis/09_ROI_plot.py
```

The script will generate plots using the currently uncommented dataset.

### Switch to different dataset:
Edit the script to uncomment a different `data = [...]` block:
```python
# Uncomment this block for different scenario:
data = [
    ["Visual_145", 100, 8, -72, 11, "Visual"],
    ["Visual_146", 99, -8, -81, 7, "Visual"],
    # ... more ROIs
]
```

### Change number of highlighted ROIs:
Edit the top ROI selection:
```python
top_n = 5  # Highlight top 5 instead of 3
top_df = df.nlargest(top_n, 'Count')
```

### Modify marker sizes:
```python
marker_size = normal_subset['Count'].values * 5  # Smaller markers
marker_size = top_subset['Count'].values * 15    # Larger top markers
```

### Change color scheme:
```python
network_colors = {
    "Visual": "#ff0000",    # Bright red
    "Default": "#0000ff",   # Bright blue
}
```

### Save to different location:
```python
plt.savefig('my_custom_plot.png', dpi=300, bbox_inches='tight')
plt.savefig('my_custom_plot.svg', dpi=300, bbox_inches='tight')
```

## 6. Output details

### Console output example:
```
静止画 'color_coded_brain_map_numbered_s4.png' と 'color_coded_brain_map_numbered_s4.svg' を保存しました。
```

### Plot characteristics:
- **Brain template**: MNI152 standard brain with glass effect
- **View modes**: Three orthogonal projections (sagittal, coronal, axial)
- **Marker styles**: 
  - Normal ROIs: Circular markers, semi-transparent (alpha=0.6)
  - Top ROIs: Larger circular markers, fully opaque (alpha=1.0)
  - Numbers: White TeX-rendered digits on top ROIs
- **Color schemes**: Dataset-dependent (typically red for Visual, blue for Sensory/Default)
- **Legend**: Network names with corresponding colors
- **Text box**: Top 3 ROI details in gray background box

## 7. Notes & recommendations

- **Data format**: ROI coordinates must be in MNI space (mm). Network assignments should match the color dictionary keys.
- **Marker scaling**: Count * 10 provides reasonable sizing, but may need adjustment for different count ranges.
- **Top ROI highlighting**: Top 3 are emphasized with larger markers and numbers. Adjust `top_n` for different emphasis levels.
- **Color consistency**: Use consistent color schemes across related plots for better comparison.
- **File naming**: Output filename includes `_s4` suffix. Change for different scenarios.
- **Vector output**: SVG format preserves scalability for publications and presentations.
- **Nilearn dependency**: Requires nilearn for brain plotting. Ensure proper installation.
- **Memory usage**: Plotting operations are memory-intensive. Close figures if running multiple times.

## 8. Troubleshooting

### Issue: ImportError for nilearn
- **Cause:** nilearn package not installed
- **Solution:** Install nilearn:
  ```bash
  pip install nilearn
  ```

### Issue: "ValueError: could not convert string to float"
- **Cause:** Incorrect data format in ROI list
- **Solution:** Ensure data list has correct format: [string, int, float, float, float, string]

### Issue: Plot shows no markers
- **Cause:** Coordinate values outside brain space or incorrect coordinate system
- **Solution:** Verify coordinates are in MNI space (typical range: x=-90 to 90, y=-126 to 90, z=-72 to 108)

### Issue: Colors not displaying correctly
- **Cause:** Network names don't match color dictionary keys
- **Solution:** Check that all network names in data match keys in `network_colors` dict

### Issue: Top ROI numbers not visible
- **Cause:** Marker size too small or alpha too low
- **Solution:** Increase marker_size for top ROIs and ensure alpha=1.0

### Issue: Legend overlaps with brain
- **Cause:** Figure size too small or legend positioning
- **Solution:** Adjust figure size or legend position:
  ```python
  fig = plt.figure(figsize=(14, 10))  # Larger figure
  plt.legend(bbox_to_anchor=(1.1, 1.0))  # Move legend further right
  ```

### Issue: Text box content cut off
- **Cause:** Text too long for allocated space
- **Solution:** Adjust text box position or size:
  ```python
  plt.text(1.05, 0.2, text_str, transform=plt.gca().transAxes)
  ```

### Issue: FileNotFoundError for output directory
- **Cause:** Output directory doesn't exist
- **Solution:** Create directory manually:
  ```bash
  mkdir -p ELAGAopt/Analysis_result/ROI_plot
  ```

### Issue: Plot appears empty or distorted
- **Cause:** Matplotlib backend issues or figure not properly closed
- **Solution:** Add figure clearing and ensure proper backend:
  ```python
  import matplotlib
  matplotlib.use('Agg')  # Use non-interactive backend
  plt.close('all')       # Clear previous figures
  ```

### Issue: Memory error during plotting
- **Cause:** Large datasets or multiple figures
- **Solution:** Reduce dataset size or add memory management:
  ```python
  plt.close(fig)  # Close figure after saving
  ```
