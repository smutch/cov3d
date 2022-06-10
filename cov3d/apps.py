from pathlib import Path
from torch import nn
from fastai.data.core import DataLoaders
from fastai.data.transforms import GrandparentSplitter
from fastai.data.core import DataLoaders
from fastai.data.block import DataBlock

import fastapp as fa
from rich.console import Console
console = Console()

from .transforms import CTScanBlock, BinaryBlock
from .models import ResNet3d

def get_y(scan_path:Path):
    parent_name = scan_path.parent.name
    if parent_name == "covid":
        return True
    if parent_name == "non-covid":
        return False
    raise Exception(f"Cannot determine whether sample '{scan_path}' has covid or not from the path.")


class Cov3d(fa.FastApp):
    """
    A deep learning model to detect the presence and severity of COVID19 in patients from CT-scans.
    """
    def dataloaders(
        self,
        directory:Path = fa.Param(help="The data directory."), 
        batch_size:int = fa.Param(default=4, help="The batch size."),
    ) -> DataLoaders:
        """
        Creates a FastAI DataLoaders object which Cov3d uses in training and prediction.

        Args:
            directory (Path): The data directory.
            batch_size (int, optional): The number of elements to use in a batch for training and prediction. Defaults to 32.

        Returns:
            DataLoaders: The DataLoaders object.
        """
        subdirs = ["train/covid", "train/non-covid", "validation/covid", "validation/non-covid"]
        paths = []
        for s in subdirs:
            subdir = directory/s
            assert subdir.exists()
            subdir_paths = [path for path in subdir.iterdir() if path.name.startswith("ct_scan")]
            assert len(subdir_paths) > 0
            paths += subdir_paths

        datablock = DataBlock(
            blocks=(CTScanBlock, BinaryBlock),
            splitter=GrandparentSplitter(train_name='train', valid_name='validation'),
            get_y=get_y,
        )

        dataloaders = DataLoaders.from_dblock(
            datablock, 
            source=paths,
            bs=batch_size,
        )

        return dataloaders    

    def model(
        self,
    ) -> nn.Module:
        """
        Creates a deep learning model for the Cov3d to use.

        Returns:
            nn.Module: The created model.
        """ 
        return ResNet3d()
