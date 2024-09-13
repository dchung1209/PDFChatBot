# PDFChatBot
![alt text](/home/dchung/projects/PDFChat/assets/2024-09-13 112810.png)

# Features

- **RAG + Recursive Retrieval + Reranker**: Get more precise responses from PDFs. Used LlamaIndex for the RAG pipeline and Colbert 2.0 for reranking.

- **Multi-Model Support**: Choose between Llama 3.1 and GPT-4o for language model needs.

- **Integration**: Utilized Streamlit to create a user-friendly chat interface.

- **Conversation Management**: Conversations are saved in an SQL Server, allowing you to keep track of your interactions.


# Instructions

1. **Set API Keys**
    - OpenAI API Key
    - LlamaCloud API Key
    - GroqCloud API Key (for Llama 3.1)

2. **Upload PDF**
    - Click on the file uploader to select and upload your PDF file.

3. **Process PDF**
    - Click "Process" to analyze and index your PDF.

4. **Interact with Document**
    - Type your questions in the chat input to get responses from the PDF.

5. **Save and Review Conversations**
    - Use the "Save Chat" button to save your chat history and review it later.



# Few Notes

The new released model from openAI would be a good language model to process complex mathematics questions.
