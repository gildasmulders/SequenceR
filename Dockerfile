FROM working-sequencer:v2

WORKDIR /SequenceR

COPY . /SequenceR

ENV OpenNMT_py=/SequenceR/src/lib/OpenNMT_py
ENV data_path=/SequenceR/results/Golden