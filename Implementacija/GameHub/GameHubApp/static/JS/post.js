// Author: Viktor Mitrovic 0296/2021

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

// Like/Remove Like button
function likeSinglePostRequestSetup() {
    document.getElementById("single_post_like_button").addEventListener("click", async function () {
        let like_url = this.getAttribute("data-gamehub-single-post-like-button");
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
                like_svg.setAttribute("class", "single-post-like-icon");
                like_svg_g_path.forEach(path_node => {
                    path_node.setAttribute("stroke", "white");
                });

            } else if (data["like_status"] === "LIKE_ADDED") {
                // Display liked button
                like_svg.setAttribute("class", "single-post-liked-icon");
                like_svg_g_path.forEach(path_node => {
                    path_node.setAttribute("stroke", "transparent");
                });
            }
        }
    });
}

// Delete post button
function deleteSinglePostRequestSetup() {
    let delete_button = document.getElementById("single_post_delete_button");

    if (delete_button != null) {
        delete_button.addEventListener("click", async function () {
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
                    window.location.href = this.getAttribute("data-gamehub-forum-url");
                }
            }
        });
    }
}

// Leave a comment button
function leaveCommentButtonSetup() {
    document.getElementById("leave_a_comment_button").addEventListener("click", function () {
        if (this.getAttribute("data-gamehub-signed-in") === "False") {
            window.location.href = this.getAttribute("data-gamehub-sign-in-url");
        } else {
            this.parentNode.style.display = "none";
            document.getElementById("leave_a_comment_carrier").style.display = "block";
        }
    });
}

// Leave a comment cancel button
function cancelLeaveCommentButtonSetup() {
    document.getElementById("cancel_leave_a_comment").addEventListener("click", function () {
        document.getElementById("leave_a_comment_wrapper").style.display = "block";
        document.getElementById("leave_a_comment_carrier").style.display = "none";
    });
}

