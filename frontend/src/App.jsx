import { useState, useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { Mic, MicOff, Video, VideoOff, Phone, Subtitles, Lock, Code, CheckCircle, Circle, ArrowRight } from 'lucide-react';
import styles from './App.module.css';

const INTERVIEW_STAGES = [
  { id: 'Intro', label: '1. Intro' },
  { id: 'Question 1', label: '2. Question 1' },
  { id: 'Question 1 Follow-up', label: '3. Q1 Follow-up' },
  { id: 'Question 2', label: '4. Question 2' },
  { id: 'Question 2 Follow-up', label: '5. Q2 Follow-up' },
  { id: 'Wrap-up', label: '6. Wrap-up' }
];

function App() {
  const [language, setLanguage] = useState('python');
  const [code, setCode] = useState('class Solution:\n    def twoSum(self, nums: list[int], target: int) -> list[int]:\n        # Write your code here\n        return []');
  const [isRecording, setIsRecording] = useState(false);
  const [isVideoOn, setIsVideoOn] = useState(true);
  const [isEditorEnabled, setIsEditorEnabled] = useState(false); // Locked by default
  const [isProcessing, setIsProcessing] = useState(false);
  const [isAiSpeaking, setIsAiSpeaking] = useState(false);
  const [subtitles, setSubtitles] = useState('');
  const [currentPhase, setCurrentPhase] = useState('Intro');
  
  const [problemHtml, setProblemHtml] = useState(null);
  const [timeLeft, setTimeLeft] = useState(3600); // 60 minutes in seconds
  const [isInterviewEnded, setIsInterviewEnded] = useState(false);
  const [evaluationReport, setEvaluationReport] = useState('');
  
  const videoRef = useRef(null);
  const recognitionRef = useRef(null);
  const sessionIdRef = useRef(Math.random().toString(36).substring(7));
  const preferredVoiceRef = useRef(null);
  const transcriptBufferRef = useRef('');
  const isRecordingRef = useRef(false);

  useEffect(() => {
    // Initial greeting from AI
    const initiateInterview = async () => {
        await handleUserAudioSubmission("", false, true);
    };
    initiateInterview();

    // Setup local camera stream
    async function setupCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error('Error accessing media devices:', err);
      }
    }
    setupCamera();

    // Setup Speech Recognition (Web Speech API)
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      
      recognition.onresult = (event) => {
        let currentInterim = '';
        let currentFinal = '';
        
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            currentFinal += event.results[i][0].transcript;
          } else {
            currentInterim += event.results[i][0].transcript;
          }
        }
        
        if (currentFinal) {
            transcriptBufferRef.current += currentFinal + ' ';
        }
        
        // Show current buffer + interim in subtitles
        setSubtitles(transcriptBufferRef.current + currentInterim);
      };
      
      recognition.onerror = (event) => {
        console.error("Speech recognition error", event.error);
        if (event.error !== 'no-speech') {
            isRecordingRef.current = false;
            setIsRecording(false);
        }
      };
      
      recognition.onend = () => {
        if (isRecordingRef.current) {
            try {
                recognition.start();
            } catch (e) {
                console.error("Failed to restart recognition:", e);
            }
        }
      };

      recognitionRef.current = recognition;
    } else {
      console.warn("Speech Recognition API not supported in this browser.");
    }
    
    // Cleanup
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      window.speechSynthesis.cancel();
    };
  }, []);

  useEffect(() => {
    if (isInterviewEnded) return;
    
    const timerId = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timerId);
          handleEndInterview();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    
    return () => clearInterval(timerId);
  }, [isInterviewEnded]);

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}m : ${s < 10 ? '0' : ''}${s}s`;
  };

  const handlePushToTalk = () => {
    // Interrupt AI speech when user starts speaking
    window.speechSynthesis.cancel();
    setIsAiSpeaking(false);

    if (!recognitionRef.current) return;
    
    if (isRecordingRef.current) {
      isRecordingRef.current = false;
      setIsRecording(false);
      recognitionRef.current.stop();
      
      const textToSubmit = transcriptBufferRef.current.trim();
      if (textToSubmit) {
          handleUserAudioSubmission(textToSubmit);
      } else if (isEditorEnabled) {
          handleUserAudioSubmission("I've made some progress on the code. Could you please check it?");
      } else {
          setSubtitles("");
      }
      transcriptBufferRef.current = '';
    } else {
      transcriptBufferRef.current = '';
      setSubtitles("Listening...");
      isRecordingRef.current = true;
      setIsRecording(true);
      try {
          recognitionRef.current.start();
      } catch (e) {
          console.error(e);
      }
    }
  };

  const handleUserAudioSubmission = async (transcription, isFinal = false, isInit = false) => {
    setIsProcessing(true);
    setSubtitles("Interviewer is thinking...");
    
    try {
      const formData = new FormData();
      formData.append('session_id', sessionIdRef.current);
      formData.append('language', language);
      formData.append('code', isEditorEnabled || isFinal ? code : '');
      formData.append('transcription', transcription);
      if (isFinal) {
          formData.append('is_final', 'true');
      }

      const response = await fetch('http://localhost:8000/api/submit', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (data.current_phase) {
          setCurrentPhase(data.current_phase);
      }

      if (isFinal || data.current_phase === 'Wrap-up') {
          if (isFinal) {
              setEvaluationReport(data.ai_response);
              setIsInterviewEnded(true);
          }
      }

      setSubtitles(data.ai_response);
      playAIResponse(data.ai_response);
      setIsEditorEnabled(data.editor_unlocked === true);
      
      if (data.problem_html) {
          setProblemHtml(data.problem_html);
      }
      if (data.starter_code) {
          setCode(data.starter_code);
      }
      
    } catch (error) {
      console.error("Error submitting to backend:", error);
      setSubtitles("Error connecting to interviewer.");
    } finally {
      setIsProcessing(false);
    }
  };

  const playAIResponse = (text) => {
    if (!text) return;
    const synth = window.speechSynthesis;
    synth.cancel();
    
    // Clean markdown characters for crystal-clear natural speech
    const cleanSpeech = text.replace(/[*_#`~[\]]/g, '').trim();
    const utterance = new SpeechSynthesisUtterance(cleanSpeech);
    
    if (!preferredVoiceRef.current) {
        const voices = synth.getVoices();
        preferredVoiceRef.current = voices.find(v => (v.lang.includes('en-US') || v.lang.includes('en-GB')) && (v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Samantha'))) || voices[0];
    }
    
    if (preferredVoiceRef.current) {
      utterance.voice = preferredVoiceRef.current;
    }
    
    utterance.rate = 1.05; // Slightly snappier, natural conversational pace
    utterance.pitch = 1.0;
    
    utterance.onstart = () => setIsAiSpeaking(true);
    utterance.onend = () => setIsAiSpeaking(false);
    utterance.onerror = () => setIsAiSpeaking(false);
    
    synth.speak(utterance);
  };

  const handleLanguageChange = (e) => {
    const selectedLang = e.target.value;
    setLanguage(selectedLang);
    
    if (selectedLang === 'cpp') {
        setCode('#include <bits/stdc++.h>\nusing namespace std;\n\n// Write your solution here\n');
    } else if (selectedLang === 'java') {
        setCode('import java.util.*;\n\nclass Solution {\n    // Write your solution here\n}');
    } else if (selectedLang === 'python') {
        setCode('class Solution:\n    # Write your solution here\n    pass');
    }
  };

  const handleEndInterview = () => {
    if (isInterviewEnded) return;
    
    setIsInterviewEnded(true);
    
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsRecording(false);
    
    // Stop camera
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
    }
    
    // Request final evaluation
    handleUserAudioSubmission("I would like to end the interview now. Please evaluate my performance.", true);
  };

  const getStageIndex = (phaseName) => {
    const index = INTERVIEW_STAGES.findIndex(s => s.id === phaseName);
    return index !== -1 ? index : 0;
  };

  const currentStageIdx = getStageIndex(currentPhase);

  return (
    <div className={styles.appContainer}>
      <header className={styles.header}>
        <div className={styles.logo}>
          NxtMock <span>by NxtWave</span>
        </div>

        {/* Phase Progress Indicator */}
        <div className={styles.stageTracker}>
          {INTERVIEW_STAGES.map((stage, idx) => {
            const isCompleted = idx < currentStageIdx;
            const isCurrent = idx === currentStageIdx;
            return (
              <div 
                key={stage.id} 
                className={`${styles.stageBadge} ${isCurrent ? styles.stageActive : ''} ${isCompleted ? styles.stageCompleted : ''}`}
              >
                {isCompleted ? <CheckCircle size={14} /> : <Circle size={14} />}
                <span>{stage.label}</span>
              </div>
            );
          })}
        </div>

        <div className={styles.headerInfo}>
          <div className={styles.timer}>
            <span>⏱</span> {formatTime(timeLeft)}
          </div>
          {isRecording && (
            <div className={styles.recordingStatus}>
              <div className={styles.recDot}></div> REC
            </div>
          )}
          <div className={styles.networkStatus}>📶 4.1 mb/s</div>
        </div>
      </header>

      <main className={styles.mainContent}>
        {isInterviewEnded ? (
            <section className={styles.evaluationPanel}>
               <h2>Final Interview Evaluation</h2>
               {isProcessing ? (
                   <div className={styles.evalLoading}>
                      <div className={styles.spinner}></div>
                      <p>Sanjay is compiling your comprehensive evaluation report...</p>
                   </div>
               ) : (
                   <div className={styles.reportContent}>
                       {evaluationReport}
                   </div>
               )}
            </section>
        ) : (
            <>
        <section className={styles.problemPanel}>
          {problemHtml ? (
              <div dangerouslySetInnerHTML={{ __html: problemHtml }} />
          ) : (
              <div className={styles.introEmptyState}>
                 <h2>Welcome to Your Mock Interview</h2>
                 <p>Introduce yourself to Sanjay. The problem statement will appear here as soon as you proceed to Question 1.</p>
              </div>
          )}
        </section>

        <section className={styles.editorPanel}>
          <div className={styles.editorHeader}>
            <select 
              className={styles.languageSelect}
              value={language}
              onChange={handleLanguageChange}
            >
              <option value="python">Python 3</option>
              <option value="cpp">C++14 (gcc)</option>
              <option value="java">Java 17</option>
            </select>

            <div className={styles.editorPhaseTag}>
              Phase: <strong>{currentPhase}</strong>
            </div>
          </div>
          
          <div className={styles.editorContainer}>
            <Editor
              height="100%"
              language={language}
              theme="vs-dark"
              value={code}
              onChange={(value) => setCode(value || '')}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                readOnly: !isEditorEnabled
              }}
            />
            
            {!isEditorEnabled && (
              <div className={styles.editorOverlay}>
                <Lock size={32} style={{ marginBottom: '1rem' }} />
                <p>The editor unlocks during Question 1 & Question 2.<br/>Please follow the interviewer's guidance.</p>
              </div>
            )}
          </div>
          
          {/* Subtitles Overlay beneath editor */}
          {subtitles && (
             <div className={styles.subtitlesBox}>
                 {subtitles}
             </div>
          )}
        </section>

        <section className={styles.videoPanel}>
          <div className={`${styles.videoBox} ${isAiSpeaking ? styles.aiSpeakingBox : ''}`}>
            <div className={`${styles.aiAvatar} ${isAiSpeaking ? styles.aiAvatarSpeaking : ''}`}>
               <span>AI</span>
            </div>
            <div className={styles.videoLabel}>
              Sanjay {isAiSpeaking ? '🔊 Speaking...' : isProcessing ? '⏳ Thinking...' : ''}
            </div>
          </div>

          <div className={styles.videoBox}>
            <video 
              ref={videoRef}
              autoPlay 
              playsInline 
              muted 
              className={styles.videoElement}
              style={{ display: isVideoOn ? 'block' : 'none' }}
            />
            {!isVideoOn && <div className={styles.cameraOffPlaceholder}>Camera Off</div>}
            <div className={styles.videoLabel}>You {isRecording ? '🎙 Speaking' : ''}</div>
          </div>
        </section>
        </>
        )}
      </main>

      {!isInterviewEnded && (
      <div className={styles.controlBar}>
        <button 
          className={styles.controlBtn} 
          onClick={() => setIsVideoOn(!isVideoOn)}
          title={isVideoOn ? "Turn off camera" : "Turn on camera"}
        >
          {isVideoOn ? <Video size={20} /> : <VideoOff size={20} />}
        </button>
        <button 
          className={styles.controlBtn} 
          onClick={() => {
              if (isEditorEnabled && !isProcessing) {
                  handleUserAudioSubmission("Could you please review my current code and provide feedback or hints?");
              }
          }}
          disabled={!isEditorEnabled || isProcessing}
          title="Ask Interviewer to Review Code"
        >
          <Code size={20} />
        </button>
        <button 
          className={`${styles.controlBtn} ${styles.primary} ${isRecording ? styles.recording : ''}`}
          onClick={handlePushToTalk}
          disabled={isProcessing}
          title={isRecording ? "Tap to submit answer" : "Tap to Speak"}
        >
          {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
        </button>
        <button className={`${styles.controlBtn} ${styles.danger}`} title="End interview" onClick={handleEndInterview}>
          <Phone size={20} style={{ transform: 'rotate(135deg)' }} />
        </button>
      </div>
      )}
    </div>
  );
}

export default App;
