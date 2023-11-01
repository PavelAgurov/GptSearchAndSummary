# Demo POC

## Main

### 0. Document set

This page allows to create Document set. All other operations will be in scope of Document set.

Document sets are stored in file `.document-set\document-set.json`

Default Document set can be provided by parameter `document-set` in URL:

```http://localhost:8501/?document-set=test```

### 1. Upload content

Here you can upload documents into Document set (or delete documents from Document set).

Files are uploaded into `.document-source\<document-set>` folder.

### 2. Extract plain text

All search operation works only with plain text, so this page allow to extract plain text from
different data sources.

With help of LLM you can fix formatting.

From formatted documents you can extract tables.

- Plain text files are stored in `.document-plain-text\<document-set>` folder.
- Each page has extension -nn.txt, where nn is a page number
- Meta-information about page is stored in .txt.json file (per page)
- Formatted page is stored in .txt.html file (per page)
- Extracted tables are stored in .txt.tables.json file (per page)

### 3. Indexing

TBD

### 4. Topics

TBD

### 5. Citations (similatiry search)

TBD

### 6. Summary

TBD

### 7. Knowledge tree

TBD

### 8. Tables

TBD

## How to run

```python
streamlit run main.py
```

## Backlog

### 0. Backlog: Document set

- [ ] Delete document set

### 1. Backlog: Upload content

- [x] Upload file(s)
- [x] Delete file(s)
- [x] Document set
- [ ] Document content as HTML by URL

### 2. Backlog: Extract plain text

- [x] pdf parser (per page)
- [x] docx parser (no MS Word required)
- [x] msg parser (no Outlook required)
- [x] txt parser (in fact - just copy file 'as is')
- [x] UnstructuredParser from langchain for all other file types
- [x] error processing
- [x] to save meta-information
- [x] split by Document set
- [x] LLM pre-processing for plain text
- [x] table processing
- [ ] to check: to suppot PPT by UnstructuredFileLoader we need to install libreoffice
- [ ] to check if UnstructuredFileLoader use external API and send information to their API
- [ ] break words for paragpaphs

### 3. Backlog: Indexing

- [x] create Qdrant vector db in memory or in file
- [x] index name - it's possible to create many indexes
- [x] support OpenAI or SBERT embeddings
- [x] min chunk size to ignore "empty" chunks/paragpaphs
- [x] to save meta-information into db
- [x] split by Document set
- [x] delete existed index
- [x] allow to use formatted plain text for indexing

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
- [ ] role and permissions


