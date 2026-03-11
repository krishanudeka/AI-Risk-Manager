let analyticsChart

window.onload = loadDashboard

async function loadDashboard(){

const res = await fetch("http://127.0.0.1:8000/dashboard")
const data = await res.json()

/* ---------------- NO DATA STATE ---------------- */

if(data.no_data){

document.querySelector(".flex-1").innerHTML = `
<div class="flex items-center justify-center min-h-screen">

<div class="bg-white p-12 rounded-xl shadow text-center max-w-2xl w-full">

<h2 class="text-2xl font-bold mb-4">
No Data Available
</h2>

<p class="text-gray-600 mb-6">
Upload client spreadsheets or use manual entry to generate AI insights.
</p>

<button onclick="window.location.href='upload.html'"
class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">

Upload Data

</button>

<button onclick="window.location.href='manual.html'"
class="px-6 py-3 border rounded-lg ml-4 hover:bg-gray-200">

Manual Entry

</button>

</div>

</div>
`

return
}

window.lifecycleData = data.lifecycle_distribution || {}
window.riskData = data.risk_distribution || {}
window.heatmapData = data.heatmap || []
window.financialData = data.financial_trend || []
window.riskMatrix = data.risk_matrix || []
window.forecast = data.forecast || []
window.churnForecast = data.churn_forecast || []

document.getElementById("burnout").innerText = data.burnout + "%"

document.getElementById("forecast").innerText =
data.forecast.map(d => "$" + Math.round(d.forecast)).join(" → ")

document.getElementById("totalClients").innerText =
data.summary.total_clients

document.getElementById("highRiskClients").innerText =
data.summary.high_risk_clients

document.getElementById("dependency").innerText =
"Top Client: " + data.dependency_risk.top_client + "% | " +
"Top 5 Clients: " + data.dependency_risk.top_5_clients + "%"

drawRiskGauge(data.risk_score,data.risk_status)

drawAnalyticsChart("revenue")

document
.getElementById("chartSelector")
.addEventListener("change",function(){
drawAnalyticsChart(this.value)
})

loadTable(data.top_clients)

loadSignals(data.alerts)

}


function drawRiskGauge(score,status){

const ctx = document.getElementById("riskGauge")

new Chart(ctx,{

type:"doughnut",

data:{
datasets:[{
data:[score,100-score],
backgroundColor:["#ef4444","#e5e7eb"],
borderWidth:0,
cutout:"75%"
}]
},

options:{

responsive:true,
maintainAspectRatio:false,

plugins:{
legend:{
display:true,
position:"bottom",
labels:{
boxWidth:14,
generateLabels:()=>[
{ text:"Business Risk", fillStyle:"#ef4444"},
{ text:"Healthy Capacity", fillStyle:"#e5e7eb"}
]
}
},

tooltip:{
callbacks:{
label:(context)=>{
if(context.dataIndex===0){
return "Business Risk: "+score+"%"
}
return "Healthy Capacity: "+(100-score).toFixed(1)+"%"
}
}
}

}

}

})

document.getElementById("riskStatus").innerHTML =

`
<div style="font-size:28px;font-weight:bold">
${score}%
</div>

<div style="color:#666">
${status}
</div>
`

}



