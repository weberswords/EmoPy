import os, csv, cv2, math, datetime
from skimage import color, io
import numpy as np
from keras.preprocessing.image import ImageDataGenerator


EMOTION_DIMENSION_COUNT = 4 # emotional dimensions: arousal, valence, expectation, power

class ImageProcessor:
    """
    Contains various image preprocessing methods.

    :param from_csv: if true, images will be extracted from csv file
    :param target_labels: list of target label values/strings
    :param datapath: location of image dataset
    :param target_dimensions: final dimensions of training images
    :param raw_dimensions: initial dimensions of raw training images
    :param csv_label_col: index of label value column in csv
    :param csv_image_col: index of image column in csv
    :param rgb: true if images are in rgb
    :param channels: number of desired channels. if raw images are grayscale, may still want 3 channels for desired neural net input
    """
    def __init__(self, from_csv=None, target_labels=None, datapath=None, target_dimensions=None, raw_dimensions=None, csv_label_col=None, csv_image_col=None, augment_data=False, rgb=False, channels=3):
        self.from_csv = from_csv
        self.datapath = datapath
        self.target_dimensions = target_dimensions
        self.raw_dimensions = raw_dimensions
        self.csv_label_col = csv_label_col
        self.csv_image_col = csv_image_col
        self.augment_data = augment_data
        self.target_labels = target_labels
        self.rgb = rgb
        self.channels = channels

    def get_training_data(self):
        """
        :return: list of images from specified location with preliminary processing applied
        """
        if self.from_csv:
            return self._get_training_data_from_csv()
        else:
            images = self._get_image_feature_array_from_directory()
            labels = self._get_training_label_array()
            return images, labels

    def _get_image_feature_array_from_directory(self):
        """
        :return:  list of images from directory location, resized to specified target dimensions
        """
        images = list()
        for sub_directory in os.listdir(self.datapath):
            if not sub_directory.startswith('.'):
                sub_directory_path = self.datapath + '/' + sub_directory
                for image_file in os.listdir(sub_directory_path):
                    if not image_file.startswith('.'):
                        image_file_path = sub_directory_path + '/' + image_file
                        image = io.imread(image_file_path)
                        image.resize(self.target_dimensions)
                        image = color.rgb2gray(image)
                        images.append(image)
        return np.array(images)

    def _get_time_series_image_feature_array_from_directory(self, datapath, target_image_dims, vector=True):
        feature_type_index = 0 if vector else 1
        feature = Feature()
        features = list()
        for sub_directory in os.listdir(datapath):
            if not sub_directory.startswith('.'):
                sub_directory_path = datapath + '/' + sub_directory
                feature_batch = list()
                for image_file in os.listdir(sub_directory_path):
                    if not image_file.startswith('.'):
                        image_file_path = sub_directory_path + '/' + image_file
                        feature_batch.append(feature.extract(target_image_dims, self.feature_parameters, feature_type_index=feature_type_index, image_file=image_file_path))

                features.append(feature_batch)

        return np.array(features)

    def _get_training_data_from_csv(self):
        """
        :return:  list of images from csv file, resized to specified target dimensions
        """
        print('Extracting training data from csv...')
        start = datetime.datetime.now()

        images = list()
        labels = list()
        with open(self.datapath) as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='"')

            for row in reader:
                if row[self.csv_label_col] == 'emotion': continue
                if int(row[self.csv_label_col]) not in self.target_labels:
                    continue

                label = [0]*7
                label[int(row[self.csv_label_col])] = 1.0
                labels.append(np.array(label))

                image = np.asarray([int(pixel) for pixel in row[self.csv_image_col].split(' ')], dtype=np.uint8).reshape(self.raw_dimensions)
                image = cv2.resize(image, self.target_dimensions, interpolation=cv2.INTER_LINEAR)

                if not self.rgb and self.channels==3:
                    image = np.array([image, image, image]).reshape((self.target_dimensions[0], self.target_dimensions[1], 3))

                images.append(image)

        if self.augment_data:
            data_gen = ImageDataGenerator(rotation_range=180)
            data_gen.fit(images)   # TODO: functionality: send data_gen new image set to feature extractor
                                # TODO: functionality: ImDataGen input will be dependent on experimentation results for emotion subsets

        end = datetime.datetime.now()
        print('Training data extraction runtime - ' + str(end-start))

        return np.array(images), np.array(labels)

    def _get_training_label_array(self):
        raw_training_labels = self._get_raw_training_labels()
        training_label_array = list()
        for time_series_key in raw_training_labels:
            time_series = raw_training_labels[time_series_key]
            training_label_array += time_series

        return np.array(training_label_array)

    def _get_raw_training_labels(self):
        # Uses 20 photo series from the Cohn-Kanade dataset
        # hand labeled by AP
        # arousal(least, most), valence(negative, positive), power, anticipation
        raw_training_labels = {1: [10, [.6, .4, .7, .6], [.9, .1, .8, .9]],
                               2: [9, [.2, .5, .6, .1], [.3, .4, .5, .2]],
                               3: [10, [.8, .9, .2, .9], [.99, .99, .1, .99]],
                               4: [10, [.2, .4, .4, .5], [.8, .2, .7, .6]],
                               5: [8, [.2, .4, .2, .1], [.5, .5, .5, .5]],
                               6: [10, [.8, .2, .2, .5], [.9, .1, .1, .5]],
                               7: [10, [.7, .4, .5, .6], [.8, .2, .8, .7]],
                               8: [9, [.5, .5, .4, .5], [.6, .4, .5, .3]],
                               9: [10, [.6, .4, .4, .7], [.9, .1, .1, .9]],
                               10: [10, [.1, .5, .2, .1], [.7, .2, .2, .5]],
                               11: [10, [.2, .4, .5, .2], [.3, .5, .4, .2]],
                               12: [10, [.6, .2, .2, .4], [.8, .1, .1, .4]],
                               13: [10, [.6, .4, .7, .5], [.8, .2, .8, .5]],
                               14: [9, [.1, .5, .5, .5], [.1, .4, .5, .4]],
                               15: [10, [.1, .4, .5, .5], [.8, .3, .4, .9]],
                               16: [10, [.6, .4, .7, .6], [.7, .2, .2, .5]],
                               17: [10, [.5, .4, .6, .5], [.7, .2, .7, .6]],
                               18: [10, [.7, .4, .2, .7], [.9, .1, .1, .9]],
                               19: [10, [.7, .3, .3, .5], [.8, .1, .1, .6]],
                               20: [10, [.6, .3, .2, .5], [.9, .1, .1, .6]]}
        labels = dict()
        for time_series_key in raw_training_labels:
            time_series = raw_training_labels[time_series_key]
            num_images = time_series[0]
            increment = [(time_series[2][emotion_dimension_idx] - time_series[1][emotion_dimension_idx]) / num_images for emotion_dimension_idx in range(EMOTION_DIMENSION_COUNT)]
            labels[time_series_key] = [[increment[label_idx]*image_idx + (time_series[1][label_idx]) for label_idx in range(EMOTION_DIMENSION_COUNT)] for image_idx in range(num_images)]

        return labels

    def _get_time_delay_training_data(self, datapoints, labels, time_delay=2):
        """
        Adds time delay dimension to given datapoints.

        :param datapoints: list of datapoints
        :param labels: list of labels
        :param time_delay: number of previous time steps to add to each datapoint
        :return: list of time-delayed datapoints
        """
        features = list()
        for data_point_idx in range(time_delay, len(datapoints)):
            data_point = [datapoints[data_point_idx - offset] for offset in range(time_delay + 1)]
            features.append([data_point])

        labels = labels[time_delay:len(labels)]

        return (features, labels)