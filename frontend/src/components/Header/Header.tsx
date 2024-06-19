import "./Header.css";
import logo from "../../assets/logo.png";
import backIcon from "../../assets/back.png"; // Ensure this icon is available in your assets

interface HeaderProps {
  showSettings: boolean;
  onToggleSettings: () => void;
}

export function Header({ showSettings, onToggleSettings }: HeaderProps) {
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
        <button onClick={onToggleSettings} className={`settings-button ${showSettings ? 'pressed' : ''}`}>
          Settings
        </button>
      </div>
    </div>
  );
}

