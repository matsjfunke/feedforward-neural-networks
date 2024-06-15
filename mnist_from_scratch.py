"""
matsjfunke
"""
import math
import numpy as np  # linear algebra
import pandas as pd  # data processing CSV file
import matplotlib.pyplot as plt


# 1. load data
# The labeled training dataset consists of 42000 images, each of size 28x28 = 784 pixels. Labels are from 0 to 9 for pixelbrightness
train_data = pd.read_csv("./input/train.csv")

# separating labels and pixels
train_labels = np.array(train_data.loc[:, 'label'])
train_data = np.array(train_data.loc[:, train_data.columns != 'label'])


# 2. data visualization
# input number visualization.
index = 42  # change  index to view other numbers
plt.title(f"labeled as : {train_labels[index]}")
plt.imshow(train_data[index].reshape(28, 28), cmap="binary")
plt.show()


# distribution of numbers 0-9 accross training set
print("train data")
y_value = np.zeros((1, 10))
for i in range(10):
    print("occurance of ", i, "=", np.count_nonzero(train_labels == i))
    y_value[0, i-1] = np.count_nonzero(train_labels == i)

y_value = y_value.ravel()
x_value = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
plt.xlabel('number label')
plt.ylabel('count')
plt.bar(x_value, y_value, 0.7, color='r')
plt.xticks(x_value)
plt.show()


# 3. data preparation
# ensuring that train_data is a vector, and train_label is a matrix of 0's and 1's
train_data = np.reshape(train_data, [784, 42000])  # reshapes the training data, each image: originally 28x28 pixels is flattened into vector of 784 elements
train_label = np.zeros((10, 42000))  # one-hot encoding transforms categorical labels into  binary format
for col in range(42000):
    val = train_labels[col]
    for row in range(10):
        if (val == row):
            train_label[val, col] = 1
print("train_data shape=" + str(np.shape(train_data)))
print("train_label shape=" + str(np.shape(train_label)))


# 3. forward propagation
# activation functions (forward propagation)
# Z: linear transformation (pre-activation value)
def sigmoid(Z):
    activation_function = 1 / (1 + np.exp(-Z))
    cache = Z
    return activation_function, cache


def relu(Z):
    activation_function = np.maximum(0, Z)
    cache = Z
    return activation_function, cache


def softmax(Z):
    exponential_Z = np.exp(Z)
    activation_function = exponential_Z / np.sum(exponential_Z)
    cache = Z
    return activation_function, cache


# initializing the parameters (weights and biases)
def initialize_parameters_deep(layer_dims):
    parameters = {}
    layer_count = len(layer_dims)

    for layer in range(1, layer_count):
        parameters['W' + str(layer)] = np.random.randn(layer_dims[layer], layer_dims[layer - 1]) / np.sqrt(layer_dims[layer - 1])
        parameters['b' + str(layer)] = np.zeros((layer_dims[layer], 1))

    return parameters


# Computes the linear part of a layer's forward propagation
# A: activations from previous layer (or input data)
# W: weight matrix of current layer
# b: bias vector of current layer
def linear_forward(A, W, b):
    Z = np.dot(W, A) + b
    cache = (A, W, b)
    assert (Z.shape == (W.shape[0], A.shape[1]))
    return Z, cache


# Computes forward propagation layer with activation functions
# A_prev: activations from previous layer (or input data)
# W: weight matrix of current layer
# b: bias vector of current layer
def linear_activation_forward(A_prev, W, b, activation):
    if activation == "sigmoid":
        # Inputs: "A_prev, W, b". Outputs: "A, activation_cache".
        Z, linear_cache = linear_forward(A_prev, W, b)
        A, activation_cache = sigmoid(Z)
    elif activation == "relu":
        # Inputs: "A_prev, W, b". Outputs: "A, activation_cache".
        Z, linear_cache = linear_forward(A_prev, W, b)
        # print("Z="+str(Z))
        A, activation_cache = relu(Z)
    elif activation == "softmax":
        # Inputs: "A_prev, W, b". Outputs: "A, activation_cache".
        Z, linear_cache = linear_forward(A_prev, W, b)
        A, activation_cache = softmax(Z)
    cache = (linear_cache, activation_cache)

    return A, cache


