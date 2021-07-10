FROM cytomineuliege/software-python3-base:latest

ARG working_dir=/cytomine_tmp
ARG report_src_dir=/cytomine_report_source

WORKDIR $working_dir

RUN pip install numpy pandas Pillow bs4 sklearn pdfkit boto3

ADD app.py app.py

ENTRYPOINT ["python", "app.py"]
