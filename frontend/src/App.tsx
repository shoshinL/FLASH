import { useState, useEffect } from "react";
import { Header, Heading, Editor, Settings, LoadingView, ResultsView } from "./components";

interface LoadingStatus {
  progress: number;
  message: string;
}

interface Flashcard {
  Type: string;
  Front?: string;
  Back?: string;
  Text?: string;
  BackExtra?: string;
}

interface Results {
  flashcards: Flashcard[];
  filename: string;
}

function App() {
  const [showSettings, setShowSettings] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [loadingStatus, setLoadingStatus] = useState<LoadingStatus>({ progress: 0, message: "" });
  const [results, setResults] = useState<Results | null>(null);

  // New state for Editor
  const [content, setContent] = useState<string>("");
  const [file, setFile] = useState<string | null>(null);
  const [filePath, setFilePath] = useState<string | null>(null);
  const [cardAmount, setCardAmount] = useState<number>(5);

  useEffect(() => {
    const handleBackendUpdate = (event: CustomEvent) => {
      const { progress, message, result } = event.detail;
      if (result) {
        console.log('Received result from backend:', result);
        finishLoading(result);
      } else {
        updateLoadingStatus(progress, message);
      }
    };

    window.addEventListener('backendUpdate', handleBackendUpdate as EventListener);

    return () => {
      window.removeEventListener('backendUpdate', handleBackendUpdate as EventListener);
    };
  }, []);

  const toggleSettings = () => {
    if (!isLoading && !results) {
      setShowSettings(!showSettings);
    }
  };

  const startLoading = () => {
    setIsLoading(true);
    setLoadingStatus({ progress: 0, message: "Initializing..." });
  };

  const updateLoadingStatus = (progress: number, message: string) => {
    setLoadingStatus({ progress, message });
  };

  const finishLoading = (result: Results) => {
    console.log('Finishing loading with result:', result);
    setIsLoading(false);
    setResults(result);
    // Reset Editor state after generation
    setContent("");
    setFile(null);
    setFilePath(null);
    setCardAmount(5);
  };

  const resetResults = () => {
    console.log('Resetting results');
    setResults(null);
  };

  const isEditorView = !isLoading && !results;

  console.log('App render - isLoading:', isLoading, 'results:', results);

  return (
    <>
      <Header 
        showSettings={showSettings} 
        onToggleSettings={toggleSettings}
        isSettingsEnabled={isEditorView}
      />
      {showSettings ? (
        <Settings />
      ) : isLoading ? (
        <LoadingView status={loadingStatus} />
      ) : results ? (
        <ResultsView results={results.flashcards} filename={results.filename} onReset={resetResults} />
      ) : (
        <>
          <Heading />
          <Editor 
            content={content}
            setContent={setContent}
            file={file}
            setFile={setFile}
            filePath={filePath}
            setFilePath={setFilePath}
            cardAmount={cardAmount}
            setCardAmount={setCardAmount}
            onGenerateStart={startLoading}
          />
        </>
      )}
    </>
  );
}

export default App;