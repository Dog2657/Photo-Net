import { request } from "/static/requester.js"



const [htmlString, error] = await request(`/${albemId}/get-viewer`)

if(error)
    throw new Error("Failed to load viewer:", error);

const parser = new DOMParser();
const html = parser.parseFromString(htmlString, 'text/html');

function init(){
    //Add viewer css styles
    document.head.innerHTML += `<link rel="stylesheet" href="/static/ImageViewer/css/main.css">`
    

    //Add script file
    var script = document.createElement('script');
    script.src = '/static/ImageViewer/main.js';
    script.defer = true;
    script.type = "module"

    document.head.appendChild(script);

    //Added viewer to document
    const viewer = document.body.insertBefore(
        html.body.querySelector('details'),
        document.body.children[0]
    );


    viewer.querySelector('header > a.CloseBNT').onclick = (e) => {
        e.preventDefault()
        window.history.back();
    }

    const openImageViewer = (e) => {
        e.preventDefault()

        viewer.querySelector('img').src = e.target.src
        viewer.open = true

        const src_split = e.target.src.split("/")
        const imageIndex = Number(src_split[src_split.length-1])

        window.history.pushState(undefined, "pageTitle", `/${albemId}/i/${imageIndex}`);
    }

    document.querySelectorAll("body > section.Images > a").forEach(element => {
        element.addEventListener('click', openImageViewer)
    });

    window.addEventListener('popstate', (event) => {
        viewer.open = false
    })
}


if(["complete", "interactive"].indexOf(document.readyState)  !== -1)
    init()
else
    document.onload = async () => init
