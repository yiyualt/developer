## ADDED Requirements

### Requirement: DocumentLoader abstract interface
DocumentLoader SHALL define an ABC with a `load()` method that returns a list of Document objects. Each Document SHALL contain `page_content` (str) and `metadata` (dict, default empty).

#### Scenario: ABC enforces load method
- **WHEN** a class inherits DocumentLoader but does not implement `load()`
- **THEN** instantiation raises TypeError

#### Scenario: Document content and metadata
- **WHEN** a Document is created with content "Hello world" and metadata {"source": "test.txt"}
- **THEN** `doc.page_content` equals "Hello world" and `doc.metadata` equals {"source": "test.txt"}

### Requirement: TextLoader implementation
TextLoader SHALL implement DocumentLoader and load plain text files. It SHALL accept a `file_path` parameter and set `metadata["source"]` to the file path.

#### Scenario: Load a text file
- **WHEN** TextLoader is created with file_path="data/readme.txt" and `load()` is called
- **THEN** a list containing one Document is returned, with `page_content` equal to the file's text content and `metadata["source"]` equal to "data/readme.txt"

#### Scenario: Load non-existent file
- **WHEN** TextLoader is created with a file_path that does not exist and `load()` is called
- **THEN** a FileNotFoundError is raised