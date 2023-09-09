import { request } from "/static/requester.js"

const accessDialog = document.querySelector('dialog[data-name=accessManagement]')

function createAccessElement(userId, username, email, type){
    const instance = document.createElement('article')
    instance.setAttribute('data-userId', userId)
    instance.innerHTML += 
    `<div class="username">${username}</div>
    <div class="email">${email}</div>`

    const select = document.createElement("select")
    select.innerHTML =
        `<option value="none">None</option>
        <option value="viewer" ${type == 'viewer'? 'selected':''}>Viewer</option>
        <option value="editor" ${type == 'editor'? 'selected':''}>Editor</option>`


    select.onchange = async (e) => {
        const userId = e.target.parentNode.getAttribute("data-userId")
        const [result, error] = await request(`/${albemId}/update-access?userId=${userId}&access=${e.target.value}`, "PATCH")
        if(error){
            console.info("TODO: handle errors")
            return
        }

        if(e.target.value == "none")
            accessDialog.querySelector('.body').querySelector(`article[data-userid="${userId}"]`).remove()
    }
    

    instance.appendChild(select)
    accessDialog.querySelector('.body').appendChild(instance)
}

document.querySelector('dialog[data-name=accessManagement] > form.addAccess').onsubmit = async (event) => {
    event.preventDefault()

    const input = event.target.querySelector('input')
    const select = event.target.querySelector('select')


    const [result, error] = await request(`/${albemId}/add-access?userSelector=${input.value}&access=${select.value}`, "POST")
    if(error){
        accessDialog.querySelector('div.errorMessage').textContent = error
        return
    }


    input.value = ""
    select.value = 'viewer'

    createAccessElement(result?.userId, result?.username, result?.email, result?.type)
}

document.querySelector('dialog[data-name=accessManagement] > form.addAccess > input').oninput = ({target}) => {
    accessDialog.querySelector('div.errorMessage').textContent = ""
}

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
        createAccessElement(userId, username, email, type)
    });
}