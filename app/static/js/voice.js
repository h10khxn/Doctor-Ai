const MicButton = (() => {
  let recognition = null;
  let isRecording = false;

  function isSupported() {
    return "webkitSpeechRecognition" in window || "SpeechRecognition" in window;
  }

  function init(targetInputId, buttonEl) {
    if (!isSupported()) {
      if (buttonEl) {
        buttonEl.disabled = true;
        buttonEl.title = "Voice input requires Chrome or Edge";
      }
      return;
    }

    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SR();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.continuous = false;

    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      const input = document.getElementById(targetInputId);
      if (input) {
        input.value = (input.value + " " + transcript).trim();
        input.dispatchEvent(new Event("input"));
      }
    };

    recognition.onend = () => {
      isRecording = false;
      if (buttonEl) {
        buttonEl.classList.remove("recording");
        buttonEl.setAttribute("aria-pressed", "false");
        buttonEl.title = "Click to speak";
      }
    };

    recognition.onerror = (e) => {
      console.warn("Speech error:", e.error);
      isRecording = false;
      if (buttonEl) {
        buttonEl.classList.remove("recording");
        buttonEl.setAttribute("aria-pressed", "false");
      }
    };

    if (buttonEl) {
      buttonEl.addEventListener("click", () => {
        if (!isRecording) {
          recognition.start();
          isRecording = true;
          buttonEl.classList.add("recording");
          buttonEl.setAttribute("aria-pressed", "true");
          buttonEl.title = "Listening... click to stop";
        } else {
          recognition.stop();
        }
      });
    }
  }

  return { init, isSupported };
})();
