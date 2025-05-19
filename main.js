// This file contains the JavaScript code for the website. 

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('topic-input');
    const searchButton = document.getElementById('search-button');
    const papersList = document.getElementById('papers-list');
    const gapsList = document.getElementById('gaps-list');

    async function callGradio(input1, input2) {
        const response = await fetch("http://127.0.0.1:7860/api/predict/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                data: [input1, input2]
            })
        });
        const result = await response.json();
        return result.data;
    }

    async function callGradio5(topic, task) {
        // 1. Push job to queue
        const session_hash = Math.random().toString(36).substring(2, 15); // random session
        const pushResponse = await fetch("http://127.0.0.1:7860/queue/push/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                data: [topic, task],
                fn_index: 0,
                session_hash
            })
        });
        const pushResult = await pushResponse.json();
        const { hash } = pushResult;

        // 2. Poll for result
        while (true) {
            await new Promise(res => setTimeout(res, 1000)); // wait 1s
            const dataResponse = await fetch(`http://127.0.0.1:7860/queue/data?session_hash=${session_hash}`);
            const dataResult = await dataResponse.json();
            if (dataResult.status === "COMPLETE" && dataResult.data) {
                return dataResult.data[0]; // result string
            }
            if (dataResult.status === "FAILED") {
                throw new Error("Gradio job failed");
            }
        }
    }

    searchButton.addEventListener('click', async () => {
        const topic = searchInput.value.trim();
        if (topic) {
            papersList.innerHTML = "<li>Loading top papers...</li>";
            gapsList.innerHTML = "<li>Loading research gaps...</li>";

            try {
                const papersOutput = await callGradio5(topic, "Find Top Research Papers");
                const gapsOutput = await callGradio5(topic, "Find Research Gaps and Ideas");

                papersList.innerHTML = papersOutput
                    .split('\n')
                    .filter(line => line.trim())
                    .map(line => `<li>${line}</li>`)
                    .join('');
                gapsList.innerHTML = gapsOutput
                    .split('\n')
                    .filter(line => line.trim())
                    .map(line => `<li>${line}</li>`)
                    .join('');
            } catch (error) {
                console.error("Error fetching from Gradio:", error);
                papersList.innerHTML = "<li>Failed to load papers.</li>";
                gapsList.innerHTML = "<li>Failed to load research gaps.</li>";
            }
        } else {
            alert('Please enter a search topic.');
        }
    });
});

