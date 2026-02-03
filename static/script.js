async function processData() {
    const input = document.getElementById('inputData').value;
    const resultDiv = document.getElementById('result');
    
    try {
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ input: input })
        });
        
        const data = await response.json();
        resultDiv.innerHTML = `<strong>Результат:</strong> ${data.result}`;
    } catch (error) {
        resultDiv.innerHTML = `<strong>Ошибка:</strong> ${error}`;
    }
}