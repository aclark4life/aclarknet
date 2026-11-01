// Via ChatGPT
function createSparkline(canvas) {
  // Get the dataset and labels from data attributes
  var dataset = JSON.parse(canvas.getAttribute("data-dataset"));
  var labels = JSON.parse(canvas.getAttribute("data-labels"));
  var values = dataset[0];
  if (values.length < 2) {
    return;
  }

  // Get the width, height, and color from style attribute
  var width = parseInt(canvas.style.width, 10);
  var height = parseInt(canvas.style.height, 10);
  var color = canvas.style.color;

  // Get the 2d rendering context of the canvas
  var ctx = canvas.getContext("2d");

  // Calculate the scale for x and y axes; a flat line sits mid-height
  var min = Math.min(...values);
  var range = Math.max(...values) - min;
  var scaleX = width / (labels.length - 1);
  var y = function (value) {
    return range === 0 ? height / 2 : height - (value - min) * (height / range);
  };

  // Draw the sparkline
  ctx.beginPath();
  ctx.moveTo(0, y(values[0]));
  for (var i = 1; i < labels.length; i++) {
    ctx.lineTo(i * scaleX, y(values[i]));
  }
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.stroke();
}

document.querySelectorAll('canvas[data-chart="spark-line"]').forEach(function (canvas) {
  try {
    createSparkline(canvas);
  } catch (error) {
    console.log(error);
  }
});
