import gdown
import pandas as pd

url = "https://drive.google.com/uc?id=15BPH7-3GGWBfXPJQ3stkT6SHQECbT-pt"
output = "shifts.csv"
gdown.download(url, output, quiet=False)

df = pd.read_csv("shifts.csv", index_col=0)
