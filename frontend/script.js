document.addEventListener('DOMContentLoaded', () => {
    const videoForm = document.getElementById('videoForm');
    const statusContainer = document.getElementById('status');
    const resultContainer = document.getElementById('result');
    const videoPlayer = document.getElementById('videoPlayer');
    const downloadBtn = document.getElementById('downloadBtn');
    const newVideoBtn = document.getElementById('newVideoBtn');
    const progressBar = document.querySelector('.progress');

    // API endpoints
    const API_BASE_URL = 'http://localhost:5000/api';
    const CONTENT_ENDPOINT = `${API_BASE_URL}/content/generate`;
    const VIDEO_ENDPOINT = `${API_BASE_URL}/video/generate`;

    // Check API health
    async function checkAPIHealth() {
        try {
            const response = await fetch('http://localhost:5000/health');
            if (!response.ok) {
                throw new Error('API is not responding');
            }
            const data = await response.json();
            console.log('API is healthy:', data);
        } catch (error) {
            console.error('API health check failed:', error);
            alert('Cannot connect to the backend server. Please make sure it is running on port 5000.');
        }
    }

    // Call health check on page load
    checkAPIHealth();

    // Handle form submission
    videoForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Get form data
        const formData = {
            topic: document.getElementById('topic').value,
            duration: parseInt(document.getElementById('duration').value),
            detailLevel: document.querySelector('input[name="detailLevel"]:checked').value
        };

        // Show status container and hide result
        statusContainer.classList.remove('hidden');
        resultContainer.classList.add('hidden');
        videoForm.classList.add('hidden');

        try {
            // Generate content
            progressBar.style.width = '30%';
            console.log('Sending content generation request...');
            const contentResponse = await fetch(CONTENT_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!contentResponse.ok) {
                const errorData = await contentResponse.json();
                throw new Error(errorData.error || 'Failed to generate content');
            }

            const contentData = await contentResponse.json();
            console.log('Content generated successfully:', contentData);

            // Generate video
            progressBar.style.width = '60%';
            console.log('Sending video generation request...');
            const videoResponse = await fetch(VIDEO_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    content: contentData.content,
                    presentation_path: contentData.presentation_path
                })
            });

            if (!videoResponse.ok) {
                const errorData = await videoResponse.json();
                throw new Error(errorData.error || 'Failed to generate video');
            }

            const videoData = await videoResponse.json();
            console.log('Video generated successfully:', videoData);

            // Show result
            progressBar.style.width = '100%';
            setTimeout(() => {
                statusContainer.classList.add('hidden');
                resultContainer.classList.remove('hidden');
                
                // Set video source
                const videoUrl = `${API_BASE_URL}/video/download/${videoData.video_path}`;
                videoPlayer.src = videoUrl;
                
                // Set up download button
                downloadBtn.onclick = () => {
                    window.location.href = videoUrl;
                };
            }, 1000);

        } catch (error) {
            console.error('Error:', error);
            alert(`Error: ${error.message}`);
            resetUI();
        }
    });

    // Handle new video button
    newVideoBtn.addEventListener('click', () => {
        resetUI();
    });

    // Reset UI to initial state
    function resetUI() {
        videoForm.classList.remove('hidden');
        statusContainer.classList.add('hidden');
        resultContainer.classList.add('hidden');
        progressBar.style.width = '0%';
        videoForm.reset();
        videoPlayer.src = '';
    }
}); 