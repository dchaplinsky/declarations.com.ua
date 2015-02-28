from elasticsearch_dsl import DocType


class Declaration(DocType):

    class Meta:
        index = 'catalog'
