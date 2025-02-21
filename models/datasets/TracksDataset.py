import pandas as pd
import torch
from torch.utils.data import Dataset
import numpy as np


class TracksDataset(Dataset):
    def __init__(self, tracks_data: pd.DataFrame):
        self.data = tracks_data

    def __len__(self):
        return len(self.data)

    def get_item(self, idx):
        return self.data.iloc[idx].values

    def __getitem__(self, idx):
        unpacked_data = (
            self.data.iloc[idx].drop("id_track").explode().values.astype(np.float64)
        )
        return torch.from_numpy(unpacked_data)
