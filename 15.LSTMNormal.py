import numpy as np
import tensorflow as tf
from tensorflow.contrib import rnn
import _12_input_data as input_data
import pickle as pic

input_vec_size = 18
lstm_size = 18
time_step_size = 18

batch_size = 20
test_size = 13

def init_weights(shape):
    return tf.Variable(tf.random_normal(shape, stddev=0.01))

def model(X, W, B, lstm_size):
    XT = tf.transpose(X, [1, 0, 2])
    XR = tf.reshape(XT, [-1, lstm_size])
    X_split = tf.split(XR, time_step_size, 0)
    lstm = rnn.BasicLSTMCell(lstm_size, forget_bias=1.0,state_is_tuple=True)
    # print (lstm._kernel)
    # print (lstm._bias)
    outputs, _states = rnn.static_rnn(lstm, X_split, dtype=tf.float32)
    return tf.matmul(outputs[-1],W)+B, lstm.state_size

# mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)

# trX, trY, teX, teY = mnist.train.images, mnist.train.labels, mnist.test.images, mnist.test.labels
file_a = open('x.pickle', 'rb')
data = pic.load(file_a)
trX = data[0:73]
teX = data[0:63]
file_a.close()

file_b = open('y.pickle', 'rb')
data = pic.load(file_b)
trY = data[0:73]
teY = data[0:63]
file_b.close()

# 将每张图用一个28x28的矩阵表示,(73,18,18,1)
# print (type(trY[0]))
trX = trX.reshape(-1, 18, 18)
teX = teX.reshape(-1, 18, 18)
# print (trX)

X = tf.placeholder("float", [None, 18, 18])
Y = tf.placeholder("float", [None, 20])

W = init_weights([lstm_size, 20])
B = init_weights([20])

py_x, state_size = model(X, W, B, lstm_size)

cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=py_x, labels=Y))
train_op = tf.train.RMSPropOptimizer(0.001, 0.9).minimize(cost)

predict_op = tf.argmax(py_x, 1)

with tf.Session() as sess:
    tf.global_variables_initializer().run()
    # params = tf.get_collection('params')
    # print(sess.run(params))
    for i in range(51):
        for start, end in zip(range(0, len(trX), batch_size), range(batch_size, len(trX)+1, batch_size)):
            sess.run(train_op, feed_dict={X: trX[start:end], Y: trY[start: end]})
        s = len(teX)
        test_indices = np.arange(len(teX))
        np.random.shuffle(test_indices)
        test_indices = test_indices[0: test_size]
        predict = sess.run(predict_op, feed_dict={X: teX[test_indices]})
        print("Iteration：", i)
        print("Train set: 73 persons.")
        print("Test set: 13 persons.")
        print("Predict: ", predict)
        actually = np.argmax(teY[test_indices], axis=1)
        print("Manual: ", actually)
        delta = np.mean(np.fabs(predict - actually))
        print("Predict error:", delta)
        print("Accuracy: ", np.mean(actually == predict))
        print("-------------------------------")
        # if i >= 1900:
            # print(delta)