function drawAnalyticsChart(type){

const ctx=document.getElementById("analyticsChart")

if(analyticsChart) analyticsChart.destroy()



/* ---------------- REVENUE ---------------- */

if(type==="revenue"){

analyticsChart=new Chart(ctx,{

type:"line",

data:{
labels:window.financialData.map(d=>d.date),

datasets:[{
label:"Revenue ($)",
data:window.financialData.map(d=>d.revenue),
borderColor:"#2563eb",
backgroundColor:"rgba(37,99,235,0.2)",
fill:true,
tension:0.4
}]
},

options:{
maintainAspectRatio:false,
plugins:{legend:{display:true}},
scales:{
y:{
title:{display:true,text:"Revenue ($)"}
}
}
}

})

}



/* ---------------- PROFIT ---------------- */

if(type==="profit"){

analyticsChart=new Chart(ctx,{

type:"line",

data:{
labels:window.financialData.map(d=>d.date),

datasets:[{

label:"Net Cash Flow ($)",

data:window.financialData.map(d=>d.net_cash_flow),

borderColor:"#16a34a",

backgroundColor:"rgba(22,163,74,0.2)",

fill:true,

tension:0.4

}]
},

options:{
maintainAspectRatio:false,
scales:{
y:{
title:{display:true,text:"Profit ($)"}
}
}
}

})

}



/* ---------------- FORECAST ---------------- */

if(type==="forecast"){

analyticsChart=new Chart(ctx,{

type:"line",

data:{
labels:window.forecast.map(d=>d.month),

datasets:[

{
label:"Best Case",
data:window.forecast.map(d=>d.upper),
borderColor:"rgba(0,0,0,0)",
backgroundColor:"rgba(37,99,235,0.2)",
fill:true
},

{
label:"Expected Revenue",
data:window.forecast.map(d=>d.forecast),
borderColor:"#2563eb",
tension:0.4
},

{
label:"Worst Case",
data:window.forecast.map(d=>d.lower),
borderColor:"#ef4444",
borderDash:[5,5]
}

]

},

options:{
maintainAspectRatio:false,
plugins:{legend:{display:true}},
scales:{
y:{title:{display:true,text:"Revenue Forecast ($)"}}
}
}

})

}



/* ---------------- LIFECYCLE ---------------- */

if(type==="lifecycle"){

const labels = Object.keys(window.lifecycleData)
const values = Object.values(window.lifecycleData)

analyticsChart=new Chart(ctx,{

type:"pie",

data:{
labels:labels,

datasets:[{
data:values,
backgroundColor:[
"#3b82f6",
"#10b981",
"#f59e0b",
"#ef4444",
"#6366f1"
]
}]
},

options:{
maintainAspectRatio:false,

plugins:{
legend:{position:"bottom"},

tooltip:{
callbacks:{
label:function(context){

const total = context.dataset.data.reduce((a,b)=>a+b)
const val = context.raw
const percent = ((val/total)*100).toFixed(1)

return context.label + ": " + percent + "%"
}
}
}
}

}

})

}



/* ---------------- RISK DISTRIBUTION ---------------- */

if(type==="risk"){

const labels = Object.keys(window.riskData).map(v =>
v == "0" ? "Safe Clients" : "Churn Risk"
)

const values = Object.values(window.riskData)

analyticsChart = new Chart(ctx,{

type:"doughnut",

data:{
labels:labels,

datasets:[{
data:values,

backgroundColor:[
"#22c55e",
"#ef4444"
]
}]
},

options:{
maintainAspectRatio:false,

plugins:{
legend:{position:"bottom"},

tooltip:{
callbacks:{
label:function(context){

const total = context.dataset.data.reduce((a,b)=>a+b)
const val = context.raw
const percent = ((val/total)*100).toFixed(1)

return context.label + ": " + percent + "%"
}
}
}

}

}

})

}



/* ---------------- CLIENT HEALTH ---------------- */

if(type==="heatmap"){

analyticsChart=new Chart(ctx,{

type:"bar",

data:{
labels:window.heatmapData.map(d=>d.client_id),

datasets:[{

label:"Client Risk %",

data:window.heatmapData.map(d=>d["RISK_%"]),

backgroundColor:window.heatmapData.map(d=>{

const r = d["RISK_%"]

if(r < 30) return "#22c55e"
if(r < 60) return "#f59e0b"
return "#ef4444"

})

}]
},

options:{
maintainAspectRatio:false,

plugins:{
legend:{display:true}
},

scales:{
x:{display:false},
y:{
title:{display:true,text:"Churn Risk (%)"},
beginAtZero:true
}
}

}

})

}



/* ---------------- RISK MATRIX ---------------- */

if(type==="matrix"){

analyticsChart=new Chart(ctx,{

type:"scatter",

data:{
datasets:[{

label:"Clients",

data:window.riskMatrix.map(d=>({

x:d.PREDICTIVE_CLV,
y:d["RISK_%"],
id:d.client_id

})),

backgroundColor:"#2563eb"

}]
},

options:{

maintainAspectRatio:false,

plugins:{
legend:{display:false},

tooltip:{
callbacks:{
label:function(context){

const point=context.raw

return [

"Client: "+point.id,
"CLV: $"+Math.round(point.x).toLocaleString(),
"Risk: "+point.y.toFixed(1)+"%"

]

}
}
}

},

scales:{

x:{
title:{display:true,text:"Client Lifetime Value ($)"}
},

y:{
title:{display:true,text:"Churn Risk (%)"},
beginAtZero:true
}

}

}

})

}

}



/* ---------------- TABLE ---------------- */

function loadTable(clients){

const tbody=document.getElementById("clientTable")

tbody.innerHTML=""

clients.forEach(c=>{

let churn="Safe"

window.churnForecast.forEach(ch=>{

if(ch.client_id===c.client_id){

churn="High"

}

})

const row=document.createElement("tr")

row.innerHTML=`

<td>${c.client_id}</td>

<td>$${Math.round(c.PREDICTIVE_CLV).toLocaleString()}</td>

<td>${c["RISK_%"].toFixed(1)}%</td>

<td>${c.STAGE}</td>

<td class="${churn==="High"?"text-red-500":"text-green-600"}">${churn}</td>

<td class="text-blue-600">${c.PRICE_STRATEGY}</td>

`

tbody.appendChild(row)

})

}



/* ---------------- ALERTS ---------------- */

function loadSignals(alerts){

const ul=document.getElementById("alerts")

ul.innerHTML=""

alerts.forEach(a=>{

const li=document.createElement("li")

li.innerText=a

ul.appendChild(li)

})

}