FROM cytomineuliege/software-python3-base:v2.8.2-py3.7.6-slim

RUN pip install numpy pandas Pillow bs4 sklearn
RUN mkdir /CytomineScriptRunner

ADD combined_report_template.html /CytomineScriptRunner/combined_report_template.html
ADD segscript.py /CytomineScriptRunner/segscript.py
ADD segmentation_job.py /CytomineScriptRunner/segmentation_job.py
ADD app.py /CytomineScriptRunner/app.py

RUN chmod -R 777 /CytomineScriptRunner

ENTRYPOINT ["python", "/CytomineScriptRunner/app.py"]
