from nlp.bow import Text
from collections import Counter
from math import log, sqrt
import numpy as np


class NLPJob:

    def __init__(self, texts=(), method='weighted', stop_words=None):
        self._texts = [Text(data, stop_words=stop_words) for data in texts]
        self._method = method
        self._update_weights()

    def __len__(self):
        return len(self._texts)

    def __iter__(self):
        for text in self._texts:
            yield text.data

    def __getitem__(self, idx):
        return self._texts[idx].data

    def stem_words(self):
        words = set()
        for text in self._texts:
            words.update(text.stem_words())
        return sorted(words)

    def common_words(self, n=None, by_document=False):
        counter = Counter()
        if by_document:
            N = len(self._texts)
            for text in self._texts:
                counter += text.bow('boolean')
            common = counter.most_common(n)
            return [(word, count / N) for (word, count) in common]
        else:
            for text in self._texts:
                counter += text.bow('count')
            total = sum(counter.values())
            common = counter.most_common(n)
            return [(word, count / total) for (word, count) in common]

    def corpus_frequency(self):
        counter = Counter()
        for text in self._texts:
            counter += Counter(text.bow('frequency'))
        return counter

    def weights(self):
        N = len(self._texts)
        frequencies = self.corpus_frequency()
        return {stem: log(N / freq) for (stem, freq) in frequencies.items()}

    def vector(self, i):
        text = self._texts[i]
        words = self.stem_words()
        return np.array([text.bow(self._method).get(w, 0.0) for w in words])

    def matrix(self):
        N = len(self._texts)
        return np.array([self.vector(i) for i in range(N)])

    def angle(self, i, j):
        return np.arccos(self._cos_angle(i, j))

    def similarity(self, i, j, method='triangular'):
        u = self.vector(i)
        v = self.vector(j)

        if method == 'angle':
            similarity = (self._cos_angle(u, v) + 1 / 2)
        elif method == 'triangular':
            norm_u = self._norm(u)
            norm_v = self._norm(v)
            if norm_u == norm_v == 0:
                similarity = 1.0
            similarity = 1 - self._norm(u - v) / (norm_u + norm_v)
        else:
            raise ValueError('Invalid similarity method: %r' % method)

        return similarity

    def _update_weights(self):
        weights = self.weights()
        for text in self._texts:
            text.weights = weights

    def _cos_angle(self, i, j):
        u = self.vector(i)
        v = self.vector(j)
        return u.dot(v) / (self._norm(u) * self._norm(v))

    def _norm(self, u):
        return sqrt((u * u).sum())