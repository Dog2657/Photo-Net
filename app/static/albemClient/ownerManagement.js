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


    result.forEach(({userId, username, email, type}) => {
        const instance = document.createElement('article')
        instance.setAttribute('data-userId', userId)
        instance.innerHTML += 
        `<div class="username">${username}</div>
        <div class="email">${email}</div>`

        const select = document.createElement("select")
        select.innerHTML =
            `<option value="none">None</option>
            <option value="viewer" selected="${type == 'viewer'}">Viewer</option>
            <option value="editor" selected="${type == 'editor'}">Editor</option>`

        instance.appendChild(select)
        modalBody.appendChild(instance)
    });
}