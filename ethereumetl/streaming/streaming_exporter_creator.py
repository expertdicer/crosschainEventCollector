from blockchainetl.streaming.exporter.mongo_event_exporter import MongodbEventExporter


def create_steaming_lending_log_exporter(output, collector_id='events', db_prefix=""):
    if not collector_id:
        return None
    streaming_exporter_type = determine_item_exporter_type(output)
    if streaming_exporter_type == StreamingExporterType.MONGODB:
        streaming_exporter = MongodbEventExporter(connection_url=output, collector_id=collector_id,
                                                  db_prefix=db_prefix)
    else:
        streaming_exporter = None
    return streaming_exporter


def determine_item_exporter_type(output):
    if output is not None and output.startswith('mongodb'):
        return StreamingExporterType.MONGODB
    else:
        return StreamingExporterType.UNKNOWN


class StreamingExporterType:
    MONGODB = 'mongodb'
    UNKNOWN = 'unknown'
