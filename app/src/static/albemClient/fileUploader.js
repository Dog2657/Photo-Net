import { request } from "/static/requester.js"

const uploadModal = document.querySelector('dialog[data-name=uploadModal]')

document.querySelector('body > header.AlbemHeader > button.upload').onclick = () => { uploadModal.showModal() }

async function handleFilesUpload(files){
    const containor = uploadModal.querySelector('section.file-statuses');
    const data = new FormData

    let html = ""
    Array.from(files).forEach((file, index) => {
        data.append('files', file)

        var filename = file.name
        var size = `${(file.size / 1024).toFixed(2)} KB`;

        html += `<div data-finished="false">
            <div class="icon"> <span class="loader"></span> </div>
            <div class="filename">${filename}</div>
            <div class="size">${size}</div></div>`
    });

    containor.innerHTML = html + containor.innerHTML
    
    const prefixCount = document.querySelector('section.Images').children.length
    const pendingElements = containor.querySelectorAll('[data-finished="false"]')
    const socket = new WebSocket(
        `${(production)? "wss":"ws"}://${window.location.host}/api/${albemId}/live-upload-statuses`);

    socket.addEventListener("message", ({data}) => {
        const { index, state } = JSON.parse(data)

        pendingElements[index].setAttribute('data-finished', true)
        pendingElements[index].querySelector('.icon').innerHTML = (state == 'success')? "&#x2713;" : "&#x274C;"

        if(state == 'success'){
            const i = prefixCount + index
            document.querySelector('section.Images').innerHTML += 
            `<a data href="/${albemId}/i/${i}">
                <img src="/${albemId}/get-image/${i}">
            </a>`
        }
    });

    const [result, error] = await request(`/api/${albemId}/upload-images`, "POST", data)
    if(error){
        for(const element of pendingElements)
            element.querySelector('.icon').innerHTML = "&#x274C;";
        return 
    }
}




uploadModal.querySelector('form > label > input[type=file]').oninput = ({target}) => {
    handleFilesUpload(target.files)
}

uploadModal.querySelector('form').ondragover = (e) => {
    e.preventDefault()
}
uploadModal.querySelector('form').ondrop = (e) => {
    e.preventDefault()
    handleFilesUpload(e.dataTransfer.files)
}

