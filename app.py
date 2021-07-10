import os
import sys
import logging

from cytomine import CytomineJob
from cytomine.models import AnnotationCollection, Job


def main(argv):
  print('Entering main@@@@')
  with CytomineJob.from_cli(argv) as cj:
    
    cj.job.update(status=Job.RUNNING, progress=0, statusComment='Starting...')
    # annotations = AnnotationCollection()
    # annotations.project = cj.parameters.cytomine_id_project

    # cj.job.update(status=Job.RUNNING, progress=10, statusComment='Fetching annotations...')
    # annotations.fetch()

    # for annotation in annotations:
    #   img_name = f'{annotation.image}-{annotation.id}.jpg'
    #   cj.job.update(status=Job.RUNNING, progress=30, statusComment=f'Downloading image for annotation {annotation.id}...')
    #   annotation.dump(dest_pattern=os.path.join('./', img_name))


if __name__ == '__main__':
  main(sys.argv[1:])
