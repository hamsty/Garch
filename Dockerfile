FROM alpine:edge
RUN apk add sudo
RUN echo "%wheel ALL=(ALL) ALL" >> /etc/sudoers.d/wheelsudo
RUN cat /etc/sudoers.d/wheelsudo
RUN echo -e "root\nroot" | passwd
RUN echo -e "admin\nadmin"| sudo adduser --home /app/ --ingroup wheel --shell /bin/sh  admin
RUN echo "root" |sudo -S echo "@testing http://nl.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
USER admin
RUN echo "admin" |sudo -S apk add gcc make python3-dev py3-pip py3-wheel R R-dev R-doc g++ py3-numpy-dev py3-pandas@testing py3-cffi ipython R-mathlib cython py3-pyzmq ipython-doc

ENV LD_LIBRARY_PATH /usr/lib/R/lib/:${LD_LIBRARY_PATH}
RUN echo "admin" | sudo -S pip install rpy2 jupyter

WORKDIR /app
COPY . /app/
CMD ["jupyter","notebook","--ip=0.0.0.0"]

