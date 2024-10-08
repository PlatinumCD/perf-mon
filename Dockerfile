FROM waggle/plugin-base:1.1.1-base

COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r /app/requirements.txt

COPY app.py /app/
COPY monitor_units /app/monitor_units

WORKDIR /app
ENTRYPOINT ["python3", "/app/app.py"]
