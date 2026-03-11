window.onload = loadForecast

let revenueRisk = 0


async function loadForecast(){

const res = await fetch("http://127.0.0.1:8000/forecast")

const data = await res.json()

if(data.no_data){
alert("Upload data first")
return
}

updateSummary(data.summary)

drawForecastChart(data.revenue_forecast)

populateChurnTable(data.churn_forecast)

populateRiskClients(data.high_risk_clients)

revenueRisk = data.summary.revenue_at_risk

initSimulator()

}



function updateSummary(s){

document.getElementById("nextMonth").innerText = "$"+s.next_month_revenue.toLocaleString()

document.getElementById("nextQuarter").innerText = "$"+s.next_quarter_revenue.toLocaleString()

document.getElementById("revenueRisk").innerText = "$"+s.revenue_at_risk.toLocaleString()

document.getElementById("confidence").innerText = s.confidence+"%"

}



function drawForecastChart(data){

const labels = data.map(d => d.month)

const values = data.map(d => d.revenue)

const ctx = document.getElementById("forecastChart")

new Chart(ctx,{
type:"line",
data:{
labels:labels,
datasets:[{
label:"Forecast Revenue",
data:values,
borderWidth:2,
tension:0.3
}]
}
})

}



function populateChurnTable(data){

const table = document.querySelector("#churnTable tbody")

table.innerHTML=""

data.forEach(c=>{

table.innerHTML += `
<tr>
<td>${c.month}</td>
<td>${c.expected_churn}</td>
<td>$${c.revenue_loss.toLocaleString()}</td>
</tr>
`

})

}



function populateRiskClients(data){

const table = document.querySelector("#riskClients tbody")

table.innerHTML=""

data.forEach(c=>{

table.innerHTML += `
<tr>
<td>${c.client}</td>
<td>${c.probability}%</td>
<td>$${c.clv.toLocaleString()}</td>
<td>$${c.revenue_risk.toLocaleString()}</td>
</tr>
`

})

}



function initSimulator(){

const slider = document.getElementById("churnSlider")

const impact = document.getElementById("simImpact")

slider.oninput = function(){

const percent = slider.value

document.getElementById("churnPercent").innerText = percent + "%"

const loss = revenueRisk * (percent/100)

impact.innerText = "$" + Math.round(loss).toLocaleString()

if(loss > 100000){
impact.style.color = "#dc2626"
}else{
impact.style.color = "#2f6fed"
}

}

}