from cytomine.models import Term


class Centroid:
    """
    Color output from k-means segmentation
    """

    def __init__(self, r=None, g=None, b=None, area_p=None):
        self.r_value = r
        self.g_value = g
        self.b_value = b
        self.area_percent = area_p


class SegmentationJob:
    """
    Data container for storing segmentation result
    """

    def __init__(self, annotation_id=None, term_ids=None, img_name=None, seg_img_name=None):
        self.annotation_id = annotation_id
        self.term_ids = term_ids
        self.term_names = []
        self.centroids = []
        self.image_name = img_name
        self.segmented_image_name = seg_img_name

    def add_centroid(self, centroid):
        self.centroids.append(centroid)


def rename_annotation(job: SegmentationJob):
    for t in job.term_ids:
        term_name = Term().fetch(t).name
        job.term_names.append(term_name)


class SegmentationJobCollection:
    """
    Holds list of SegmentationJobs and calculation methods
    """

    def __init__(self, k=None):
        self.jobs = []
        self.k = k

    def add_job(self, job):
        rename_annotation(job)
        self.jobs.append(job)
