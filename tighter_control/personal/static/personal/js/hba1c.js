$.ajax({
    method: "GET",
    url: endpoint,
    success: function(data){
            console.log(data)
         console.log(data.hBA1c)
         console.log(data["Highest Glucose reading"])


         document.getElementById("hbA1cRsult").innerHTML = data.hBA1c;
         
    
    },
    error: function(error_data){
            console.log("error")
            console.log(error_data)
    }
})