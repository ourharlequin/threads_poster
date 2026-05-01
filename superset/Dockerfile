FROM apache/superset:4.1.1
USER root
RUN pip install --no-cache-dir "duckdb==1.2.1" "duckdb-engine==0.13.4"
COPY superset_config.py /app/pythonpath/superset_config.py
COPY setup_db.py /app/pythonpath/setup_db.py
COPY docker-init.sh /app/docker-init.sh
RUN chmod +x /app/docker-init.sh
USER superset
ENTRYPOINT ["/app/docker-init.sh"]
