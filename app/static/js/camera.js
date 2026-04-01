const CameraCapture = (() => {
  let stream = null;

  async function startCamera(videoEl) {
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      });
      videoEl.srcObject = stream;
      await videoEl.play();
      return { success: true };
    } catch (err) {
      return { error: "Camera access denied: " + err.message };
    }
  }

  function stopCamera(videoEl) {
    if (stream) {
      stream.getTracks().forEach(t => t.stop());
      stream = null;
    }
    if (videoEl) videoEl.srcObject = null;
  }

  function captureFrame(videoEl, canvasEl) {
    canvasEl.width  = videoEl.videoWidth  || 640;
    canvasEl.height = videoEl.videoHeight || 480;
    canvasEl.getContext("2d").drawImage(videoEl, 0, 0, canvasEl.width, canvasEl.height);
    return canvasEl.toDataURL("image/jpeg", 0.8);
  }

  async function analyzeFrame(videoEl, canvasEl) {
    const b64 = captureFrame(videoEl, canvasEl);

    // Show preview
    const preview = document.getElementById("camera-preview");
    const previewContainer = document.getElementById("camera-preview-container");
    if (preview) preview.src = b64;
    if (previewContainer) previewContainer.hidden = false;

    const resultsDiv = document.getElementById("results");
    if (resultsDiv) {
      resultsDiv.hidden = false;
      resultsDiv.innerHTML = `
        <div class="loading-spinner">
          <div class="spinner"></div>
          <p style="margin-top:0.75rem">Analyzing image...</p>
        </div>`;
    }

    try {
      const res = await fetch("/predict-image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: b64 }),
      });
      const data = await res.json();

      if (!res.ok || data.error) {
        if (resultsDiv) resultsDiv.innerHTML = `<div class="alert alert-danger">${data.error || "Analysis failed."}</div>`;
        const labelEl = document.getElementById("camera-label-text");
        if (labelEl) labelEl.textContent = "";
        return;
      }

      const labelEl = document.getElementById("camera-label-text");
      if (labelEl) labelEl.textContent = `Detected: ${data.image_label} (${data.image_confidence}% confidence)`;

      if (resultsDiv) renderResults(data, resultsDiv);
    } catch {
      if (resultsDiv) resultsDiv.innerHTML = `<div class="alert alert-danger">Network error. Please try again.</div>`;
    }
  }

  return { startCamera, stopCamera, captureFrame, analyzeFrame };
})();
