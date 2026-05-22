from crack_detection.process_image_frame import predict

class CrackDetector:
    def predict(self, image_path):
        classification_data = None
        if image_path:
            print(f"Predicting cracks for {image_path}...")
            try:
                classification_data = predict(image_path)
            except Exception as e:
                print(f"Error classifying cracks: {e}")
                
        return classification_data