# Computes forward propagation for the entire neural network
# X: input data
# AL: model prediction
# parameters: dictionary containing parameters (weights and biases) of the model
def model_forward_propagation(X, parameters):
    caches = []
    A = X
    network_layer = len(parameters) // 2

    # Forward propagation for layers 1 to (L-1) with ReLU activation
    for layer in range(1, network_layer):
        A_prev = A
        A, cache = linear_activation_forward(A_prev, parameters['W' + str(layer)], parameters['b' + str(layer)], activation="relu")
        caches.append(cache)

    # Forward propagation for the last layer (L) with softmax activation
    AL, cache = linear_activation_forward(A, parameters['W' + str(network_layer)], parameters['b' + str(network_layer)], activation="softmax")
    caches.append(cache)
    return AL, caches


# 4. cost calculation
def compute_cost(predicted_output, truth):
    example_count = truth.shape[1]
    cost = (-1 / example_count) * np.sum(np.multiply(truth, np.log(predicted_output)) + np.multiply(1 - truth, np.log(1 - predicted_output)))
    print("cost = " + str(cost))
    return cost


# 5.visualize graph of cost
def plot_graph(cost_plot):
    x_value = list(range(1, len(cost_plot) + 1))
    plt.xlabel('iteration')
    plt.ylabel('cost')
    plt.plot(x_value, cost_plot, 0., color='r')
    plt.show()


# 6. backward propagation
# derivative of activation function (backward propagation)
# remember gradients are used to find the minimum
def sigmoid_gradient(activation_fn_gradient, cache):
    Z = cache
    sigmoid_Z = 1 / (1 + np.exp(-Z))
    linear_transformation_gradient = activation_fn_gradient * sigmoid_Z * (1 - sigmoid_Z)

    assert (linear_transformation_gradient.shape == Z.shape)
    return linear_transformation_gradient


def relu_gradient(activation_fn_gradient, cache):
    Z = cache
    linear_transformation_gradient = np.array(activation_fn_gradient, copy=True)
    linear_transformation_gradient[Z <= 0] = 0

    assert (linear_transformation_gradient.shape == Z.shape)
    return linear_transformation_gradient


def softmax_gradient(Z, cache):
    Z = cache
    label_count = 10
    linear_transformation_gradient = np.zeros((42000, label_count))
    Z = np.transpose(Z)
    for row in range(0, 42000):
        denominator = (np.sum(np.exp(Z[row, :]))) * (np.sum(np.exp(Z[row, :])))
        for col in range(0, 10):
            sums = 0
            for j in range(0, 10):
                if (j != col):
                    sums = sums+(math.exp(Z[row, j]))

            linear_transformation_gradient[row, col] = (math.exp(Z[row, col]) * sums) / denominator
    linear_transformation_gradient = np.transpose(linear_transformation_gradient)
    Z = np.transpose(Z)

    assert (linear_transformation_gradient.shape == Z.shape)
    return linear_transformation_gradient


# Computes the linear part of a layer's backward propagation
def linear_backward(linear_transformation_gradient, cache):
    A_prev, W, b = cache
    training_examples = A_prev.shape[1]

    gradient_W = 1. / training_examples * np.dot(linear_transformation_gradient, A_prev.T)
    gradient_b = (1 / training_examples) * np.sum(linear_transformation_gradient, axis=1, keepdims=True)
    dA_prev = np.dot(W.T, linear_transformation_gradient)  # gradient of the cost with respect to the activations of the previous layer
    return dA_prev, gradient_W, gradient_b


# computes gradients for the combined linear and activation part of a single layer
    # using the linear_backward function and the derivations of activation functions (relu, sigmoid, softmax)
