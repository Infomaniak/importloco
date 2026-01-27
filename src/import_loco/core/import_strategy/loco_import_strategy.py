class LocoImportStrategy:
    def __init__(self, filters, parser, endpoint, destination_filename):
        self.filters = filters
        self.parser = parser
        self.endpoint = endpoint
        self.destination_filename = destination_filename

    def get_localizable_path(self, project_config, language):
        root = project_config.main_target_localizable_path if self.use_main_target else project_config.localizable_path
        return f"{root}/{language}/{self.destination_filename}"
