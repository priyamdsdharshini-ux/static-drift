from langchain_ollama import ChatOllama
from dotenv import load_dotenv

load_dotenv()

def create_llm():
    llm = ChatOllama(
        model="qwen3:0.6b",  # use llama3.2:3b or qwen3:4b if tool calling is unreliable
        temperature=0,       # 0 = most consistent answers, important for medical info
        num_predict=1024
    )

    return llm

if __name__ == "__main__":
    user_input = input("Ask a question to the LLM: ")

    llm = create_llm()
    response = llm.invoke(user_input)

    print("\n\n\nCLEAN RESPONSE\n\n\n", response.content)
