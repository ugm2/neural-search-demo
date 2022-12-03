FROM python:3.9
WORKDIR /home/user/app
COPY packages.txt /root/packages.txt
RUN apt-get update && xargs -r -a packages.txt apt-get install -y && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /home/user/app/requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir streamlit==1.10.0 
COPY --from=lfs /app /home/user/app
COPY ./ /home/user/app
