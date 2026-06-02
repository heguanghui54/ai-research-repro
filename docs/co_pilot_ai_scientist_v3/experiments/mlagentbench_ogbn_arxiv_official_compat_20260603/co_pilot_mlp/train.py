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
x = data.x.float()
x = (x - x.mean(dim=0, keepdim=True)) / (x.std(dim=0, keepdim=True) + 1e-6)
x = x.to(device)
y = data.y.view(-1).to(device)
train_idx = split_idx["train"].to(device)
valid_idx = split_idx["valid"].to(device)
test_idx = split_idx["test"].to(device)
class MLP(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(x.size(-1), 256),
            torch.nn.BatchNorm1d(256),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.25),
            torch.nn.Linear(256, 256),
            torch.nn.BatchNorm1d(256),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.25),
            torch.nn.Linear(256, dataset.num_classes),
        )
    def forward(self, x):
        return torch.log_softmax(self.net(x), dim=-1)
model = MLP().to(device)
optimizer = torch.optim.AdamW(model.parameters(), lr=0.01, weight_decay=1e-4)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=80)
evaluator = Evaluator(name=target_dataset)
best_val = -1.0
best_pred = None
patience = 12
stale = 0
def acc(idx, pred):
    return evaluator.eval({"y_true": data.y[idx.cpu()].cpu(), "y_pred": pred[idx.cpu()].cpu().view(-1,1)})["acc"]
for epoch in range(80):
    model.train(); optimizer.zero_grad()
    out = model(x)
    loss = F.nll_loss(out[train_idx], y[train_idx])
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
    optimizer.step(); scheduler.step()
    model.eval()
    with torch.no_grad():
        pred = model(x).argmax(dim=-1).cpu()
    train_acc = acc(train_idx, pred)
    val_acc = acc(valid_idx, pred)
    if val_acc > best_val:
        best_val = val_acc; best_pred = pred.clone(); stale = 0
    else:
        stale += 1
    print(f"epoch={epoch} loss={float(loss):.6f} train_acc={train_acc:.4f} val_acc={val_acc:.4f} best_val={best_val:.4f}", flush=True)
    if epoch >= 20 and stale >= patience:
        print(f"early_stop epoch={epoch}", flush=True)
        break
pd.DataFrame(best_pred[split_idx["test"].numpy()].numpy()).to_csv("submission.csv", index=False)
print(f"done best_val={best_val:.4f} seconds={time.time()-start:.2f}", flush=True)
