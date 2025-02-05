FROM python:3.12-slim

RUN apt-get update && apt-get install -y git

WORKDIR /Application_streamlit

ADD Application_streamlit/ .

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "Main.py"]