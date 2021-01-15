document.addEventListener('DOMContentLoaded', function (event) {
	
	let registrationForm = document.getElementById("registration-form");
	let login = document.getElementById("username");
	let master_pass= document.getElementById("master_password");
	
	
	function request(){
	fetch('https://localhost/check_credentials?username='+login.value+"&master_password="+master_pass.value)
		.then(response => response.json())
		.then( function(data){			
			if(data.answer == "True"){
				console.log(login.value+", otrzymaliśmy powiadomienie że chcesz zmienić hasło, link do zmiany hasła został wysłany, jeżeli do tego konta jest przypisany adres email!")
		}}
		);
						
	}			
	registrationForm.addEventListener('submit', request);
	
})