FROM heartexlabs/label-studio:1.23.1 AS upstream

# CUDA's NVIDIA driver libraries require glibc; upstream may be Alpine/musl.
FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir label-studio==1.23.1
COPY --from=upstream /label-studio/label_studio /label-studio/label_studio
COPY --from=upstream /label-studio/web /label-studio/web
WORKDIR /label-studio
RUN rm -f /label-studio/label_studio/sitecustomize.py
ENV PYTHONPATH=/label-studio:/label-studio/label_studio \
    LABEL_STUDIO_BASE_DATA_DIR=/label-studio/data

COPY third-party/mask_cleanup /label-studio/label_studio/mask_cleanup
COPY third-party/gaussian_mask /label-studio/label_studio/gaussian_mask
COPY third-party/u_net_labeller /label-studio/label_studio/u_net_labeller
RUN pip install --no-cache-dir torch==2.7.1 --index-url https://download.pytorch.org/whl/cu126
RUN python /label-studio/label_studio/u_net_labeller/install.py
RUN python /label-studio/label_studio/mask_cleanup/install.py
RUN python /label-studio/label_studio/mask_cleanup/patch_editor.py /label-studio/web/dist/apps/labelstudio/358.js
COPY patches/brush_coordinates.py /label-studio/patches/brush_coordinates.py
RUN python /label-studio/patches/brush_coordinates.py /label-studio/web/dist/apps/labelstudio/358.js
COPY draft_preview /label-studio/label_studio/draft_preview
RUN python /label-studio/label_studio/draft_preview/install.py

# Keep project data in the mounted data directory and allow importing files
# placed there when local file serving is enabled.
ENV LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true \
    LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=/label-studio/data

EXPOSE 8080

CMD ["label-studio", "start", "--host", "0.0.0.0", "--port", "8080"]
