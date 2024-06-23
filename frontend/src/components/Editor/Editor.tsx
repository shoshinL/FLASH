import { useState, useRef } from "react";
import "./Editor.css";
import fileIcon from "../../assets/file-import-solid.svg";
import pdfFileIcon from "../../assets/file-pdf-solid.svg";
import trashcanIcon from "../../assets/trash-can-solid.svg";
import lightningIcon from "../../assets/lightning.svg";

interface FileWithPath extends File {
  path?: string;
}

interface EditorProps {
  onGenerateStart: () => void;
}

export function Editor({ onGenerateStart }: EditorProps) {
  const [content, saveContent] = useState("");
  const [file, setFile] = useState<string | null>(null);
  const [filePath, setFilePath] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [cardAmount, setCardAmount] = useState(5);
  const fileUploadRef = useRef<HTMLDivElement>(null);

  const handleFileUpload = () => {
    // @ts-ignore
    window.pywebview.api.select_file().then((selectedFile: string | null) => {
      if (selectedFile) {
        setFile(selectedFile.split(/(\\|\/)/g).pop() || "");
        setFilePath(selectedFile);
      }
    });
  };

  const handleFileReset = (e: React.MouseEvent) => {
    e.stopPropagation();
    setFile(null);
    setFilePath(null);
  };

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!fileUploadRef.current?.contains(e.relatedTarget as Node)) {
      setIsDragging(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer?.files;
    if (files && files.length > 0) {
      const droppedFile = files[0] as FileWithPath;
      if (droppedFile.type === "application/pdf") {
        setFile(droppedFile.name);
        if (droppedFile.path) {
          setFilePath(droppedFile.path);
        }
      }
    }
  };

  const handleGenerateCards = async () => {
    if (!file) {
      //TODO: hier den guten Alert nutzen
      window.pywebview.api.show_alert("Please select a .pdf file for the flashcards.");
      return;
    }

    onGenerateStart();
    try {
      await window.pywebview.api.generate_flashcards_test(content, filePath, cardAmount);
    } catch (error) {
      console.error("Error generating flashcards:", error);
      // Error handling is now managed in the App component
    }
  }

  return (
    <div className="editor-container">
      <textarea
        className="textarea"
        placeholder="Enter what the flashcards should focus on in the document below..."
        value={content}
        onChange={(e) => saveContent(e.target.value)}
      />
      <div
        ref={fileUploadRef}
        className={`file-upload ${file ? "file-selected" : ""} ${isDragging ? "dragging" : ""}`}
        onClick={handleFileUpload}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="file-icon">
          <img src={file ? pdfFileIcon : fileIcon} alt="File Icon" />
        </div>
        <div className="file-text">
          {file ? (
            <>
              <span>{file}</span>
              <div className="file-reset" onClick={handleFileReset}>
                <img src={trashcanIcon} alt="Delete" />
              </div>
            </>
          ) : (
            <>
              <span>{isDragging ? "DROP HERE" : "Select .pdf"}</span>
              <span className="file-hint">Or drag and drop here</span>
            </>
          )}
        </div>
      </div>
      <div className="controls-container">
        <select
          className="dropdown"
          value={cardAmount}
          onChange={(e) => setCardAmount(Number(e.target.value))}
        >
          {[3, 5, 10, 15, 20, 25, 30].map(num => (
            <option key={num} value={num}>{num} Flashcards</option>
          ))}
        </select>
        <button
          className="generate-button"
          onClick={handleGenerateCards}
        >
          <img src={lightningIcon} alt="Lightning" />
          Generate
        </button>
      </div>
    </div>
  );
}