let QUESTIONS = [];

function renderQuestions() {
    // Generate the HTML for each question
    const quizContainer = document.getElementById('questions');
    QUESTIONS.forEach((question, index) => {
        const questionElement = document.createElement('div');
        questionElement.innerHTML = `
            <h2>Otázka ${index + 1}</h2>
            <p>${question.question}</p>
        `;

        if (question.type === 'choice') {
            question.options.forEach((option) => {
                questionElement.innerHTML += `
                    <div class="option">
                    <input type="radio" id="${option}" name="${question.id}" value="${option}">
                    <label for="${option}">${option}</label>
                    </div>
                `;
            });
        } else if (question.type === 'text') {
            questionElement.innerHTML += `<input type="text" id="${question.id}">`;
        }

        quizContainer.appendChild(questionElement);
    });
}

window.onload = function () {
    fetch('questions')
        .then((response) => response.json())
        .then((data) => {
            QUESTIONS = data.questions;
            console.log(QUESTIONS);
            renderQuestions();
        })
        .catch((error) => console.error('Error:', error));

    document
        .getElementById('submit-button')
        .addEventListener('click', function () {
            try {
                const answers = QUESTIONS.map((question) => {
                    if (question.type === 'choice') {
                        let possibly_checked = document.querySelector(
                            `input[name="${question.id}"]:checked`
                        );
                        if (!possibly_checked) {
                            throw new Error(
                                `Prosím zodpovězte otázku ${question.id}`
                            );
                        }
                        return {
                            question_id: question.id,
                            answer: possibly_checked.value,
                        };
                    } else if (question.type === 'text') {
                        let answer = document.getElementById(question.id).value;
                        if (!answer) {
                            throw new Error(
                                `Prosím zodpovězte otázku ${question.id}`
                            );
                        }
                        return {
                            question_id: question.id,
                            answer,
                        };
                    }
                });

                fetch('submit_quiz', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ answers }),
                })
                    .then((response) => response.json())
                    .then((data) => {
                        if (data.is_correct) {
                            alert('Správně! Výsledky se zobrazí pod kvízem.');
                        } else {
                            alert(
                                'Špatně! Zkuste to znovu.'
                            );
                        }

                        document.getElementById('result').innerHTML =
                            data.message;
                    });
            } catch (error) {
                alert(error);
                return;
            }
        });
};
