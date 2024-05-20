import pandas as pd
import numpy as np

df_time = pd.read_csv("./single_func_buggy_ver.csv")
cp_time = np.array(df_time["compile_time"].tolist())
te_time = np.array(df_time["test_time"].tolist())

max_cp_time = np.max(cp_time)
max_te_time = np.max(te_time)

total_cp_time = np.sum(cp_time)
total_te_time = np.sum(te_time)

print(len(df_time), max_cp_time, max_te_time, total_cp_time, total_te_time)