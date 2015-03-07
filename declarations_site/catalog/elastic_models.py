from elasticsearch_dsl import DocType, Object, String, Completion, Nested


class Declaration(DocType):
    general = Object(
        properties={
            'full_name_suggest': Completion(preserve_separators=False),
            'family_raw': String(),
            'family': Nested(
                properties={
                    'name': String()
                }
            ),
            'post': Object(
                properties={
                    'post': String(),
                    'office': String()
                }
            )
        }
    )

    class Meta:
        index = 'catalog'
