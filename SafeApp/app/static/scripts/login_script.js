document.addEventListener('DOMContentLoaded', function (event) {
		
	function submitForm() {
        document.getElementById("login-form").submit()
    }

    document.getElementById('submit').onclick = function() {
        setTimeout(submitForm, 1000); 
		
    }
	
});