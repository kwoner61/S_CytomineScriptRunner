FROM cytomineuliege/software-python3-base:v2.8.2-py3.7.6-slim

RUN pip install numpy pandas Pillow bs4 sklearn
RUN mkdir /CytomineScriptRunner
RUN chmod 775 /CytomineScriptRunner

ADD combined_report_template.html /CytomineScriptRunner/combined_report_template.html
ADD segscript.py /CytomineScriptRunner/segscript.py
ADD app.py /CytomineScriptRunner/app.py

ENTRYPOINT ["python", "/CytomineScriptRunner/app.py"]
