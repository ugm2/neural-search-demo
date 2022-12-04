FROM python:3.8.9
COPY . /app
WORKDIR /app
RUN apt-get update && xargs -r -a packages.txt apt-get install -y && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir streamlit==1.10.0 
EXPOSE 8501
CMD streamlit run app.py