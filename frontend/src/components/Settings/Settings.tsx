import { useState, useEffect } from "react";
import "./Settings.css";

interface SettingsProps {
  apiBaseUrl: string;
}

export function Settings({ apiBaseUrl }: SettingsProps) {
  const [ankiDataLocation, setAnkiDataLocation] = useState<string>("C:/Users/NAME/Anki2");
  const [ankiProfiles, setAnkiProfiles] = useState<string[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<string>("");
  const [ankiDecks, setAnkiDecks] = useState<string[]>([]);
  const [selectedDeck, setSelectedDeck] = useState<string>("");
  const [apiKeySet, setApiKeySet] = useState<boolean>(false);

  useEffect(() => {
    // Fetch profiles from API
    fetch(`${apiBaseUrl}/anki/profiles`)
      .then(response => response.json())
      .then(data => setAnkiProfiles(data))
      .catch(error => console.error('Error fetching profiles:', error));

    // Fetch decks from API
    fetch(`${apiBaseUrl}/anki/decks`)
      .then(response => response.json())
      .then(data => setAnkiDecks(data))
      .catch(error => console.error('Error fetching decks:', error));

    // Check if API key is set
    fetch(`${apiBaseUrl}/anki/api-key-status`)
      .then(response => response.json())
      .then(data => setApiKeySet(data.isSet))
      .catch(error => console.error('Error checking API key status:', error));
  }, [apiBaseUrl]);

  const handleSelectFilePath = () => {
    // Trigger backend API call to select a file
    fetch(`${apiBaseUrl}/anki/select-file-path`)
      .then(response => response.json())
      .then(data => setAnkiDataLocation(data.filePath))
      .catch(error => console.error('Error selecting file path:', error));
  };

  const handleResetApiKey = () => {
    // Trigger backend API call to reset API key
    fetch(`${apiBaseUrl}/anki/reset-api-key`, { method: 'POST' })
      .then(response => response.json())
      .then(data => setApiKeySet(data.isSet))
      .catch(error => console.error('Error resetting API key:', error));
  };

  return (
    <div className="settings-container">
      <div className="settings-item">
        <label>Anki Data Location: </label>
        <input 
          type="text" 
          className="file-path-input" 
          value={ankiDataLocation} 
          readOnly 
          onClick={handleSelectFilePath} 
        />
      </div>

      <div className="settings-item">
        <label>Anki Profile: </label>
        <select
          value={selectedProfile}
          onChange={(e) => setSelectedProfile(e.target.value)}
        >
          <option value="">Select Profile</option>
          {ankiProfiles.map((profile) => (
            <option key={profile} value={profile}>
              {profile}
            </option>
          ))}
        </select>
      </div>

      <div className="settings-item">
        <label>Anki Deck: </label>
        <select
          value={selectedDeck}
          onChange={(e) => setSelectedDeck(e.target.value)}
        >
          <option value="">Select Deck</option>
          {ankiDecks.map((deck) => (
            <option key={deck} value={deck}>
              {deck}
            </option>
          ))}
        </select>
      </div>

      <div className="settings-item">
        <button
          className="reset-api-key-button"
          onClick={handleResetApiKey}
          style={{ backgroundColor: apiKeySet ? 'red' : 'gray' }}
        >
          {apiKeySet ? '(Re)set API key' : 'Set API key'}
        </button>
      </div>
    </div>
  );
}
