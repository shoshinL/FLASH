/**
 * Anki Integration Settings Component
 *
 * Handles Anki database path, profile, and deck selection.
 */

interface AnkiSettingsProps {
  // Current settings
  ankiDbPath: string;
  profile: string;
  deckName: string;

  // Available options
  profiles: string[];
  decks: Record<string, number>;

  // Messages
  error: string | null;

  // Event handlers
  onSelectAnkiPath: () => Promise<void>;
  onProfileChange: (profile: string) => Promise<void>;
  onDeckChange: (deckName: string) => Promise<void>;
}

export function AnkiSettings({
  ankiDbPath,
  profile,
  deckName,
  profiles,
  decks,
  error,
  onSelectAnkiPath,
  onProfileChange,
  onDeckChange
}: AnkiSettingsProps) {
  return (
    <div className="anki-settings">
      {error && <div className="error-message">{error}</div>}

      <div className="settings-item">
        <label>Anki Database File: </label>
        <input
          type="text"
          className="file-path-input"
          value={ankiDbPath}
          readOnly
          onClick={onSelectAnkiPath}
        />
      </div>

      <div className="settings-item">
        <label>Anki Profile: </label>
        <select
          value={profile}
          onChange={(e) => onProfileChange(e.target.value)}
        >
          {profiles.map((profileOption) => (
            <option key={profileOption} value={profileOption}>
              {profileOption}
            </option>
          ))}
        </select>
      </div>

      <div className="settings-item">
        <label>Anki Deck: </label>
        <select
          value={deckName}
          onChange={(e) => onDeckChange(e.target.value)}
        >
          {Object.entries(decks).map(([name, id]) => (
            <option key={id} value={name}>
              {name}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
