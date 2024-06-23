import { useRef, useState } from "react";
import "./Editor.css";
import fileIcon from "../../assets/file-import-solid.svg";
import pdfFileIcon from "../../assets/file-pdf-solid.svg";
import trashcanIcon from "../../assets/trash-can-solid.svg";
import lightningIcon from "../../assets/lightning.svg";

interface FileWithPath extends File {
  path?: string;
}

interface EditorProps {
  content: string;
  setContent: (content: string) => void;
  file: string | null;
  setFile: (file: string | null) => void;
  filePath: string | null;
  setFilePath: (filePath: string | null) => void;
  cardAmount: number;
  setCardAmount: (cardAmount: number) => void;
  onGenerateStart: () => void;
}

export function Editor({
  content,
  setContent,
  file,
  setFile,
  filePath,
  setFilePath,
  cardAmount,
  setCardAmount,
  onGenerateStart
}: EditorProps) {
  const [isDragging, setIsDragging] = useState(false);
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
      window.pywebview.api.show_alert("Please select a .pdf file for the flashcards!");
      return;
    }

    const settings_valid = await window.pywebview.api.valid_settings();
    if (!settings_valid) {
      return;
    }

    onGenerateStart();
    try {
      await window.pywebview.api.generate_flashcards(content, filePath, cardAmount);
    } catch (error) {
      console.error("Error generating flashcards:", error);
    }
  }

  return (
    <div className="editor-container">
      <textarea
        className="textarea"
        placeholder="Enter what the flashcards should focus on in the document below..."
        value={content}
        onChange={(e) => setContent(e.target.value)}
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