import pandas as pd

def load_exoplanet_data(path):
    df = pd.read_csv(path)
    df = df[df['pl_orbper'].notnull()]
    df['pl_orbper'] = pd.to_numeric(df['pl_orbper'], errors='coerce')
    return df