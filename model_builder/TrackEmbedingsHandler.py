import torch
import os
import logging
import pandas as pd


class TrackEmbedingsHandler:
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
        logging.info(f"TrackEmbedingsHandler initializing using: {str(self.device)}")

        serialized_file = self.manifest["model"]["serializedFile"]
        model_pt_path = os.path.join(model_dir, serialized_file)
        if not os.path.isfile(model_pt_path):
            raise RuntimeError("Missing the model.pt file")

        self.model = torch.jit.load(model_pt_path)

        self.initialized = True
        logging.info(f"TrackEmbedingsHandler initialized")

    @staticmethod
    def postprocess_hash_to_list(x):
        str_x = str(x)
        if len(str_x) < 8:
            str_x = "0" * (8 - len(str_x)) + str_x
        return [int(x) for x in str_x]

    def preprocess(self, data):
        input_data = pd.Series(data[0].get("body"))
        input_data["id_artist_hash"] = TrackEmbedingsHandler.postprocess_hash_to_list(
            input_data["id_artist_hash"]
        )

        unpacked_data = []
        for data in input_data.drop("id_track").values:
            if type(data) != list:
                unpacked_data.append(data)
            else:
                unpacked_data += data

        tensor_data = torch.tensor(unpacked_data)
        return tensor_data

    def handle(self, data, _):
        data = self.preprocess(data)
        pred_out = self.model.forward(data)
        return [pred_out.tolist()]
