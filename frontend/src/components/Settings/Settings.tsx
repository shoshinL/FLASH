import { useState, useEffect } from "react";
import "./Settings.css";
import { ProviderSettings } from "./ProviderSettings";
import { AnkiSettings } from "./AnkiSettings";
import type { Settings, ProfilesResponse, DecksResponse, AnkiPathResponse } from "../../types/settings";
import { isSettings, isProfilesResponse, isDecksResponse, isAnkiPathResponse } from "../../utils/typeGuards";


export function Settings() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [profiles, setProfiles] = useState<string[]>([]);
  const [decks, setDecks] = useState<Record<string, number>>({});
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"llm" | "embedding" | "api_keys" | "anki">("llm");

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

  if (!settings) {
    return <div>Loading settings...</div>;
  }

  return (
    <div className="settings-container">
      {/* Tab Navigation */}
      <div className="settings-tabs">
        <button
          className={`settings-tab ${activeTab === "llm" ? "active" : ""}`}
          onClick={() => setActiveTab("llm")}
        >
          Language Model
        </button>
        <button
          className={`settings-tab ${activeTab === "embedding" ? "active" : ""}`}
          onClick={() => setActiveTab("embedding")}
        >
          Embedding Model
        </button>
        <button
          className={`settings-tab ${activeTab === "api_keys" ? "active" : ""}`}
          onClick={() => setActiveTab("api_keys")}
        >
          API Keys
        </button>
        <button
          className={`settings-tab ${activeTab === "anki" ? "active" : ""}`}
          onClick={() => setActiveTab("anki")}
        >
          Anki
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === "llm" ? (
        <ProviderSettings mode="llm" />
      ) : activeTab === "embedding" ? (
        <ProviderSettings mode="embedding" />
      ) : activeTab === "api_keys" ? (
        <ProviderSettings mode="api_keys" />
      ) : (
        <AnkiSettings
          ankiDbPath={settings.anki_db_path}
          profile={settings.profile}
          deckName={settings.deck_name}
          profiles={profiles}
          decks={decks}
          error={error}
          onSelectAnkiPath={handleSelectAnkiPath}
          onProfileChange={handleProfileChange}
          onDeckChange={handleDeckChange}
        />
      )}
    </div>
  );
}