import { useState, useRef, useEffect } from "react";
import "./Editor.css";
import fileIcon from "../../assets/file-import-solid.svg";
import pdfFileIcon from "../../assets/file-pdf-solid.svg";
import trashcanIcon from "../../assets/trash-can-solid.svg";

interface FileWithPath extends File {
  path?: string;
}

export function Editor() {
  const [content, saveContent] = useState("");
  const [file, setFile] = useState<string | null>(null);
  const [filePath, setFilePath] = useState<string | null>(null); // Store full file path
  const [isDragging, setIsDragging] = useState(false);
  const fileUploadRef = useRef<HTMLDivElement>(null);

  const handleFileUpload = () => {
    window.pywebview.api.select_file().then((selectedFile: unknown) => {
      const selectedFilePath = selectedFile as string; // Assert type to string
      setFile(selectedFilePath.split(/(\\|\/)/g).pop() || ""); // Extract and set file name
      setFilePath(selectedFilePath); // Store full file path
    });
  };

  const handleFileReset = (e: React.MouseEvent) => {
    e.stopPropagation();
    setFile(null);
    setFilePath(null); // Reset full file path
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
          setFilePath(droppedFile.path); // Store full file path
        }
        // Handle the file upload logic
      }
    }
  };

  useEffect(() => {
    const handleWindowDragEnter = (e: DragEvent) => handleDragEnter(e as unknown as React.DragEvent);
    const handleWindowDragLeave = (e: DragEvent) => handleDragLeave(e as unknown as React.DragEvent);
    const handleWindowDragOver = (e: DragEvent) => handleDragOver(e as unknown as React.DragEvent);
    const handleWindowDrop = (e: DragEvent) => handleDrop(e as unknown as React.DragEvent);

    window.addEventListener("dragenter", handleWindowDragEnter);
    window.addEventListener("dragleave", handleWindowDragLeave);
    window.addEventListener("dragover", handleWindowDragOver);
    window.addEventListener("drop", handleWindowDrop);

    return () => {
      window.removeEventListener("dragenter", handleWindowDragEnter);
      window.removeEventListener("dragleave", handleWindowDragLeave);
      window.removeEventListener("dragover", handleWindowDragOver);
      window.removeEventListener("drop", handleWindowDrop);
    };
  }, []);

  return (
    <div className="editor-container">
      <textarea
        className="textarea"
        placeholder="Enter wishes and context for the flashcard generation here..."
        value={content}
        onChange={(e) => {
          saveContent(e.target.value);
        }}
      />
      <div
        ref={fileUploadRef}
        className={`file-upload ${file ? "file-selected" : ""} ${isDragging ? "dragging" : ""}`}
        onClick={handleFileUpload}
      >
        <div className="file-icon">
          <img
            src={file ? pdfFileIcon : fileIcon}
            alt="File Icon"
          />
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
              {!isDragging && <span className="file-hint">Or drag and drop here</span>}
            </>
          )}
        </div>
      </div>
      <button
        className="button"
        onClick={() => {
          window.pywebview.api.make_card(content, filePath).then((card: unknown) => {
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
