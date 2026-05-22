from deployment.inference import classify_live_tap

class SoundClassifier:
    def predict(self, audio_path):
        classification_data = None
        if audio_path:
            print(f"Predicting audio for {audio_path}...")
            try:
                prediction = classify_live_tap(audio_path)
                classification_data = {"type": prediction}
            except Exception as e:
                print(f"Error classifying audio: {e}")
        return classification_data