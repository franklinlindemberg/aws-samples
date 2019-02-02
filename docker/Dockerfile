FROM amazonlinux:2017.03

WORKDIR /app

ADD deploy.sh /app

RUN yum -y install git \
    python36 \
    python36-pip \
    python36-devel \
    zip \
    gcc \
    && yum clean all

RUN python3 -m pip install --upgrade pip \
    awscli \
    troposphere \
    awacs

ENTRYPOINT ["/app/deploy.sh"]
