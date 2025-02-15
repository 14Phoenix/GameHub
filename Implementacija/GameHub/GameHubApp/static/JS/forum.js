// Author: Viktor Mitrovic 0296/2021

// Submit forms for adding and removing moderators using JavaScript
async function submitForm(form, response_message_id, insert_node_pivot) {
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

        let previous_message = document.getElementById(response_message_id);
        if (previous_message != null) {
            previous_message.remove();
        }

        if (data["message"] != null && data["status"] != null) {
            let message = document.createElement("div");
            message.id = response_message_id;
            message.innerHTML = data["message"];
            if (data["status"] === 0) {
                message.style.color = "red";
            }
            let buttons = document.getElementById(insert_node_pivot);
            form.insertBefore(message, buttons);
        }
    }
}

// Add and remove moderators
function moderatorSubmitFormsSetup() {
    let add_moderator_form = document.getElementById('form_add_moderator');
    let remove_moderator_form = document.getElementById('form_remove_moderator');

    if (add_moderator_form == null || remove_moderator_form == null) return;

    add_moderator_form.addEventListener('submit', async function (event) {
        event.preventDefault(); // Prevent the default form submission
        await submitForm(this, "add_moderator_message", "add_moderator_buttons");
    });

    remove_moderator_form.addEventListener('submit', async function (event) {
        event.preventDefault(); // Prevent the default form submission
        await submitForm(this, "remove_moderator_message", "remove_moderator_buttons");
    });
}

// Clear popup's form
function popupClearForm(input_id, response_message_id) {
    document.getElementById(input_id).value = "";
    let previous_message = document.getElementById(response_message_id);
    if (previous_message != null) {
        previous_message.remove();
    }
}

// Set up event listeners for buttons that clear popup forms
function popupClearFormSetup() {
    let close_x_add_moderator_button = document.getElementById("close_x_add_moderator_button");
    let close_cancel_add_moderator_button = document.getElementById("close_cancel_add_moderator_button");
    let close_x_remove_moderator_button = document.getElementById("close_x_remove_moderator_button");
    let close_cancel_remove_moderator_button = document.getElementById("close_cancel_remove_moderator_button");

    if (close_x_add_moderator_button == null ||
        close_cancel_add_moderator_button == null ||
        close_x_remove_moderator_button == null ||
        close_cancel_remove_moderator_button == null) return;

    close_x_add_moderator_button.addEventListener("click", function () {
        popupClearForm("add_moderator_username_input", "add_moderator_message");
    });
    close_cancel_add_moderator_button.addEventListener("click", function () {
        popupClearForm("add_moderator_username_input", "add_moderator_message");
    });
    close_x_remove_moderator_button.addEventListener("click", function () {
        popupClearForm("remove_moderator_username_input", "remove_moderator_message");
    });
    close_cancel_remove_moderator_button.addEventListener("click", function () {
        popupClearForm("remove_moderator_username_input", "remove_moderator_message");
    });
}

// Get the value of a cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Create post button
function createPostButtonSetup() {
    document.getElementById("create_post_button").addEventListener("click", function () {
        window.location.href = this.getAttribute("data-gamehub-create-post");
    });
}

// Follow/Unfollow button
function followUnfollowRequestSetup() {
    document.getElementById("follow_button").addEventListener("click", async function () {
        let follow_url = this.getAttribute("data-gamehub-follow-url");
        const csrftoken = getCookie("csrftoken");

        const response = await fetch(
            follow_url, {
                method: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                mode: 'same-origin',
                redirect: "follow",
            }
        );

        if (response.redirected) {
            window.location.href = response.url;
        } else {
            const data = await response.json();

            if (data["follow_status"] === "UNFOLLOWED") {
                this.setAttribute("class", "follow-forum-button");
                this.innerHTML = "Follow";
            } else if (data["follow_status"] === "FOLLOWED") {
                this.setAttribute("class", "unfollow-forum-button");
                this.innerHTML = "Unfollow";
            }
        }
    });
}

// Assign URLs for blog posts
function postsURLsSetup() {
    let posts = document.querySelectorAll("[data-gamehub-post-url]");

    posts.forEach(post => {
        post.addEventListener("click", function () {
            window.location.href = this.getAttribute("data-gamehub-post-url");
        });
    });
}

// Like/Remove Like buttons
function likePostRequestSetup() {
    let like_buttons = document.querySelectorAll("[data-gamehub-like-button]");

    like_buttons.forEach(like_button => {
        like_button.addEventListener("click", async function (event) {
            event.stopPropagation(); // Prevent the click event from bubbling up to parent elements

            let like_url = this.getAttribute("data-gamehub-like-button");
            const csrftoken = getCookie("csrftoken");

            const response = await fetch(
                like_url, {
                    method: "POST",
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    mode: 'same-origin',
                    redirect: "follow",
                }
            );

            if (response.redirected) {
                window.location.href = response.url;
            } else {
                const data = await response.json();

                let like_svg = Array.from(this.childNodes).filter(node => {
                    return node.nodeType === Node.ELEMENT_NODE && node.tagName.toLowerCase() === 'svg';
                })[0];

                let like_svg_g = Array.from(like_svg.childNodes).filter(node => {
                    return node.nodeType === Node.ELEMENT_NODE && node.tagName.toLowerCase() === 'g';
                })[2];

                let like_svg_g_path = Array.from(like_svg_g.childNodes).filter(node => {
                    return node.nodeType === Node.ELEMENT_NODE && node.tagName.toLowerCase() === 'path';
                });

                if (data["like_status"] === "LIKE_REMOVED") {
                    // Display like button
                    like_svg.setAttribute("class", "like-icon");
                    like_svg_g_path.forEach(path_node => {
                        path_node.setAttribute("stroke", "white");
                    });

                } else if (data["like_status"] === "LIKE_ADDED") {
                    // Display liked button
                    like_svg.setAttribute("class", "liked-icon");
                    like_svg_g_path.forEach(path_node => {
                        path_node.setAttribute("stroke", "transparent");
                    });
                }
            }
        });
    });
}

// Delete post buttons
function deletePostRequestSetup() {
    let delete_buttons = document.querySelectorAll("[data-gamehub-delete-post-button]");

    delete_buttons.forEach(delete_button => {
        delete_button.addEventListener("click", async function (event) {
            event.stopPropagation(); // Prevent the click event from bubbling up to parent elements

            let delete_url = this.getAttribute("data-gamehub-delete-post-button");
            const csrftoken = getCookie("csrftoken");

            const response = await fetch(
                delete_url, {
                    method: "POST",
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    mode: 'same-origin',
                    redirect: "follow",
                }
            );

            if (response.redirected) {
                window.location.href = response.url;
            } else {
                const data = await response.json();

                if (data["delete_status"] === 'DELETE_SUCCESS') {
                    this.parentNode.remove();
                }
            }
        });
    });
}

document.addEventListener("DOMContentLoaded", function () {
    moderatorSubmitFormsSetup();
    popupClearFormSetup();
    createPostButtonSetup();
    followUnfollowRequestSetup();
    postsURLsSetup();
    likePostRequestSetup();
    deletePostRequestSetup();
});
