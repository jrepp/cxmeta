import abc
from cxmeta.pipeline.stream import Chunk
from cxmeta.pipeline.source_module import Module
from cxmeta.pipeline.combiner import Combiner


def cxmeta_footer() -> str:
    link = "https://github.com/jrepp/cxmeta"
    return "\n\n_Generated by [{link}]({link}) :cactus:_".format(link=link)


def make_md_link(name, link):
    return ":link: [{}]({})".format(name, link)


class GfmStyle(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def start_module(self, module: Module) -> str:
        pass

    @abc.abstractmethod
    def end_module(self, module: Module) -> str:
        pass

    @abc.abstractmethod
    def start_source_file(self, module: Module, source_file: Combiner) -> str:
        pass

    @abc.abstractmethod
    def end_source_file(self, module: Module, source_file: Combiner) -> str:
        pass

    @abc.abstractmethod
    def chunk(
        self, module: Module, source_file: Combiner, chunk: Chunk
    ) -> str:
        pass