import threading
import time
import tensorflow as tf
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
import asyncio
import email_alert
import sms_alert
import datetime

class VehicleCrash:
    def __init__(self, detections_update_label, content, button1):
        self.detections_update_label = detections_update_label
        self.content = content
        self.source = None
        self.running = False
        self.button1 = button1
        self.count = 0
        self.model_loaded = False
        self.detect_fn = None
        self.image_ref = None  # Fix for Tkinter image update issue
        self.load_model()

    def set_source(self, source):
        self.source = source

    # Enable Mixed Precision for better performance
    tf.keras.mixed_precision.set_global_policy('mixed_float16')

    PATH_TO_SAVED_MODEL = "inference_graph/saved_model"
    category_index = label_map_util.create_category_index_from_labelmap(
        "label_map.pbtxt", use_display_name=True
    )

    def load_model(self):
        """Loads the TensorFlow detection model."""
        if not self.model_loaded:
            self.detections_update_label.configure(text="Loading model...")
            self.detect_fn = tf.saved_model.load(self.PATH_TO_SAVED_MODEL)
            self.model_loaded = True
            self.detections_update_label.configure(text="Model Loaded!")

    def perform_label_detected(self):
        """Handles crash detection alerts and triggers notifications."""
        self.detections_update_label.configure(text="🚨 Vehicle Crash Detected! Sending Alerts...")
        asyncio.run(self.send_alerts())
        self.detections_update_label.configure(text="✅ Alerts Sent Successfully!")
        time.sleep(0.5)
        self.detections_update_label.configure(text="")

    async def send_alerts(self):
        """Sends crash alerts via email and SMS."""
        await asyncio.to_thread(email_alert.Email(self.source).run_mail)
        await asyncio.to_thread(sms_alert.Sms(self.source).run_sms)

    @tf.function  # Optimize function execution
    def process_frame(self, frame):
        """Processes video frames and runs the crash detection model."""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Use OpenCV's blob function for faster pre-processing
        blob = cv2.dnn.blobFromImage(frame_rgb, size=(300, 300), swapRB=True, crop=False)
        input_tensor = tf.convert_to_tensor(blob, dtype=tf.float32)[tf.newaxis, ...]

        detections = self.detect_fn(input_tensor)
        return detections

    def visualize_and_detect(self, frame, image, bboxes, labels, scores, thresh=0.92):
        """Draws bounding boxes and handles crash detection logic."""
        (h, w, _) = image.shape

        for bbox, label, score in zip(bboxes, labels, scores):
            if score > thresh:
                xmin, ymin, xmax, ymax = int(bbox[1] * w), int(bbox[0] * h), int(bbox[3] * w), int(bbox[2] * h)
                cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                cv2.putText(
                    image, f"{label}: {int(score * 100)}%", (xmin, ymin - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2
                )

                self.count += 1
                if self.count == 20:
                    threading.Thread(target=self.perform_label_detected, daemon=True).start()  # Run in background
                    self.count = 0
                    break
        return image

    def run_detection(self):
        """Starts real-time crash detection."""
        if self.source is None:
            return
        self.running = True
        self.button1.config(text="✅ Detection ON", bg="red")

        video_capture = cv2.VideoCapture(self.source)
        canvas = tk.Canvas(self.content, width=1000, height=600)
        canvas.pack(side="top", anchor="n", padx=10, pady=40)

        while self.running:
            ret, frame = video_capture.read()
            if not ret:
                break

            detections = self.process_frame(frame)
            scores = detections['detection_scores'][0, :1].numpy()
            bboxes = detections['detection_boxes'][0, :1].numpy()
            labels = detections['detection_classes'][0, :1].numpy().astype(np.int64)

            # Ensure safe lookup in category index
            labels = [self.category_index.get(n, {'name': 'Unknown'})['name'] for n in labels]

            frame = self.visualize_and_detect(frame, frame, bboxes, labels, scores, 0.92)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame).resize((1000, 600))
            self.image_ref = ImageTk.PhotoImage(image)  # Keep reference to prevent garbage collection

            canvas.create_image(0, 0, image=self.image_ref, anchor=tk.NW)
            canvas.update()

        video_capture.release()
        self.running = False
        self.button1.config(text="🛑 Detection OFF", bg="#FFC107")
