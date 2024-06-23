import './LoadingView.css';

interface LoadingStatus {
  progress: number;
  message: string;
}

interface LoadingViewProps {
  status: LoadingStatus;
}

export function LoadingView({ status }: LoadingViewProps) {
  return (
    <div className="loading-container">
      <h2>Generating Flashcards</h2>
      <div className="progress-bar">
        <div 
          className="progress-bar-fill"
          style={{ width: `${status.progress}%` }}
        >
          <div className="stripes"></div>
        </div>
      </div>
      <p className="status-message">{status.message}</p>
    </div>
  );
}