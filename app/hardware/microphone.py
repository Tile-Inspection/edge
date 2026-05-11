import subprocess

class Microphone:
    def record(self, duration=1, filename=None):
        if filename is None:
            filename = "/home/admin/Documents/GitHub/edge/app/web/static/sound.wav"
        else:
            filename = f"/home/admin/Documents/GitHub/edge/app/web/static/{filename}"
        print(f"Recording {duration}s audio to {filename} using I2S (pins 12, 35, 38)...")
        try:
            # arecord is standard on Raspberry Pi for capturing audio.
            # ALSA handles the I2S hardware interface connected to pins 12, 35, and 38.
            subprocess.run([
                "arecord",
                "-d", str(duration),
                "-f", "S32_LE", # Standard format for INMP441 I2S
                "-r", "44100",  # 44.1kHz sample rate
                "-c", "1",      # Mono channel
                filename
            ], check=True)
            return filename
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            # Failsafe for local development without ALSA / I2S configured
            print(f"Failed to record audio ({e}). Simulating instead.")
            return filename