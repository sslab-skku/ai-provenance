FROM python:3.9.20

COPY . /visualizer
WORKDIR /visualizer

ENTRYPOINT ["python3", "visualizer.py"]
CMD ["-i", "/target/logfile"]
