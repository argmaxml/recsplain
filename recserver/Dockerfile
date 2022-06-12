FROM golang:bullseye

RUN echo "deb http://deb.debian.org/debian bullseye main contrib non-free" >> /etc/apt/sources.list
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y  \
    make \
    wget \
    git \
    libmkl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/Kitware/CMake/releases/download/v3.23.0/cmake-3.23.0-linux-x86_64.sh -O /tmp/cmake.sh && \
    chmod +x /tmp/cmake.sh && \
    /tmp/cmake.sh --skip-license --prefix=/usr/local && \
    rm -rf /tmp/cmake.sh

WORKDIR /
RUN git clone --depth 1 --branch v1.7.2 https://github.com/facebookresearch/faiss.git
WORKDIR /faiss
RUN cmake -B build . -DFAISS_ENABLE_GPU=OFF -DBUILD_SHARED_LIBS=ON -DFAISS_ENABLE_PYTHON=OFF -DFAISS_ENABLE_C_API=ON \
    && make -C build -j4 faiss \
    && make -C build install \
    && cp build/c_api/libfaiss_c.so /usr/lib

WORKDIR /root
RUN git clone https://github.com/argmaxml/recsplain
WORKDIR /root/recsplain/recserver
RUN go build . && mv recserver /root/ && mkdir /root/views && cp run.sh views/index.html /root/views/ && cp run.sh /root/
WORKDIR /root
COPY *.json /root/
COPY *.npy /root/
COPY *.csv /root/
EXPOSE 8088
CMD [ "./recserver" ]