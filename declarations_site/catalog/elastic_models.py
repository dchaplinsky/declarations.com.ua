from elasticsearch_dsl import DocType, Object, String, Completion, Nested, Date, Boolean


class NoneAwareDate(Date):
    """Elasticsearch DSL Date field chokes on None values and parses empty
    strings as current date, hence the workaround.
    TODO: move this upstream in some form."""
    def _to_python(self, data):
        if data is None:
            return data
        return super(NoneAwareDate, self)._to_python(data)


class Declaration(DocType):
    """Declaration document.
    Assumes there's a dynamic mapping with all fields not indexed by default."""
    general = Object(
        properties={
            'full_name_suggest': Completion(preserve_separators=False),
            'full_name': String(index='analyzed'),
            'name': String(index='analyzed'),
            'patronymic': String(index='analyzed'),
            'last_name': String(index='analyzed'),
            'family_raw': String(index='analyzed'),
            'family': Nested(
                properties={
                    'name': String(index='analyzed'),
                    'relations': String(index='no'),
                    'inn': String(index='no')
                }
            ),
            'post_raw': String(index='analyzed'),
            'post': Object(
                properties={
                    'region': String(index='not_analyzed'),
                    'office': String(index='not_analyzed'),
                    'post': String(index='analyzed')
                }
            )
        }
    )
    declaration = Object(
        properties={
            'date': NoneAwareDate(),
            'notfull': Boolean(index='no'),
            'notfull_lostpages': String(index='no'),
            'additional_info': Boolean(index='no'),
            'additional_info_text': String(index='no'),
            'needs_scancopy_check': Boolean(index='no')
        }
    )
    intro = Object(
        properties={
            'declaration_year': String(index="not_analyzed")
        }
    )

    class Meta:
        index = 'declarations_new'
