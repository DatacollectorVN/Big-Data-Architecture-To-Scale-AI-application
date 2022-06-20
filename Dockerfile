FROM python:3.7

WORKDIR /chest-xray-v2

# gcc compiler and opencv prerequisites
RUN apt update \
    && apt install -y htop wget nano git build-essential libglib2.0-0 libsm6 libxext6 libxrender-dev

EXPOSE 8501

COPY . .

# FOR X86
RUN /bin/bash -c "pip3 install -r requirements_docker.txt \
    && pip3 install cython \
    && pip3 install -U 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI' \
    && python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/index.html \
    && python src/download_5_classes_model.py --model_directory snapshots"

# FOR ARM (APPLE M1)
# RUN /bin/bash -c "pip3 install -r requirements_docker.txt \
#     && pip3 install cython \
#     && pip3 install -U 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI' \
#     && python -m pip install 'git+https://github.com/facebookresearch/detectron2.git' \
#     && python src/download_5_classes_model.py --model_directory snapshots"


ENTRYPOINT ["streamlit", "run"]

CMD ["streamlit_inference.py"]