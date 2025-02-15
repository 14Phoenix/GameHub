// Author: Nemanja Mićanović 0595/2021

function showPlacesAndLoadTeams(numberOfPlaces, isKnockout, tournamentStarted, teamNames, teamPoints, winsToPromote, isPrivileged) {
    let table = document.getElementById("tourTable");
    let tableTr = table.children[0].children;

    if (isKnockout) showPlacesForKnockoutFormat(numberOfPlaces, tableTr);
    else showPlacesForPointsFormat(numberOfPlaces, tableTr);

    addOtherListeners(isPrivileged);
    if (isPrivileged) addListenersForPopUpButtons();

    if (tournamentStarted) {
        if (isKnockout) loadTeamsForKnockoutFormat(numberOfPlaces, teamNames, teamPoints, winsToPromote);
        else loadTeamsForPointsFormat(numberOfPlaces, teamNames, teamPoints);
    }
}


function showPlacesForKnockoutFormat(numberOfPlaces, tableTr) {
    let numberOfTd = numberOfPlaces;
    let rowspan = 1;
    let column = 0;

    while (numberOfTd >= 1) {
        let offset = 0;

        for (let row = 0; row < numberOfTd; row++) {
            // New <td>
            let td = document.createElement("td");
            td.setAttribute("rowspan", rowspan.toString());
            td.style.verticalAlign = "middle";
            if (numberOfTd !== 1) td.style.minWidth = "250px";

            // <div> inside <td>
            let div = createDivForTd("200px");
            if (row % 2 === 0) div.style.marginTop = "10px";
            else div.style.marginBottom = "10px";
            setAttributes(div, column, row);

            // <span> for position inside <div>
            let positionSpan = createSpanForPosition(row);

            // <span> for team name inside <div>
            let teamSpan = createSpanForTeamName();

            // <span> for points inside <div>
            let pointsSpan = createSpanForPoints();

            // Append childs
            div.appendChild(positionSpan);
            div.appendChild(teamSpan);
            div.appendChild(pointsSpan);
            td.appendChild(div);
            tableTr[offset].appendChild(td);
            offset += rowspan;
        }

        rowspan *= 2;
        numberOfTd /= 2;
        column += 1;
    }
}


function showPlacesForPointsFormat(numberOfPlaces, tableTr) {
    let leftIndex = 0;
    let rightIndex = Math.ceil(numberOfPlaces / 2);

    for (let i = 0; i < numberOfPlaces; i++) {
        // New <td>
        let td = document.createElement("td");
        td.setAttribute("rowspan", "2");

        // <div> inside <td>
        let div = createDivForTd("400px");
        let column = (i % 2 === 0) ? 0 : 1;
        let row = Math.floor(i / 2);
        setAttributes(div, column, row);

        // <span> for position inside <div>
        let positionSpan;
        if (i % 2 === 0) positionSpan = createSpanForPosition(leftIndex++);
        else positionSpan = createSpanForPosition(rightIndex++);

        // <span> for team name inside <div>
        let teamSpan = createSpanForTeamName();

        // <span> for points inside <div>
        let pointsSpan = createSpanForPoints();

        div.appendChild(positionSpan);
        div.appendChild(teamSpan);
        div.appendChild(pointsSpan);
        td.appendChild(div);
        tableTr[i].appendChild(td);
    }
}


function createDivForTd(width) {
    let div = document.createElement("div");
    div.style.display = "flex";
    div.style.width = width;
    div.style.height = "50px";
    div.style.backgroundColor = "#686868";
    div.style.border = "3px solid black";
    div.style.cursor = "pointer";
    return div;
}


function createSpanForPosition(row) {
    let positionSpan = document.createElement("span");
    positionSpan.innerText = (row + 1) + ".";
    positionSpan.style.textAlign = "center";
    //positionSpan.style.flexGrow = "1";
    positionSpan.style.margin = "auto";
    positionSpan.style.color = "white";
    //positionSpan.style.backgroundColor = "black";
    //positionSpan.style.fontWeight = "bold";
    return positionSpan;
}


function createSpanForTeamName() {
    let teamSpan = document.createElement("span");
    teamSpan.style.textAlign = "center";
    teamSpan.style.flexGrow = "10";
    teamSpan.style.margin = "auto";
    return teamSpan;
}


