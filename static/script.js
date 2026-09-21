const university = document.getElementById("university");
const question = document.getElementById("question");
const messages = document.getElementById("messages");
const sendBtn = document.getElementById("sendBtn");
const uploadBtn = document.getElementById("uploadBtn");
const uniName = document.getElementById("uniName");
const uniMeta = document.getElementById("uniMeta");
const officialLink = document.getElementById("officialLink");
const statusText = document.getElementById("statusText");
const stateFilter = document.getElementById("stateFilter");

let universities = [];


function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}


function renderMarkdown(text) {

    if (!text) {
        return "";
    }

    let html = escapeHtml(text);

    html = html.replace(
        /```([\s\S]*?)```/g,
        '<pre class="code-block"><code>$1</code></pre>'
    );

    html = html.replace(
        /`([^`\n]+)`/g,
        "<code>$1</code>"
    );

    html = html.replace(
        /^\s*#{1,6}\s+(.+)$/gm,
        "<h4>$1</h4>"
    );

    html = html.replace(
        /\*\*\*(.+?)\*\*\*/g,
        "<strong><em>$1</em></strong>"
    );

    html = html.replace(
        /___(.+?)___/g,
        "<strong><em>$1</em></strong>"
    );

    html = html.replace(
        /\*\*(.+?)\*\*/g,
        "<strong>$1</strong>"
    );

    html = html.replace(
        /__(.+?)__/g,
        "<strong>$1</strong>"
    );

    html = html.replace(
        /(?<!\*)\*([^*\n]+)\*(?!\*)/g,
        "<em>$1</em>"
    );

    html = html.replace(
        /(?<!\w)_([^_\n]+)_(?!\w)/g,
        "<em>$1</em>"
    );

    html = html.replace(
        /^\s*[-•]\s+(.+)$/gm,
        "<li>$1</li>"
    );

    html = html.replace(
        /(?:<li>.*?<\/li>\s*)+/gs,
        match => `<ul>${match}</ul>`
    );

    html = html.replace(
        /^\s*\d+\.\s+(.+)$/gm,
        "<li>$1</li>"
    );

    html = html.replace(
        /\n{2,}/g,
        "</p><p>"
    );

    html = html.replace(
        /\n/g,
        "<br>"
    );

    if (
        !html.startsWith("<h4>") &&
        !html.startsWith("<ul>") &&
        !html.startsWith("<pre")
    ) {
        html = `<p>${html}</p>`;
    }

    return html;
}


async function getJsonResponse(response) {

    const contentType =
        response.headers.get("content-type") || "";

    if (
        contentType.includes("application/json")
    ) {
        return await response.json();
    }

    const text =
        await response.text();

    return {
        error:
            `Server returned HTTP ${response.status}. ` +
            `The server did not return JSON.`,
        details:
            text.substring(0, 500)
    };
}


function renderUniversities() {

    const selectedState =
        stateFilter
            ? stateFilter.value
            : "";

    const selectedUniversity =
        university.value;

    const filtered =
        selectedState
            ? universities.filter(
                u => u.state === selectedState
            )
            : universities;

    university.innerHTML =
        '<option value="">Select a university</option>';

    filtered.forEach(u => {

        const option =
            document.createElement("option");

        option.value =
            u.id;

        option.textContent =
            `${u.name} — ${u.city}`;

        university.appendChild(
            option
        );
    });

    if (
        filtered.some(
            u => u.id === selectedUniversity
        )
    ) {
        university.value =
            selectedUniversity;
    } else {
        updateUniversity();
    }
}


async function loadData() {

    try {

        const [
            universityResponse,
            statusResponse
        ] = await Promise.all([
            fetch("/api/universities"),
            fetch("/api/status")
        ]);

        const universityData =
            await getJsonResponse(
                universityResponse
            );

        const statusData =
            await getJsonResponse(
                statusResponse
            );

        if (
            universityData.error
        ) {
            throw new Error(
                universityData.error
            );
        }

        universities =
            universityData.universities || [];

        renderUniversities();

        if (
            statusData.mongodb
        ) {

            statusText.textContent =
                `${statusData.indexed_count || 0} university indexes ready`;

        } else {

            statusText.textContent =
                "AI online • MongoDB offline";
        }

    } catch (error) {

        console.error(
            "Loading error:",
            error
        );

        statusText.textContent =
            "Backend connection error";
    }
}


function updateUniversity() {

    const selected =
        universities.find(
            u => u.id === university.value
        );

    if (!selected) {

        uniName.textContent =
            "Select a university";

        uniMeta.textContent =
            "AP + Telangana university knowledge base";

        officialLink.href =
            "#";

        return;
    }

    uniName.textContent =
        selected.name;

    uniMeta.textContent =
        `${selected.state} • ${selected.type} • ${selected.city}`;

    officialLink.href =
        selected.official_url || "#";
}


function addMessage(
    text,
    type
) {

    const row =
        document.createElement("div");

    row.className =
        `message ${type}`;

    const bubble =
        document.createElement("div");

    bubble.className =
        "bubble";

    if (
        type === "bot"
    ) {

        bubble.innerHTML =
            renderMarkdown(text);

    } else {

        bubble.textContent =
            text;
    }

    row.appendChild(
        bubble
    );

    messages.appendChild(
        row
    );

    messages.scrollTop =
        messages.scrollHeight;
}


function addSources(
    sources
) {

    if (
        !sources ||
        !sources.length
    ) {
        return;
    }

    const box =
        document.createElement("div");

    box.className =
        "sources";

    const title =
        document.createElement("div");

    title.className =
        "sources-title";

    title.textContent =
        "RETRIEVED SOURCE DOCUMENTS";

    box.appendChild(
        title
    );

    sources.forEach(
        source => {

            const row =
                document.createElement("div");

            row.className =
                "source-row";

            const icon =
                document.createElement("span");

            icon.textContent =
                "📄 ";

            row.appendChild(
                icon
            );

            const name =
                document.createElement("span");

            const page =
                source.page
                    ? ` • page ${source.page}`
                    : "";

            name.textContent =
                `${source.title}${page}`;

            row.appendChild(
                name
            );

            if (
                source.source_url
            ) {

                const link =
                    document.createElement("a");

                link.href =
                    source.source_url;

                link.target =
                    "_blank";

                link.rel =
                    "noopener noreferrer";

                link.textContent =
                    " official site ↗";

                row.appendChild(
                    link
                );
            }

            box.appendChild(
                row
            );
        }
    );

    messages.appendChild(
        box
    );

    messages.scrollTop =
        messages.scrollHeight;
}


async function ask() {

    if (
        !university.value
    ) {

        addMessage(
            "Please select a university first.",
            "bot"
        );

        return;
    }

    const q =
        question.value.trim();

    if (!q) {
        return;
    }

    addMessage(
        q,
        "user"
    );

    question.value =
        "";

    sendBtn.disabled =
        true;

    sendBtn.textContent =
        "Thinking...";

    sendBtn.classList.add(
        "thinking"
    );

    try {

        const response =
            await fetch(
                "/api/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            university:
                                university.value,

                            question:
                                q
                        })
                }
            );

        const data =
            await getJsonResponse(
                response
            );

        if (
            !response.ok
        ) {

            let errorMessage =
                data.error ||
                "Request failed";

            if (
                data.details
            ) {

                errorMessage +=
                    `\n\nDetails:\n${data.details}`;
            }

            throw new Error(
                errorMessage
            );
        }

        addMessage(
            data.answer ||
            "No answer was returned.",
            "bot"
        );

        addSources(
            data.sources
        );

    } catch (error) {

        console.error(
            "Chat error:",
            error
        );

        addMessage(
            error.message ||
            "Something went wrong. Check the Flask terminal.",
            "bot"
        );

    } finally {

        sendBtn.disabled =
            false;

        sendBtn.textContent =
            "Send";

        sendBtn.classList.remove(
            "thinking"
        );
    }
}


async function upload() {

    if (
        !university.value
    ) {

        alert(
            "Select a university first."
        );

        return;
    }

    const fileInput =
        document.getElementById(
            "file"
        );

    const file =
        fileInput.files[0];

    const uploadStatus =
        document.getElementById(
            "uploadStatus"
        );

    if (!file) {

        uploadStatus.textContent =
            "Choose a document first.";

        return;
    }

    const form =
        new FormData();

    form.append(
        "university",
        university.value
    );

    form.append(
        "file",
        file
    );

    uploadBtn.disabled =
        true;

    uploadBtn.textContent =
        "Indexing...";

    uploadStatus.textContent =
        "Extracting text and creating embeddings...";

    try {

        const response =
            await fetch(
                "/api/upload",
                {
                    method: "POST",
                    body: form
                }
            );

        const data =
            await getJsonResponse(
                response
            );

        if (
            !response.ok
        ) {

            let errorMessage =
                data.error ||
                "Upload failed";

            if (
                data.details
            ) {

                errorMessage +=
                    `\n${data.details}`;
            }

            throw new Error(
                errorMessage
            );
        }

        uploadStatus.textContent =
            data.message ||
            "Document indexed successfully.";

        await loadData();

    } catch (error) {

        console.error(
            "Upload error:",
            error
        );

        uploadStatus.textContent =
            error.message ||
            "Upload failed.";

    } finally {

        uploadBtn.disabled =
            false;

        uploadBtn.textContent =
            "Upload & index";
    }
}


university.addEventListener(
    "change",
    updateUniversity
);


if (
    stateFilter
) {

    stateFilter.addEventListener(
        "change",
        renderUniversities
    );
}


sendBtn.addEventListener(
    "click",
    ask
);


uploadBtn.addEventListener(
    "click",
    upload
);


document
    .querySelectorAll(
        ".suggestions button"
    )
    .forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    question.value =
                        button.dataset.q;

                    question.focus();
                }
            );
        }
    );


question.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            ask();
        }
    }
);


loadData();