<div align="center">
  <img src="https://github.com/shoshinL/FLASH/assets/97098427/f458ea88-f839-4be7-a48f-e5024ca93aab" alt="Logo" width="200">

  # FLASH - Flashcard Leveraging Agentic Study Help
</div>

## 📚 About FLASH

FLASH is an application that automatically generates Anki Flashcards from your Notes, Lecture Slides, or Papers (in .pdf format). It integrates seamlessly with Anki and saves the cards directly into your Anki storage. It even syncs automatically if you have syncing set up!

## 🚀 Getting Started

### Prerequisites

1. Download and install [Anki](https://apps.ankiweb.net/)

### Installation

#### Option 1: Windows Executable

- Simply download the .exe file provided here and run it!

**Note:** Windows Defender might try to delete and claim it's a trojan. This happens because it was generated using PyInstaller without a signed certificate.

#### Option 2: Build from Source

1. Clone the repository
2. Run the following commands:
```shell
npm run init
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

```shell
npm run init
```

```shell
npm run start
```

```shell
npm run build
```

**Note:** If any dependency issues arise please refer to the [pywebview documentation](https://pywebview.flowrl.com/guide/installation.html#dependencies)
## 🔧 How It Works

FLASH processes documents through the following steps:

1. **Document Processing**
   - Read and split the document into small and large chunks

2. **Embedding and Question Generation**
   - Embed small chunks using nv-embed-v1
   - Generate questions from large chunks

3. **Question Refinement**
   - Deduplicate generated questions

4. **Answer Generation**
   - Create parallel subgraphs for each question
   - Retrieve relevant document chunks
   - Generate and validate answers

5. **Flashcard Creation**
   - Route Q&A pairs to appropriate Flashcard Generation Experts
   - Generate various card types (Basic, Reversed, Cloze, etc.)

6. **User Review**
   - Present generated cards to the user for final editing

7. **Anki Integration**
   - Write cards to selected Anki deck
   - Sync with AnkiWeb (if enabled)
