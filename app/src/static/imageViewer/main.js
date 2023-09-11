import { request } from "/static/requester.js"

const modal = document.querySelector("details.ImageViewer")
const deleteDialog = modal.querySelector('dialog[data-name=deletion]')

if(modal.querySelector( "header > button.DeleteBNT"))
    modal.querySelector( "header > button.DeleteBNT").onclick = () => { deleteDialog.showModal() }

deleteDialog.querySelector('form.Options > button[data-type=deny]').onclick = () => { deleteDialog.close() }
deleteDialog.querySelector('form.Options').onsubmit = async(e) => {
    e.preventDefault()

    const [result, error] = await request(`/api/${albemId}/delete-image/${window.location.pathname.split('/')[3]}`, "DELETE")
    if(error){
        console.error("Failed to update password:", error)
        return
    }

    window.location.replace(`/${albemId}`)
}