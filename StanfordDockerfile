FROM centos:centos7

RUN mkdir /var/www
WORKDIR /var/www
RUN yum -y install java wget unzip
RUN wget http://nlp.stanford.edu/software/stanford-ner-2014-08-27.zip
RUN unzip stanford-ner-2014-08-27.zip -d ner
RUN rm stanford-ner-2014-08-27.zip


ENV STANFORD_NER_PATH /var/www/ner/stanford-ner-2014-08-27/stanford-ner.jar
ENV STANFORD_NER_MODEL /var/www/ner/stanford-ner-2014-08-27/classifiers/english.all.3class.distsim.crf.ser.gz

ENV MEMORY 700m
ENV ENCODING "utf-8"
ENV PORT 1447
ENV OUTPUT_FORMAT slashTags
ENV PRESERVE_SPACING "true"

EXPOSE 1447

ENTRYPOINT java -Xmx$MEMORY -cp $STANFORD_NER_PATH edu.stanford.nlp.ie.NERServer \
	-loadClassifier $STANFORD_NER_MODEL -port $PORT \
    -tokenizerFactory edu.stanford.nlp.process.WhitespaceTokenizer \
    -tokenizerOptions "tokenizeNLs=true" \
	-outputFormat $OUTPUT_FORMAT \