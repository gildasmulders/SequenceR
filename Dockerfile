FROM working-sequencer:v2

WORKDIR /SequenceR

RUN rm -r ./test-results/*

COPY . /SequenceR