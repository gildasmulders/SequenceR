FROM ubuntu:16.04

RUN apt-get update
RUN apt-get -y install locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y python3.6 && apt-get install -y python3-pip nano
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 2
RUN apt-get update && pip3 install torch==1.2.0 numpy==1.19.5 scipy==1.5.4 && pip3 install gensim && apt install -y default-jre && pip3 install javalang && pip3 install urllib3==1.26.3 && pip3 install configargparse torchtext==0.4.0 pandas==1.1.5 && pip3 install seaborn==0.9.0

WORKDIR /SequenceR

COPY . /SequenceR

ENV OpenNMT_py=/SequenceR/src/lib/OpenNMT-py
ENV data_path=/SequenceR/results/Golden