function createSpanForPoints() {
    let pointsSpan = document.createElement("span");
    pointsSpan.style.textAlign = "center";
    pointsSpan.style.flexGrow = "1";
    pointsSpan.style.margin = "auto";
    pointsSpan.style.color = "black";
    pointsSpan.style.backgroundColor = "white";
    pointsSpan.style.fontWeight = "bold";
    return pointsSpan;
}


function setAttributes(div, column, row) {
    div.setAttribute("data-gamehub-popup-button", "edit_team");
    div.setAttribute("id", column + "_" + row);
    div.addEventListener("click", function () {
        if (div.children[1].innerText === "") return;    // <span> for team name
        let popup = document.getElementById("edit_team_popup");
        popup.setAttribute("data-gamehub-meta-div", this.id);
        let popupTextField = document.getElementsByName("points")[0];
        popupTextField.value = "";
        let popupTitle = document.getElementById("title_edit_team");
        popupTitle.innerHTML = "<b>Edit team:</b> " + "<span style='color: yellow'>" + this.children[1].innerHTML + "</span>";
    })
}


function loadTeamsForKnockoutFormat(numberOfPlaces, teamNames, teamPoints, winsToPromote) {
    let numberOfTd = numberOfPlaces;
    let column = 0;

    // Reset fields
    while (numberOfTd >= 1) {
        for (let row = 0; row < numberOfTd; row++) {
            let div = document.getElementById(column + "_" + row);
            div.children[1].innerText = "";    // <span> for team name
            div.children[2].innerText = "";    // <span> for points
        }

        numberOfTd /= 2;
        column += 1;
    }

    let maxPoints = Math.log2(numberOfPlaces) * winsToPromote;

    // Update fields
    for (let i = 0; i < numberOfPlaces; i++) {
        if (teamPoints[i] > maxPoints) teamPoints[i] = maxPoints;
        let row = i;
        column = 0;

        do {
            let div = document.getElementById(column + "_" + row);
            div.children[1].innerText = teamNames[i];    // <span> for team name

            if (teamNames[i] !== "") {
                if (teamPoints[i] - winsToPromote >= 0) div.children[2].innerText = winsToPromote;    // <span> for points
                else div.children[2].innerText = teamPoints[i];    // <span> for points
            }

            column++;
            row = Math.floor(row / 2);
            teamPoints[i] -= winsToPromote;
        }
        while (teamPoints[i] >= 0);
    }
}


function loadTeamsForPointsFormat(numberOfPlaces, teamNames, teamPoints) {
    let column = 0;
    let row = 0;

    // Reset fields for team names
    for (let i = 0; i < numberOfPlaces; i++) {
        column = (i % 2 === 0) ? 0 : 1;
        row = Math.floor(i / 2);

        let div = document.getElementById(column + "_" + row);
        div.children[1].innerText = "";    // <span> for team name
        div.children[2].innerText = "";    // <span> for points
    }

    let halfIndex = Math.ceil(numberOfPlaces / 2);

    // Update fields for team names
    for (let i = 0; i < numberOfPlaces; i++) {
        if (i < halfIndex) {
            column = 0;
            row = i;
        }
        else {
            column = 1;
            row = i - halfIndex;
        }

        let div = document.getElementById(column + "_" + row);
        div.children[1].innerText = teamNames[i];    // <span> for team name
        div.children[2].innerText = teamPoints[i];    // <span> for points
    }
}


function addListenersForPopUpButtons() {
    // All buttons that open popups
    let popup_buttons= document.querySelectorAll("[data-gamehub-popup-button]");

    popup_buttons.forEach(button => {
        button.addEventListener("click", function () {
            let target_popup = button.getAttribute("data-gamehub-popup-button");
            if (target_popup === "edit_team") {
                if (button.children[1].innerText === "") return;    // <span> for team name
            }
            let popup = document.querySelector("[data-gamehub-popup=" + target_popup + "]");
            popup.style.visibility = "visible";
        });
    });

    // All buttons that close popups
    let popup_close_buttons = document.querySelectorAll("[data-gamehub-popup-close]");

    popup_close_buttons.forEach(close_button => {
        close_button.addEventListener("click", function () {
            let target_popup = close_button.getAttribute("data-gamehub-popup-close");
            let popup = document.querySelector("[data-gamehub-popup=" + target_popup + "]");
            popup.style.visibility = "hidden";
        });
    });
}


