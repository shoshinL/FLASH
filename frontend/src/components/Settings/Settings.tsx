import { useState, useEffect } from "react";
import "./Settings.css";

interface Settings {
  anki_db_path: string;
  profile: string;
  deck_name: string;
  api_key_set: boolean;
  anki_data_location_valid: boolean;
}

interface ProfilesResponse {
  profiles: string[];
}

interface DecksResponse {
  decks: Record<string, number>;
}

interface AnkiPathResponse {
  anki_db_path: string;
  profile: string;
  deck_name: string;
  profiles: string[];
  decks: Record<string, number>;
}

function isSettings(obj: any): obj is Settings {
  return (
    typeof obj === "object" &&
    typeof obj.anki_db_path === "string" &&
    typeof obj.profile === "string" &&
    typeof obj.deck_name === "string" &&
    typeof obj.api_key_set === "boolean"
  );
}

function isProfilesResponse(obj: any): obj is ProfilesResponse {
  return typeof obj === "object" && Array.isArray(obj.profiles);
}

function isDecksResponse(obj: any): obj is DecksResponse {
  return typeof obj === "object" && typeof obj.decks === "object";
}

function isAnkiPathResponse(obj: any): obj is AnkiPathResponse {
  return (
    typeof obj === "object" &&
    typeof obj.anki_db_path === "string" &&
    typeof obj.profile === "string" &&
    typeof obj.deck_name === "string" &&
    Array.isArray(obj.profiles) &&
    typeof obj.decks === "object"
  );
}


export function Settings() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [profiles, setProfiles] = useState<string[]>([]);
  const [decks, setDecks] = useState<Record<string, number>>({});
  const [error, setError] = useState<string | null>(null);
  const [apiKey, setApiKey] = useState<string>("");

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response: unknown = await window.pywebview.api.get_settings();
      if (isSettings(response)) {
        setSettings(response);
        if (response.anki_db_path) {
          await fetchProfiles(response.anki_db_path);
          if (response.profile) {
            await fetchDecks(response.profile);
          }
        }
      } else {
        throw new Error("Invalid settings response");
      }
    } catch (error) {
      console.error('Error fetching settings:', error);
      setError('Failed to load settings. Please try again.');
    }
  };

  const fetchProfiles = async (dbPath: string) => {
    try {
      const response: unknown = await window.pywebview.api.get_profiles(dbPath);
      if (isProfilesResponse(response)) {
        setProfiles(response.profiles);
      } else {
        throw new Error("Invalid profiles response");
      }
    } catch (error) {
      console.error('Error fetching profiles:', error);
      setProfiles([]);
      setError('Failed to load Anki profiles. Please check your Anki database path.');
    }
  };

  const fetchDecks = async (profile: string) => {
    try {
      const response: unknown = await window.pywebview.api.get_decks(profile);
      if (isDecksResponse(response)) {
        setDecks(response.decks);
      } else {
        throw new Error("Invalid decks response");
      }
    } catch (error) {
      console.error('Error fetching decks:', error);
      setDecks({});
      setError('Failed to load Anki decks. Please check your selected profile.');
    }
  };

  const handleProfileChange = async (profile: string) => {
    if (profile === settings?.profile) return;
    try {
      const response: unknown = await window.pywebview.api.set_profile(profile);
      if (isAnkiPathResponse(response)) {
        setSettings(prevSettings => ({ 
          ...prevSettings!, 
          profile: response.profile,
          deck_name: response.deck_name
        }));
        setDecks(response.decks);
        setError(null);
      } else {
        throw new Error("Invalid profile change response");
      }
    } catch (error) {
      console.error('Error setting profile:', error);
      setError('Failed to set Anki profile. Please try again.');
    }
  };

  const handleDeckChange = async (deckName: string) => {
    if (deckName === settings?.deck_name) return;
    try {
      const response: unknown = await window.pywebview.api.set_deck(deckName);
      if (typeof response === "object" && response !== null && 'success' in response && response.success) {
        setSettings(prevSettings => ({ ...prevSettings!, deck_name: deckName }));
        setError(null);
      } else {
        setError('Failed to set Anki deck. Please try again.');
      }
    } catch (error) {
      console.error('Error setting deck:', error);
      setError('Failed to set Anki deck. Please try again.');
    }
  };

  const handleSelectAnkiPath = async () => {
    try {
      const response: unknown = await window.pywebview.api.select_file_path();
      if (isAnkiPathResponse(response)) {
        setSettings(prevSettings => ({ 
          ...prevSettings!,
          anki_db_path: response.anki_db_path,
          profile: response.profile,
          deck_name: response.deck_name,
          anki_data_location_valid: true
        }));
        setProfiles(response.profiles);
        setDecks(response.decks);
        setError(null);
      } else if (typeof response === "object" && response !== null && 'error' in response) {
        setError(response.error as string);
      } else {
        throw new Error("Invalid Anki path response");
      }
    } catch (error) {
      console.error('Error selecting Anki path:', error);
      setError('Failed to set Anki database path. Please try again.');
    }
  };

  const handleSetApiKey = async () => {
    try {
      const response: unknown = await window.pywebview.api.set_api_key(apiKey);
      if (typeof response === "object" && response !== null && 'success' in response) {
        if (response.success) {
          setSettings(prevSettings => ({ ...prevSettings!, api_key_set: true }));
          setError(null);
          setApiKey("");
        } else {
          setError('Invalid API key. Please make sure it is a valid OpenAI API key.');
        }
      } else {
        throw new Error("Invalid API key set response");
      }
    } catch (error) {
      console.error('Error setting API key:', error);
      setError('Failed to set API key. Please try again.');
    }
  };

  if (!settings) {
    return <div>Loading settings...</div>;
  }

  return (
    <div className="settings-container">
      {error && <div className="error-message">{error}</div>}
      <div className="settings-item">
        <label>Anki Database File: </label>
        <input 
          type="text" 
          className="file-path-input" 
          value={settings.anki_db_path} 
          readOnly 
          onClick={handleSelectAnkiPath} 
        />
      </div>
      <div className="settings-item">
        <label>Anki Profile: </label>
        <select
          value={settings.profile}
          onChange={(e) => handleProfileChange(e.target.value)}
        >
          {profiles.map((profile) => (
            <option key={profile} value={profile}>
              {profile}
            </option>
          ))}
        </select>
      </div>
      <div className="settings-item">
        <label>Anki Deck: </label>
        <select
          value={settings.deck_name}
          onChange={(e) => handleDeckChange(e.target.value)}
        >
          {Object.entries(decks).map(([name, id]) => (
            <option key={id} value={name}>
              {name}
            </option>
          ))}
        </select>
      </div>
      <div className="settings-item">
        <label>API Key: </label>
        <input
          type="text"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          placeholder="Enter your OpenAI API key"
        />
        <button
          className="api-key-button"
          onClick={handleSetApiKey}
          style={{ backgroundColor: settings.api_key_set ? 'red' : 'darkgrey' }}
        >
          {settings.api_key_set ? 'Reset API Key' : 'Set API Key'}
        </button>
      </div>
    </div>
  );
}