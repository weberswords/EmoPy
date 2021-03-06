import sys
sys.path.append('../')
from imageprocessor import ImageProcessor
from neuralnets import ConvolutionalLstmNN
from featureextractor import FeatureExtractor
import numpy as np
from skimage import color, io

time_delay = 1
raw_dimensions = (48, 48)
target_dimensions = (64, 64)
channels = 1
verbose = True
using_feature_extraction = True
target_labels = [0,1,2,3,4,5,6]


print('--------------- Convolutional LSTM Model -------------------')
print('Collecting data...')
csv_file_path = "image_data/sample.csv"
imageProcessor = ImageProcessor(from_csv=True, target_labels=target_labels, datapath=csv_file_path, target_dimensions=target_dimensions, raw_dimensions=raw_dimensions, csv_label_col=0, csv_image_col=1, channels=1)
images, labels = imageProcessor.get_training_data()
if verbose:
	print ('images shape: ' + str(images.shape))

print('Extracting features...')
featureExtractor = FeatureExtractor(images, return_2d_array=True)
featureExtractor.add_feature('hog', {'orientations': 8, 'pixels_per_cell': (16, 16), 'cells_per_block': (1, 1)})
raw_features = featureExtractor.extract()
features = list()
for feature in raw_features:
   features.append([[feature]])
features = np.array(features)
if verbose:
    print('feature shape: ' + str(features.shape))
    print('label shape: ' + str(labels.shape))

print('Creating training/testing data...')
validation_split = 0.15

print('Training net...')
model = ConvolutionalLstmNN(target_dimensions, channels, target_labels, time_delay=time_delay)
model.fit(features, labels, validation_split)