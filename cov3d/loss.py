import torch
from torch import nn
import torch.nn.functional as F
from torch import Tensor
from torch.autograd import Variable

class FocalLoss(nn.Module):
    def __init__(
        self,
        gamma:float=2.0,
        weights:Tensor=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.gamma = gamma
        self.weights = weights

    def forward(self, predictions: Tensor, target: Tensor) -> Tensor:
        """
        Adapted from https://github.com/clcarwin/focal_loss_pytorch/blob/master/focalloss.py
        """
        target = target.view(-1,1)
        log_probabilities = F.log_softmax(predictions, dim=-1)
        log_probability = log_probabilities.gather(1,target)
        probability = Variable(log_probability.data.exp())
        loss = -(1-probability)** self.gamma * log_probability

        # Weights
        if self.weights is not None:
            self.weights = self.weights.to(target.device)
            loss *= torch.gather(self.weights, -1, target)

        return loss.mean()


class WeightedCrossEntropyLoss(nn.CrossEntropyLoss):
    def __init__(self, *args, **kwargs):
        kwargs['reduction'] = 'none'
        super().__init__(*args, **kwargs)

    def forward(self, predictions: Tensor, target: Tensor, weights: Tensor) -> Tensor:
        result = super().forward(predictions, target)
        assert result.shape == weights.shape
        result *= weights

        return result.mean()
    


class WeightedFocusLoss(nn.CrossEntropyLoss):
    def __init__(self, gamma:float=0.0, *args, **kwargs):
        kwargs['reduction'] = 'none'
        super().__init__(*args, **kwargs)
        self.gamma = gamma

    def forward(self, predictions: Tensor, target: Tensor, weights: Tensor) -> Tensor:
        target = target.view(-1,1)
        log_probabilities = F.log_softmax(predictions, dim=-1)
        log_probability = log_probabilities.gather(1,target)
        probability = Variable(log_probability.data.exp())
        result = -(1-probability)** self.gamma * log_probability

        result = result.squeeze()
        assert result.shape == weights.shape
        result *= weights

        return result.mean()    