// Like comment
async function likeComment(like_button) {
    let like_url = like_button.getAttribute("data-gamehub-comment-like-button");
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

        let like_svg = Array.from(like_button.childNodes).filter(node => {
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
}

// Like/Remove Like buttons
function likeCommentRequestSetup() {
    let like_buttons = document.querySelectorAll("[data-gamehub-comment-like-button]");

    like_buttons.forEach(like_button => {
        like_button.addEventListener("click", function () {
            likeComment(this);
        });
    });
}

// Delete comment
async function deleteComment(delete_button) {
    let delete_url = delete_button.getAttribute("data-gamehub-delete-comment-button");
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

        if (data["delete_status"] === "DELETE_SUCCESS") {
            delete_button.parentNode.remove();
        }
    }
}

// Delete comment buttons
function deleteCommentRequestSetup() {
    let delete_buttons = document.querySelectorAll("[data-gamehub-delete-comment-button]");

    delete_buttons.forEach(delete_button => {
        delete_button.addEventListener("click", function () {
            deleteComment(this);
        });
    });
}

// Renders the comment and returns a node
function renderComment(comment_info) {
    let comment = document.createElement("div");
    comment.classList.add("comment");

    let username_link = document.createElement("a");
    username_link.classList.add("comment-username");
    username_link.href = comment_info["username_url"];
    username_link.innerHTML = comment_info["username"];
    comment.appendChild(username_link);

    let comment_body = document.createElement("p");
    comment_body.classList.add("comment-body");
    comment_body.innerHTML = comment_info["body"];
    comment.appendChild(comment_body);

    let comment_like_button = document.createElement("button");
    comment_like_button.classList.add("single-post-like-button");
    comment_like_button.setAttribute("data-gamehub-comment-like-button", comment_info["like_url"]);
    comment_like_button.addEventListener("click", function () {
        likeComment(this);
    });
    comment.appendChild(comment_like_button);

    let comment_like_icon_class = "";
    let comment_like_icon_path_color = "";
    if (comment_info["comment_liked"]) {
        comment_like_icon_class = "single-post-liked-icon";
        comment_like_icon_path_color = "transparent";
    } else {
        comment_like_icon_class = "single-post-like-icon";
        comment_like_icon_path_color = "white";
    }

    comment_like_button.innerHTML = `<svg class="${comment_like_icon_class}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">` +
                                        `<g stroke-width="0"></g>` +
                                        `<g stroke-linecap="round" stroke-linejoin="round"></g>` +
                                        `<g>` +
                                            `<path d="M7.47998 18.35L10.58 20.75C10.98 21.15 11.88 21.35 12.48 21.35H16.28C17.48 21.35 18.78 20.45 19.08 19.25L21.48 11.95C21.98 10.55 21.08 9.34997 19.58 9.34997H15.58C14.98 9.34997 14.48 8.84997 14.58 8.14997L15.08 4.94997C15.28 4.04997 14.68 3.04997 13.78 2.74997C12.98 2.44997 11.98 2.84997 11.58 3.44997L7.47998 9.54997" stroke="${comment_like_icon_path_color}" stroke-width="1.5" stroke-miterlimit="10"></path>` +
                                            `<path d="M2.38 18.35V8.55002C2.38 7.15002 2.98 6.65002 4.38 6.65002H5.38C6.78 6.65002 7.38 7.15002 7.38 8.55002V18.35C7.38 19.75 6.78 20.25 5.38 20.25H4.38C2.98 20.25 2.38 19.75 2.38 18.35Z" stroke="${comment_like_icon_path_color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path>` +
                                        `</g>` +
                                    `</svg>`;

    if (comment_info["comment_owner"]) {
        let comment_delete_button = document.createElement("button");
        comment_delete_button.classList.add("single-post-delete-button");
        comment_delete_button.setAttribute("data-gamehub-delete-comment-button", comment_info["delete_url"]);
        comment_delete_button.addEventListener("click", function () {
            deleteComment(this);
        });

        comment_delete_button.innerHTML = `<svg class="single-post-delete-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">` +
                                               `<g stroke-width="0"></g>` +
                                               `<g stroke-linecap="round" stroke-linejoin="round"></g>` +
                                               `<g>` +
                                                   `<path d="M21 5.97998C17.67 5.64998 14.32 5.47998 10.98 5.47998C9 5.47998 7.02 5.57998 5.04 5.77998L3 5.97998" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path>` +
                                                   `<path d="M8.5 4.97L8.72 3.66C8.88 2.71 9 2 10.69 2H13.31C15 2 15.13 2.75 15.28 3.67L15.5 4.97" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path>` +
                                                   `<path d="M18.85 9.14001L18.2 19.21C18.09 20.78 18 22 15.21 22H8.79002C6.00002 22 5.91002 20.78 5.80002 19.21L5.15002 9.14001" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path>` +
                                                   `<path d="M10.33 16.5H13.66" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path>` +
                                                   `<path d="M9.5 12.5H14.5" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path>` +
                                               `</g>` +
                                           `</svg>`;

        comment.appendChild(comment_delete_button);
    }

    return comment;
}

// Post a comment button
function postCommentRequestSetup() {
    document.getElementById("post_comment_button").addEventListener("click", async function () {
        let create_comment_url = this.getAttribute("data-gamehub-create-comment-url");
        const csrftoken = getCookie("csrftoken");

        let formData = new FormData();
        formData.append("body", document.getElementById("comment_body").value);

        const response = await fetch(
            create_comment_url, {
                method: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                mode: 'same-origin',
                redirect: "follow",
                body: formData
            }
        );

        if (response.redirected) {
            window.location.href = response.url;
        } else {
            const data = await response.json();

            if (data["comment_status"] === "SUCCESS") {
                document.getElementById("comment_body").value = "";
                document.getElementById("leave_a_comment_wrapper").style.display = "block";
                document.getElementById("leave_a_comment_carrier").style.display = "none";
                let new_comment = renderComment(data["comment_info"]);
                document.getElementById("comment_section").appendChild(new_comment);
            } else if (data["comment_status"] === "FAIL") {
                let pivot = document.getElementById("create_comment_buttons");
                let parent = document.getElementById("leave_a_comment_carrier");

                let message = document.createElement("div");
                message.style.color = "red";
                message.innerHTML = data["message"];

                parent.insertBefore(message, pivot);
            }
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    likeSinglePostRequestSetup();
    deleteSinglePostRequestSetup();
    leaveCommentButtonSetup();
    cancelLeaveCommentButtonSetup();
    postCommentRequestSetup();
    likeCommentRequestSetup();
    deleteCommentRequestSetup();
});
