from torch import randn
from torch.nn import MaxPool2d
from backpack import extend


def data():
    N, C, Hin, Win = 100, 10, 32, 32
    KernelSize = 4

    X = randn(N, C, Hin, Win, requires_grad=True)
    module = extend(MaxPool2d(KernelSize))
    out = module(X)

    Hout = int(Hin / KernelSize)
    Wout = int(Win / KernelSize)
    vout = randn(N, C, Hin, Win)
    vin = randn(N, C, Hout, Wout)

    return {
        "X": X,
        "module": module,
        "output": out,
        "vout_ag": vout,
        "vout_bp": vout.view(N, -1, 1),
        "vin_ag": vin,
        "vin_bp": vin.view(N, -1, 1),
    }
