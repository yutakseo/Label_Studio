FROM heartexlabs/label-studio:1.23.1

COPY third-party/mask_cleanup /label-studio/label_studio/mask_cleanup
COPY third-party/gaussian_mask /label-studio/label_studio/gaussian_mask
RUN python /label-studio/label_studio/mask_cleanup/install.py
RUN python /label-studio/label_studio/mask_cleanup/patch_editor.py /label-studio/web/dist/apps/labelstudio/358.js
COPY patches/brush_coordinates.py /label-studio/patches/brush_coordinates.py
RUN python /label-studio/patches/brush_coordinates.py /label-studio/web/dist/apps/labelstudio/358.js

# Keep project data in the mounted data directory and allow importing files
# placed there when local file serving is enabled.
ENV LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true \
    LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=/label-studio/data

EXPOSE 8080

CMD ["label-studio", "start", "--host", "0.0.0.0", "--port", "8080"]
