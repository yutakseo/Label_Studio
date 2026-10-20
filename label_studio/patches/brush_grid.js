/* Paint square stamps on a tenth-of-an-image-pixel lattice. */
globalThis.__labelStudioSquareBrush = function(ctx, points, width, cellX = 0.1, cellY = cellX, originX = 0, originY = 0) {
  if (points.length < 2 || !(width > 0 && cellX > 0 && cellY > 0)) return;
  const cells = Math.max(1, Math.round(width / cellX));
  const stamp = (x, y) => {
    const left = Math.floor((x - originX) / cellX - cells / 2 + 1e-7);
    const top = Math.floor((y - originY) / cellY - cells / 2 + 1e-7);
    ctx.rect(originX + left * cellX, originY + top * cellY, cells * cellX, cells * cellY);
  };
  ctx.beginPath();
  stamp(points[0], points[1]);
  for (let i = 2; i < points.length; i += 2) {
    const x = points[i - 2], y = points[i - 1];
    const dx = points[i] - x, dy = points[i + 1] - y;
    const steps = Math.ceil(Math.max(Math.abs(dx) / cellX, Math.abs(dy) / cellY));
    for (let j = 1; j <= steps; j++) stamp(x + dx * j / steps, y + dy * j / steps);
  }
  ctx.fill();
};
