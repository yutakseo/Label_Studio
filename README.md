## 이 저장소의 실행 구조

공식 저장소의 `label_studio` 이름과 공식 로컬 저장소 예제의 `files` 이름을 사용합니다. 이 저장소는 Docker 확장 구성으로, 공식 소스 트리 전체를 복제한 구조는 아닙니다.

```text
label_studio/       Dockerfile, 확장 코드, 서버 데이터
  data/            DB, 업로드 파일, 내보내기 결과
files/             로컬 저장소로 연결하는 원본 데이터셋
  <dataset>/       images/, masks/, tasks.json, label_config.xml
docker-compose.yml
```

브러쉬와 지우개 크기는 최소 크기는 0.2픽셀이고, 그 위로는 0.5픽셀 단위로 최대 30픽셀까지 조절할 수 있습니다. 슬라이더, 크기 조절 단축키, 마우스 휠에 동일하게 적용됩니다. 브러쉬와 지우개는 이미지 좌표계의 0.1픽셀 사각형 격자에 맞춰 사각형 도장을 이어서 칠합니다. 그리는 중, 다시 표시할 때, 내보낼 때 동일한 방식으로 처리합니다. 내보내는 래스터 마스크의 해상도는 원본 이미지와 같습니다.

와콤 등 태블릿 펜의 Pointer 입력을 이미지 편집기의 마우스 그리기 처리로 연결합니다. 펜을 누른 상태의 이동과 떼기, 입력 취소 및 창 포커스 해제를 처리합니다.

상단 라벨 탭에는 저장된 작성자를 표시하고, 선택한 라벨을 편집 중이면 현재 계정과 `작업 중`, 변경된 자동 저장 초안이면 초안 계정과 `미제출 초안`을 표시합니다. 편집하지 않은 가져온 라벨에는 현재 계정 이름을 붙이지 않습니다. 작성자가 없는 가져온 마스크는 `작성자 미지정`으로 표시하며, 마지막 저장자를 원 작성자로 바꾸지는 않습니다.

작업 목록의 `Annotated by` 열과 작업자 필터는 기록된 작성자만 사용합니다. 가져오기나 마지막 저장자 정보로 작성자를 추정하지 않습니다. 작성자가 없는 라벨은 라벨 결과를 변경해 저장한 사용자에게 귀속되며, 결과가 같은 저장이나 메타데이터 변경만으로는 작성자를 지정하지 않습니다.

`mask_original`은 원본 비교용 탭입니다. 일반 export 직렬화에서 해당 prediction을 제외하며, 저장된 작업 라벨은 유지합니다. 기존에 생성한 export 파일은 새로 생성해야 이 규칙이 적용됩니다.

`docker compose up -d --build`로 실행합니다. `label_studio/data`는 `/label-studio/data`, `files`는 `/label-studio/data/files`에 마운트합니다. `LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=/label-studio/data`이므로 이미지 URL은 `/data/local-files/?d=files/<dataset>/images/...` 형식입니다.

프로젝트의 Local Files 소스 저장소 경로는 `/label-studio/data/files/<dataset>`, JSON 파일 필터는 `.*\.json$`, `use_blob_urls`는 `false`로 설정합니다. 같은 데이터를 UI Import와 저장소 Sync로 중복 가져오지 마세요. 등록 후 데이터셋 폴더명을 변경할 때는 태스크 URL, 저장소 경로 및 동기화 기록도 함께 이전해야 합니다.

`label_config.xml`은 프로젝트의 Labeling Interface에 직접 적용하는 설정 원본입니다. 웹 UI에서 Import한 파일은 Label Studio가 별도로 `label_studio/data/media/upload/` 아래에 관리합니다. DB와 데이터셋은 별도로 백업하세요.

