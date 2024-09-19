import os
import cv2
import numpy as np
from skimage.feature import hog
from sklearn import svm
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler

# Function to extract features from an image
def extract_features(image_path):
    print(f"Extracting features from {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error reading image: {image_path}")
        return None

    # Resize image to a fixed size
    image = cv2.resize(image, (128, 128))

    # HOG Feature Extraction
    # Since the image is in color, specify the channel_axis for multichannel images
    hog_features = hog(image, pixels_per_cell=(16, 16), cells_per_block=(2, 2), visualize=False, channel_axis=-1)

    # SIFT Feature Extraction
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(gray_image, None)
    if descriptors is None:
        sift_features = np.zeros((128,))  # Default if no keypoints detected
    else:
        sift_features = np.mean(descriptors, axis=0)  # Average of SIFT descriptors

    # Color Histogram
    color_hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    color_hist = cv2.normalize(color_hist, color_hist).flatten()

    # Combine all features
    features = np.concatenate((hog_features, sift_features, color_hist))
    print(f"Features extracted for {image_path}")
    return features

# Load dataset from train and test directories
def load_data(data_dir):
    print("Loading data...")
    X = []
    y = []
    categories = ['animals', 'man_made', 'nature', 'people']
    label_map = {category: idx for idx, category in enumerate(categories)}

    # Load training data
    for category in categories:
        category_path_train = os.path.join(data_dir, 'train', category)
        print(f"Loading training data from category: {category}")

        for img_file in os.listdir(category_path_train):
            img_path = os.path.join(category_path_train, img_file)
            features = extract_features(img_path)
            if features is not None:
                X.append(features)
                y.append(label_map[category])

    # Load testing data
    for category in categories:
        category_path_test = os.path.join(data_dir, 'test', category)
        print(f"Loading testing data from category: {category}")

        for img_file in os.listdir(category_path_test):
            img_path = os.path.join(category_path_test, img_file)
            features = extract_features(img_path)
            if features is not None:
                X.append(features)
                y.append(label_map[category])

    print("Data loading complete.")
    return np.array(X), np.array(y)

# Main script
if __name__ == "__main__":
    print("Starting image classification using SVM...")
    
    data_dir = 'Labelled Dataset'  # Path to your dataset directory
    
    # Load the data
    X, y = load_data(data_dir)
    
    # Print data information
    print(f"Total images processed: {len(y)}")
    print(f"Number of features per image: {X.shape[1]}")

    # Standardize features
    print("Standardizing features...")
    scaler = StandardScaler()
    
    # Training on 80%, testing on 20%
    X_train = scaler.fit_transform(X[:len(y)//5 * 4])  # 80% for training
    y_train = y[:len(y)//5 * 4]
    X_test = scaler.transform(X[len(y)//5 * 4:])        # 20% for testing
    y_test = y[len(y)//5 * 4:]

    print(f"Training data size: {X_train.shape}")
    print(f"Test data size: {X_test.shape}")
    
    # Train the SVM model
    print("Training the SVM model...")
    model = svm.SVC(kernel='linear')
    model.fit(X_train, y_train)

    print("Model training complete.")

    # Predictions
    print("Making predictions on test data...")
    y_pred = model.predict(X_test)

    # Evaluation
    print("Classification report:")
    print(classification_report(y_test, y_pred, target_names=['animals', 'man_made', 'nature', 'people']))

    print("Classification process complete.")
