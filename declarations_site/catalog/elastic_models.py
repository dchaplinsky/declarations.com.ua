from elasticsearch_dsl import DocType, Mapping
from elasticsearch_dsl.connections import connections


class MyUglyMapping(object):
    doc_type = "declarations"
    properties = {
        doc_type: {
            "properties": {
                "general": {
                    "type": "object",

                    "properties": {
                        "full_name_suggest": {
                            "type": "completion",
                            "preserve_separators": False
                        },

                        "family_raw": {
                            "type": "string"
                        },

                        "family": {
                            "properties": {
                                "name": {"type": "string"},
                            },
                            "type": "object"
                        },

                        "post": {
                            "properties": {
                                "post": {"type": "string"},
                                "office": {"type": "string"},
                            },
                            "type": "object"
                        }
                    }
                }
            }
        }
    }

    def save(self, index, using="default"):
        # TODO: analyzers, ...
        es = connections.get_connection(using)
        if not es.indices.exists(index=index):
            es.indices.create(
                index=index, body={'mappings': self.properties}
            )
        else:
            es.indices.put_mapping(
                index=index,
                doc_type=self.doc_type,
                body=self.properties
            )


class Declaration(DocType):
    class Meta:
        index = 'catalog'
        mapping = Mapping('declarations')
