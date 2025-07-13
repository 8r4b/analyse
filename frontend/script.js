const recordBtn = document.getElementById('recordBtn');  // The button to start recording
const stopBtn = document.getElementById('stopBtn');      // The button to stop recording
const transcriptEl = document.getElementById('transcript');  // Element to display the transcript text
const analysisEl = document.getElementById('analyses');      // Element to display analysis results

let mediaRecorder;     // This will hold the MediaRecorder instance
let audioChunks = [];  // This array will store audio data chunks as they come in


recordBtn.onclick = async () => {
    // Disable Record button and enable Stop button
    recordBtn.disabled = true;
    stopBtn.disabled = false;

    // Clear any previous audio chunks
    audioChunks = [];

    // Ask for microphone access and get the audio stream
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    // Create a new MediaRecorder using the audio stream
    mediaRecorder = new MediaRecorder(stream);

    // When there is audio data available, push it into audioChunks
    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };

    // Define what happens when recording stops
    mediaRecorder.onstop = async () => {
        // Combine all audio chunks into a single audio Blob
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });

        // Create a FormData object and append the audio file to it
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.webm');

        try {
            // Send audio to the server to get a transcript
            const transcribeRes = await fetch('http://localhost:8000/transcribe', {
                method: 'POST',
                body: formData
            });

            // Parse the JSON response
            const transcribeData = await transcribeRes.json();

            // Extract transcript text or fallback message
            const transcript = transcribeData.transcript || "No transcript returned";

            // Display transcript on the page
            transcriptEl.innerText = transcript;

            // Send the same audio to the server for analysis
            const analyzeRes = await fetch('http://localhost:8000/analyze', {
                method: 'POST',
                body: formData
            });

            // Parse analysis JSON response
            const analysis = await analyzeRes.json();

            // Safely convert numeric values or fallback to "N/A"
            const sentimentScore = (typeof analysis.sentiment_score === 'number') ? analysis.sentiment_score.toFixed(2) : "N/A";
            const readabilityScore = (typeof analysis.readability_score === 'number') ? analysis.readability_score.toFixed(2) : "N/A";
            const confidenceScore = (typeof analysis.confidence_score === 'number') ? analysis.confidence_score.toFixed(0) : "N/A";
            const overallScore = (typeof analysis.overall_score === 'number') ? analysis.overall_score.toFixed(2) : "N/A";

            // Create a formatted feedback message using template literals
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

            // Display feedback on the page
            analysisEl.innerText = feedback;

        } catch (error) {
            // Handle errors gracefully by showing a message and logging the error
            console.error('Error:', error);
            transcriptEl.innerText = 'Error during transcription or analysis.';
            analysisEl.innerText = '';
        }
    };

    // Start recording audio
    mediaRecorder.start();
};

stopBtn.onclick = () => {
    // Re-enable the record button and disable the stop button
    recordBtn.disabled = false;
    stopBtn.disabled = true;

    // Stop the mediaRecorder — triggers the onstop event defined earlier
    mediaRecorder.stop();
};
