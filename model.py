# model.py
import torch
import torch.nn as nn

# Hyperparameters initialization
in_channels = 1
conv1_out_channels = 6
conv1_kernel_size = 5

conv2_out_channels = 16
conv2_kernel_size = 5

conv3_out_channels = 120
conv3_kernel_size = 5

fc1_out_features = 84
fc2_out_features = 10

pool_kernel_size = 2
pool_stride = 2

class LeNet5(nn.Module):
    def __init__(self):
        super(LeNet5, self).__init__()
        
        # First convolutional layer (C1)
        self.conv1 = nn.Conv2d(in_channels, conv1_out_channels, kernel_size=conv1_kernel_size)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.AvgPool2d(kernel_size=pool_kernel_size, stride=pool_stride)
        
        # Second convolutional layer (C3)
        self.conv2 = nn.Conv2d(conv1_out_channels, conv2_out_channels, kernel_size=conv2_kernel_size)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.AvgPool2d(kernel_size=pool_kernel_size, stride=pool_stride)
        
        # Third convolutional layer (C5)
        self.conv3 = nn.Conv2d(conv2_out_channels, conv3_out_channels, kernel_size=conv3_kernel_size)
        self.relu3 = nn.ReLU()
        
        # Fully connected layers (F6 and OUTPUT)
        self.fc1 = nn.Linear(conv3_out_channels, fc1_out_features)
        self.relu4 = nn.ReLU()
        self.fc2 = nn.Linear(fc1_out_features, fc2_out_features)  # 10 classes output
        
    def forward(self, x):
        # Convolutional layers
        x = self.pool1(self.relu1(self.conv1(x)))
        x = self.pool2(self.relu2(self.conv2(x)))
        x = self.relu3(self.conv3(x))
        
        # Flatten the feature maps
        x = x.view(-1, conv3_out_channels)
        
        # Fully connected layers
        x = self.relu4(self.fc1(x))
        x = self.fc2(x)
        
        return x
