# tools.py
import os
from langchain_community.document_loaders import DirectoryLoader,TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import HuggingFacePipeline
from transformers import pipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
DATA_FOLDER="RAG-DATA"
CHROMA_PATH="data/chroma_db"
if not os.path.exists(DATA_FOLDER):
    raise FileNotFoundError(f"{DATA_FOLDER} folder not found")
print("Files in RAG-DATA:",os.listdir(DATA_FOLDER))
loader=DirectoryLoader(
    DATA_FOLDER,
    glob="**/*.txt",
    loader_cls=TextLoader
)
documents=loader.load()
print(f"Loaded {len(documents)} documents")
text_splitter=RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
splits=text_splitter.split_documents(documents)
print(f"Created {len(splits)} chunks")
embedding=HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
vectorstore=Chroma.from_documents(
    documents=splits,
    embedding=embedding,
    persist_directory=CHROMA_PATH
)
print("Vector DB size:",vectorstore._collection.count())
retriever=vectorstore.as_retriever(search_kwargs={"k":3})
generator=pipeline(
    "text2text-generation",
    model="google/flan-t5-base"
)
llm=HuggingFacePipeline(pipeline=generator)
rag_prompt=PromptTemplate(
    input_variables=["context","question"],
    template="""
You are a college information assistant.
Answer the question using ONLY the context below.
If the answer is not in the context,say "I don't know".
Context:
{context}
Question:
{question}
Answer:
"""
)
rag_chain=(
    {
        "context":retriever,
        "question":RunnablePassthrough()
    }
    |rag_prompt
    |llm
    |StrOutputParser()
)
def ask(question:str)->str:
    return rag_chain.invoke(question).strip()
if __name__=="__main__":
    print("\nTEST RESULT:")
    print(ask("Is Wi-Fi available in hostel?"))