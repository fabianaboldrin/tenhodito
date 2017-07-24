from django.core.management.base import BaseCommand
from nlp.naive_bayes import ThemeNaiveBayesClassifier


class Command(BaseCommand):

    def handle(self, *args, **options):
        print(ThemeNaiveBayesClassifier().classifier)
