import os
import sys

import cv2
from PIL import Image
from cytomine import CytomineJob
from cytomine.models import AnnotationCollection, Job, JobData

import segscript


def main(argv):
  n = 6
  working_dir = '/CytomineScriptRunner'
  seg_img_names = []
  stats_lists = []

  with CytomineJob.from_cli(argv) as cj:
    cj.job.update(status=Job.RUNNING, progress=0, statusComment='Starting...')
    annotations = AnnotationCollection()
    annotations.project = cj.parameters.cytomine_id_project

    cj.job.update(status=Job.RUNNING, progress=10, statusComment='Fetching annotations...')
    annotations.fetch()

    i = 0
    image_names = []
    for annotation in annotations:
      img_name = f'{annotation.image}-{annotation.id}.jpg'
      seg_image_name = f'kmeans-k{n}-{img_name}'
      img_src = os.path.join(working_dir, img_name)
      
      cj.job.update(status=Job.RUNNING, progress=30+i, statusComment=f'Running Segmentation for annotation {annotation.id}...')
      annotation.dump(dest_pattern=img_src)
      img = cv2.imread(img_src)
      img_uri = upload_job_data(cj.job.id, img_name, img_src)

      seg, stats = segscript.K_means_seg(img, n)
      masked, updated_stats = segscript.rgb_mask(seg, stats.copy())
      
      Image.fromarray(masked).save(os.path.join(working_dir, seg_image_name))
      masked_uri = upload_job_data(cj.job.id, seg_image_name, os.path.join(working_dir, seg_image_name))
      
      image_names.append(get_img_src(img_uri))
      seg_img_names.append(get_img_src(masked_uri))
      stats_lists.append(updated_stats)
      i += 20

    report_file_path = os.path.join(working_dir, f'combined-k{n}-report.html')
    template_file_path = os.path.join(working_dir, 'combined_report_template.html')
    segscript.generate_combined_report(n, image_names, seg_img_names, stats_lists, report_file_path, template_file_path)

    cj.job.update(status=Job.RUNNING, progress=90, statusComment=f'Uploading report...')
    upload_job_data(cj.job.id, 'Segmentation Report', report_file_path)


def upload_job_data(job_id, key, filename):
  job_data = JobData(job_id, key, filename)
  job_data = job_data.save()
  saved_data = job_data.upload(filename)
  return saved_data.uri().replace('.json', '')


def get_img_src(job_data_uri):
  return f'https://test.cytomine.lamis.life/api/{job_data_uri}/view'


if __name__ == '__main__':
  main(sys.argv[1:])