function addOtherListeners(isPrivileged) {
    // Data from tour_event popup (leave, start, finish and delete tournament opens this popup)
    let tour_event_title = document.getElementById("title_tour_event");
    let tour_event_submit_button = document.getElementById("tour_event_submit_button");

    // On leave tournament
    document.getElementById("leaveTour").addEventListener("click", function () {
        tour_event_title.innerText = "Are you sure you want to leave this tournament ?";
        tour_event_submit_button.setAttribute("name", "leave");
        tour_event_submit_button.innerText = "Leave Tournament";
    });

    if (!isPrivileged) {
        let popup = document.getElementById("tour_event_popup");

        document.getElementById("leaveTour").addEventListener("click", function () {
            popup.style.visibility = "visible";
        });

        let popup_close_buttons = document.querySelectorAll("[data-gamehub-popup-close='tour_event']");

        popup_close_buttons.forEach(close_button => {
            close_button.addEventListener("click", function () {
                popup.style.visibility = "hidden";
            });
        });
    }

    if (isPrivileged) {
        // On start tournament
        document.getElementById("startTour").addEventListener("click", function () {
            tour_event_title.innerText = "Are you sure you want to start this tournament ?";
            tour_event_submit_button.setAttribute("name", "start");
            tour_event_submit_button.innerText = "Start Tournament";
        });

        // On finish tournament
        document.getElementById("finishTour").addEventListener("click", function () {
            tour_event_title.innerText = "Are you sure you want to finish this tournament ?";
            tour_event_submit_button.setAttribute("name", "finish");
            tour_event_submit_button.innerText = "Finish Tournament";
        });

        // On delete tournament
        document.getElementById("deleteTour").addEventListener("click", function () {
            tour_event_title.innerText = "Are you sure you want to DELETE this tournament ?";
            tour_event_submit_button.setAttribute("name", "delete");
            tour_event_submit_button.innerText = "Delete Tournament";
        });

        // On team kick from tournament
        let kickButtons = document.getElementsByClassName("kickTour");
        for (let i = 0; i < kickButtons.length; i++) {
            kickButtons[i].addEventListener("click", function () {
                tour_event_title.innerText = "Are you sure you want to kick this team ?";
                tour_event_submit_button.setAttribute("name", "kick_" + kickButtons[i].id);
                tour_event_submit_button.innerText = "Kick";
            });
        }

        // On form submit for edit_team popup
        document.getElementById('form_edit_team').addEventListener('submit', async function (event) {
            event.preventDefault();    // Prevent the default form submission
            await submitFormEditTeam(this);
        });
    }
}


async function submitFormEditTeam(form) {
    const csrf_token = getCookie('csrftoken')

    let popup = document.getElementById("edit_team_popup");
    let divId = popup.getAttribute("data-gamehub-meta-div").split("_");
    let column = parseInt(divId[0]);
    let row = parseInt(divId[1]);
    let teamName = document.getElementById(column + "_" + row).children[1].innerText;

    let pointsToAdd = parseInt(form["points"].value);
    if (isNaN(pointsToAdd)) pointsToAdd = 0;

    const response = await fetch(
        form.action, {
            method: "POST",
            headers: {
                'X-CSRFToken': csrf_token
            },
            body: JSON.stringify({
                "teamName": teamName,
                "pointsToAdd": pointsToAdd
            }),
            mode: "same-origin",
            redirect: "follow"
        }
    );

    if (response.redirected) {
        window.location.href = response.url;
        return;
    }
    const data = await response.json();

    if (data["numberOfPlaces"] != null && data["teamNames"] != null && data["teamPoints"] != null && data["isKnockout"] != null && data["winsToPromote"] != null) {
        if (data["isKnockout"] === "true") loadTeamsForKnockoutFormat(data["numberOfPlaces"], data["teamNames"], data["teamPoints"], data["winsToPromote"]);
        else loadTeamsForPointsFormat(data["numberOfPlaces"], data["teamNames"], data["teamPoints"]);
    }
}


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
