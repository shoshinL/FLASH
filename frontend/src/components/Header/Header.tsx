import "./Header.css";
import logo from "../../assets/logo.png";
import backIcon from "../../assets/arrow-left-long-solid.svg";
import gearIcon from "../../assets/gear-solid.svg";

interface HeaderProps {
  showSettings: boolean;
  onToggleSettings: () => void;
  isSettingsEnabled: boolean;
}

export function Header({ showSettings, onToggleSettings, isSettingsEnabled }: HeaderProps) {
  return (
    <div className="header-container">
      {showSettings ? (
        <img src={backIcon} alt="Back" className="logo button-icon" onClick={onToggleSettings} />
      ) : (
        <>
          <img className="logo" src={logo} alt="Logo" />
          <h2 className="header-title">FLASH</h2>
        </>
      )}
      <div className="settings">
        <button 
          onClick={onToggleSettings} 
          className={`settings-button ${showSettings ? 'pressed' : ''} ${!isSettingsEnabled ? 'disabled' : ''}`}
          disabled={!isSettingsEnabled}
        >
          <img src={gearIcon} alt="Settings" className="settings-icon" />
          <span>Settings</span>
        </button>
      </div>
    </div>
  );
}