window.onload = loadClients


async function loadClients(){

const res = await fetch("http://127.0.0.1:8000/clients")
const data = await res.json()

/* -------- NO DATA STATE -------- */

if(data.no_data){

document.getElementById("clientsTable").innerHTML = `
<tr>
<td colspan="5" class="p-10 text-center text-gray-500 text-lg">
No data uploaded yet.<br>
Please upload client data to view analytics.
</td>
</tr>
`

return
}


/* ---------- SAFETY CHECK ---------- */

if(!data.clients || data.clients.length === 0){

document.getElementById("clientsTable").innerHTML = `
<tr>
<td colspan="5" class="p-6 text-center text-gray-500">
No clients found
</td>
</tr>
`

return
}

renderClients(data.clients)

}


function renderClients(clients){

const table = document.getElementById("clientsTable")

table.innerHTML=""

clients.forEach(c=>{

let riskColor="text-green-600"

if(c["RISK_%"]>60) riskColor="text-red-600"
else if(c["RISK_%"]>30) riskColor="text-yellow-600"

const row = document.createElement("tr")

row.className="border-b"

row.innerHTML = `

<td class="p-4">${c.client_id}</td>

<td class="p-4">
$${Math.round(c.PREDICTIVE_CLV).toLocaleString()}
</td>

<td class="p-4 ${riskColor}">
${c["RISK_%"].toFixed(1)}%
</td>

<td class="p-4">
${c.STAGE}
</td>

<td class="p-4 text-blue-600">
${c.PRICE_STRATEGY}
</td>

`

table.appendChild(row)

})

}


function searchClients(){

const input =
document.getElementById("searchInput")
.value
.toLowerCase()

const rows =
document.querySelectorAll("#clientsTable tr")

rows.forEach(row=>{

if(row.innerText.toLowerCase().includes(input))
row.style.display=""

else
row.style.display="none"

})

}


function downloadClients(){

window.location.href =
"http://127.0.0.1:8000/download-clients"

}