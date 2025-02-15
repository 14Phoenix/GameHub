// Author: Viktor Mitrovic 0296/2021

// Display Notification container
function displayNotificationContainer() {
    let notification_bell = document.getElementById("notification_bell_button");
    let notification_container = document.getElementById("notification_container");

    let boundingBoxBell = notification_bell.getBoundingClientRect()
    let boundingBoxContainer = notification_container.getBoundingClientRect();

    notification_container.style.top = boundingBoxBell.top + boundingBoxBell.height + 10 + "px";
    notification_container.style.left = boundingBoxBell.left + boundingBoxBell.width - boundingBoxContainer.width + "px";
}

// Notification container setup
function notificationContainerSetup() {
    let notification_bell = document.getElementById("notification_bell_button");
    let notification_container = document.getElementById("notification_container");

    if (notification_bell == null || notification_container == null) return;

    let like_svg = Array.from(notification_bell.childNodes).filter(node => {
        return node.nodeType === Node.ELEMENT_NODE && node.tagName.toLowerCase() === 'svg';
    })[0];

    let displayNotificationsFlag = true;

    notification_container.addEventListener("focusout", function (event) {
        if (notification_container.style.visibility === 'hidden') return;

        if (event.relatedTarget != null && event.relatedTarget.classList.contains("notification-focus-ignore")) return;

        if (event.relatedTarget === notification_bell) {
            displayNotificationsFlag = false;
        }
        
        like_svg.style.fill = "none";
        notification_container.style.visibility = 'hidden';
    })

    notification_bell.addEventListener("click", function () {
        if (!displayNotificationsFlag) {
            displayNotificationsFlag = true;
            return;
        }

        if (notification_container.style.visibility !== 'visible') {
            displayNotificationContainer();
            like_svg.style.fill = "white";
            notification_container.style.visibility = 'visible';
            notification_container.focus();
        } else {
            like_svg.style.fill = "none";
            notification_container.style.visibility = 'hidden';
        }
    });

    window.addEventListener("scroll", displayNotificationContainer);
    window.addEventListener("resize", displayNotificationContainer);
}

// Inbox and Join team requests buttons
function notificationButtonsSetup() {
    let notification_inbox = document.getElementById("notification_inbox");
    let notification_inbox_icon = document.getElementById("notification_inbox_icon");
    let notification_team_request = document.getElementById("notification_team_request_button");
    let notification_team_request_icon = document.getElementById("notification_team_request_icon");

    if (notification_inbox == null || notification_team_request == null) return;

    let notification_container_title = document.getElementById("notification_container_header_title");
    let notification_list = document.getElementById("notification_list");
    let team_request_list = document.getElementById("team_request_list");

    notification_inbox.addEventListener("click", function () {
        notification_container_title.innerHTML = "Notifications";

        notification_team_request_icon.style.fill = "none";

        notification_inbox_icon.style.fill = "white";
        document.getElementById("SVGRepo_iconCarrier_inbox_path_1").setAttribute("stroke", "#1a1a1b");

        team_request_list.style.display = 'none';
        notification_list.style.display = 'block';
    });

    notification_team_request.addEventListener("click", function () {
        notification_container_title.innerHTML = "Team join requests";

        notification_inbox_icon.style.fill = "none";
        document.getElementById("SVGRepo_iconCarrier_inbox_path_1").setAttribute("stroke", "white");

        notification_team_request_icon.style.fill = "white";

        notification_list.style.display = 'none';
        team_request_list.style.display = 'block';
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

// Send team request response
async function sendTeamRequestResponse(button) {
    let response_url = button.parentNode.getAttribute("data-gamehub-notification-team-request");
    let response_status = button.getAttribute("data-gamehub-notification-team-request-status");
    const csrftoken = getCookie("csrftoken");

    const response = await fetch(
        response_url, {
            method: "POST",
            headers: {
                'X-CSRFToken': csrftoken
            },
            mode: 'same-origin',
            redirect: "follow",
            body: JSON.stringify({
                "REQUEST_STATUS": response_status
            })
        }
    );

    if (response.redirected) {
        window.location.href = response.url;
    } else {
        const data = await response.json();

        button.parentNode.parentNode.style.display = 'none';
        document.getElementById("notification_container").focus();
    }
}

// Accept/Reject team request buttons
function teamRequestResponseSetup() {
    let response_buttons = document.querySelectorAll("[data-gamehub-notification-team-request-status]");

    response_buttons.forEach(button => {
        button.addEventListener("click", async function () {
            await sendTeamRequestResponse(this);
        });
    });
}

document.addEventListener("DOMContentLoaded", function () {
    notificationContainerSetup();
    notificationButtonsSetup();
    teamRequestResponseSetup();
});
