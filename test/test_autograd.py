"""Test autograd functionality like retain_graph."""
from pytest import raises
from torch import rand, randint
from torch.nn import CrossEntropyLoss, Linear, Module, Sequential

from backpack import extend


def test_retain_graph():
    model = extend(Sequential(Linear(4, 6), Linear(6, 5)))
    loss_fn = extend(CrossEntropyLoss())

    # after a forward pass graph is not clear
    loss = loss_fn(model(rand(8, 4)), randint(5, (8,)))
    with raises(AssertionError):
        _clear_input_output(model)

    # after a normal backward pass graph should be clear
    loss.backward()
    _clear_input_output(model)

    # after a backward pass with retain_graph=True graph is not clear
    loss = loss_fn(model(rand(8, 4)), randint(5, (8,)))
    loss.backward(retain_graph=True)
    with raises(AssertionError):
        _clear_input_output(model)

    # doing several backward passes with retain_graph=True
    for _ in range(3):
        loss.backward(retain_graph=True)

    # finally doing a normal backward pass that verifies graph is clear again
    loss.backward()
    _clear_input_output(model)


def _clear_input_output(parent_module: Module) -> bool:
    if list(parent_module.children()):
        return all([_clear_input_output(module) for module in parent_module.children()])
    elif hasattr(parent_module, "input0") or hasattr(parent_module, "output"):
        raise AssertionError(
            f"graph should be clear, but {parent_module} has input0 or output."
        )
    else:
        return True
