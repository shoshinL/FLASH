<div align="center">
  <img src="https://github.com/shoshinL/FLASH/assets/97098427/f458ea88-f839-4be7-a48f-e5024ca93aab" alt="Logo">
</div>

# FLASH - Flashcard Leveraging Agentic Study Help 
Flash is an Application that automatically generates Anki Flashcards out of your Notes, Lecture Slides or Papers (in .pdf Format).
It integrates seamlessly with Anki and saves the cards directly into your Anki storage. It even syncs automatically, if you have syncing set up!

### How do I use this?
1. Download and install [Anki](https://apps.ankiweb.net/)
2. If you're on Windows, simply dowload the .exe file provided here and run it!
   Windows Defender might try to delete and claim it's a trojan though. 
   That happens because I generated it using PyInstaller and don't have a Certificate I could sign it with. 

Alternatively can also build the project yourself like so:
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

If any dependency issues arise please refer to the [pywebview documentation](https://pywebview.flowrl.com/guide/installation.html#dependencies)

### How does it work?
Here's how the document get's processed:
1. The Document is read and split up into small and large chunks.
2. Small chunks get embedded using nv-embed-v1, large chunks get handed to the Question Generators.
3. The Questions Generators take into account the added context by the user and generate guestions about the document.
4. The generated questions get deduplicated.
5. For each question an instance of a subgraph for Answer Generation gets created in parallel.
5.1 Relevant small document chunks get retrieved from the vector database.
5.2 The retrieved chunks get checked for relevance and irrelevant ones get removed.
5.3 An answer is generated.
5.4 The answer gets checked for hallucination. If it is hallucinated it is tried one time to regenerate it.
6. All the question and answer pairs get routet to the Flashcard Generation Expert that fits them best. Possible variants are: Basic, Basic (and reversed), Basic (type in the answer), Cloze, Cloze-List.
7. Once the cards are generated they are sent to the frontend for a last check/edit by the user.
8. They are written onto the Anki deck the user selected. If the user has sync enabled they are synced to their AnkiWeb account as well.
