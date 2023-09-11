export async function request(
    url,
    method = "GET",
    body = {},
    headers = {},
    cache = "default",
    mode = "cors",
    redirect = "follow",
    referrerPolicy = "no-referrer"
){
    try {
        const response = await fetch(url, {
            method,
            mode,
            cache, 
            credentials: "include",
            headers,
            redirect,
            referrerPolicy,
            body: (method != "GET")? body : undefined
        });

        const json = await response.json()

        if(!response.ok)
            throw json.detail 

        return [json, null]

    } catch (error) {
        return [null, error]
    }
};