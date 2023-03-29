FROM nvidia/cuda:11.6.1-cudnn8-devel-ubuntu20.04

RUN apt update && DEBIAN_FRONTEND=noninteractive apt install git bzip2 wget unzip python3-pip python3-dev cmake libgl1-mesa-dev python-is-python3 libgtk2.0-dev -yq

# Create a working directory
WORKDIR /app

# Install Python packages
COPY requirements.txt requirements.txt
RUN pip3 install python-dotenv

RUN pip3 install -r requirements.txt

COPY . .
ENV HOST 0.0.0.0

CMD ["./start.sh"]
EXPOSE 5000
EXPOSE 8000
