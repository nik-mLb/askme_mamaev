const question_cards = document.getElementsByClassName('question-body');

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

if (question_cards.length > 0) {
    const question_card = question_cards[0];
    const likeButton = question_card.querySelector('.like-button');
    const likeCounter = question_card.querySelector('.like-counter'); 
    const questionId = question_card.dataset.questionId;
    
    if (likeButton){
        function updateButtonState(liked) {
            if (liked) {
                likeButton.textContent = 'Dislike!';
                likeButton.setAttribute('data-liked', 'True');
            } else {
                likeButton.textContent = 'Like!';
                likeButton.setAttribute('data-liked', 'False');
            }
        }

        const initialLikedState = likeButton.getAttribute('data-liked') === 'True';
        updateButtonState(initialLikedState);
        likeButton.addEventListener('click', () => {
            const request = new Request(`/like_question_async/${questionId}`, {
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
    } else{
        console.log('LikeButoon not found')
    }
}