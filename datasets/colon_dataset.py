import torch

class ColonDataset(torch.utils.data.Dataset):
    def __init__(self, root, split='train', transform=None, target_transform=None):
        self.transform = transform
        self.target_transform = target_transform

    def __getitem__(self, idx):
        if idx < self.size:
            data = self.data[idx]
            label = self.label[idx]
        else:
            raise Exception
        if self.transform:
            data = self.transform(data)
        return data, label

    def __len__(self):
        return self.data.size
