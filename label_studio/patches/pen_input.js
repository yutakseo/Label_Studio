/* Feed pen coordinates directly to the image editor; keep mouse input native. */
globalThis.__labelStudioPenInput = function(editor) {
  const container = editor.props.item.containerRef;
  let active = null, suppressUntil = 0;
  const options = {capture: true, passive: false};
  function validSample(event, stage) {
    if (!Number.isFinite(event.clientX) || !Number.isFinite(event.clientY)) return false;
    // A viewport-origin sample outside the canvas cannot be a pen position
    // on this editor. Keep genuine canvas-origin strokes when it is at 0,0.
    if (event.clientX === 0 && event.clientY === 0) {
      const bounds = stage.content.getBoundingClientRect();
      return bounds.left <= 0 && bounds.top <= 0 &&
        bounds.left + bounds.width > 0 && bounds.top + bounds.height > 0;
    }
    return true;
  }
  function wrapped(event, stage) {
    const bounds = stage.content.getBoundingClientRect();
    const scaleX = bounds.width / stage.content.clientWidth || 1;
    const scaleY = bounds.height / stage.content.clientHeight || 1;
    const evt = new MouseEvent('mousemove', {
      clientX: event.clientX, clientY: event.clientY,
      button: 0, buttons: active ? 1 : 0,
      ctrlKey: event.ctrlKey, shiftKey: event.shiftKey,
      altKey: event.altKey, metaKey: event.metaKey,
    });
    Object.defineProperties(evt, {
      target: {value: stage.content.querySelector("canvas") || stage.content},
      currentTarget: {value: stage.content},
      offsetX: {value: (event.clientX - bounds.left) / scaleX},
      offsetY: {value: (event.clientY - bounds.top) / scaleY},
      movementX: {value: active ? event.clientX - active.last.clientX : 0},
      movementY: {value: active ? event.clientY - active.last.clientY : 0},
    });
    stage.setPointersPositions(evt);
    return {evt, target: stage.getIntersection(stage.getPointerPosition()) || stage, currentTarget: stage};
  }
  function finish(event) {
    if (!active) return;
    const stroke = active;
    const input = wrapped(event || stroke.last, stroke.stage);
    active = null;
    suppressUntil = Date.now() + 400;
    editor.handleMouseUp(input);
    window.removeEventListener('mousemove', editor.handleGlobalMouseMove);
    window.removeEventListener('mouseup', editor.handleGlobalMouseUp);
  }
  function pointer(event) {
    if (event.pointerType !== 'pen') return;
    if (event.type === 'pointerdown') {
      const stage = editor.props.item.stageRef;
      if (active || event.button !== 0 || !stage || !stage.content.contains(event.target) || !validSample(event, stage)) return;
      active = {id: event.pointerId, stage, last: event};
    }
    if (!active || active.id !== event.pointerId) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    suppressUntil = Date.now() + 400;
    if (event.type === 'pointerup' || event.type === 'pointercancel') {
      // Cancellation coordinates are not a drawing sample (some drivers send 0,0).
      finish(event.type === 'pointercancel' || !validSample(event, active.stage) ? active.last : event);
      return;
    }
    if (event.type === 'pointermove' && !(event.buttons & 1)) {
      // A missed release must not connect the stroke to subsequent pen hover.
      finish(active.last);
      return;
    }
    if (!validSample(event, active.stage)) return;
    const input = wrapped(event, active.stage);
    active.last = event;
    if (event.type === 'pointerdown') editor.handleMouseDown(input);
    else editor.handleMouseMove(input);
  }
  function mouse(event) {
    // Global editor mouse listeners also receive events outside the container.
    // During a pen stroke they must never append a second set of coordinates.
    if (event.isTrusted && (active || (Date.now() < suppressUntil && container.contains(event.target)))) {
      event.preventDefault();
      event.stopImmediatePropagation();
    }
  }
  function contextmenu(event) {
    if (container.contains(event.target) &&
        (active || Date.now() < suppressUntil || event.pointerType === 'pen')) {
      event.preventDefault();
      event.stopImmediatePropagation();
    }
  }
  const blur = () => finish();
  for (const type of ['pointerdown', 'pointermove', 'pointerup', 'pointercancel']) window.addEventListener(type, pointer, options);
  for (const type of ['mousedown', 'mousemove', 'mouseup', 'click']) window.addEventListener(type, mouse, options);
  window.addEventListener('contextmenu', contextmenu, options);
  window.addEventListener('blur', blur);
  return () => {
    finish();
    for (const type of ['pointerdown', 'pointermove', 'pointerup', 'pointercancel']) window.removeEventListener(type, pointer, options);
    for (const type of ['mousedown', 'mousemove', 'mouseup', 'click']) window.removeEventListener(type, mouse, options);
    window.removeEventListener('contextmenu', contextmenu, options);
    window.removeEventListener('blur', blur);
  };
};
