import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

def create_orbit_animation(positions, planet_labels, dynamic_scaling=True, show_trails=True):
    """
    Creates a 3D animated orbit visualization using Plotly.

    Args:
        positions (list of list of (x, y)): Planet trajectories.
        planet_labels (list of str): Labels for each planet.
        use_dynamic_scaling (bool): Whether to auto-scale the plot.
        show_trails (bool): Whether to show orbit trails.
        trail_length (int): Number of past positions to show in trail.

    Returns:
        plotly.graph_objects.Figure: The animated orbit figure.
    """
    inclinations = np.linspace(0, 0.2, len(positions))
    min_len = min(len(orbit) for orbit in positions)

    if use_dynamic_scaling:
        max_radius = max(np.max([np.linalg.norm(pos) for pos in orbit]) for orbit in positions)
        scale = max_radius * 1.5
    else:
        scale = 5

    x_history = [[] for _ in range(len(positions))]
    y_history = [[] for _ in range(len(positions))]
    z_history = [[] for _ in range(len(positions))]

    frames = []
    for frame in range(min_len):
        data = [go.Scatter3d(
            x=[0], y=[0], z=[0],
            mode='markers',
            marker=dict(size=12, color='gold', opacity=0.8),
            name='Star'
        )]
        for i, orbit in enumerate(positions):
            x, y = orbit[frame]
            z = y * np.sin(inclinations[i])
            x_history[i].append(x)
            y_history[i].append(y)
            z_history[i].append(z)
            x_history[i] = x_history[i][-trail_length:]
            y_history[i] = y_history[i][-trail_length:]
            z_history[i] = z_history[i][-trail_length:]

            label = planet_labels[i] if i < 2 else None
            base_color = (50+i*20, 100+i*10, 200-i*15)
            color = f'rgb{base_color}'

            data.append(go.Scatter3d(
                x=[x], y=[y], z=[z],
                mode='markers+text' if label else 'markers',
                marker=dict(size=10, color=color),
                text=[label] if label else None,
                textposition="top center",
                name=label or f'Planet {i+1}'
            ))

            if show_trails and len(x_history[i]) > 1:
                for j in range(1, len(x_history[i])):
                    fade = j / len(x_history[i])
                    segment_color = f'rgba({base_color[0]}, {base_color[1]}, {base_color[2]}, {fade:.2f})'
                    data.append(go.Scatter3d(
                        x=[x_history[i][j-1], x_history[i][j]],
                        y=[y_history[i][j-1], y_history[i][j]],
                        z=[z_history[i][j-1], z_history[i][j]],
                        mode='lines',
                        line=dict(color=segment_color, width=2),
                        showlegend=False
                    ))

        frames.append(go.Frame(data=data, name=str(frame)))

    init_data = [go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(size=12, color='gold', opacity=0.8),
        name='Star'
    )]
    for i, orbit in enumerate(positions):
        x, y = orbit[0]
        z = y * np.sin(inclinations[i])
        label = planet_labels[i] if i < 2 else None
        color = f'rgb({50+i*20}, {100+i*10}, {200-i*15})'
        init_data.append(go.Scatter3d(
            x=[x], y=[y], z=[z],
            mode='markers+text' if label else 'markers',
            marker=dict(size=10, color=color),
            text=[label] if label else None,
            textposition="top center",
            name=label or f'Planet {i+1}'
        ))

    layout = go.Layout(
        scene=dict(
            xaxis=dict(range=[-scale, scale], title='X'),
            yaxis=dict(range=[-scale, scale], title='Y'),
            zaxis=dict(range=[-scale/2, scale/2], title='Z'),
            aspectmode='cube'
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        showlegend=True,
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            buttons=[dict(label="▶ Play", method="animate", args=[None, {"frame": {"duration": 40, "redraw": True}, "fromcurrent": True}])]
        )]
    )

    return go.Figure(data=init_data, layout=layout, frames=frames)


def plot_resonances(pairs):
    """
    Plots orbital period resonances between planet pairs using Matplotlib.

    Args:
        pairs (list of tuples): Each tuple contains (p1, p2, ratio),
            where p1 and p2 are orbital periods and ratio is the approximate resonance.

    Returns:
        matplotlib.figure.Figure: The generated resonance plot.
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    cmap = cm.get_cmap('viridis', len(pairs))

    for i, (p1, p2, ratio) in enumerate(pairs):
        ax.plot([0, 1], [p1, p2], marker='o', color=cmap(i), linewidth=2)
        ax.text(0.5, (p1 + p2) / 2, f"{ratio}:1", fontsize=10,
                ha='center', va='bottom', color=cmap(i))

    ax.set_ylabel("Orbital Period (days)")
    ax.set_xticks([])
    ax.set_title("Detected Resonances Between Planet Pairs")
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend([f"{p1:.2f}:{p2:.2f} ~ {ratio}:1" for p1, p2, ratio in pairs],
              loc='upper right', fontsize=8)
    fig.tight_layout()
    return fig
