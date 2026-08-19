import { useState, useEffect } from 'react';
import { Briefcase, Building, Code, Sparkles, Check, FileText } from 'lucide-react';
import styles from './SetupModal.module.css';

const TRACKS = [
  {
    id: 'google',
    name: 'Google SDE (L4/L5)',
    description: 'Algorithmic efficiency, graph traversals, interval scheduling & prefix sums.',
    tag: 'Algorithms & Scale',
    color: '#4285F4'
  },
  {
    id: 'meta',
    name: 'Meta Fast-Paced DSA',
    description: 'High-speed problem solving, sliding window, two-pointers & clean code.',
    tag: 'Speed & Pointers',
    color: '#0668E1'
  },
  {
    id: 'amazon',
    name: 'Amazon SDE + LP',
    description: 'Data structures, heaps, greedy algorithms & operational trade-offs.',
    tag: 'DSA + Leadership',
    color: '#FF9900'
  },
  {
    id: 'general',
    name: 'General SDE Track',
    description: 'Comprehensive tier-1 mock interview covering core computer science algorithms.',
    tag: 'Standard DSA',
    color: '#10B981'
  }
];

export default function SetupModal({ onStart, isOpen }) {
  const [candidateName, setCandidateName] = useState('Prathmesh');
  const [selectedTrack, setSelectedTrack] = useState('google');
  const [resumeBio, setResumeBio] = useState('3rd year CS student with experience in Python, FastAPI, and data structures.');
  const [preferredLang, setPreferredLang] = useState('python');

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    onStart({
      candidateName: candidateName.trim() || 'Candidate',
      track: selectedTrack,
      resumeBio: resumeBio.trim(),
      language: preferredLang
    });
  };

  return (
    <div className={styles.modalOverlay}>
      <div className={styles.modalCard}>
        <div className={styles.header}>
          <div className={styles.badge}>
            <Sparkles size={16} /> AI Mock Interview Setup
          </div>
          <h2>Configure Your Interview Session</h2>
          <p>Choose your target company track and background to personalize Sanjay's evaluation.</p>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.inputGroup}>
            <label>Candidate Name</label>
            <input 
              type="text" 
              value={candidateName} 
              onChange={(e) => setCandidateName(e.target.value)}
              placeholder="e.g. Alex Chen"
              required 
            />
          </div>

          <div className={styles.inputGroup}>
            <label>Preferred Language</label>
            <div className={styles.langSelector}>
              {['python', 'cpp', 'java'].map((lang) => (
                <button
                  type="button"
                  key={lang}
                  className={`${styles.langBtn} ${preferredLang === lang ? styles.langActive : ''}`}
                  onClick={() => setPreferredLang(lang)}
                >
                  {lang === 'python' ? 'Python 3' : lang === 'cpp' ? 'C++17' : 'Java 17'}
                </button>
              ))}
            </div>
          </div>

          <div className={styles.inputGroup}>
            <label>Select Company Track</label>
            <div className={styles.trackGrid}>
              {TRACKS.map((t) => {
                const isSelected = selectedTrack === t.id;
                return (
                  <div
                    key={t.id}
                    className={`${styles.trackCard} ${isSelected ? styles.trackSelected : ''}`}
                    onClick={() => setSelectedTrack(t.id)}
                  >
                    <div className={styles.trackHeader}>
                      <span className={styles.trackTag} style={{ borderColor: t.color, color: t.color }}>
                        {t.tag}
                      </span>
                      {isSelected && <Check size={18} className={styles.checkIcon} />}
                    </div>
                    <h4>{t.name}</h4>
                    <p>{t.description}</p>
                  </div>
                );
              })}
            </div>
          </div>

          <div className={styles.inputGroup}>
            <label>
              <FileText size={15} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '4px' }} />
              Resume Summary / Tech Stack (Optional)
            </label>
            <textarea
              rows={2}
              value={resumeBio}
              onChange={(e) => setResumeBio(e.target.value)}
              placeholder="e.g., Fullstack developer with React & Node.js, built high-scale payment microservices."
            />
          </div>

          <button type="submit" className={styles.startBtn}>
            Start Live Mock Interview &rarr;
          </button>
        </form>
      </div>
    </div>
  );
}
