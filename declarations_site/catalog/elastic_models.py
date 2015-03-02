from elasticsearch_dsl import DocType, Mapping

declarations_mapping = Mapping('declarations')
declarations_mapping.field("general", 'object')
declarations_mapping["general"].property(
    'full_name_suggest', 'completion',
    preserve_separators=False
)


class Declaration(DocType):
    class Meta:
        index = 'catalog'
        mapping = declarations_mapping
