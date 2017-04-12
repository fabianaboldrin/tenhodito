from collections import Counter, UserString
from math import log, sqrt
import re
import string

from functools import lru_cache
from Stemmer import Stemmer
from click import progressbar, secho
from lazyutils import lazy
import numpy as np
from stop_words import get_stop_words


DEFAULT_STOP_WORDS = get_stop_words('portuguese')
DEFAULT_STOP_WORDS += ['é', 'president', 'sr', 'govern', 'tod',
                       'anos', 'deput', 'quer', 'senhor', 'porqu',
                       'revisã', 'orador', 'sras', 'srs', ]
stemmer = Stemmer('portuguese')


class Text(UserString):

    def __init__(self, data, method=None, stop_words=DEFAULT_STOP_WORDS,
                 ngrams=1, weights=None):
        super().__init__(data)
        self.words = self._get_words(data)
        self.stems = self._stemize(data, stop_words=stop_words, ngrams=ngrams)
        self.weights = weights
        self.method = method

    def __repr__(self):
        data = self.data
        if len(data) >= 10:
            data = data[:10] + '...'
        return '%s(%r)' % (type(self).__name__, data)

    def __str__(self):
        return self.data

    def words_count(self):
        data = [w for w in self.words if w and w not in DEFAULT_STOP_WORDS]
        return Counter(data)

    def all_words(self):
        """Return a sorted list of unique words presents in text.

        Returns:
            list
        """
        return sorted(set(self.words))

    def stem_words(self):
        """Return a sorted list of unique stemmed words presents in text.

        Returns:
            list
        """
        return sorted(set(self.stems))

    @lru_cache(1024)
    def bow(self, method='boolean'):
        return self._bag_of_words(method)

    def _bag_of_words(self, method='boolean'):
        count = Counter(self.stems)
        bow = None
        if method == 'boolean':
            bow = Counter({stem: 1 for stem in count})
        elif method == 'frequency':
            total = sum(count.values())
            bow = Counter({stem: n / total for (stem, n) in count.items()})
        elif method == 'count':
            return count
        elif method == 'weighted':
            if self.weights is not None:
                counter = self._bag_of_words('frequency')
                bow = Counter({stem: self.weights.get(stem, 1) * freq
                               for (stem, freq) in counter.items()})
            else:
                raise RuntimeError('Must define .weights attribute first')
        else:
            raise ValueError('Invalid method: %r' % method)

        return bow

    def _get_words(self, text):
        words = text.casefold().split()
        words = [self._remove_punctuation(word) for word in words]
        return words

    def _stemize(self, text, stop_words=None, ngrams=1):
        if stop_words is None:
            stop_words = DEFAULT_STOP_WORDS

        stop_words_stems = set(stemmer.stemWords(stop_words))
        words = stemmer.stemWords(self.words)

        data = [w for w in words if w and w not in stop_words_stems]

        if ngrams > 1:
            result = []
            for i in range(len(data) - ngrams + 1):
                words = data[i:i + ngrams]
                result.append(' '.join(words))
            return result
        else:
            return data

    def _remove_punctuation(self, word):
        regex = re.compile('[%s]' % re.escape(string.punctuation))
        return regex.sub('', word)


class Corpus:

    def __init__(self, texts=(), ngrams=1, method='frequency', stop_words=None):
        secho('Creating corpus with %d texts' % len(texts), bold=True)
        self._texts = self._get_texts(texts, ngrams, stop_words)
        self._method = method
        self._update_weights()

    def __len__(self):
        return len(self._texts)

    def __iter__(self):
        for text in self._texts:
            yield text

    def __getitem__(self, idx):
        return self._texts[idx]

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

    @lazy
    def frequency(self):
        counter = Counter()
        label = 'Calculating frequency'
        with progressbar(self._texts, label=label.ljust(50)) as data:
            for text in data:
                counter += Counter(text.bow('frequency'))
        return counter

    def weights(self):
        N = len(self._texts)
        frequencies = self.frequency
        label = 'Calculating weights'
        with progressbar(frequencies.items(), label=label.ljust(50)) as data:
            return {stem: log(N / freq) for (stem, freq) in data}

    @lru_cache(1024)
    def vector(self, i):
        text = self._texts[i]
        words = self.stem_words()
        return np.array([text.bow(self._method).get(w, 0.0) for w in words])

    def matrix(self):
        N = len(self._texts)
        label = 'Building corpus matrix'
        with progressbar(range(N), label=label.ljust(50)) as data:
            return np.array([self.vector(i) for i in data])

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

    def similarity_matrix(self, method='triangular'):
        N = len(self._texts)
        similarity = np.ones([N, N], dtype=float)
        label = 'Building similarity matrix'
        with progressbar(range(N), label=label.ljust(50)) as data:
            for i in data:
                for j in range(i + 1, N):
                    value = self.similarity(i, j, method)
                    similarity[i, j] = similarity[j, i] = value
            return similarity

    def _get_texts(self, texts, ngrams, stop_words):
        label = 'Extracting words and stems'
        text_list = []
        with progressbar(texts, label=label.ljust(50)) as data:
            for text in data:
                text_list.append(Text(text, ngrams=ngrams,
                                      stop_words=stop_words, ))
        return text_list

    def _update_weights(self):
        weights = self.weights()
        label = 'Updating weights'
        with progressbar(self._texts, label=label.ljust(50)) as data:
            for text in data:
                text.weights = weights

    def _norm(self, u):
        return sqrt((u * u).sum())
