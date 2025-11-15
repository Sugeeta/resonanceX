def detect_resonances(periods, tolerance=0.05):
    """
    Detects approximate integer orbital resonances between adjacent planet periods.

    Args:
        periods (list of float): Orbital periods in days.
        tolerance (float): Allowed fractional deviation from exact resonance.

    Returns:
        list of tuples: Each tuple is (p1, p2, ratio) where p2/p1 ≈ ratio.
    """
    resonances = []
    sorted_periods = sorted(periods)
    for i in range(len(sorted_periods) - 1):
        p1, p2 = sorted_periods[i], sorted_periods[i + 1]
        if p1 == 0 or p2 == 0:
            continue
        ratio = p2 / p1
        nearest = round(ratio)
        if abs(ratio - nearest) / nearest < tolerance:
            resonances.append((p1, p2, nearest))
    return resonances