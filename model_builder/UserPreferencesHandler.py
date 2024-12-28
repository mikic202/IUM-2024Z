import torch
import os
import logging
import pandas as pd
import numpy as np


class UserPreferencesHandler:
    def __init__(self):
        self._context = None
        self.initialized = False
        self.model = None
        self.device = None

    def initialize(self, context):
        self.manifest = context.manifest

        properties = context.system_properties
        model_dir = properties.get("model_dir")
        self.device = torch.device(
            "cuda:" + str(properties.get("gpu_id"))
            if torch.cuda.is_available()
            else "cpu"
        )
        logging.info(f"UserPreferencesHandler initializing using: {str(self.device)}")

        serialized_file = self.manifest["model"]["serializedFile"]
        model_pt_path = os.path.join(model_dir, serialized_file)
        if not os.path.isfile(model_pt_path):
            raise RuntimeError("Missing the model.pt file")

        self.model = torch.jit.load(model_pt_path, map_location=self.device)

        self.initialized = True
        logging.info(f"UserPreferencesHandler initialized")

    @staticmethod
    def postprocess_hash_to_list(x):
        str_x = str(x)
        if len(str_x) < 8:
            str_x = "0" * (8 - len(str_x)) + str_x
        return [int(x) for x in str_x]

    def preprocess(self, data):
        input_data = pd.DataFrame(data[0].get("body").get("data"))
        sessions = []
        for session in (
            input_data.drop("track_id", axis=1)
            .drop("session_id", axis=1)
            .drop("user_id", axis=1)
            .values
        ):
            unpacked_data = np.array([])
            for data in session:
                unpacked_data = np.append(unpacked_data, data)
            sessions.append(torch.tensor(unpacked_data))
        sessions = torch.stack(sessions)
        return torch.stack([sessions]).float().to(self.device)

    def handle(self, data, _):
        data = self.preprocess(data)
        pred_out = self.model.forward(
            data, torch.tensor([len(data[0])]).int().to(self.device)
        )
        return [pred_out.tolist()]
