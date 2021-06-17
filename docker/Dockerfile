FROM supervisely/base-py-sdk:6.1.81

# https://github-releases.githubusercontent.com/371759295/5760d400-cf57-11eb-9178-910b148d81ca?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20210617%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20210617T074338Z&X-Amz-Expires=300&X-Amz-Signature=3739086b2e83393d54bcc13dfb525867cff9ac604c2c5de4d52e790d395deb02&X-Amz-SignedHeaders=host&actor_id=12828725&key_id=0&repo_id=371759295&response-content-disposition=attachment%3B%20filename%3Dilastik-1.4.0b14-Linux.tar.bz2&response-content-type=application%2Foctet-stream

#RUN wget https://files.ilastik.org/ilastik-1.4.0b14-Linux.tar.bz2 -O /ilastik-1.4.0b14-Linux.tar.bz2
#RUN mkdir ilastik-build
#RUN tar -xf /ilastik-1.4.0b14-Linux.tar.bz2 -C /ilastik-build

#RUN apt-get install unzip
#RUN wget https://github.com/supervisely-ecosystem/ilastik-demo/releases/download/v0/ilastik-1.4.0b14-Linux.zip -O /ilastik-1.4.0b14-Linux.zip
#RUN mkdir /ilastik-build
#RUN unzip /ilastik-1.4.0b14-Linux.zip -d /ilastik-build
#COPY roi.py /ilastik-build/ilastik-meta/ilastik/lazyflow/roi.py


RUN wget  https://files.ilastik.org/ilastik-1.4.0b15-Linux.tar.bz2 -O /ilastik-1.4.0b15-Linux.tar.bz2
RUN mkdir ilastik-build
RUN tar -xf /ilastik-1.4.0b15-Linux.tar.bz2 -C /ilastik-bui
