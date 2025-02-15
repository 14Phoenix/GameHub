// Author: Tadija Goljic 0272/2021

function changeAboutSectionField() {
    let popupTextArea = document.getElementById("new-about-section-area");
    if (popupTextArea.value.length > 200) {
        popupTextArea.value = popupTextArea.value.substring(0, 200);
    }

    document.getElementById('profile_about_section').value = popupTextArea.value;
}

document.addEventListener('DOMContentLoaded', function () {
    let inputFileField = document.getElementById('profile_picture')
    let profilePictureDisplay = document.createElement('img')
    profilePictureDisplay.style.display = 'none'

    let profilePictureDiv = document.getElementById('picture_div')
    profilePictureDiv.prepend(profilePictureDisplay)

    inputFileField.addEventListener('change', function () {
        if (this.files && this.files[0]) {
            let fileReader = new FileReader()

            fileReader.onload = function (event) {
                let svgPlaceholder = document.getElementById('profile_picture_placeholder')
                if (svgPlaceholder != null) {
                    svgPlaceholder.remove()
                }

                let initialLoadProfilePic = document.getElementById("profile_picture_initial_load")
                if (initialLoadProfilePic != null) {
                    initialLoadProfilePic.remove()
                }

                profilePictureDisplay.setAttribute('src', event.target.result)
                profilePictureDisplay.setAttribute('class', 'user-profile-picture')
                profilePictureDisplay.style.display = 'inline'
            }
            fileReader.readAsDataURL(this.files[0])
        }
    })
})