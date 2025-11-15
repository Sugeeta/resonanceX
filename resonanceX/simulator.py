import rebound
import numpy as np

def simulate_orbits(periods, masses, duration=100, steps=1000, use_resonant_chain=False):
    """
    Simulates planetary orbits using REBOUND with mutual interactions and optional resonant chain setup.

    Args:
        periods (list of float): Orbital periods in days.
        masses (list of float): Planet masses in solar masses.
        duration (float): Total simulation time in days.
        steps (int): Number of time steps.
        use_resonant_chain (bool): If True, adjusts periods to form a resonant chain.

    Returns:
        list of list of (x, y) tuples: Trajectories for each planet.
    """
    try:
        # Validate inputs
        if not periods or not masses:
            raise ValueError("Periods and masses must be non-empty lists.")
        if len(periods) != len(masses):
            raise ValueError("Periods and masses must be the same length.")
        if any(p <= 0 for p in periods):
            raise ValueError("All orbital periods must be positive.")
        if steps <= 0 or duration <= 0:
            raise ValueError("Duration and steps must be positive.")

        sim = rebound.Simulation()
        sim.units = ('days', 'AU', 'Msun')
        sim.integrator = "whfast"
        sim.dt = duration / steps / 10

        sim.add(m=1.0)  # central star

        # Optional: adjust periods to form a resonant chain (e.g., 3:2, 4:3, etc.)
        if use_resonant_chain:
            base_period = periods[0]
            ratios = [1.0]
            for i in range(1, len(periods)):
                ratios.append(ratios[-1] * (3/2))  # 3:2 resonance chain
            periods = [base_period * r for r in ratios]

        # Add planets with realistic orbital parameters
        for i in range(len(periods)):
            a = (periods[i] ** 2) ** (1 / 3)
            e = 0.01 * (i + 1)
            inc = np.radians(0.5 * i)
            omega = np.radians(90)
            Omega = np.radians(0)
            M = np.radians(360 * i / len(periods))
            sim.add(m=masses[i], a=a, e=e, inc=inc, omega=omega, Omega=Omega, M=M)

        sim.move_to_com()

        times = np.linspace(0, duration, steps)
        trajectories = [[] for _ in range(len(periods))]

        for t in times:
            sim.integrate(t)
            for i, p in enumerate(sim.particles[1:]):
                trajectories[i].append((p.x, p.y))

        return trajectories

    except Exception as e:
        print(f"[simulate_orbits] Error: {e}")
        return [[] for _ in range(len(periods))]