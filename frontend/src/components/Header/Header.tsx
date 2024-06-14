import "./Header.css";
import logo from "../../assets/logo.png";

export function Header() {
  return (
    <div className="header-container">
      <img className="logo" src={logo} alt="FLASH" />
      <h2>FLASH</h2>

      <div className="links">
        <a href="https://pywebview.flowrl.com/" target="_blank">
          Documentation
        </a>
      </div>
    </div>
  );
}
