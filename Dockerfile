FROM python:3.12.6

WORKDIR Application_streamlit

ADD Application_streamlit/ .

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "Main.py"]