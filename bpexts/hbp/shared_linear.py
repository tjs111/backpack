"""Hessian backpropagation for multiple layers sharing the input.

This allows to treat weights/bias independently during optimization,
leading to smaller Hessians, thereby allowing for in principle massively
parallel optimization.
"""

from numpy import cumsum
from .linear import HBPLinear
from .parallel import HBPParallel


class HBPParallelFactory(HBPParallel):
    """Factory for layers sharing the same input."""

    @classmethod
    def hbp_linear_with_splitting(cls, in_features, out_features_list,
                                  bias=True):
        """Return linear layers acting in parallel on the same input.

        Parameters:
        -----------
        in_features : (int)
            Number of input features
        out_features_list : (list(int))
            Output features for each of the parallel modules
        bias : (bool)
            Use bias terms in linear layers

        Returns:
        --------
        (HBPSharedLinear)
        """
        layers = []
        for idx, out in enumerate(out_features_list):
            layers.append(HBPLinear(in_features=in_features,
                                    out_features=out,
                                    bias=bias))
        return cls(layers)

    @classmethod
    def fromHBPLinear(cls, hbp_linear, out_features_list):
        """Convert a linear layer into multiple parallel linear layers.

        Parameters:
        -----------
        hbp_linear : (HBPLinear)
            Linear layer with backpropagation functionality
        out_features_list : (list(int))
            Output features for each of the parallel modules

        Returns:
        --------
        (HBPSharedLinear)
        """
        if not sum(out_features_list) == hbp_linear.out_features:
            raise ValueError('Invalid splitting: {} does not sum'
                             'to {}'.format(out_features_list,
                                            hbp_linear.out_features))
        layers = []
        in_features = hbp_linear.in_features
        has_bias = (hbp_linear.bias is not None)
        idx = [0] + list(cumsum(out_features_list))
        idx = [(idx[i], idx[i + 1]) for i in range(len(idx) - 1)]
        for out, (i, j) in zip(out_features_list, idx):
            layer = HBPLinear(in_features=in_features,
                              out_features=out,
                              bias=has_bias)
            layer.weight.data = hbp_linear.weight.data[i:j, :]
            if has_bias:
                layer.bias.data = hbp_linear.bias.data[i:j]
            layers.append(layer)
        return cls(layers)

    @classmethod
    def fromHBPCompositionActivationLinear(cls, hbp_composition,
                                           out_features_list):
        """Convert linear(activation) into multiple parallel modules.

        Parameters:
        -----------
        hbp_composition : (HBPCompositionActivationLinear)
            Composition layer linear(activation)
        out_features_list : (list(int))
            Output features for each of the parallel modules

        Returns:
        --------
        (HBPSharedLinear)

        """
        hbp_composition_cls = hbp_composition.__class__
        if not sum(out_features_list) == hbp_composition.linear.out_features:
            raise ValueError('Invalid splitting: {} does not sum'
                             'to {}'.format(
                                 out_features_list,
                                 hbp_composition.linear.out_features))
        layers = []
        in_features = hbp_composition.linear.in_features
        has_bias = (hbp_composition.linear.bias is not None)
        idx = [0] + list(cumsum(out_features_list))
        idx = [(idx[i], idx[i + 1]) for i in range(len(idx) - 1)]
        for out, (i, j) in zip(out_features_list, idx):
            layer = hbp_composition_cls(in_features=in_features,
                                        out_features=out,
                                        bias=has_bias)
            layer.linear.weight.data = hbp_composition.linear.weight.data[i:j, :]
            if has_bias:
                layer.linear.bias.data = hbp_composition.linear.bias.data[i:j]
            layers.append(layer)
        return cls(layers)
