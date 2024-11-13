# app.py
from fastapi import FastAPI, HTTPException
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from nltk.tokenize import sent_tokenize
from fastapi.middleware.cors import CORSMiddleware
import nltk 
nltk.download('punkt')

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Models
retriever_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
generator_model = AutoModelForSeq2SeqLM.from_pretrained('facebook/bart-large-cnn')#still not sure about the model
generator_tokenizer = AutoTokenizer.from_pretrained('facebook/bart-large-cnn')# better models can be used

# Prepare Document Chunks for FAISS
# Read paragraphs from a .txt file
file_path = 'paragraphs.txt'

with open(file_path, 'r', encoding='utf-8') as file:
    # Read the file contents and split by double newlines (blank lines between paragraphs)
    paragraphs = [para.strip() for para in file.read().split('\n\n') if para.strip()]

# print("Paragraphs =", paragraphs)


# Split paragraphs into chunks of 3–5 sentences
def chunk_paragraph(paragraph, max_chunk_size=5):
    sentences = sent_tokenize(paragraph)
    chunks = [" ".join(sentences[i:i + max_chunk_size]) for i in range(0, len(sentences), max_chunk_size)]
    return chunks

# Process paragraphs
chunks = []
for paragraph in paragraphs:
    chunks.extend(chunk_paragraph(paragraph))

# Encode chunks and add to FAISS index
doc_embeddings = retriever_model.encode(chunks, convert_to_tensor=True)
faiss_index = faiss.IndexFlatL2(doc_embeddings.shape[1])
faiss_index.add(doc_embeddings.cpu().detach().numpy())

@app.post("/generate_response/")
async def generate_response(query: str):
    # Step 1: Retrieve relevant chunks
    query_embedding = retriever_model.encode([query])
    _, doc_indices = faiss_index.search(query_embedding, k=5)  # Retrieve top 5 chunks
    retrieved_docs = [chunks[i] for i in doc_indices[0]]
    
    # Step 2: Generate response
    input_text = " ".join(retrieved_docs) + " " + query
    inputs = generator_tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
    outputs = generator_model.generate(**inputs, max_length=150)
    response = generator_tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return {"response": response}
