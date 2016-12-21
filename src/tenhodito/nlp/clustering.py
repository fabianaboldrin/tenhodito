from nlp.bow import Corpus
from scipy.cluster.vq import kmeans2

def kmeans(job, k, whiten=True):
    """
    Performs a k-means classification for all documents in the given job.

    Args:
        job (list or Corpus):
            A list of texts or a Corpus
            instance.
        k (int):
            The desired number of clusters.

    Return:
        centroids:
            A 2D array with all found centroids.
        labels:
            A sequence in witch the i-th element correspond to the cluster index
            for the i-th document.
    """

    if not isinstance(job, Corpus):
        job = Corpus(job)

    data = job.matrix()
    std = 1
    if whiten:
        std = data.std(axis=0)
        std[std == 0] = 1
        data /= std[None, :]
    centroids, labels = kmeans2(data, k, minit='points')
    centroids *= std
    return centroids, labels
