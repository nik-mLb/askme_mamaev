const answers = document.getElementsByClassName('answer-body');

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


for (const answer of answers){
    const likeButton = answer.querySelector('.answer-like-button');
    const likeCounter = answer.querySelector('.answer-like-counter'); 
    const questionId = answer.dataset.questionId;
    const answerId = answer.dataset.answerId;



    if (likeButton){
        function updateButtonState(liked) {
            if (liked) {
                likeButton.textContent = 'Dislike!';
                likeButton.setAttribute('data-liked-answer', 'True');
            } else {
                likeButton.textContent = 'Like!';
                likeButton.setAttribute('data-liked-answer', 'False');
            }
        }
        
        const initialLikedState = likeButton.getAttribute('data-liked-answer') === 'True';
        updateButtonState(initialLikedState);
        likeButton.addEventListener('click', () => {
            const request = new Request(`/like_answer_async/${questionId}/${answerId}`, {
                method: "POST",
                headers: {'X-CSRFToken': getCookie('csrftoken')},
                mode: 'same-origin',
            });

            fetch(request)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then((data) => {
                    console.log({data});
                    likeCounter.value = data.likes_count; 
                    updateButtonState(data.liked); 
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        });
    }else {
        console.log('LikeButoon not found');
    }
}