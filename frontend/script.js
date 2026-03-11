async function uploadFiles(){

    const txFile = document.getElementById("transactions").files[0]
    const clientsFile = document.getElementById("clients").files[0]
    const invoicesFile = document.getElementById("invoices").files[0]

    if(!txFile){
        alert("Transactions file required")
        return
    }

    const formData = new FormData()

    formData.append("transactions", txFile)

    if(clientsFile)
        formData.append("clients", clientsFile)

    if(invoicesFile)
        formData.append("invoices", invoicesFile)

    document.getElementById("status").innerText = "Uploading..."

    const response = await fetch(
        "http://127.0.0.1:8000/upload",
        {
            method:"POST",
            body:formData
        }
    )

    const data = await response.json()

    localStorage.setItem("analysis", JSON.stringify(data))

    window.location.href = "dashboard.html"
}