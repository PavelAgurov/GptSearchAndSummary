# Demo POC

## Main

### 1. Upload files

TBD

### 2. Extract plain text

TBD

### 3. Indexing

TBD

### 4. Topics

TBD

### 5. Citations (similatiry search)

TBD

### 6. Summary

TBD

## How to run

```python
streamlit run main.py
```

## Backlog

### 1. Backlog: Upload files

- [x] Upload file(s)
- [x] Delete file(s)
- [x] Document set

### 2. Backlog: Extract plain text

- [x] pdf parser (per page)
- [x] docx parser (no MS Word required)
- [x] msg parser (no Outlook required)
- [x] txt parser (in fact - just copy file 'as is')
- [x] UnstructuredParser from langchain for all other file types
- [x] error processing
- [x] to save meta-information
- [x] split by Document set
- [ ] to check: to suppot PPT by UnstructuredFileLoader we need to install libreoffice
- [ ] to check if UnstructuredFileLoader use external API and send information to their API
- [ ] break words for paragpaphs
- [ ] table processing

### 3. Backlog: Indexing

- [x] create Qdrant vector db in memory or in file
- [x] index name - it's possible to create many indexes
- [x] support OpenAI or SBERT embeddings
- [x] min chunk size to ignore "empty" chunks/paragpaphs
- [x] to save meta-information into db
- [x] split by Document set
- [x] delete existed index

### 4. Backlog: Topics

- [ ] similairy request per topic
- [ ] summary prompt per topic

### 5. Backlog: Citations (similatiry search)

- [x] similarity search
- [x] add refs to the source paragpaphs
- [X] post processing - LLM score
- [x] select Document set
- [ ] select topic or custom request
- [ ] how to use metainformation

### 6. Backlog: Summary and Q&A

- [ ] select Document set
- [ ] build LLM summary/refine
- [ ] simple Q&A
- [ ] conversional Q&A

### 7. Backlog: Other

- [ ] restAPI
- [ ] user UI
- [ ] docker
- [ ] Azure Gpt Key support
- [ ] conversional Q&A

### 8. Backlog: Testing

- [ ] test set
- [ ] test set score (to compare facts?)
- [ ] user's feedback for chunks

### 9. Backlog: extended

- [ ] load KB data


