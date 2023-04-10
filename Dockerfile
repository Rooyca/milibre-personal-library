FROM python:3.9

WORKDIR /code/app

COPY ./requirements.txt /code/requirements.txt

RUN pip install --upgrade pip \
	pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./ /code/app

ENTRYPOINT ["python", "milibre.py"]

