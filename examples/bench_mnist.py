from sklearn.cross_validation import train_test_split
from sklearn.datasets import fetch_mldata

import sys
import time
import logging
import numpy as np

np.set_printoptions(precision=4)
np.set_printoptions(suppress=True)

log = logging.getLogger()
log.setLevel(logging.DEBUG)

stdout = logging.StreamHandler(sys.stdout)
stdout.setLevel(logging.DEBUG)
stdout.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
log.addHandler(stdout)

mnist = fetch_mldata('MNIST original')
X_train, X_test, y_train, y_test = train_test_split(mnist.data / 255.0, mnist.target, test_size=0.33, random_state=1234)

classifiers = []


try:
    from nolearn.dbn import DBN
    clf = DBN(
        [X_train.shape[1], 300, 10],
        learn_rates=0.3,
        learn_rate_decays=0.9,
        epochs=10,
        verbose=1)
    classifiers.append(('nolearn.dbn', clf))
except ImportError:
    pass


try:
    from nolearn.lasagne import NeuralNet
    from lasagne.layers import InputLayer, DenseLayer
    from lasagne.nonlinearities import softmax
    from lasagne.updates import nesterov_momentum

    clf = NeuralNet(
        layers=[
            ('input', InputLayer),
            ('hidden1', DenseLayer),
            ('output', DenseLayer),
            ],
        input_shape=(None, 784),
        output_num_units=10,
        output_nonlinearity=softmax,
        eval_size=0.0,

        more_params=dict(
            hidden1_num_units=300,
        ),

        update=nesterov_momentum,
        update_learning_rate=0.02,
        update_momentum=0.9,

        max_epochs=10,
        verbose=1
        )
    classifiers.append(('nolearn.lasagne', clf))

except ImportError:
    pass


try:
    from sknn.mlp import MultiLayerPerceptronClassifier

    clf = MultiLayerPerceptronClassifier(
        layers=[("Rectifier", 300), ("Softmax",)],
        learning_rate=0.02,
        learning_rule='momentum',
        batch_size=25,
        n_stable=10,
        n_iter=10,
        verbose=0,
    )
    classifiers.append(('sknn.mlp', clf))
except ImportError:
    pass


for name, clf in classifiers:
    start = time.time()
    clf.fit(X_train.astype(np.float32), y_train.astype(np.int32))

    from sklearn.metrics import classification_report

    y_pred = clf.predict(X_test)
    print name
    print "\tAccuracy:", clf.score(X_test, y_test)
    print "\tTime:", time.time() - start
    print "\tReport:"
    print classification_report(y_test, y_pred)
