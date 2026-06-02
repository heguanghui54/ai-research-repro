import random, time
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from ogb.nodeproppred import Evaluator, PygNodePropPredDataset

SEED = 20260603
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
target_dataset = "ogbn-arxiv"
start = time.time()
dataset = PygNodePropPredDataset(name=target_dataset, root="networks")
data = dataset[0]
split_idx = dataset.get_idx_split()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
x = data.x.to(device).float()
y = data.y.view(-1).to(device)
train_idx = split_idx["train"].to(device)
valid_idx = split_idx["valid"].to(device)
test_idx = split_idx["test"].to(device)
class MLP(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.lin1 = torch.nn.Linear(x.size(-1), 16)
        self.bn1 = torch.nn.BatchNorm1d(16)
        self.lin2 = torch.nn.Linear(16, dataset.num_classes)
    def forward(self, x):
        z = F.relu(self.bn1(self.lin1(x)))
        return torch.log_softmax(self.lin2(z), dim=-1)
model = MLP().to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=1.0)
evaluator = Evaluator(name=target_dataset)
def acc(idx, pred):
    return evaluator.eval({"y_true": data.y[idx.cpu()].cpu(), "y_pred": pred[idx.cpu()].cpu().view(-1,1)})["acc"]
for epoch in range(4):
    model.train(); optimizer.zero_grad()
    out = model(x)
    loss = F.nll_loss(out[train_idx], y[train_idx])
    loss.backward(); optimizer.step()
    model.eval()
    with torch.no_grad():
        pred = model(x).argmax(dim=-1).cpu()
    print(f"epoch={epoch} loss={float(loss):.6f} train_acc={acc(train_idx, pred):.4f} val_acc={acc(valid_idx, pred):.4f}", flush=True)
model.eval()
with torch.no_grad():
    pred = model(x).argmax(dim=-1).cpu().numpy()
pd.DataFrame(pred[split_idx["test"].numpy()]).to_csv("submission.csv", index=False)
print(f"done seconds={time.time()-start:.2f}", flush=True)
