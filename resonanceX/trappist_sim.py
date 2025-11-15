import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from scipy.integrate import solve_ivp

G = 1.0  # normalized gravitational constant

def n_body_equations(t, y, masses):
    N = len(masses)
    positions = y[:3*N].reshape(N, 3)
    velocities = y[3*N:].reshape(N, 3)
    accelerations = np.zeros((N, 3))

    for i in range(N):
        for j in range(N):
            if i != j:
                r = positions[j] - positions[i]
                dist = np.linalg.norm(r)
                accelerations[i] += G * masses[j] * r / dist**3

    dydt = np.concatenate([velocities.flatten(), accelerations.flatten()])
    return dydt

def simulate_trappist1():
    periods = np.array([1.51, 2.42, 3.06, 4.05, 6.10, 9.21, 12.35])
    masses = np.array([0.85, 1.38, 0.41, 0.62, 0.68, 1.34, 0.66]) * 3e-6
    N = len(masses)
    star_mass = 1.0
    masses = np.insert(masses, 0, star_mass)

    positions = np.zeros((N + 1, 3))
    velocities = np.zeros((N + 1, 3))
    for i in range(1, N + 1):
        r = periods[i - 1] ** (2/3)
        positions[i] = [r, 0, 0]
        velocities[i] = [0, np.sqrt(G * star_mass / r), 0]

    velocities[0] = -np.sum(masses[1:, None] * velocities[1:], axis=0) / star_mass

    y0 = np.concatenate([positions.flatten(), velocities.flatten()])
    t_span = (0, 100)
    t_eval = np.linspace(*t_span, 1000)
    sol = solve_ivp(n_body_equations, t_span, y0, args=(masses,), t_eval=t_eval)

    return sol, masses, periods

def compute_energy(sol, masses, frame):
    N = len(masses)
    positions = sol.y[:3*N, frame].reshape(N, 3)
    velocities = sol.y[3*N:, frame].reshape(N, 3)
    kinetic = 0.5 * np.sum(masses[:, None] * velocities**2)
    potential = 0
    for i in range(N):
        for j in range(i+1, N):
            r = np.linalg.norm(positions[i] - positions[j])
            potential -= G * masses[i] * masses[j] / r
    return kinetic + potential

def compute_angular_momentum(sol, masses, frame):
    N = len(masses)
    positions = sol.y[:3*N, frame].reshape(N, 3)
    velocities = sol.y[3*N:, frame].reshape(N, 3)
    L = np.sum(np.cross(positions, masses[:, None] * velocities), axis=0)
    return np.linalg.norm(L)

def animate_simulation(sol, masses, periods, save=False):
    import streamlit as st
    import tempfile

    N = len(masses)
    fig, ax = plt.subplots()
    max_radius = np.max(np.abs(sol.y[:3*N]))
    ax.set_xlim(-max_radius * 1.2, max_radius * 1.2)
    ax.set_ylim(-max_radius * 1.2, max_radius * 1.2)
    ax.set_aspect('equal')
    ax.set_title("TRAPPIST-1 Orbital Resonance Animation")

    colors = plt.cm.viridis(np.linspace(0, 1, N))
    lines = [ax.plot([], [], 'o', color=colors[i])[0] for i in range(N)]
    trails = [ax.plot([], [], '-', lw=0.5, alpha=0.5, color=colors[i])[0] for i in range(N)]
    labels = [ax.text(0, 0, f"{chr(98+i)}", fontsize=8, ha='left') for i in range(N-1)]
    x_history = [[] for _ in range(N)]
    y_history = [[] for _ in range(N)]

    resonance_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=10, color='blue')
    energy_text = ax.text(0.02, 0.90, '', transform=ax.transAxes, fontsize=10, color='green')
    momentum_text = ax.text(0.02, 0.85, '', transform=ax.transAxes, fontsize=10, color='purple')

    def update(frame):
        for i in range(N):
            x = sol.y[i*3][frame]
            y = sol.y[i*3 + 1][frame]
            x_history[i].append(x)
            y_history[i].append(y)
            lines[i].set_data([x], [y])
            trails[i].set_data(x_history[i], y_history[i])
            if i > 0:
                labels[i-1].set_position((x, y))

        ratios = [round(periods[i+1]/periods[i], 2) for i in range(len(periods)-1)]
        resonance_text.set_text(f"Period Ratios: {ratios}")
        energy_text.set_text(f"Total Energy: {compute_energy(sol, masses, frame):.4f}")
        momentum_text.set_text(f"Angular Momentum: {compute_angular_momentum(sol, masses, frame):.4f}")
        return lines + trails + labels + [resonance_text, energy_text, momentum_text]

    ani = FuncAnimation(fig, update, frames=len(sol.t), interval=30, blit=True)

    if save:
        ani.save("trappist1_orbits.mp4", writer="ffmpeg", fps=30)
    else:
        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmpfile:
            ani.save(tmpfile.name, writer=PillowWriter(fps=30))
            st.image(tmpfile.name, caption="Orbital Animation", use_column_width=True)