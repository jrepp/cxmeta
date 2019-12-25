from cxmeta.config.project import Project
from cxmeta.config import random_name


class Builder(object):
    def __init__(self):
        self.modules = dict()
        self.project = None

    def build_from_config(self, config=dict()):
        self.modules = dict()
        self.project = Project(
            name=config.get("name", "project-" + random_name()), config=config
        )
        self.setup_pipeline(config.get("pipeline", list()))
        return self.project

    def setup_pipeline(self, pipeline):
        pass

    def build_default(self):
        self.project = Project(name="default-" + random_name(), config=dict())
        self.setup_pipeline(list())
        return self.project
