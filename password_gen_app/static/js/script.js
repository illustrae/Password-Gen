document.querySelectorAll('#copy-icon').forEach(icon => {
    icon.addEventListener('click', (event) => {
        let input = event.target.previousElementSibling
        if(input.localName == "input"){
            let saved_value = input.value
            navigator.clipboard.writeText(input.value)  
            input.value = "Copied!"
            setTimeout(()=>input.value = saved_value, 1000);
        }else{
            let saved_value = input.innerHTML
            navigator.clipboard.writeText(input.innerHTML)  
            input.innerHTML = "Copied!"
            setTimeout(()=>input.innerHTML = saved_value, 1000);
        }
        
    })
})



