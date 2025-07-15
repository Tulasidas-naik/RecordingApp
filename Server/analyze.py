from flask import Flask, request, jsonify
from flask_cors import CORS
# import librosa
import numpy as np
import soundfile as sf
from pydub import AudioSegment
from io import BytesIO

app = Flask(__name__)
CORS(app)

@app.route('/audioAnalyze', methods= ['POST'])
def analyze():
    print(request.files, "...................")
    if 'audio' not in request.files:
        return jsonify({'error': 'no audio file'}), 400

    audio_file = request.files['audio']

    if audio_file.filename == '':
        print("No selected file.")
        return jsonify({"error": "No selected file"}), 400
    
    # It's good practice to ensure the file type, though Flask-CORS helps here
    # and the frontend sets the mimetype.
    if not audio_file.filename.lower().endswith('.wav') and \
       audio_file.mimetype != 'audio/wav':
        print(f"Unsupported file type: {audio_file.filename}, Mime: {audio_file.mimetype}")
        return jsonify({"error": "Unsupported file type. Please upload a WAV audio file."}), 415 # 415 Unsupported Media Type


    try:
        # Read the incoming blob
        audio_segment = AudioSegment.from_file(BytesIO(audio_file.read()))

        # Export to a standard PCM WAV format (e.g., 16-bit, 44.1kHz, mono)
        # Create an in-memory buffer for the converted audio
        pcm_wav_buffer = BytesIO()
        audio_segment.export(pcm_wav_buffer, format="wav", 
                            parameters=["-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1"])
        pcm_wav_buffer.seek(0) # Rewind the buffer to the beginning

        # Now use your analysis library with the converted audio
        audio_data, samplerate = sf.read(pcm_wav_buffer) 

        if audio_data.ndim > 1: # If stereo, take the mean across channels
            average_amplitude = np.mean(np.abs(audio_data))
        else: # If mono
            average_amplitude = np.mean(np.abs(audio_data))
        
        # Scale average amplitude to a 0-1 range for a "score"
        # This is a very simplistic example. Adjust logic as needed.
        score = min(1.0, average_amplitude * 10.0) # Adjust multiplier based on expected amplitude range

        # Example: Determine anomaly based on score threshold
        anomaly = False
        if score < 0.3 or score > 0.95: # Very low or very high amplitude could be an "anomaly"
            anomaly = True

        # ----------------------------------------------------

        # 6. Return the analysis results as JSON
        return jsonify({
            "score": float(f"{score:.2f}"), # Format to 2 decimal places
            "anomaly": anomaly,
            "message": "Audio analyzed successfully!"
        }), 200 

    except Exception as e:
        print(f"Error during audio conversion/processing: {e}")
        return jsonify({"error": f"Failed to process audio. Details: {str(e)}"}), 500
    
if __name__ == '__main__':
    app.run(debug=True)


        
    