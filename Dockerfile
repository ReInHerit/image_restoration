#
#FROM nvidia/cuda:11.6.1-cudnn8-devel-ubuntu20.04 # for GPU acceleration. Works also wothout GPU but the image is much largern than the CPU-only image

# CPU-based image
FROM cnstark/pytorch:1.13.1-py3.9.12-ubuntu20.04

RUN apt update && DEBIAN_FRONTEND=noninteractive apt install git bzip2 wget unzip python3-pip python3-dev cmake libgl1-mesa-dev python-is-python3 libgtk2.0-dev -yq

# Create a working directory
WORKDIR /app
# Install Python packages
COPY requirements.txt requirements.txt
RUN pip3 install python-dotenv

RUN pip3 install -r requirements.txt
COPY start.sh .
COPY . .
ENV HOST 0.0.0.0
ENV PORT=${PORT:-8000}
EXPOSE ${PORT}
EXPOSE 5000

CMD ./start.sh


