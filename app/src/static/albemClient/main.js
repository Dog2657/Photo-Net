document.querySelector('body > header button.Share').onclick = () => {
    document.querySelector('dialog[data-name=share]').showModal()
}


{//Copy link init
    const containor = document.querySelector('dialog[data-name=share] > section.Link')
    const text = document.createTextNode(window.location.href);
    const button = document.createElement('button')

    button.textContent = "Copy"
    button.onclick = async() => {
        try{
            await navigator.clipboard.writeText(window.location.href)
        } catch (error){
            console.error("Failed to set clipboard:", error)
        }
    }

    containor.append(text)
    containor.append(button)
}
{//Share qr code init
    var qrcode = new QRCode(document.querySelector('dialog[data-name=share] > section.QR-Code'), {
        text: window.location.href,
        colorDark: "#000000",
        colorLight: "transparent",
        correctLevel: QRCode.CorrectLevel.H
    });
}