def linear_activation_backward(dA, cache, activation):
    linear_cache, activation_cache = cache
    if activation == "relu":
        dZ = relu_gradient(dA, activation_cache)
        dA_prev, gradient_W, gradient_b = linear_backward(dZ, linear_cache)
    elif activation == "sigmoid":
        dZ = sigmoid_gradient(dA, activation_cache)
        dA_prev, gradient_W, gradient_b = linear_backward(dZ, linear_cache)
    elif activation == "softmax":
        dZ = softmax_gradient(dA, activation_cache)
        dA_prev, gradient_W, gradient_b = linear_backward(dZ, linear_cache)
    return dA_prev, gradient_W, gradient_b


# computes gradients for all layers in the model
    # by chaining linear_activation_backward for each layer during backpropagation
def model_backward_propagation(AL, truth, caches):
    grads = {}
    layer_count = len(caches)  # This is the same as len(layers_dims) - 1
    dAL = - (np.divide(truth, AL) - np.divide(1 - truth, 1 - AL))
    M = len(layers_dims)  # Total number of layers including input layer
    current_cache = caches[M - 2]
    grads["dA" + str(M - 1)], grads["dW" + str(M - 1)], grads["db" + str(M - 1)] = linear_activation_backward(dAL, current_cache, activation="softmax")

    for layer in reversed(range(layer_count-1)):
        current_cache = caches[layer]
        dA_prev_temp, dW_temp, db_temp = linear_activation_backward(grads["dA" + str(layer + 2)], current_cache, activation="relu")
        grads["dA" + str(layer + 1)] = dA_prev_temp
        grads["dW" + str(layer + 1)] = dW_temp
        grads["db" + str(layer + 1)] = db_temp

    return grads


# 7. upgrade function for weights and bias
def update_parameters(parameters, grads, learning_rate):
    len_update = len(parameters) // 2  # contains both weights & biases for each layer

    for layer_idx in range(len_update):
        parameters["W" + str(layer_idx+1)] = parameters["W" + str(layer_idx+1)] - (learning_rate * grads["dW" + str(layer_idx+1)])
        parameters["b" + str(layer_idx+1)] = parameters["b" + str(layer_idx+1)] - (learning_rate * grads["db" + str(layer_idx+1)])

    return parameters


# 8. defining structure of neural network -> adjust layers_dims for different shapes
# function to call sub_functions
def train_neural_net(X, Y, layers_dims, learning_rate, max_iterations, tolerance):
    print("training...")
    cost_plot = np.zeros(max_iterations)
    parameters = initialize_parameters_deep(layers_dims)

    for i in range(0, max_iterations):
        AL, caches = model_forward_propagation(X, parameters)

        cost = compute_cost(AL, Y)

        grads = model_backward_propagation(AL, Y, caches)

        parameters = update_parameters(parameters, grads, learning_rate)

        cost_plot[i] = cost
        if i > 0 and abs(cost_plot[i] - cost_plot[i-1]) < tolerance:
            print(f"Training stopped early at iteration {i} due to convergence within tolerance.")
            cost_plot = cost_plot[:i+1]  # Truncate cost_plot to the number of iterations run
            break

    plot_graph(cost_plot)
    print("training done")
    return parameters


# input layer of 28* 28=784 pixel value, output layer of 10 classes / predictions(0 to 9).
layers_dims = [784, 500, 400, 300, 100, 10]  # n-layer model (n=6 including input and output layer)
# first hidden layer has 500 nodes, second hiden layer has 400 nodes

parameters = train_neural_net(train_data, train_label, layers_dims, learning_rate=0.0005, max_iterations=35, tolerance=0.3)
# variable parameter in network learning_rate, max_iterations, tolerance


# 9. test model prediction
def test_prediction(parameters, X, index):
    # Ensure X is of the right shape (input layer)
    X_sample = X[:, index].reshape(-1, 1)

    # Perform forward propagation
    AL, _ = model_forward_propagation(X_sample, parameters)

    # Convert output to predicted label
    predicted_label = np.argmax(AL, axis=0)[0]

    return predicted_label


sample_index = 42  # Change this index to predict other samples
predicted_label = test_prediction(parameters, train_data, sample_index)
print(f"Predicted label for sample index {train_labels[sample_index]}: {predicted_label}")
