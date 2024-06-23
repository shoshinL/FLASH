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
      <div className="loading-content">
        <h2>Generating Flashcards</h2>
        <div className="progress-bar">
          <div className="progress" style={{ width: `${status.progress}%` }}></div>
        </div>
        <p className="status-message">{status.message}</p>
      </div>
    </div>
  );
}