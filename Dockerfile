FROM python:3.8.9
WORKDIR /home/user/app
RUN apt-get install -y   git   git-lfs   ffmpeg   libsm6   libxext6   cmake   libgl1-mesa-glx   && rm -rf /var/lib/apt/lists/*   && git lfs install
RUN pip install --no-cache-dir pip==22.0.2 && pip install --no-cache-dir         datasets         huggingface-hub       "protobuf<4" "click<8.1"
RUN apt-get update && xargs -r -a packages.txt apt-get install -y && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir streamlit==1.10.0 
COPY --chown=user --from=lfs /app /home/user/app
COPY --chown=user ./ /home/user/app
