import { useState } from "react";
import "./Editor.css";

export function Editor() {
  const [content, saveContent] = useState(
    "Using Python as backend, you can perform operations that are not allowed in Javascript, for example disk access. Click button below to save this content to hard drive."
  );
  const [file, setFile] = useState(null);

  const handleFileUpload = () => {
    window.pywebview.api.select_file().then((selectedFile) => {
      //setFile(selectedFile);
      selectedFile
    });
  };

  const handleFileReset = () => {
    setFile(null);
  };

  return (
    <div className="editor-container">
      <textarea
        className="textarea"
        value={content}
        onChange={(e) => {
          saveContent(e.target.value);
        }}
      />
      <div
        className={`file-upload ${file ? "file-selected" : ""}`}
        onClick={handleFileUpload}
      >
        <div className="file-icon">
          <img
            src={file ? "new-file-icon.png" : "file-icon.png"}
            alt="File Icon"
          />
        </div>
        <div className="file-text">
          {file ? (
            <>
              <span>FILE.NAME (in braces)</span>
              <div className="file-reset" onClick={handleFileReset}>
                <img src="trashcan-icon.png" alt="Delete" />
              </div>
            </>
          ) : (
            <>
              <span>Select .pdf</span>
              <br />
              <span className="file-hint">Or drag and drop here</span>
            </>
          )}
        </div>
      </div>
      <button
        className="button"
        onClick={() => {
          window.pywebview.api.save_content(content);
        }}
      >
        Save
      </button>

      <button
        className="button"
        onClick={() => {
          window.pywebview.api.make_card(content).then((card: unknown) => {
            alert(JSON.stringify(card));
          });
        }}>
        MAKE CARD
      </button>

      <button
        className="button"
        onClick={() => {
          window.pywebview.api.reset_api_key();
        }}
      >
        Reset API Key
      </button>
    </div>
  );
}
