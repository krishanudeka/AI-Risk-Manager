let currentClient = 0
let totalClients = 0
let clientData = []

function generateForms(){

totalClients = parseInt(document.getElementById("clientCount").value)

document.getElementById("totalSteps").innerText = totalClients

clientData = []

for(let i=0;i<totalClients;i++){
clientData.push({})
}

currentClient = 0

renderClientForm()
updateProgress()

}


function renderClientForm(){

const container = document.getElementById("formContainer")

const clientID = "C" + String(currentClient+1).padStart(3,'0')

const saved = clientData[currentClient] || {}

container.innerHTML = `

<div class="client-card">

<h3>${clientID}</h3>

<label>Client Name</label>
<input type="text" id="name" placeholder="Enter client name" value="${saved.name || ""}">

<label>Industry</label>
<select id="industry">
<option ${saved.industry==="Tech"?"selected":""}>Tech</option>
<option ${saved.industry==="Finance"?"selected":""}>Finance</option>
<option ${saved.industry==="Retail"?"selected":""}>Retail</option>
<option ${saved.industry==="Marketing"?"selected":""}>Marketing</option>
<option ${saved.industry==="Art"?"selected":""}>Art</option>
<option ${saved.industry==="Healthcare"?"selected":""}>Healthcare</option>
<option ${saved.industry==="Education"?"selected":""}>Education</option>
<option ${saved.industry==="Manufacturing"?"selected":""}>Manufacturing</option>
<option ${saved.industry==="Consulting"?"selected":""}>Consulting</option>
<option ${saved.industry==="Real Estate"?"selected":""}>Real Estate</option>
</select>

<label>Contract Type</label>
<select id="contract">
<option ${saved.contract==="Retainer"?"selected":""}>Retainer</option>
<option ${saved.contract==="Project"?"selected":""}>Project</option>
<option ${saved.contract==="Hourly"?"selected":""}>Hourly</option>
</select>

<label>Monthly Revenue</label>
<input type="number" id="revenue" value="${saved.revenue || ""}">

<label>Avg Payment Delay (days)</label>
<input type="number" id="delay" value="${saved.delay || ""}">

<div class="nav-buttons">

<button onclick="prevClient()" ${currentClient===0 ? "disabled":""}>Previous</button>

${
currentClient === totalClients-1
? `<button onclick="submitData()" class="submit-small">Submit</button>`
: `<button onclick="nextClient()">Next</button>`
}

</div>

</div>

`

}


function updateProgress(){

document.getElementById("currentStep").innerText = currentClient + 1

const percent = ((currentClient+1) / totalClients) * 100

document.getElementById("progressFill").style.width = percent + "%"

}


function nextClient(){

saveCurrentClient()

currentClient++

renderClientForm()
updateProgress()

}


function prevClient(){

saveCurrentClient()

currentClient--

renderClientForm()
updateProgress()

}


function saveCurrentClient(){

clientData[currentClient] = {

client_id: "C" + String(currentClient+1).padStart(3,'0'),
name: document.getElementById("name").value,
industry: document.getElementById("industry").value,
contract_type: document.getElementById("contract").value,
base_value: parseFloat(document.getElementById("revenue").value || 0),
avg_payment_delay: parseFloat(document.getElementById("delay").value || 0)

}

}


async function submitData(){

saveCurrentClient()

try{

const res = await fetch("http://127.0.0.1:8000/manual-entry",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body: JSON.stringify({clients:clientData})
})

const data = await res.json()

console.log(data)

// redirect to dashboard
window.location.href = "dashboard.html"

}catch(error){

console.error(error)
alert("Error submitting manual data")

}

}


window.onload = function(){
generateForms()
}