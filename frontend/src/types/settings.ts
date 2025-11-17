/**
 * Settings-related type definitions
 */

export interface Settings {
  anki_db_path: string;
  profile: string;
  deck_name: string;
  api_key_set: boolean;
  anki_data_location_valid: boolean;
}

export interface ProfilesResponse {
  profiles: string[];
}

export interface DecksResponse {
  decks: Record<string, number>;
}

export interface AnkiPathResponse {
  anki_db_path: string;
  profile: string;
  deck_name: string;
  profiles: string[];
  decks: Record<string, number>;
}
