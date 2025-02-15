// Author: Tadija Goljic 0272/2021

function getCookie(name) {
    let cookieValue = null
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';')
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim()
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
                break
            }
        }
    }
    return cookieValue
}

function filterTeams() {
    document.getElementById('notFull').addEventListener('click', async function () {
        let teamPlayersInfo = document.querySelectorAll('div[id^="team-players"]')
        let teams = document.querySelectorAll('div[id^="container-of-team"]')
        for (let i = 0; i < teams.length; i++) {
            let players = teamPlayersInfo[i].innerHTML.split('/')
            if (document.getElementById('notFull').checked) {
                if (parseInt(players[0]) >= parseInt(players[1])) {
                    teams[i].style.display = 'none'
                }
            } else {
                teams[i].style.display = 'flex'
            }
        }
    })

    document.getElementById('search-field').addEventListener('input', async function () {
        let teamNameInfo = document.querySelectorAll('div[id^="team-name"]')
        let teams = document.querySelectorAll('div[id^="container-of-team"]')
        let filterText = document.getElementById('search-field').value
        for (let i = 0; i < teams.length; i++) {
            console.log(teamNameInfo[i])
            if (teamNameInfo[i].innerHTML.startsWith(filterText)) {
                teams[i].style.display = 'flex'
            } else {
                teams[i].style.display = 'none'
            }
        }
    })
}

document.addEventListener('DOMContentLoaded', function () {
    filterTeams()
})
