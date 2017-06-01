FROM docker.elastic.co/elasticsearch/elasticsearch:5.4.0
RUN elasticsearch-plugin install analysis-ukrainian
COPY elasticsearch.yml config/
USER root
RUN chown elasticsearch:elasticsearch config/elasticsearch.yml
USER elasticsearch
