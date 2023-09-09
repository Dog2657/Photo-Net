import { request } from "/static/requester.js"

const accessDialog = document.querySelector('dialog[data-name=accessManagement]')

document.querySelector('body > header button.Usermanagement').onclick = async() => {
    accessDialog.showModal()

    const [result, error] = await request(`/${albemId}/access-list`)
    if(error){
        modalBody.innerHTML = `<div style='color: red'>${error}</div>`
        return
    }

    const modalBody = accessDialog.querySelector('.body')
    modalBody.style.minHeight = 'unset'
    modalBody.innerHTML = ""

    const updateUserAccess = async (e) => {
        const userId = e.target.parentNode.getAttribute("data-userId")
        const [result, error] = await request(`/${albemId}/update-access?userId=${userId}&access=${e.target.value}`, "PATCH")
        if(error){
            console.info("TODO: handle errors")
            return
        }

        if(e.target.value == "none")
            modalBody.querySelector(`article[data-userid="${userId}"]`).remove()
    }


    result.forEach(({userId, username, email, type}) => {
        const instance = document.createElement('article')
        instance.setAttribute('data-userId', userId)
        instance.innerHTML += 
        `<div class="username">${username}</div>
        <div class="email">${email}</div>`

        const select = document.createElement("select")
        select.onchange = updateUserAccess
        select.innerHTML =
            `<option value="none">None</option>
            <option value="viewer" selected="${type == 'viewer'}">Viewer</option>
            <option value="editor" selected="${type == 'editor'}">Editor</option>`

        instance.appendChild(select)
        modalBody.appendChild(instance)
    });
}