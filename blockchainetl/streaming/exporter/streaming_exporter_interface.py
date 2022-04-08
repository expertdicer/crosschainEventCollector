import logging

logger = logging.getLogger("Streaming exporter")


class StreamingExporterInterface(object):
    """Manages connection to  database and makes async queries
    """

    def __init__(self, connection_url, collector_id):
        self._conn = None

    def get_collector(self, collector_id):
        return

    def update_collector(self, collector):
        """
        """

    def update_latest_updated_at(self, collector_id, latest_updated_at):
        """
        """

    def open(self):
        pass

    def export_items(self, items):
        pass

    def close(self):
        pass
