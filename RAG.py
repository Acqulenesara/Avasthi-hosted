import PyPDF2
import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from nltk.tokenize import sent_tokenize
import nltk

# Load env variables
load_dotenv()
api_key = os.getenv("PINECONE_API_KEY")
cloud_region = os.getenv("PINECONE_ENVIRONMENT")

# Load SentenceTransformer model (384 dimensions)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
embedding_dimension = 384   # IMPORTANT

# Download nltk data
nltk.download('punkt')

# PDF path
pdf_file = "C:/Users/acqul/PycharmProjects/flow/The_Stress_Management.pdf"

def extract_text_from_pdf(pdf_file):
    with open(pdf_file, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

pdf_text = extract_text_from_pdf(pdf_file)

def split_text(text, max_tokens=4000):
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = len(sentence.split())
        if current_tokens + sentence_tokens > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_tokens = sentence_tokens
        else:
            current_chunk.append(sentence)
            current_tokens += sentence_tokens

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

texts = split_text(pdf_text)

print("Generating embeddings...")
embeddings = model.encode(texts, convert_to_numpy=True).tolist()

data_to_upsert = []
for i, (text, embedding) in enumerate(zip(texts, embeddings)):
    metadata = {"text": text}
    data_to_upsert.append({"id": f"pdf-text-{i}", "values": embedding, "metadata": metadata})

# Connect to Pinecone
pc = Pinecone(api_key=api_key)
index_name = "flow-384"

# Create Pinecone index for 384-dim model if not exists
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=embedding_dimension,
        metric='cosine',
        spec=ServerlessSpec(
            cloud="aws",
            region=cloud_region.split("-")[1]
        )
    )

index = pc.Index(index_name)
print(f"Pinecone index '{index_name}' initialized!")

print("Upserting vectors...")
index.upsert(data_to_upsert)
print(f"✅ {len(data_to_upsert)} vectors uploaded successfully!")

# Debug check
def debug_pinecone_upsert(index):
    example_ids = [f"pdf-text-{i}" for i in range(2)]
    fetched = index.fetch(ids=example_ids)
    vectors = fetched.vectors

    print(f"\nRetrieved {len(vectors)} vectors")

    for vec_id, vec_data in vectors.items():
        print(f"ID: {vec_id}")
        print(f"Metadata: {vec_data.get('metadata')}")
        print(f"Embedding sample: {vec_data.get('values')[:5]} ...")

debug_pinecone_upsert(index)
