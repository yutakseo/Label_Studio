FROM heartexlabs/label-studio:latest

# Keep project data in the mounted data directory and allow importing files
# placed there when local file serving is enabled.
ENV LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true \
    LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=/label-studio/data

EXPOSE 8080

CMD ["label-studio", "start", "--host", "0.0.0.0", "--port", "8080"]
