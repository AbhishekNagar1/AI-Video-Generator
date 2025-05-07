document.getElementById("generateBtn").addEventListener("click", async function() {
    const topic = document.getElementById("topic").value;
    const duration = parseInt(document.getElementById("duration").value);
    const level = document.getElementById("level").value;

    const response = await fetch("/generate_video/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ topic, duration, level })
    });

    if (response.ok) {
        const data = await response.json();
        document.getElementById("videoResult").innerHTML = `
            <p>${data.message}</p>
            <video controls>
                <source src="${data.video_url}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        `;
    } else {
        const error = await response.json();
        alert("Error: " + error.detail);
    }
});
