import { useState } from "react";
import "./Editor.css";

export function Editor() {
  const [content, saveContent] = useState(
    "Using Python as backend, you can perform operations that are not allowed in Javascript, for example disk access. Click button below to save this content to hard drive."
  );

  return (
    <div className="editor-container">
      <textarea
        className="textarea"
        value={content}
        onChange={(e) => {
          saveContent(e.target.value);
        }}
      />
      <br />
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
          // @ts-expect-error
          window.pywebview.api.make_card(content).then((card: string) => {
            alert(card);
          });
        }}>
        MAKE CARD
      </button>

      <button
        className="button"
        onClick={() => {
          // @ts-expect-error
          window.pywebview.api.get_anki_deck().then((deck: string) => {
            alert(deck);
          });
        }}>
        Get Anki Deck
      </button>


    </div>
  );
}