공식 참고: [저장소 소스 코드](https://github.com/HumanSignal/label-studio), [Docker와 로컬 저장소](https://labelstud.io/guide/start.html#Run-Label-Studio-on-Docker-and-use-Local-Storage).

---

<img src="https://user-images.githubusercontent.com/12534576/192582340-4c9e4401-1fe6-4dbb-95bb-fdbba5493f61.png"/>

![GitHub](https://img.shields.io/github/license/heartexlabs/label-studio?logo=heartex) ![label-studio:build](https://github.com/HumanSignal/label-studio/workflows/label-studio:build/badge.svg) ![GitHub release](https://img.shields.io/github/v/release/heartexlabs/label-studio?include_prereleases)

[Website](https://labelstud.io/) • [Docs](https://labelstud.io/guide/) • [Join Slack Community <img src="https://app.heartex.ai/docs/images/slack-mini.png" width="18px"/>](https://slack.labelstud.io/?source=github-1)


## What is Label Studio?

<!-- <a href="https://labelstud.io/blog/release-130.html"><img src="https://github.com/HumanSignal/label-studio/raw/master/docs/themes/htx/source/images/release-130/LS-Hits-v1.3.png" align="right" /></a> -->

Label Studio is an open source data labeling tool. It lets you label data types like audio, text, images, videos, and time series with a simple and straightforward UI and export to various model formats. It can be used to prepare raw data or improve existing training data to get more accurate ML models.

- [Try out Label Studio](#try-out-label-studio)
- [What you get from Label Studio](#what-you-get-from-label-studio)
- [Included templates for labeling data in Label Studio](#included-templates-for-labeling-data-in-label-studio)
- [Set up machine learning models with Label Studio](#set-up-machine-learning-models-with-Label-Studio)
- [Integrate Label Studio with your existing tools](#integrate-label-studio-with-your-existing-tools)

![Gif of Label Studio annotating different types of data](/images/annotation_examples.gif)

Have a custom dataset? You can customize Label Studio to fit your needs. Read an [introductory blog post](https://towardsdatascience.com/introducing-label-studio-a-swiss-army-knife-of-data-labeling-140c1be92881) to learn more. 

## Try out Label Studio

Install Label Studio locally or deploy it in a cloud instance. [Or sign up for a free trial of our Starter Cloud edition!](https://humansignal.com/platform/starter-cloud/) You can learn more about what each edition offers [here](https://labelstud.io/guide/label_studio_compare). 

- [Install locally with Docker](#install-locally-with-docker)
- [Run with Docker Compose (Label Studio + Nginx + PostgreSQL)](#run-with-docker-compose)
- [Install locally with pip](#install-locally-with-pip)
- [Install locally with poetry](#install-locally-with-poetry)
- [Install locally with Anaconda](#install-locally-with-anaconda)
- [Install for local development](#install-for-local-development)
- [Deploy in a cloud instance](#deploy-in-a-cloud-instance)

### Install locally with Docker
Official Label Studio docker image is [here](https://hub.docker.com/r/heartexlabs/label-studio) and it can be downloaded with `docker pull`. 
Run Label Studio in a Docker container and access it at `http://localhost:8080`.


```bash
docker pull heartexlabs/label-studio:latest
docker run -it -p 8080:8080 -v $(pwd)/mydata:/label-studio/data heartexlabs/label-studio:latest
```
You can find all the generated assets, including SQLite3 database storage `label_studio.sqlite3` and uploaded files, in the `./mydata` directory.

#### Override default Docker install
You can override the default launch command by appending the new arguments:
```bash
docker run -it -p 8080:8080 -v $(pwd)/mydata:/label-studio/data heartexlabs/label-studio:latest label-studio --log-level DEBUG
```

#### Build a local image with Docker
If you want to build a local image, run:
```bash
docker build -t heartexlabs/label-studio:latest .
```

### Run with Docker Compose
Docker Compose script provides production-ready stack consisting of the following components:

- Label Studio
- [Nginx](https://www.nginx.com/) - proxy web server used to load various static data, including uploaded audio, images, etc.
- [PostgreSQL](https://www.postgresql.org/) - production-ready database that replaces less performant SQLite3.

To start using the app from `http://localhost` run this command:
```bash
docker-compose up
```

### Run with Docker Compose + MinIO
You can also run it with an additional MinIO server for local S3 storage. This is particularly useful when you want to 
test the behavior with S3 storage on your local system. To start Label Studio in this way, you need to run the following command:
````bash
# Add sudo on Linux if you are not a member of the docker group
docker compose -f docker-compose.yml -f docker-compose.minio.yml up -d
````
If you do not have a static IP address, you must create an entry in your hosts file so that both Label Studio and your 
browser can access the MinIO server. For more detailed instructions, please refer to [our guide on storing data](docs/source/guide/storedata.md).


### Install locally with pip

```bash
# Requires Python >=3.10
pip install label-studio

# Start the server at http://localhost:8080
label-studio
```

### Install locally with poetry

```bash
### install poetry
pip install poetry

### set poetry environment
poetry new my-label-studio
cd my-label-studio
poetry add label-studio

### activate poetry environment
poetry shell

### Start the server at http://localhost:8080
label-studio
```

### Install locally with Anaconda

```bash
conda create --name label-studio
conda activate label-studio
conda install psycopg2
pip install label-studio
```

### Install for local development

You can run the latest Label Studio version locally without installing the package from pypi. 

```bash
# Install all package dependencies
pip install poetry
poetry install
# Run database migrations
python label_studio/manage.py migrate
python label_studio/manage.py collectstatic
# Start the server in development mode at http://localhost:8080
python label_studio/manage.py runserver
```

### Deploy in a cloud instance

You can deploy Label Studio with one click in Heroku, Microsoft Azure, or Google Cloud Platform: 

<a href="https://www.heroku.com/deploy?template=https://github.com/HumanSignal/label-studio/tree/heroku-persistent-pg"><img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy" height="30px"></a>
[<img src="https://aka.ms/deploytoazurebutton" height="30px">](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fhumansignal%2Flabel-studio%2Fdevelop%2Fazuredeploy.json)
[<img src="https://deploy.cloud.run/button.svg" height="30px">](https://deploy.cloud.run)


#### Apply frontend changes

For information about updating the frontend, see [label-studio/web/README.md](https://github.com/HumanSignal/label-studio/blob/develop/web/README.md#installation-instructions).


#### Install dependencies on Windows 
To run Label Studio on Windows, download and install the following wheel packages from [Gohlke builds](https://www.lfd.uci.edu/~gohlke/pythonlibs) to ensure you're using the correct version of Python:
- [lxml](https://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml)

```bash
# Upgrade pip 
pip install -U pip

# If you're running Win64 with Python 3.8, install the packages downloaded from Gohlke:
pip install lxml‑4.5.0‑cp38‑cp38‑win_amd64.whl

# Install label studio
pip install label-studio
```

### Run test suite
To add the tests' dependencies to your local install:

```bash
poetry install --with test
```

Alternatively, it is possible to run the unit tests from a Docker container in which the test dependencies are installed:


```bash
make build-testing-image
make docker-testing-shell
```

In either case, to run the unit tests:

```bash
cd label_studio

# sqlite3
DJANGO_DB=sqlite DJANGO_SETTINGS_MODULE=core.settings.label_studio pytest -vv

# postgres (assumes default postgres user,db,pass. Will not work in Docker
# testing container without additional configuration)
DJANGO_DB=default DJANGO_SETTINGS_MODULE=core.settings.label_studio pytest -vv
```
 
## What you get from Label Studio

https://github.com/user-attachments/assets/525ad5ff-6904-4398-b507-7e8954268d69

- **Multi-user labeling** sign up and login, when you create an annotation it's tied to your account.
- **Multiple projects** to work on all your datasets in one instance.
- **Streamlined design** helps you focus on your task, not how to use the software.
- **Configurable label formats** let you customize the visual interface to meet your specific labeling needs.
- **Support for multiple data types** including images, audio, text, HTML, time-series, and video. 
- **Import from files or from cloud storage** in Amazon AWS S3, Google Cloud Storage, or JSON, CSV, TSV, RAR, and ZIP archives. 
- **Integration with machine learning models** so that you can visualize and compare predictions from different models and perform pre-labeling.
- **Embed it in your data pipeline** REST API makes it easy to make it a part of your pipeline

## Included templates for labeling data in Label Studio 

Label Studio includes a variety of templates to help you label your data, or you can create your own using specifically designed configuration language. The most common templates and use cases for labeling include the following cases:

<img src="/images/template-types.png" />

## Set up machine learning models with Label Studio

Connect your favorite machine learning model using the Label Studio Machine Learning SDK. Follow these steps:

1. Start your own machine learning backend server. See [more detailed instructions](https://github.com/HumanSignal/label-studio-ml-backend).
2. Connect Label Studio to the server on the model page found in project settings.

This lets you:

- **Pre-label** your data using model predictions. 
- Do **online learning** and retrain your model while new annotations are being created. 
- Do **active learning** by labeling only the most complex examples in your data.

## Integrate Label Studio with your existing tools

You can use Label Studio as an independent part of your machine learning workflow or integrate the frontend or backend into your existing tools.  

## Ecosystem

| Project | Description |
|-|-|
| label-studio | Server, distributed as a pip package |
| [Frontend library](web/libs/editor/) | The Label Studio frontend library. This uses React to build the UI and mobx-state-tree for state management. |  
| [Data Manager library](web/libs/datamanager/) | A library for the Data Manager, our data exploration tool. | 
| [label-studio-converter](https://github.com/HumanSignal/label-studio-sdk/tree/master/src/label_studio_sdk/converter) | Encode labels in the format of your favorite machine learning library |
| [label-studio-transformers](https://github.com/HumanSignal/label-studio-transformers) | Transformers library connected and configured for use with Label Studio |

## Citation

Include a citation for Label Studio in the **References** section of your articles:

```tex
@misc{Label Studio,
  title={{Label Studio}: Data labeling software},
  url={https://github.com/HumanSignal/label-studio},
  note={Open source software available from https://github.com/HumanSignal/label-studio},
  author={
    Maxim Tkachenko and
    Mikhail Malyuk and
    Andrey Holmanyuk and
    Nikolai Liubimov},
  year={2020-2025},
}
```

## License

This software is licensed under the [Apache 2.0 LICENSE](/LICENSE) © [Heartex](https://www.heartex.com/). 2020-2025

<img src="https://user-images.githubusercontent.com/12534576/192582529-cf628f58-abc5-479b-a0d4-8a3542a4b35e.png" title="Hey everyone!" width="180" />

사용자별 마스크 저장을 분리합니다. 다른 사용자의 라벨을 수정하면 본인 소유의 사본으로 저장하며 원본은 유지합니다. 초안은 본인만 수정·삭제할 수 있고, 라벨 저장 시 다른 사용자의 초안을 삭제하지 않습니다. 변경·삭제 전 라벨과 초안은 `label_studio/data/mask-revisions/`에 별도 이력으로 보관합니다.

탭 생성과 선택은 Label Studio 기본 `+` 버튼과 탭 메뉴를 사용합니다. 다른 사용자의 원본 탭은 읽기 전용으로 표시합니다.
