import numpy as np
import pickle as pkl


class NaiveBayesWithSmoothing:
    
    def __init__(self, *hyperparameters):
        argCount = len(hyperparameters)
        if argCount == 0:
            self._alpha = 0.0
        else:
            self._alpha = float((hyperparameters[0])[0])
        self._X = None
        self._y = None
        self._Xtrain = None
        self._ytrain = None
        self._XVal = None
        self._yVAl = None
        self._classes = None
        self._wordProbVec = None
        self._classProbVec = None
        
    def load(self, inFilePath = 'model.npy'):
        pass
    
    def dump(self, outFilePath = 'model.npy'):
        pass
    
    def split_data(self, X):
        inds = np.arange(X.shape[0])
        n_train = np.floor(X.shape[0] * 0.7)
        np.random.shuffle(inds)
        train_inds = inds[:n_train]
        val_inds = inds[n_train:]
        self._Xtrain = X[train_inds,:-1] 
        self._ytrain = X[train_inds,-1] 
        self._XVal = X[val_inds,:-1]
        self._yVAl = X[val_inds,-1]

    def get_classes(self):
        return self._classes
    
    def log_prob(self, p):
        if p != 0.0:
            return np.log(p)
        return 0.0

    def train(self, data, labels, classes):
        print('Training the classifier...')
        self._X = data
        
        self._y = labels
        n, d = self._X.shape
        # Getting classes
        self._classes = classes
        # Computing classes probabilities
        self._classProbVec = np.zeros(self._classes.shape)
        for i, c in enumerate(self._classes):
            c_idx = np.where(self._y == i)[0]
            self._classProbVec[i] = self.log_prob(c_idx.shape[0]) - self.log_prob(n)
            
        # Computing words likelihoods
        self._wordProbVec = np.zeros((d, self._classes.shape[0]))
        for i, c in enumerate(self._classes):
            c_idx = np.where(self._y == i)[0]
            log_denominator = self.log_prob(np.sum(self._X[c_idx]) + self._alpha * d)
            for v in range(d):
                numerator = np.sum(self._X[c_idx, v], axis=0) + self._alpha
                self._wordProbVec[v, i] = self.log_prob(numerator) - log_denominator

    # Returns the class to which the sentence belongs 
    def predict(self, sentences):
        print('Predicting new comments...')
        bag_of_words = sentences
        n = bag_of_words.shape[0]
        predictions = np.zeros((n, self._classes.shape[0]))
        for i, test_sentence in enumerate(bag_of_words):
            for k, c in enumerate(self._classes):
                p = 0.0
                idx_list = np.where(test_sentence != 0)[0]  # TODO handle the case where no words in the voc are present
                for j in idx_list:
                    p += self._wordProbVec[j, k] 
                predictions[i, k] = p + self._classProbVec[k]
        
        return np.argmax(predictions, axis=1)
    
    # Training + Validation
    def fit(self, data, labels, classes):
        self.split_data(X)
