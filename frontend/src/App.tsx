import { useState } from "react";
import { Header, Heading, Editor, Settings } from "./components";

function App() {
  const [showSettings, setShowSettings] = useState<boolean>(false); // Explicit type definition for useState
  const apiBaseUrl = "http://your-api-base-url"; // Replace with your actual API base URL

  const toggleSettings = () => {
    setShowSettings(!showSettings);
  };

  return (
    <>
      <Header showSettings={showSettings} onToggleSettings={toggleSettings} />
      {showSettings ? (
         <Settings apiBaseUrl={apiBaseUrl} />
      ) : (
        <>
          <Heading />
          <Editor />
        </>
      )}
    </>
  );
}

export default App;
