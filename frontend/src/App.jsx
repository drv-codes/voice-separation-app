import React, { useState, useRef, useEffect } from 'react';
import { Upload, Play, Pause, Download, Music, X, Mic, Layers, Wand2, Sparkles } from 'lucide-react';
import './App.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;


const App = () => {
  // Application State
  const [mode, setMode] = useState('speech');
  const [file, setFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  // Audio Player State
  const [playingTrack, setPlayingTrack] = useState(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  
  const audioRef = useRef(new Audio());
  const [isDragOver, setIsDragOver] = useState(false);

  // Audio Event Listeners
  useEffect(() => {
    const audio = audioRef.current;
    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => setDuration(audio.duration);
    const onEnded = () => { setPlayingTrack(null); setCurrentTime(0); };

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('loadedmetadata', updateDuration);
    audio.addEventListener('ended', onEnded);

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('loadedmetadata', updateDuration);
      audio.removeEventListener('ended', onEnded);
    };
  }, []);

  // Stop audio on mode change or new result
  useEffect(() => { stopAudio(); }, [results, mode]);

  const stopAudio = () => {
    const audio = audioRef.current;
    audio.pause();
    audio.currentTime = 0;
    setPlayingTrack(null);
    setCurrentTime(0);
  };

  const togglePlay = (track) => {
    const audio = audioRef.current;
    if (playingTrack === track.speaker_id) {
      audio.pause();
      setPlayingTrack(null);
    } else {
      audio.src = `${API_BASE_URL}/download?file=${encodeURIComponent(track.audio)}`;
      audio.play().catch(e => console.error("Audio playback error:", e));
      setPlayingTrack(track.speaker_id);
    }
  };

  const handleSeek = (e) => {
    const time = parseFloat(e.target.value);
    audioRef.current.currentTime = time;
    setCurrentTime(time);
  };

  const formatTime = (t) => {
    if (isNaN(t)) return "0:00";
    const m = Math.floor(t / 60);
    const s = Math.floor(t % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  const switchMode = (newMode) => {
    setMode(newMode);
    setFile(null);
    setResults(null);
    setError(null);
    setProgress(0);
  };

  const startProcessing = async (selectedFile) => {
    setIsProcessing(true);
    setProgress(0);
    setError(null);
    stopAudio();

    // Simulated progress bar for UX feedback
    const interval = setInterval(() => {
      setProgress(p => (p >= 90 ? 90 : p + 5));
    }, mode === 'music' ? 400 : 250);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      let endpoint = '/process-audio';
      if (mode === 'music') endpoint = '/separate-music';
      if (mode === 'clean') endpoint = '/enhance-audio';

      const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error(`Server Error: ${res.statusText}`);
      const data = await res.json();
      
      clearInterval(interval);
      setProgress(100);
      
      // Short delay to allow progress bar to fill
      setTimeout(() => {
        setResults(data);
        setIsProcessing(false);
      }, 500);
    } catch (err) {
      clearInterval(interval);
      setIsProcessing(false);
      setError(err.message);
    }
  };

  const handleDownloadAll = () => {
    if (results?.job_id) {
      window.location.href = `${API_BASE_URL}/jobs/${results.job_id}/download-all?mode=${mode}`;
    }
  };

  return (
    <div className="app-container">
      {/* NAVIGATION */}
      <nav>
        <div className="max-w-container nav-content">
          <div className="brand-section">
            <Sparkles className="brand-icon" size={32} />
            <span className="brand-text">A.R.Y.A Ai</span>
          </div>
          <div className="status-badge">
             {mode === 'music' ? 'Music Mode' : mode === 'clean' ? 'Cleaner Mode' : 'Voice Mode'}
          </div>
        </div>
      </nav>

      <main className="max-w-container">
        
        {/* HERO HEADER */}
        <div className="hero-section">
          <h1 className="hero-title">
            {mode === 'music' ? 'Separate Music' : mode === 'clean' ? 'Enhance Audio' : 'Isolate Voices'} 
            <span className="text-highlight">
              {mode === 'clean' ? ' Instantly' : ' with Precision'}
            </span>
          </h1>
          <p className="hero-subtitle">
            {mode === 'music' 
              ? "Extract Vocals, Drums, Bass, and Other instruments using our advanced engine."
              : mode === 'clean'
              ? "Remove background noise and clarify speech instantly."
              : "Identify speakers and download isolated conversation tracks."}
          </p>
        </div>

        {error && <div className="error-msg">⚠️ {error}</div>}

        {/* MAIN GLASS INTERFACE */}
        <div className="glass-panel">
          
          {!file ? (
            /* --- UPLOAD STATE --- */
            <div 
              className="upload-area"
              onClick={() => document.getElementById('file-input').click()}
              onDragOver={e => { e.preventDefault(); setIsDragOver(true); }}
              onDragLeave={() => setIsDragOver(false)}
              onDrop={e => {
                e.preventDefault(); setIsDragOver(false);
                if (e.dataTransfer.files[0]) {
                  setFile(e.dataTransfer.files[0]);
                  startProcessing(e.dataTransfer.files[0]);
                }
              }}
              style={{
                  borderColor: isDragOver ? '#B088F9' : undefined,
                  transform: isDragOver ? 'scale(1.01)' : undefined
              }}
            >
              <div className="upload-content">
                <input id="file-input" type="file" hidden accept="audio/*" onChange={e => {
                  if (e.target.files[0]) {
                     setFile(e.target.files[0]);
                     startProcessing(e.target.files[0]);
                  }
                }}/>
                <div className="upload-icon-wrapper">
                  {mode === 'music' ? <Music size={40} color="#B088F9"/> : 
                   mode === 'clean' ? <Wand2 size={40} color="#B088F9"/> :
                   <Upload size={40} color="#B088F9"/>}
                </div>
                <h3 style={{fontSize:'1.8rem', marginBottom:'12px', color:'#fff', fontWeight: 700}}>
                  Drag & drop audio file here
                </h3>
                <p style={{color:'#E6E6FA', opacity: 0.8}}>
                  Supported formats: MP3, WAV, FLAC
                </p>
              </div>
            </div>
          ) : !results ? (
            /* --- PROCESSING STATE --- */
            <div className="processing-state">
               <div className="loader-video-wrapper">
                   {/* Hosted Video: ARYA AI Loader */}
                   <video
                     src="https://2rjltiresrygcfqg.public.blob.vercel-storage.com/arya_img.mp4"
                     poster="/arya_poster.jpg"
                     className="loader-video"
                     autoPlay loop muted playsInline preload="auto"
                   />
                   {/* --- THE SCANNER LINE (RESTORED) --- */}
                   <div className="scan-line"></div>
               </div>
               
               <h3 className="status-text">Processing Audio...</h3>
               <p style={{color:'#D8BFD8', marginTop: '8px'}}>{file.name}</p>
               
               <div className="progress-track">
                 <div className="progress-bar" style={{width: `${progress}%`}}></div>
               </div>
            </div>
          ) : (
            /* --- RESULTS STATE --- */
            <div>
              <div className="results-header-video">
                {/* Hosted Video: ARYA AI Eyes Loop */}
                <video
                  src="https://2rjltiresrygcfqg.public.blob.vercel-storage.com/arya_eyes_loop.mp4" 
                  poster="/arya_poster.jpg"
                  className="loader-video"
                  autoPlay loop muted playsInline preload="auto"
                />
                 {/* Optional: Add scan line here too if desired, just copy the div above */}
                 <div className="scan-line"></div>
              </div>

              <div className="results-top-bar">
                <h3 style={{fontSize: '1.5rem', fontWeight: 700}}>
                    {mode === 'clean' ? 'Enhancement Complete' : 'Separation Complete'}
                </h3>
                <button onClick={() => { setFile(null); setResults(null); }} className="control-btn">
                    <X size={24} />
                </button>
              </div>

              <div className="tracks-list">
                {results.speakers.map((track) => (
                  <div key={track.speaker_id} className={`track-card ${playingTrack === track.speaker_id ? 'is-active' : ''}`}>
                    <button 
                      className={`control-btn ${playingTrack === track.speaker_id ? 'playing' : ''}`} 
                      onClick={() => togglePlay(track)}
                    >
                      {playingTrack === track.speaker_id ? <Pause size={24}/> : <Play size={24}/>}
                    </button>
                    
                    <div className="track-details">
                      <div className="track-name">
                         {track.speaker_id}
                         {track.type === 'stem' && <span className="badge">STEM</span>}
                         {track.type === 'enhanced' && <span className="badge">CLEAN</span>}
                      </div>
                      
                      {playingTrack === track.speaker_id ? (
                        <div>
                          <input type="range" min="0" max={duration} value={currentTime} onChange={handleSeek} className="seek-bar" style={{'--progress': `${(currentTime/duration)*100}%`}} />
                          <div style={{fontSize:'0.8rem', marginTop:'8px', color:'#B088F9', fontWeight:'700'}}>
                            {formatTime(currentTime)} / {formatTime(duration)}
                          </div>
                        </div>
                      ) : (
                        <div style={{fontSize:'0.9rem', color:'rgba(255,255,255,0.5)', marginTop:'4px'}}>
                            Ready to play
                        </div>
                      )}
                    </div>
                    <a href={`${API_BASE_URL}/download?file=${encodeURIComponent(track.audio)}`} download className="control-btn" style={{border: 'none'}}>
                        <Download size={24}/>
                    </a>
                  </div>
                ))}
              </div>

              <button className="btn-primary-action" onClick={handleDownloadAll}>
                  DOWNLOAD ALL TRACKS (ZIP)
              </button>
            </div>
          )}
        </div>

        {/* MODE SWITCHER */}
        <div className="features-grid">
          <div className={`feature-card ${mode === 'speech' ? 'is-active' : ''}`} onClick={() => switchMode('speech')}>
            <Mic size={36} className="feature-icon" />
            <h3>Voice Isolation</h3>
            <p>Advanced speaker diarization to separate distinct voices.</p>
          </div>
          <div className={`feature-card ${mode === 'music' ? 'is-active' : ''}`} onClick={() => switchMode('music')}>
            <Layers size={36} className="feature-icon" />
            <h3>Stem Export</h3>
            <p>Separate vocals, drums, bass, and other instruments.</p>
          </div>
          <div className={`feature-card ${mode === 'clean' ? 'is-active' : ''}`} onClick={() => switchMode('clean')}>
            <Wand2 size={36} className="feature-icon" />
            <h3>Audio Cleaner</h3>
            <p>Professional grade noise reduction and normalization.</p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;
