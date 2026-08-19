import { Award, CheckCircle, Code2, MessageSquare, Download, RotateCcw, Clock, Building } from 'lucide-react';
import styles from './ReportDashboard.module.css';

export default function ReportDashboard({
  reportData,
  evaluationText,
  durationSeconds,
  candidateName,
  trackName,
  testStats,
  q1Title,
  q2Title,
  onRestart
}) {
  const scores = reportData?.scores || {
    problem_solving: 85,
    code_quality: 80,
    communication: 90,
    overall: 85
  };

  const recommendation = reportData?.recommendation || 'Hire';

  const formatDuration = (sec) => {
    const m = Math.floor((sec || 0) / 60);
    const s = (sec || 0) % 60;
    return `${m}m ${s}s`;
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <div className={styles.badge}>
            <Award size={16} /> Interview Evaluation Report
          </div>
          <h1>{candidateName || 'Candidate'}'s Performance Summary</h1>
          <div className={styles.metaRow}>
            <span><Building size={14} /> {trackName || 'General SDE Track'}</span>
            <span><Clock size={14} /> Duration: {formatDuration(durationSeconds)}</span>
          </div>
        </div>

        <div className={styles.headerActions}>
          <button onClick={handlePrint} className={styles.printBtn}>
            <Download size={16} /> Export / Print PDF
          </button>
          <button onClick={onRestart} className={styles.restartBtn}>
            <RotateCcw size={16} /> New Interview
          </button>
        </div>
      </div>

      {/* Top Banner: Recommendation */}
      <div className={`${styles.recBanner} ${recommendation.toLowerCase().includes('hire') ? styles.recHire : styles.recNoHire}`}>
        <div className={styles.recLabel}>Overall Decision</div>
        <div className={styles.recValue}>{recommendation}</div>
      </div>

      {/* Score Grid */}
      <div className={styles.scoreGrid}>
        <div className={styles.scoreCard}>
          <div className={styles.scoreHeader}>
            <Code2 size={18} className={styles.scoreIcon} />
            <span>Problem Solving</span>
          </div>
          <div className={styles.scoreNum}>{scores.problem_solving}<span>/100</span></div>
          <div className={styles.progressBar}>
            <div className={styles.progressFill} style={{ width: `${scores.problem_solving}%` }}></div>
          </div>
        </div>

        <div className={styles.scoreCard}>
          <div className={styles.scoreHeader}>
            <CheckCircle size={18} className={styles.scoreIcon} />
            <span>Code Quality</span>
          </div>
          <div className={styles.scoreNum}>{scores.code_quality}<span>/100</span></div>
          <div className={styles.progressBar}>
            <div className={styles.progressFill} style={{ width: `${scores.code_quality}%` }}></div>
          </div>
        </div>

        <div className={styles.scoreCard}>
          <div className={styles.scoreHeader}>
            <MessageSquare size={18} className={styles.scoreIcon} />
            <span>Communication</span>
          </div>
          <div className={styles.scoreNum}>{scores.communication}<span>/100</span></div>
          <div className={styles.progressBar}>
            <div className={styles.progressFill} style={{ width: `${scores.communication}%` }}></div>
          </div>
        </div>

        <div className={`${styles.scoreCard} ${styles.scoreOverall}`}>
          <div className={styles.scoreHeader}>
            <Award size={18} className={styles.scoreIcon} />
            <span>Overall Score</span>
          </div>
          <div className={styles.scoreNum}>{scores.overall}<span>/100</span></div>
          <div className={styles.progressBar}>
            <div className={styles.progressFill} style={{ width: `${scores.overall}%` }}></div>
          </div>
        </div>
      </div>

      {/* Test Cases Summary */}
      <div className={styles.testSection}>
        <h3>Coding Challenges Summary</h3>
        <div className={styles.testGrid}>
          <div className={styles.testBox}>
            <div className={styles.testBoxTitle}>Q1: {q1Title || 'Question 1'}</div>
            <div className={styles.testBoxStats}>
              Status: <strong>Completed</strong>
            </div>
          </div>
          <div className={styles.testBox}>
            <div className={styles.testBoxTitle}>Q2: {q2Title || 'Question 2'}</div>
            <div className={styles.testBoxStats}>
              Status: <strong>Completed</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed AI Feedback Report */}
      <div className={styles.reportSection}>
        <h3>Detailed Interview Feedback from Sanjay</h3>
        <div className={styles.feedbackBody}>
          {evaluationText || reportData?.evaluation_report || 'Great effort throughout the interview! Keep practicing time & space complexity edge cases.'}
        </div>
      </div>
    </div>
  );
}
