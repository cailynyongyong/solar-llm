### 환경설정

가상 환경 만들고 .env 파일 만들어서 UPSTAGE API Key 넣어주세요. 예시 .env 파일은 .env.example에서 찾을 수 있습니다.

```
python -m venv venv
source venv/bin/activate
pip install --upgrade --quiet  langchain langchain-community python-dotenv langchain-core langchain-upstage
python chatbot.py
```

학습시킬 예시 PDF 파일에 들어갈 텍스트는 test.txt 파일에서 찾을 수 있습니다.
