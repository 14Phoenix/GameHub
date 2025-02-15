// Author: Viktor Mitrovic 0296/2021

document.addEventListener("DOMContentLoaded", function () {
    let popup_buttons = document.querySelectorAll("[data-gamehub-popup-button]");

    popup_buttons.forEach(button => {
        button.addEventListener("click", function () {
            let target_popup = button.getAttribute("data-gamehub-popup-button");
            let popup = document.querySelector("[data-gamehub-popup=" + target_popup + "]");
            popup.style.visibility = "visible";
        });
    });

    let popup_close_buttons = document.querySelectorAll("[data-gamehub-popup-close]");

    popup_close_buttons.forEach(close_button => {
        close_button.addEventListener("click", function () {
            let target_popup = close_button.getAttribute("data-gamehub-popup-close");
            let popup = document.querySelector("[data-gamehub-popup=" + target_popup + "]");
            popup.style.visibility = "hidden";
        });
    });
});
