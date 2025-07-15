import React, { useState } from 'react'
import { AudioRecorder, useAudioRecorder } from 'react-audio-voice-recorder';
import './Recorder.css'

function Recorder() {
	const recorderControls = useAudioRecorder();
	// const [isRecording, setIsRecording] = useState(false);
	const [result, setResult] = useState(null);

	const addAudioElement = async(blob) => {
    const url = URL.createObjectURL(blob);
    const audio = document.createElement("audio");
    audio.src = url;
    audio.controls = true;
    document.body.appendChild(audio);
  };

  const analyzeAudio = async (blob) => {
    const formData = new FormData()
    const file = new File([blob], 'recording.wav', {
      type: 'audio/wav',
    });
    formData.append('audio', file);

    try{
      const data = await fetch('http://127.0.0.1:5000/audioAnalyze', {
        method: 'POST',
        body: formData,
      })

      const res = await data.json()
      setResult(res)
    } catch(err){
      console.log('error while analyzing audio')
      return err;
    }
  }

 	const handleStart = () =>{
    setResult(null)
		recorderControls.startRecording()
	}

	const handleStop = () =>{
		recorderControls.stopRecording()
	}
	
  return (
    <div className='recorder'>
      <AudioRecorder 
        onRecordingComplete={async (blob) => {
          await addAudioElement(blob)
          await analyzeAudio(blob)
        }}
        // downloadOnSavePress={true}
        recorderControls={recorderControls}
      />
      <div className='buttons'>
        <button type='button' onClick={() => handleStart()}>Start Recording</button>
        <button type='button' onClick={() => handleStop()}>Stop Recording</button>
      </div>

      {result && <div>
          <h2>Analysis Results</h2>
          <p>Score : {result.score}</p>
          {result.anomaly ? <p> Anomaly Detected</p> : <p> All clear, No anomalies</p>}
        </div>}
    </div>
  )
}

export default Recorder
