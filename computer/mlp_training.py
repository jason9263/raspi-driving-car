import cv2
import numpy as np
import glob

print 'Loading training data...'
e0 = cv2.getTickCount()

# load training data
image_array = np.zeros((1, 38400), 'float')
label_array = np.zeros((1, 4), 'float')
training_data = glob.glob('training_data/*.npz')

for single_npz in training_data:
    with np.load(single_npz) as data:
        print data.files
        train_temp = data['train']
        train_labels_temp = data['train_labels']
        print train_temp.shape
        print train_labels_temp.shape
    image_array = np.vstack((image_array, train_temp))
    label_array = np.vstack((label_array, train_labels_temp))

train = image_array[1:, :]
train_labels = label_array[1:, :]
print train
print type(train)
print train_labels

print train.shape
print train_labels.shape

e00 = cv2.getTickCount()
time0 = (e00 - e0)/ cv2.getTickFrequency()
print 'Loading image duration:', time0

# set start time
e1 = cv2.getTickCount()

# create MLP
layer_sizes = np.array([38400, 32, 4], dtype=np.float32)
# model = cv2.ml.ANN_MLP()
model = cv2.ml.ANN_MLP_create()
model.setLayerSizes(layer_sizes)
# model.create(layer_sizes)
criteria = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 500, 0.0001)
criteria2 = (cv2.TERM_CRITERIA_COUNT, 100, 0.001)


model.setTrainMethod(cv2.ml.ANN_MLP_BACKPROP | cv2.ml.ANN_MLP_UPDATE_WEIGHTS)
model.setActivationFunction(cv2.ml.ANN_MLP_SIGMOID_SYM)
model.setTermCriteria(criteria)



# params = dict(term_crit = criteria,
#                train_method = cv2.ml.ANN_MLP_BACKPROP,
#                bp_dw_scale = 0.001,
#                bp_moment_scale = 0.0 )

print 'Training MLP ...'
num_iter = model.train(np.array(train, dtype=np.float32), cv2.ml.ROW_SAMPLE,np.array(train_labels, dtype=np.float32))
# set end time
e2 = cv2.getTickCount()
time = (e2 - e1)/cv2.getTickFrequency()
print 'Training duration:', time

# save param
model.save('mlp_xml/mlp.xml')

print 'Ran for %d iterations' % num_iter

ret, resp = model.predict(train)
prediction = resp.argmax(-1)
print 'Prediction:', prediction
true_labels = train_labels.argmax(-1)
print 'True labels:', true_labels

print 'Testing...'
train_rate = np.mean(prediction == true_labels)
print 'Train rate: %f:' % (train_rate*100)