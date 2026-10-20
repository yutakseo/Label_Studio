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
COPY patches/brush_size.py /label-studio/patches/brush_size.py
RUN python /label-studio/patches/brush_size.py /label-studio/web/dist/apps/labelstudio/358.js
COPY patches/brush_grid.py patches/brush_grid.js /label-studio/patches/
RUN python /label-studio/patches/brush_grid.py /label-studio/web/dist/apps/labelstudio/358.js
COPY patches/pen_input.py patches/pen_input.js /label-studio/patches/
RUN python /label-studio/patches/pen_input.py /label-studio/web/dist/apps/labelstudio/358.js
COPY patches/annotation_author.py /label-studio/patches/annotation_author.py
RUN python /label-studio/patches/annotation_author.py /label-studio/web/dist/apps/labelstudio/358.js
COPY patches/user_tabs.py patches/user_tabs.js /label-studio/patches/
RUN python /label-studio/patches/user_tabs.py /label-studio/web/dist/apps/labelstudio/358.js
COPY patches/annotated_by.py /label-studio/patches/annotated_by.py
RUN python /label-studio/patches/annotated_by.py /label-studio/label_studio/data_manager/managers.py
COPY patches/annotation_ownership.py /label-studio/patches/annotation_ownership.py
RUN python /label-studio/patches/annotation_ownership.py /label-studio/label_studio/tasks/api.py
COPY patches/tree_export_compat.py /label-studio/patches/tree_export_compat.py
RUN python /label-studio/patches/tree_export_compat.py /label-studio/label_studio/mask_cleanup/tree_export
COPY draft_preview /label-studio/label_studio/draft_preview
RUN python /label-studio/label_studio/draft_preview/install.py
COPY patches/user_isolation.py /label-studio/patches/user_isolation.py
RUN python /label-studio/patches/user_isolation.py /label-studio/label_studio

# Keep project data in the mounted data directory and allow importing files
# placed there when local file serving is enabled.
ENV LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true \
    LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=/label-studio/data

EXPOSE 8080

CMD ["label-studio", "start", "--host", "0.0.0.0", "--port", "8080"]
