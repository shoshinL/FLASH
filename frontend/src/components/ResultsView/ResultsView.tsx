import { useState, useEffect, useRef } from 'react';
import './ResultsView.css';

interface Flashcard {
  Type: string;
  Front?: string;
  Back?: string;
  Text?: string;
  BackExtra?: string;
}

interface ResultsViewProps {
  results: Flashcard[];
  filename: string;
  onReset: () => void;
}

export function ResultsView({ results, filename, onReset }: ResultsViewProps) {
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [acceptedCards, setAcceptedCards] = useState<Flashcard[]>([]);
  const [savingStatus, setSavingStatus] = useState<string>('');
  const [animationClass, setAnimationClass] = useState('');
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setCards(results);
  }, [results]);

  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (currentIndex < cards.length && !isEditingTextarea()) {
        if (event.key === 'ArrowLeft') {
          handleReject();
        } else if (event.key === 'ArrowRight') {
          handleAccept();
        }
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [currentIndex, cards.length]);

  const isEditingTextarea = () => {
    return document.activeElement instanceof HTMLTextAreaElement;
  };

  const handleAccept = () => {
    if (currentIndex < cards.length) {
      setAnimationClass('swipe-right');
      setAcceptedCards(prev => [...prev, cards[currentIndex]]);
      setTimeout(() => {
        setCurrentIndex(prevIndex => prevIndex + 1);
        setAnimationClass('');
      }, 300);
    }
  };

  const handleReject = () => {
    if (currentIndex < cards.length) {
      setAnimationClass('swipe-left');
      setTimeout(() => {
        setCurrentIndex(prevIndex => prevIndex + 1);
        setAnimationClass('');
      }, 300);
    }
  };

  const handleFinish = async () => {
    try {
      const profile = await window.pywebview.api.get_selected_profile();
      const deck = await window.pywebview.api.get_selected_deck();
      setSavingStatus(`Saving your cards from "${filename}" to Anki Profile ${profile} and Deck: ${deck}`);
      
      const result = await window.pywebview.api.save_accepted_flashcards(acceptedCards, filename);
      if (result === "Success!!") {
        setSavingStatus(`Flashcards from "${filename}" successfully saved to Anki!`);
      } else {
        setSavingStatus(`ERROR: Couldn't save flashcards from "${filename}" to Anki`);
      }
      
      setTimeout(() => {
        onReset();
      }, 3000);
    } catch (error) {
      console.error("Error saving flashcards:", error);
      setSavingStatus(`ERROR: Couldn't save flashcards from "${filename}" to Anki`);
      setTimeout(() => {
        onReset();
      }, 3000);
    }
  };

  const handleEdit = (field: string, value: string) => {
    const updatedCards = [...cards];
    updatedCards[currentIndex] = { ...updatedCards[currentIndex], [field]: value };
    setCards(updatedCards);
  };

  const renderCardContent = (card: Flashcard) => {
    return (
      <div className="card-content">
        <div className="card-type">{card.Type}</div>
        <hr />
        <div className="card-field">
          <span className="field-name">{card.Front ? 'Front' : 'Text'}</span>
          <textarea
            className="editable-textarea"
            value={card.Front || card.Text || ''}
            onChange={(e) => handleEdit(card.Front ? 'Front' : 'Text', e.target.value)}
          />
        </div>
        <hr />
        <div className="card-field">
          <span className="field-name">{card.Back ? 'Back' : 'BackExtra'}</span>
          <textarea
            className="editable-textarea"
            value={card.Back || card.BackExtra || ''}
            onChange={(e) => handleEdit(card.Back ? 'Back' : 'BackExtra', e.target.value)}
          />
        </div>
      </div>
    );
  };

  useEffect(() => {
    if (currentIndex === cards.length && cards.length > 0) {
      handleFinish();
    }
  }, [currentIndex, cards.length]);

  return (
    <div className="results-container">
      <h2>Review Generated Flashcards</h2>
      {currentIndex < cards.length ? (
        <>
          <div className="card-stack">
            {cards.slice(currentIndex, currentIndex + 3).map((card, index) => (
              <div 
                key={currentIndex + index} 
                className={`flashcard ${index === 0 ? `active ${animationClass}` : ''}`}
                ref={index === 0 ? cardRef : null}
              >
                {index === 0 && renderCardContent(card)}
              </div>
            ))}
          </div>
          <div className="button-container">
            <button className="reject-button" onClick={handleReject}>✗</button>
            <button className="accept-button" onClick={handleAccept}>✓</button>
          </div>
        </>
      ) : (
        <div className="finish-container">
          <p>{savingStatus}</p>
        </div>
      )}
    </div>
  );
}