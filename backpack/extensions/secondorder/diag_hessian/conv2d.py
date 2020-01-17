import torch
import torch.nn

from backpack.core.derivatives.conv2d import Conv2DDerivatives
from backpack.utils import conv as convUtils
from backpack.utils.einsum import einsum

from .diag_h_base import DiagHBaseModule


class DiagHConv2d(DiagHBaseModule):
    def __init__(self):
        super().__init__(derivatives=Conv2DDerivatives(), params=["bias", "weight"])

    def bias(self, ext, module, g_inp, g_out, backproped):
        sqrt_h_outs = backproped["matrices"]
        sqrt_h_outs_signs = backproped["signs"]

        h_diag = torch.zeros_like(module.bias)
        for h_sqrt, sign in zip(sqrt_h_outs, sqrt_h_outs_signs):
            h_diag.add_(sign * einsum("cbijk,cbilm->i", (h_sqrt, h_sqrt)))
        return h_diag

    def weight(self, ext, module, g_inp, g_out, backproped):
        sqrt_h_outs = backproped["matrices"]
        sqrt_h_outs_signs = backproped["signs"]
        X = convUtils.unfold_func(module)(module.input0)
        h_diag = torch.zeros_like(module.weight)

        for h_sqrt, sign in zip(sqrt_h_outs, sqrt_h_outs_signs):
            h_diag_curr = convUtils.extract_weight_diagonal(module, X, h_sqrt)
            h_diag.add_(sign * h_diag_curr.view_as(module.weight))
        return h_diag
