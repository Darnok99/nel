FROM centos:centos7

RUN rpm -Uvh  http://pkgs.repoforge.org/rpmforge-release/rpmforge-release-0.5.3-1.el7.rf.x86_64.rpm
RUN yum -y install epel-release

RUN yum -y groupinstall development

RUN yum -y update && yum install -y \
wget \
tar \
python-pip \
python \
python-devel \
gcc \
gcc-c++ \
gcc-gfortran \
gcc44-gfortran \
libgfortran \
lapack \
blas \
blas-devel \
lapack-devel \
git

RUN mkdir -p /var/www/
RUN mkdir -p /etc/app

RUN wget https://github.com/schwa-lab/libschwa/releases/download/0.4.0/libschwa-0.4.0.tar.gz && \
tar zxf libschwa-0.4.0.tar.gz && \
cd libschwa-0.4.0 && \
./configure && \
make && \
make check && \
make install

ENV PKG_CONFIG_PATH $PKG_CONFIG_PATH:/usr/local/lib/pkgconfig
ENV LD_LIBRARY_PATH $LD_LIBRARY_PATH:/usr/local/lib

RUN mkdir /var/dependencies

WORKDIR /var/dependencies

RUN git clone https://github.com/wikilinks/nel.git
RUN git clone https://github.com/wikilinks/neleval.git

COPY /requirements.txt /var/www/requirements.txt
RUN pip install --upgrade -r /var/www/requirements.txt


EXPOSE 8080

COPY / /var/www/
COPY start_app.sh /var/www/start_app.sh


ENV NEL_ROOT=/var/www
ENV NEL_DATASTORE_URI='redis://redis'

RUN mkdir /var/www/output

RUN cp /var/www/scripts/run /var/www/run.sh
WORKDIR /var/www