/* Keep original author tabs read-only and edit in the signed-in user's tab. */
globalThis.__labelStudioCanEditAnnotation = function(store, annotation) {
  const userId = store.store?.user?.id;
  const ownerId = annotation.user?.id ?? annotation.completed_by?.id ?? annotation.completed_by;
  return userId != null && ownerId != null && String(userId) === String(ownerId);
};
