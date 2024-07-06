import os
import chromadb
from pypdf import PdfReader 
from chromadb.utils import embedding_functions
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from dotenv import load_dotenv
from faker import Faker
import random

faker = Faker()

load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)


class Document:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata if metadata is not None else {}

def generate_random_metadata():

    metadata = {
        'author': faker.name(),
        'date': faker.date(),
        'category': faker.word(),
        'tags': [faker.word() for _ in range(random.randint(1, 5))]
    }
    return metadata

def pdf_to_text(file):

    reader = PdfReader(file)
    text = ""
    for page_num in range( len(reader.pages)):
        text += reader.pages[page_num].extract_text()  
    # print(text)
    return text

def add_data(filename):

    text=pdf_to_text(filename)

    db_name= filename.replace(".pdf","")

    # print(db_name)

    chunks = text_splitter.split_text(text)
    docs=[]
    id=[]
    for i,chunk in enumerate(chunks):
        docs.append(chunk)
        id.append(str(i))

    client = chromadb.PersistentClient(path="C:\\Users\\reube\\OneDrive\\Desktop\\Mini Project\\PDF_Query\\database")
    collection = client.get_or_create_collection(name=db_name, embedding_function=sentence_transformer_ef)

    collection.add(
                documents=docs,
                ids=id)
                
    print("Data Added")
    print(collection.count())


    return db_name


def retrieve_section(input,db_name):

    client = chromadb.PersistentClient(path="C:\\Users\\reube\\OneDrive\\Desktop\\Mini Project\\PDF_Query\\database")
    collection = client.get_collection(name=db_name, embedding_function=sentence_transformer_ef)
    print("Available Collections: " )
    print(client.list_collections())


    results = collection.query( query_texts = input,
                                n_results=4,
                                include=["documents", "distances"])
    result=results["documents"]
    # print(result)
    
    for iresult in result:
        
        documents = [Document(page_content=text, metadata=generate_random_metadata()) for text in iresult]
        # print(documents)
    return documents

def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
    provided context just say, "answer is not available in the context at this moment", don't provide the wrong answer\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro",
                             temperature=0.3)

    prompt = PromptTemplate(template = prompt_template, input_variables = ["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain

def user_input(user_query,db_name):

    docs=retrieve_section(user_query,db_name)

    chain=get_conversational_chain()
    response = chain.invoke(
        {"input_documents":docs, "question": user_query}
        , return_only_outputs=True)
     
    # print(response['output_text'])
    return response['output_text']







if __name__ == "__main__":
    db_name=add_data("dbms.pdf")
    # db_name="dbms"
    question="What is a update problem"
    user_input(question,db_name)
    print(db_name)
        
    print("main")

    