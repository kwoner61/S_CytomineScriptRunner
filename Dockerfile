FROM cytomineuliege/software-python3-base:latest

#RUN pip install numpy pandas Pillow bs4 sklearn pdfkit boto3
RUN mkdir /CytomineScriptRunner

ADD app.py /CytomineScriptRunner/app.py

ENTRYPOINT ["python", "/CytomineScriptRunner/app.py"]
