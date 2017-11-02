from skimage import color, io
from skimage.feature import hog


class Feature:

    def extract_hog_feature_vector(self, imageFile, image_resize_length=64):
        image = io.imread(imageFile)
        image.resize((image_resize_length,image_resize_length))
        image = color.rgb2gray(image)
        featureVector, hog_image = hog(image, orientations=8, pixels_per_cell=(16, 16), cells_per_block=(1, 1), visualise=True)
        return featureVector, hog_image