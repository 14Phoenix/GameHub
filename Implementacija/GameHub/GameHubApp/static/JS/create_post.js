// Author: Viktor Mitrovic 0296/2021

// Submit form for creating a new post using JavaScript
async function submitCreatePostForm(form) {
    const formData = new FormData(form);

    const response = await fetch(
        form.action, {
            method: "POST",
            body: formData,
            redirect: "follow"
        }
    );
    if (response.redirected) {
        window.location.href = response.url;
    } else {
        const data = await response.json();

        let previous_message = document.getElementById("crete_post_message");
        if (previous_message != null)
            previous_message.remove();

        let message = document.createElement("div");
        message.id = "crete_post_message";
        message.style.color = "red";
        message.innerHTML = data["message"];

        if (data["create_post_msg_type"] === "TITLE") {
            let pivot = document.getElementById("create_post_body_header");
            form.insertBefore(message, pivot);
        }

        if (data["create_post_msg_type"] === "BODY") {
            let pivot = document.getElementById("create_post_buttons");
            form.insertBefore(message, pivot);
        }
    }
}

// Create a new post
function createPostFormSetup() {
    document.getElementById("create_post_form").addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent the default form submission
        await submitCreatePostForm(this);
    });
}

// Cancel button
function cancelButtonSetup() {
    document.getElementById("create_post_cancel").addEventListener("click", function () {
        window.location.href = this.getAttribute("data-gamehub-forum-url");
    });
}

document.addEventListener("DOMContentLoaded", function () {
    createPostFormSetup();
    cancelButtonSetup();
});
