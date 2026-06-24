## Objective
The aim of this project is to create a system where users can upload documents and ask questions about them. The system provides relevant answers without requiring users to read the complete PDF files. It also tries to reduce hallucinations by generating answers only from the uploaded documents and verifying the response before showing it to the user.

## Architecture
<img width="997" height="716" alt="image" src="https://github.com/user-attachments/assets/2ae1c81d-45ad-4def-9f50-8252a1fb6327" />

## Future Works

1. Instead of doing chunking every time, the system can save the chunks and embeddings after the document is uploaded. The chunks will remain stored until the user deletes the document, making retrieval faster.

2. The system can support more file types such as Word documents, PowerPoint presentations, images, and scanned PDFs so that users can ask questions from different kinds of files.

3. The system can be improved to handle multiple documents at the same time and provide better answers by combining information from different documents.
