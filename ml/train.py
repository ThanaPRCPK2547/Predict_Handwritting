import os
import numpy as np
import cv2
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import tensorflow as tf
from tensorflow.keras import layers, models

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "Dataset")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "ml", "models", "thai_number_model.keras")

FOLDERS = [str(i) for i in range(10, 16)]
IMG_SIZE = 28


def load_dataset():
    images, labels = [], []
    for label, folder in enumerate(FOLDERS):
        path = os.path.join(DATA_PATH, folder)
        for fname in os.listdir(path):
            img = cv2.imread(os.path.join(path, fname), cv2.IMREAD_GRAYSCALE)
            if img is not None:
                img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
                images.append(img)
                labels.append(label)
    X = np.array(images, dtype="float32").reshape(-1, IMG_SIZE, IMG_SIZE, 1) / 255.0
    y = np.array(labels)
    return X, y


def build_model():
    model = models.Sequential([
        layers.Conv2D(32, (3, 3), activation="relu", input_shape=(IMG_SIZE, IMG_SIZE, 1)),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation="relu"),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation="relu"),
        layers.Flatten(),
        layers.Dense(128, activation="relu"),
        layers.Dropout(0.4),
        layers.Dense(len(FOLDERS), activation="softmax"),
    ])
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def main():
    print("Loading dataset...")
    X, y = load_dataset()
    print(f"Loaded {len(X)} images — classes: {np.bincount(y).tolist()}")

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    model = build_model()
    model.summary()

    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(patience=3, factor=0.5, verbose=1),
    ]

    print("\nTraining...")
    model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_data=(X_val, y_val),
        callbacks=callbacks,
        verbose=1,
    )

    loss, acc = model.evaluate(X_val, y_val, verbose=0)
    print(f"\nVal accuracy: {acc*100:.2f}%  |  Val loss: {loss:.4f}")

    y_pred = np.argmax(model.predict(X_val, verbose=0), axis=1)
    print(classification_report(y_val, y_pred, target_names=FOLDERS))

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    model.save(OUTPUT_PATH)
    print(f"\nModel saved → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
