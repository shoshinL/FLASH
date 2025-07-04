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

<img src="./flash_graph.svg">

1. **Document Processing**
   - Reads and splits the document into small (for answer generation) and large (for RAG question generation) chunks.
   - Node:
     - `document_loader`:
       - Input: Document Path.
       - Function: Parses the pdf, chunks it, and embeds the small chunks for answer generation.
       - Output: Questioning Chunks, Vector Store Retriever for the answer generation chunks.

2. **Question Generation and Deduplication**
   - Generates questions from large chunks and deduplicate them semantically.
   - Nodes:
     - `question_generator`:
       - Input: Questioning Chunks, Number of Questions to generate, User defined Questioning Context.
       - Function: Generates Questions for each of the chunks.
       - Output: List of Questions for the chunk.
     - `question_deduplicator`:
       - Input: Generated Questions, Number of Questions to generate.
       - Function: Deduplicates the questions from all the questioning chunks and reduces them to the number of questions defined by the user.
       - Output: List of deduplicated questions.
      
4. **Answer Generation**
   - Creates parallel subgraph for each question, utilizes RAG pipeline to generate answers.
   - Nodes:
     - `retrieve`:
       - Input: Vectorstore-retriever, Question.
       - Function: Retrieves the 4 most similar small chunks as context for generating an answer.
       - Output: Retrieved small chunks.
     - `grade_documents`:
       - Input: Question, Retrieved small chunks.
       - Function: Filters out chunks that are not actually relevant to answering the question.
       - Output: Filtered small chunks.
     - `generate_answers`:
       - Input: Question, Filtered small chunks.
       - Function: Generates answers to the questions based on the retrieved context. (Retries once if the answer was judged to be hallucinated.)
       - Output: Question-Answer pairs.

5. **Flashcard Creation**
   - Route Q&A pairs to appropriate Flashcard Generation Experts in parralel.
   - Generate various card types (Basic, Basic and Reversed, Type in the Answer, Cloze, List) out of the Q&A pairs.

6. **User Review**
   - Present generated cards to the user for final editing and accepting/rejecting cards to be saved.

7. **Anki Integration**
   - Write cards to selected Anki deck with custom tag.
   - Sync with AnkiWeb (if enabled).
