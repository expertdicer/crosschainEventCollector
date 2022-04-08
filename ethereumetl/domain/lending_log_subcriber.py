class EventSubscriber:
    def __init__(self, topic_hash, name, list_params_in_order):
        self.topic_hash = topic_hash
        self.name = name
        self.list_params_in_order = list_params_in_order