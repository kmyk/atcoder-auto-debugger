FROM ubuntu:18.04

# install LLVM and valgrind
RUN apt-get update \
    && apt-get install -y xz-utils build-essential curl valgrind \
    && rm -rf /var/lib/apt/lists/* \
    && curl -SL http://releases.llvm.org/8.0.0/clang+llvm-8.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz \
        | tar -xJC . \
    && mv clang+llvm-8.0.0-x86_64-linux-gnu-ubuntu-18.04 clang_8.0.0 \
    && echo 'export PATH=/clang_8.0.0/bin:$PATH' >> ~/.bashrc \
    && echo 'export LD_LIBRARY_PATH=/clang_8.0.0/lib:LD_LIBRARY_PATH' >> ~/.bashrc

CMD [ "/bin/bash" ]
