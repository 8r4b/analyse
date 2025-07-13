const recordBtn = document.getElementById('recordBtn');
const stopBtn = document.getElementById('stopBtn');
const transcriptEl = document.getElementById('transcript');
const analysisEl = document.getElementById('analyses');

let mediaRecorder;
let audioChunks = [];

recordBtn.onclick = async () => {
    recordBtn.disabled = true;
    stopBtn.disabled = false;
    audioChunks = [];

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.webm');

        try {
            // Transcribe
            const transcribeRes = await fetch('http://localhost:8000/transcribe', {
                method: 'POST',
                body: formData
            });

            const transcribeData = await transcribeRes.json();
            const transcript = transcribeData.transcript || "No transcript returned";
            transcriptEl.innerText = transcript;

            // Analyze
            const analyzeRes = await fetch('http://localhost:8000/analyze', {
                method: 'POST',
                body: formData
            });

            const analysis = await analyzeRes.json();

            // Safe numeric conversions
            const sentimentScore = (typeof analysis.sentiment_score === 'number') ? analysis.sentiment_score.toFixed(2) : "N/A";
            const readabilityScore = (typeof analysis.readability_score === 'number') ? analysis.readability_score.toFixed(2) : "N/A";
            const confidenceScore = (typeof analysis.confidence_score === 'number') ? analysis.confidence_score.toFixed(0) : "N/A";
            const overallScore = (typeof analysis.overall_score === 'number') ? analysis.overall_score.toFixed(2) : "N/A";

            // Format result as a feedback letter
            const feedback = `
Dear Candidate,

Thank you for your introduction. Here's our evaluation:

➤ Transcript:
"${transcript}"

➤ Sentiment: ${analysis.sentiment || "N/A"} (${sentimentScore})
➤ Readability Score: ${readabilityScore}
➤ Confidence Score: ${confidenceScore}%
➤ Overall Score: ${overallScore} / 100

➤ Summary:
${analysis.summary || "N/A"}

${analysis.suggestions && analysis.suggestions.length > 0 ? "➤ Suggestions:\n- " + analysis.suggestions.join("\n- ") : ""}

Best regards,  
Mohamed Osama
            `.trim();

            analysisEl.innerText = feedback;

        } catch (error) {
            console.error('Error:', error);
            transcriptEl.innerText = 'Error during transcription or analysis.';
            analysisEl.innerText = '';
        }
    };

    mediaRecorder.start();
};

stopBtn.onclick = () => {
    recordBtn.disabled = false;
    stopBtn.disabled = true;
    mediaRecorder.stop();
};
