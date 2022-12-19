---
title: Neural Search Demo
emoji: 🧠🔎
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8501
pinned: true
---

## 🧠 Neural Search Demo 🔎

This is a tool to allow indexing & search content using neural capabilities using [Haystack](https://haystack.deepset.ai/overview/intro) open-source framework.

You can see the demo working [here](https://huggingface.co/spaces/ugaray96/neural-search).

### Local Setup

Install `python`, `virtualenv` and `ffmpeg` in your linux distribution system:

```shell
sudo apt-get install python3.8
sudo apt-get install python3.8-venv python3-pip
sudo apt install ffmpeg
```

Activate the environment and upgrade pip:

```shell
python3.8 -m venv env
source ./env/bin/activate
pip install pip==22.2
```

Install the requirements:

```shell
pip install --use-deprecated=legacy-resolver -r requirements.txt
```

Make sure Elasticsearch is running in the background by:

```shell
docker pull docker.elastic.co/elasticsearch/elasticsearch:7.9.2
docker run --name elasticsearch -d -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.9.2
```

Finally, run app by executing the following:

```shell
streamlit run app.py
```

And go to [localhost:8501](http://localhost:8501/) to start navigating the app.
