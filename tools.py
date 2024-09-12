import os
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import time
import base64
import uuid
import tempfile
from langchain_upstage import UpstageEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from openai import OpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_upstage import ChatUpstage
from langchain.tools.retriever import create_retriever_tool

os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os.environ["SERPAPI_API_KEY"] = os.getenv("SERPAPI_API_KEY")

if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}

session_id = st.session_state.id
client = None

def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None


def display_pdf(file):
    # Opening file from file path

    st.markdown("### PDF Preview")
    base64_pdf = base64.b64encode(file.read()).decode("utf-8")

    # Embedding PDF in HTML
    pdf_display = f"""<iframe src="data:application/pdf;base64,{base64_pdf}" width="400" height="100%" type="application/pdf"
                        style="height:100vh; width:100%"
                    >
                    </iframe>"""

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)


with st.sidebar:

    st.header(f"Add your documents!")
    
    uploaded_file = st.file_uploader("Choose your `.pdf` file", type="pdf")

    if uploaded_file:
        try:
            file_key = f"{session_id}-{uploaded_file.name}"

            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                file_key = f"{session_id}-{uploaded_file.name}"
                st.write("Indexing your document...")

                if file_key not in st.session_state.get('file_cache', {}):

                    if os.path.exists(temp_dir):
                            loader = PyPDFLoader(
                                file_path
                            )
                    else:    
                        st.error('Could not find the file you uploaded, please check again...')
                        st.stop()
                    
                    pages = loader.load_and_split()

                    vectorstore = Chroma.from_documents(pages, UpstageEmbeddings(model="solar-embedding-1-large"))

                    retriever = vectorstore.as_retriever(k=2)

                    from langchain_upstage import ChatUpstage
                    from langchain_core.messages import HumanMessage, SystemMessage

                    chat = ChatUpstage(upstage_api_key=os.getenv("UPSTAGE_API_KEY"))

                    retriever_tool = create_retriever_tool(
                        retriever,
                        "solar_search",
                        "Searches any questions related to Solar. Always use this tool when user query is related to Solar!",
                    )

                st.success("Ready to Chat!")
                display_pdf(uploaded_file)
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()     

# 웹사이트 제목
st.title("Chatbot with Tools")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 내용을 기록하기 위해 셋업
# Streamlit 특성상 활성화하지 않으면 내용이 다 날아감.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
# 프롬프트 비용이 너무 많이 소요되는 것을 방지하기 위해
MAX_MESSAGES_BEFORE_DELETION = 4

# 웹사이트에서 유저의 인풋을 받고 위에서 만든 AI 에이전트 실행시켜서 답변 받기
if prompt := st.chat_input("Ask a question!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
# 유저가 보낸 질문이면 유저 아이콘과 질문 보여주기
     # 만약 현재 저장된 대화 내용 기록이 4개보다 많으면 자르기
    if len(st.session_state.messages) >= MAX_MESSAGES_BEFORE_DELETION:
        # Remove the first two messages
        del st.session_state.messages[0]
        del st.session_state.messages[0]  

    with st.chat_message("user"):
        st.markdown(prompt)

# AI가 보낸 답변이면 AI 아이콘이랑 LLM 실행시켜서 답변 받고 스트리밍해서 보여주기
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        tavily_tool = TavilySearchResults()

        from langchain_community.utilities import SerpAPIWrapper
        
        params = {
            "engine": "naver",
            "query": prompt,
            "hl": "ko",
        }
        search = SerpAPIWrapper(params=params)

        from langchain_core.tools import Tool

        naver_tool = Tool(
            name="naver_search",
            description="Use Naver search engine",
            func=search.run,
        )

        tools = [tavily_tool, retriever_tool, naver_tool]

        from langchain.agents import AgentExecutor, create_tool_calling_agent
        from langchain import hub

        prompt = hub.pull("hwchase17/openai-tools-agent")
        agent = create_tool_calling_agent(chat, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools)

        result = agent_executor.invoke({"input": prompt, "chat_history": st.session_state.messages})

        for chunk in result["output"].split(" "):
            full_response += chunk + " "
            time.sleep(0.2)
            message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})

print("_______________________")
print(st.session_state.messages)