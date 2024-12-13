const answerss = document.getElementsByClassName('answer-body');

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

for (const answer of answerss){
    const questionId = answer.dataset.questionId;
    const answerId = answer.dataset.answerId;
    const checkbox = answer.querySelector('.correct')
    console.log(checkbox)

    if (checkbox){
        checkbox.addEventListener('change', () => {

            const request_correct = new Request(`/set_correct_answer/${questionId}/${answerId}`, {
                method: "POST",
                headers: {'X-CSRFToken': getCookie('csrftoken')},
                mode: 'same-origin',
            });

            fetch(request_correct)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then((data) => {
                    console.log({data});
                    checkbox.checked = data.is_correct;  // Обновляем состояние checkbox
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        });
    }else {
        console.log('Checkbox not found for answer:', answerId);
    }
}