import os
import sys

import cv2
import csv
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
        annotations.terms = cj.parameters.cytomine_id_terms
        replacement_colors = get_replacement_colors([cj.parameters.color_1,
                                                     cj.parameters.color_2, cj.parameters.color_3,
                                                     cj.parameters.color_4, cj.parameters.color_5,
                                                     cj.parameters.color_6])

        cj.job.update(status=Job.RUNNING, progress=10, statusComment='Fetching annotations...')
        annotations.fetch()

        i, p = 0, 0
        annotation_names = []
        num_annotations = len(annotations)
        for annotation in annotations:
            img_name = f'{annotation.image}_{annotation.id}.jpg'
            seg_image_name = f'kmeans_k{n}_{img_name}'
            img_src = os.path.join(working_dir, img_name)

            cj.job.update(status=Job.RUNNING, progress=30 + p,
                          statusComment=f'Running Segmentation for annotation {annotation.id}...')
            annotation.dump(dest_pattern=img_src, max_size=cj.parameters.max_size)
            img = cv2.cvtColor(cv2.imread(img_src), cv2.COLOR_BGR2RGB)
            img_uri = upload_job_data(cj.job.id, img_name, img_src)

            seg, stats = segscript.k_means_seg(img, n)
            masked, updated_stats = segscript.rgb_mask(n, seg, stats.copy(), replacement_colors)

            Image.fromarray(masked).save(os.path.join(working_dir, seg_image_name))
            masked_uri = upload_job_data(cj.job.id, seg_image_name, os.path.join(working_dir, seg_image_name))

            # image_src_names.append(get_img_src(img_uri))
            annotation_names.append(annotation.id)
            seg_img_names.append(get_img_src(masked_uri))
            stats_lists.append(updated_stats)
            p = ((i+1) / num_annotations) * 60
            i += 1

        generate_csv_output(cj, n, annotation_names, stats_lists, annotation.image, annotations.terms)

        # report_file_path = os.path.join(working_dir, f'combined-k{n}-report.html')
        # template_file_path = os.path.join(working_dir, 'combined_report_template.html')
        # segscript.generate_combined_report(n, image_src_names, seg_img_names, stats_lists, report_file_path,
        #                                    template_file_path)

        # cj.job.update(status=Job.RUNNING, progress=90, statusComment=f'Uploading report...')
        # upload_job_data(cj.job.id, 'Segmentation Report', report_file_path)

        cj.job.update(status=Job.SUCCESS, progress=100, statusComment=f'Finished')


def generate_csv_output(cj, k, annotation_names, stats_lists, image_id, term_id):
    csv_output_name = f'output_{image_id}.csv'
    with open(csv_output_name, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='\'', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['Image ID', 'Term ID', 'Annotation ID', 'Color', 'Area Percentile'])
        for i in range(len(annotation_names)):
            for j in range(k):
                color = f'[{stats_lists[i][j][4]}_{stats_lists[i][j][5]}_{stats_lists[i][j][6]}]'
                area = stats_lists[i][j][3]
                spamwriter.writerow([image_id, term_id, annotation_names[i], color, area])

    upload_job_data(cj.job.id, csv_output_name, csv_output_name)
    generate_csv_report(cj, csv_output_name, len(annotation_names), image_id, term_id)


def generate_csv_report(cj, csv_output_name, annotation_count, image_id, term_id):
    csv_report_name = csv_output_name.replace('output', 'report')
    with open(csv_report_name, 'w', newline='') as csv_report:
        spamwriter = csv.writer(csv_report, delimiter=',',
                                quotechar='\'', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['Image ID', 'Term ID', 'Color', 'Area Percentile Average'])

        sum_areas = {}
        with open(csv_output_name, newline='') as csv_output:
            output_reader = csv.reader(csv_output, delimiter=',',
                                       quotechar='\'', quoting=csv.QUOTE_MINIMAL)
            output_reader.__next__()
            for row in output_reader:
                color = row[3]
                area_p = row[4]
                if color in sum_areas:
                    sum_areas[color] += float(area_p)
                else:
                    sum_areas[color] = float(area_p)

        for color, sum_area in sum_areas.items():
            avg_value = round(sum_area / annotation_count * 100, 2)
            spamwriter.writerow([image_id, term_id, color, avg_value])

    upload_job_data(cj.job.id, csv_report_name, csv_report_name)


def upload_job_data(job_id, key, filename):
    job_data = JobData(job_id, key, filename)
    job_data = job_data.save()
    saved_data = job_data.upload(filename)
    if '.csv' not in filename:
        os.remove(filename)
    return saved_data.uri().replace('.json', '')


def get_img_src(job_data_uri):
    return f'https://test.cytomine.lamis.life/api/{job_data_uri}/view'


def get_replacement_colors(c_list):
    colors = []
    for c in c_list:
        color = c.split(',')
        color = list(map(int, color))
        colors.append(color)
    return colors


if __name__ == '__main__':
    main(sys.argv[1:])
