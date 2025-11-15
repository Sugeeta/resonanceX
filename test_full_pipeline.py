from resonanceX.utils import load_exoplanet_data
from resonanceX.detector import detect_resonances_in_system
from resonanceX.visualizer import plot_resonances
import matplotlib.pyplot as plt

# Load the dataset
csv_path = "datasets/nasa_exoplanets.csv"
df = load_exoplanet_data(csv_path)

# Detect resonances
tolerance = 0.05
results = detect_resonances_in_system(df, tolerance)

# Print summary
print(f"Total systems analyzed: {df['hostname'].nunique()}")
print(f"Resonant pairs found: {len(results)}")
for system, p1, p2, ratio in results[:10]:  # Show first 10
    print(f"{system}: {p1:.2f} vs {p2:.2f} ~ {ratio}:1")

# Visualize
if results:
    fig = plot_resonances([(p1, p2, ratio) for _, p1, p2, ratio in results])
    plt.show()
else:
    print("No resonances detected.")