import numpy as np
from dataclasses import dataclass
from pathlib import Path
import torch

@dataclass
class StimConfig:
    name: str
    stimulus: torch.Tensor
    start: float
    duration: float
    intensity: float


class Stimuli:
    def __init__(self, n_nodes, device, dtype):
        self.stimulus_list = []

        self.n_nodes = n_nodes
        self.device = device
        self.dtype = dtype

        self.Istim = torch.zeros((n_nodes,), device=device, dtype=dtype)

    def load_stimulus_region(self, vtx_filepath):
        with Path(vtx_filepath).open("r") as f:
            region_size = int(f.readline().strip())
    
        region = np.loadtxt(vtx_filepath, dtype=int, skiprows=2)
        
        if len(region) != region_size:
            raise Exception(f"Error loading {vtx_filepath}")
        
        return torch.from_numpy(region).to(dtype=torch.long, device=self.device)
    
    def add(self, vtx_filepath, name, start, duration, intensity):
        region = self.load_stimulus_region(vtx_filepath)
        bool_region = torch.zeros((self.n_nodes,), device=self.device, dtype=self.dtype)
        bool_region[region] = 1.0

        sc = StimConfig(name, bool_region * intensity, start, duration, intensity)
        self.stimulus_list.append(sc)


    def apply(self, t):
        applied_stimulus = []
        for stim in self.stimulus_list:
            if t >= stim.start and t <= stim.start + stim.duration:
                applied_stimulus.append(stim.stimulus)

        if len(applied_stimulus) > 0:
            return torch.stack(applied_stimulus).sum(dim=0)
        else:
            return self.Istim


if __name__ == "__main__":
    stim = Stimuli(n_nodes=1000000, device=torch.device("cuda:0"), dtype=torch.float64)
    stim.add("/home/bzhou6/Data/atrium/Case_1/Case_1.vtx",
             name="s1",
             start=0,
             duration=100,
             intensity=100)
    print(stim.apply(1).shape)