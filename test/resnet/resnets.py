"""Contains example from Katharina Ott."""

import torch
from torch.nn import MSELoss, Sequential, Tanh

from backpack import backpack, extend
from backpack.custom_module.branching import ActiveIdentity, Parallel
from backpack.custom_module.scale_module import ScaleModule
from backpack.extensions import DiagGGNExact

# parameter
dt = 0.1
in_dim, hidden_dim = (2, 10)

# define net and loss function
lin1 = torch.nn.Linear(in_dim, hidden_dim)
lin2 = torch.nn.Linear(hidden_dim, hidden_dim)
lin3 = torch.nn.Linear(hidden_dim, in_dim)
activation_function_1 = Tanh()
activation_function_2 = Tanh()
net = Sequential(lin1, activation_function_1, lin2, activation_function_2, lin3)
net = extend(net)
loss_function = extend(MSELoss())

# define input and solution
x = torch.tensor([[1.0, 2.0]])
solution = torch.tensor([[1.0, 1.0]])

# version from Katharina
logits = x + net(x) * dt
loss = loss_function(logits, solution)

"""with backpack(KFAC()):
    loss.backward()
for param in net.parameters():
    print(param.grad)
    print(param.kfac)"""


print("\nAlternative network.")
# the BackPACK equivalent
NET_KATHARINA = Parallel(
    Sequential(net, ScaleModule(weight=dt)),
    ActiveIdentity(),
)
NET_KATHARINA = extend(NET_KATHARINA)
logits_alt = NET_KATHARINA(x)
loss_alt = loss_function(logits_alt, solution)

print("Do the logits match?", torch.allclose(logits, logits_alt))
print("Do the losses match?", torch.allclose(loss, loss_alt))

with backpack(DiagGGNExact()):
    loss_alt.backward()
for param in net.parameters():
    print(param.grad)
    print(param.diag_ggn_exact)
