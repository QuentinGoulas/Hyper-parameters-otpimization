import torch as th
import numpy as np
import itertools as iter
import LE_NET5_1 as ln5
import copy

class HyperParameterOptimizer:
    '''
    A hyper parameter optimizer class to optimize the hyperparameters of a simple CNN
    '''
    def __init__(self, hpspace, seed):
        '''
        Inputs :
        - hpspace : the possible values for the hyperparameter of study (dict of numpy array)
        - method : the optimization method we want to use (seed)
        - seed : a seed model to start the optimization (torch.nn.Module)
        '''
        self.hpspace = hpspace
        self.module = copy.deepcopy(seed)
        self.seed = copy.deepcopy(seed)
        print("HyperParameterOptimizer initialized")

    def load_data(self):
        self.device = (
            "cuda"
            if th.cuda.is_available()
            else "mps"
            if th.backends.mps.is_available()
            else "cpu")
        print(f"Using {self.device} device")

        self.trainloader,self.testloader = ln5.load_data()

        self.module.to(self.device)
        # self.trainloader.to(self.device)
        # self.testloader.to(self.device)

        print("Data loaders have been initialized")
    
    def update_hyperparam(self, new_hp):
        '''
        A function to update the hyperparameter values of the module
        '''
        for hp in self.hpspace:
            # Select the node to modify
            node, next_node = self.fetch_node(hp)
            if hp == 'F6':
                node.out_features = new_hp[hp]
                next_node.in_features = new_hp[hp]
            elif hp in ['C1_chan','C3_chan','C5_chan']:
                node.out_channel = new_hp[hp]
                next_node.in_channel = new_hp[hp]
            elif hp == ['C1_kernel','C3_kernel','C5_kernel']:
                node.kernel_size = new_hp[hp]
            pass

    def fetch_node(self, hp):
        '''
        A function to fetch the nn Layer of the module with hyperparameter hp, as well as its following layer
        '''
        if hp == 'F6':
            node = self.module.fc1
            next_node = self.module.fc2
        elif hp in ['C1_chan','C1_kernel']:
            node = self.module.conv1
            next_node = self.module.conv2
        elif hp in ['C3_chan','C3_kernel']:
            node = self.module.conv2
            next_node = self.module.conv3
        elif hp in ['C5_chan','C5_kernel']:
            node = self.module.conv5
            next_node = self.module.fc1
        else :
            raise NameError('Model node unknown')
        
        return node, next_node

    def train_module(self,epochs):
        '''
        Train the optimizers' module
        '''
        criterion = th.nn.CrossEntropyLoss()
        optimizer = th.optim.Adam(self.module.parameters(), lr=0.001)

        ln5.train_model(self.module,self.trainloader,criterion,optimizer,self.device,epochs)
        acc = ln5.test_model(self.module,self.testloader,self.device)

        return acc

    def optimize(self, method, **kwargs):
        '''
        A method to optimize the hyperparameters of the module on a Le-Net 5 architecture
        Name value arguments are available to control the algorithm parameters
        '''
        if method == 'grid_search':
            '''
            Tests all combinations of the hyperparameter space to find the best combination
            '''
            hpspace = np.array([dict(zip(self.hpspace.keys(), values)) for values in iter.product(*self.hpspace.values())])
            accuracy = np.zeros(hpspace.shape)
            epochs = 2
            
            for i in range(len(hpspace)):
                self.module = copy.deepcopy(self.seed) # always start the optimization from the seed
                self.update_hyperparam(hpspace[i])
                accuracy[i] = self.train_module(epochs)

            best_hp = hpspace[np.argmax(accuracy)]
            self.result = {
                'best_hp':best_hp,
            }

            print(f"Hyperparameter optimization finished, best parameter value is {self.result['best_hp']}")
        
        if method == 'random_search':
            '''
            Selects a proportion p of the hyperparameter configurations and tries all the seleted configs
            '''
            assert 'p' in list(kwargs.keys()), "no sampling proportion given at input keyword 'p'"

            p = kwargs['p'] # proportion of samples to try in the hyperparameter optimization
            hpspace = np.array([dict(zip(self.hpspace.keys(), values)) for values in iter.product(*self.hpspace.values())])
            numel = int(np.fix(p*len(hpspace)))
            ind = np.random.choice(range(len(hpspace)),numel) # choose the hyperparameter configs to try out
            accuracy = np.zeros(ind.shape)
            epochs = 2

            for i in range(len(ind)):
                print(f"Testing hyperparameter config : {hpspace[ind[i]]}\n")
                self.module = copy.deepcopy(self.seed) # always start the optimization from the seed
                self.update_hyperparam(hpspace[ind[i]])
                accuracy[i] = self.train_module(epochs)
            
            best_hp = hpspace[ind[np.argmax(accuracy)]]
            self.result = {
                'best_hp':best_hp
            }

        if method == 'pso':
            '''
            Runs a particle swarm optimization algorithm to find the best configuration
            '''
            pass

        return self.result

######################### Test script #########################
if __name__ == '__main__':
    HPOptim = HyperParameterOptimizer({'F6':[80,160],'C3_chan':[6,12]},seed = ln5.LeNet5())
    HPOptim.load_data()
    res = HPOptim.optimize('random_search',p=0.5)
    print(res)