def detect_resonances(periods, tolerance=0.05):
    resonant_pairs = []
    for i in range(len(periods)):
        for j in range(i + 1, len(periods)):
            ratio = periods[i] / periods[j]
            if abs(ratio - round(ratio)) < tolerance:
                resonant_pairs.append((periods[i], periods[j], round(ratio)))
    return resonant_pairs

def detect_resonances_in_system(df, tolerance=0.05):
    results = []
    for system in df['hostname'].unique():
        planets = df[df['hostname'] == system]
        periods = planets['pl_orbper'].dropna().tolist()
        for i in range(len(periods)):
            for j in range(i + 1, len(periods)):
                ratio = periods[i] / periods[j]
                if abs(ratio - round(ratio)) < tolerance:
                    results.append((system, periods[i], periods[j], round(ratio)))
    return results