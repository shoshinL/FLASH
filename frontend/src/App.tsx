import { useState } from "react";
import { Header, Heading, Editor, Settings } from "./components";

function App() {
  const [showSettings, setShowSettings] = useState<boolean>(false); // Explicit type definition for useState

  const toggleSettings = () => {
    setShowSettings(!showSettings);
  };

  return (
    <>
      <Header showSettings={showSettings} onToggleSettings={toggleSettings} />
      {showSettings ? (
         <Settings />
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
