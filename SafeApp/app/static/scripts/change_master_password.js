document.addEventListener('DOMContentLoaded', function (event) {

	let registrationForm = document.getElementById("registration-form");
	
	let master_pass= document.getElementById("master_password");
	let repeat_master_pass = document.getElementById("repeat_master_password");
	let confirmButton = document.getElementById("submit");
	
	let successMsg = "Sukces";
	let successMsgId = "SukcesId";
	let failureMsg = "Bledne";
	let failureMsgId = "BledneId";
	
	let masterpasswordError = 1;
	let remasterpasswordError = 1;
	
	
	
	prepareEventOnMasterPasswordChange();
	prepareEventOnReMasterPasswordChange();
	
	registrationForm.addEventListener('submit', event => {
		if(masterpasswordError+remasterpasswordError != 0){
			event.preventDefault();
			console.log(masterpasswordError+':'+remasterpasswordError);			
			console.log('Data stopped');			
		}
		else{
			console.log('Data sent');	
		}
	
	});
	
	
	function checkPassword(passwordValue){
		let lower = 0;
		let upper = 0;
		let digit = 0;
		let special = 0;
		
		if (passwordValue.length < 8)
			return 0;
		for (let i = 0; i < passwordValue.length; i++) {
			if(passwordValue.charAt(i) >= 'a' && passwordValue.charAt(i) <= 'z')
				lower=1;
			else if(passwordValue.charAt(i) >= 'A' && passwordValue.charAt(i) <= 'Z')
				upper=1;
			else if(passwordValue.charAt(i) >= '0' && passwordValue.charAt(i) <= '9')
				digit=1;
			else if(passwordValue.charAt(i) == '!' || passwordValue.charAt(i) == '@' 
			|| passwordValue.charAt(i) == '#' || passwordValue.charAt(i) == '$' 
			|| passwordValue.charAt(i) == '%' || passwordValue.charAt(i) == '&'
			|| passwordValue.charAt(i) == '*')
				special=1;	
			  
			
		}
		let sum = lower+upper+digit+special;
		if(sum!=4)
			return 0; 
		else
			return 1;
	}
	
	function checkRePassword(passwordValue, repeat_passValue){
		if(repeat_passValue != passwordValue){
			return 0;
		}
		return 1;
	}

	function showWarningMessage(currentElem, newElemId, message) {
        let warningElem = prepareWarningElem(newElemId, message);
        appendAfterElem(currentElem, warningElem);
    }

    function removeWarningMessage(warningElemId) {
        let warningElem = document.getElementById(warningElemId);

        if (warningElem !== null) {
            warningElem.remove();
        }
    }

    function prepareWarningElem(newElemId, message) {
        let warningField = document.getElementById(newElemId);

        if (warningField === null) {
            let textMessage = document.createTextNode(message);
            warningField = document.createElement('span');

            warningField.setAttribute("id", newElemId);
            warningField.className = "warning-field";
			if(message == "Hasło średnie"){
				warningField.className = "warning-field-yellow";
			}
			else if (message == "Hasło mocne"){
				warningField.className = "warning-field-green";
			}
			
            warningField.appendChild(textMessage);
        }
        return warningField;
    }

    function appendAfterElem(currentElem, newElem) {       
        currentElem.insertAdjacentElement('afterend', newElem);
    }
	
	
	function prepareEventOnMasterPasswordChange() {     
        master_pass.addEventListener("change", updateMasterPasswordAvailabilityMessage);	
		
    }
	function prepareEventOnReMasterPasswordChange() {
		repeat_master_pass.addEventListener("change", updateMasterPasswordAvailabilityMessage);			
        	
    }
	
	function updateMasterPasswordAvailabilityMessage() {
        let warningPasswordId = "masterpasswordWarning";
		let warningPasswordMessage = "Master password must contain minimum 8 characters (uppercase and lowercase letters, digits, and special characters";
		let warningPasswordId2 = "repeat-masterpasswordWarning";
		let warningPasswordMessage2 = "Master password and repeated master password cannot be different!";
		
		if (checkPassword(master_pass.value.trim()) == 1 ){
			removeWarningMessage(warningPasswordId);
			masterpasswordError = 0;
		} else {
			removeWarningMessage(warningPasswordId2);
			showWarningMessage(master_pass, warningPasswordId, warningPasswordMessage);
			masterpasswordError = 1;
		}
		
		if(masterpasswordError == 0){
			var score = getPasswordScore(master_pass.value.trim())
			if(score < 2){			
				showWarningMessage(master_pass, warningPasswordId, "Hasło za słabe");
				masterpasswordError = 1;
			}				
			else if (score >=2 && score <3){
				showWarningMessage(master_pass, warningPasswordId, "Hasło średnie");
				masterpasswordError = 0;
			}
			else{
				showWarningMessage(master_pass, warningPasswordId, "Hasło mocne");
				masterpasswordError = 0;
			}
		}
		
		if (checkRePassword(master_pass.value.trim(), repeat_master_pass.value.trim()) == 1 ){
			removeWarningMessage(warningPasswordId2);
			remasterpasswordError = 0;
		} else {
			showWarningMessage(repeat_master_pass, warningPasswordId2, warningPasswordMessage2);
			remasterpasswordError = 1;
		}
		   
    }
	
	function updateRePasswordAvailabilityMessage() {
		if (checkRePassword(master_pass.value.trim(), repeat_master_pass.value.trim()) == 1){
			remasterpasswordError = 0;
		} else {
			remasterpasswordError = 1;
		}
    }
	
	
	function getPasswordScore(pass) {
		var len = pass.length
	 
		var frequencies = Array.from(pass).reduce((freq, c) => (freq[c] = (freq[c] || 0) + 1) && freq, {})
	 
		return Object.values(frequencies).reduce((sum, f) => sum - f/len * Math.log2(f/len), 0)  
	
	}
	
	
});