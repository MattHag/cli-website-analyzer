import abc


class CrawlerBase(abc.ABC):
    @abc.abstractmethod
    def next(self):
        ...
