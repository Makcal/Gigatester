function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) === 0) {
            return c.substring(name.length, c.length);
        }
    }
    return null;
}

function getEditorMode(language) {
    switch (language) {
        case "java":
            return "ace/mode/java";
        case "cs":
            return "ace/mode/csharp";
        case "cpp17":
        case "cpp20":
            return "ace/mode/c_cpp";
    }
    return "ace/mode/c_cpp";
}

window.addEventListener("load", () => {

    var editor = ace.edit("code_space");
    editor.setTheme("ace/theme/cloud9_night");
    editor.setShowPrintMargin(false);

    const submit = document.querySelector("input[type=submit]");
    const darkener = document.querySelector("#darkener");
    submit.addEventListener("mouseover", () => {
        darkener.style.opacity = 1;
        darkener.style.visibility = "visible";
    })

    submit.addEventListener("mouseout", () => {
        darkener.style.opacity = 0;
        setTimeout(() => {
            darkener.style.visibility = "hidden";
        }, 200);
    })

    editor.session.on('change', () => {
        document.querySelector("#program_contents").value = editor.getValue();
    })

    if (getCookie('language') !== null && ['cpp17', 'cpp20', 'java', 'cs'].includes(getCookie('language'))) {
        document.querySelector(`.lang[data-lang=${getCookie('language')}]`).classList.add("active");
        document.querySelector("#languages").value = getCookie('language');
        document.cookie = `language=${getCookie('language')}`;
    } else {
        document.querySelector(".lang").classList.add("active");
        document.querySelector("#languages").value = "cpp17";
    }


    editor.session.setMode(getEditorMode(getCookie('language')));
    if (getCookie('task') !== null)
        document.querySelector("#tasks").value = getCookie('task');
    document.querySelector("input[type=submit]").disabled = false;

    document.querySelector("#tasks").addEventListener("change", () => {
        document.cookie = `task=${document.querySelector("#tasks").value}`;
    });

    document.querySelector("form").addEventListener("submit", (e) => {
        e.preventDefault();
        document.body.classList.add("wait");
        fetch("/submit", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            redirect: "manual",
            credentials: "include",
            body: new URLSearchParams(new FormData(document.querySelector("form")))
        }).then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Network response was not ok');
            }
        }).then(json => {
            let user_id = json['user_id'];
            let interval = setInterval(() => {
                fetch("/update", {
                    method: "GET",
                    headers: {
                        "Cookie": `user_id=${user_id}, task=${document.querySelector("#tasks").value}, language=${document.querySelector("#languages").value}`
                    }
                }).then(response => {
                    if (response.ok) {
                        return response.json();
                    } else {
                        throw new Error('Network response was not ok');
                    }
                }).then(json => {
                    if (json['code'] !== 1) {
                        clearInterval(interval);
                        document.body.classList.add("res");
                        document.body.classList.remove("wait");
                        fetch("/result", {
                            method: "GET",
                            headers: {
                                "Cookie": `user_id=${user_id}`
                            }
                        }).then(response => response.json()).then(json => {
                            var verdicts = {
                                "-1": "Critical Error",
                                "2": "Time Limit Exceeded",
                                "1": "Wrong Answer",
                                "0": "Arbuz"
                            };

                            document.querySelector("#verdict").innerText = verdicts[json['code']];
                            document.querySelector("#verdict").classList.add(verdicts[json['code']].toLowerCase().replace(/ /g, "-"));
                            document.querySelector(".data").innerHTML = "<span class='no_tests'>No tests to show.</span>";
                            if (json.code === 2) {
                                document.querySelector("#time").innerHTML = `Time: ${Math.round(json['time'] * 100) / 100}s`;
                                document.querySelector("#tests").innerHTML = `Tests: ${json['tests']}`;
                                if (json['tests'] === 1) {
                                    let input;
                                    input = json['input'][0];

                                    input = input.replace(/</g, "&lt;").replace(/>/g, "&gt;");

                                    document.querySelector(".data").innerHTML = "";
                                    document.querySelector(".data").insertAdjacentHTML("beforeend", `
                                <span class="line">
                                    <span class="text_block">
                                        Input:
                                        <br>
                                        <textarea class="input code">${input}</textarea>
                                    </span>
                                </span>`);
                                }
                            } else if (json.code === 1) {
                                document.querySelector("#time").innerHTML = `Time: ${Math.round(json['time'] * 100) / 100}s`;
                                document.querySelector("#tests").innerHTML = `Tests: ${json['tests']}  Successful: ${json['tests'] - json['input'].length}  Failed: ${json['input'].length}`;
                                document.querySelector(".data").innerHTML = "";
                                for (let i = 0; i < json['output'].length; i++) {
                                    let input, output, expected;
                                    input = json['input'][i];
                                    output = json['output'][i];
                                    expected = json['expected'][i];

                                    input = input.replace(/</g, "&lt;").replace(/>/g, "&gt;");
                                    output = output.replace(/</g, "&lt;").replace(/>/g, "&gt;");
                                    expected = expected.replace(/</g, "&lt;").replace(/>/g, "&gt;");

                                    document.querySelector(".data").insertAdjacentHTML("beforeend", `
                                <span class="line">
                                    <span class="text_block">
                                        Input:
                                        <br>
                                        <textarea class="input code">${input}</textarea>
                                    </span>
                                    <span class="text_block">
                                        Expected output:
                                        <br>
                                        <textarea class="expected code">${expected}</textarea>
                                    </span>
                                    <span class="text_block">
                                        Your output:
                                        <br>
                                        <textarea class="output code">${output}</textarea>
                                    </span>
                                </span>`);
                                }
                            } else if (json.code === 0) {
                                document.querySelector("#time").innerHTML = `Time: ${Math.round(json['time'] * 100) / 100}s`;
                                document.querySelector("#tests").innerHTML = `Tests: ${json['tests']}`;
                                document.body.classList.add("watermelon-rain");
                                document.querySelector(".result").classList.add("presuccess");
                                setTimeout(() => {
                                    document.querySelector(".result").classList.add("success");
                                }, 300);
                                const watermelon = `
                                    <img alt=""
                                        src="https://purepng.com/public/uploads/large/big-green-watermelon-t18.png"
                                        class="falling-watermelon" />`;
                                document.body.insertAdjacentHTML("beforeend", watermelon.repeat(30));
                                let watermelons = document.querySelectorAll(".falling-watermelon");
                                let totalWatermelons = watermelons.length;
                                watermelons.forEach((watermelon, index) => {
                                    watermelon.style.animationDelay = `${Math.random()}s`;
                                    watermelon.style.left = `${(index / totalWatermelons) * 100}vw`;
                                    watermelon.style.animationDuration = `${Math.random() * 2 + 1}s`;
                                    watermelon.style.animationPlayState = "running";
                                    watermelon.style.zIndex = Math.random() < 0.5 ? 4 : 6;
                                });
                            }
                        });
                    } else {
                        let position = json['position'];
                        if (position === 1) {
                            document.querySelector(".cooking .text").innerHTML = `<span style="color: #317721;">Watermelons</span> will stay with you while we process your code...`;
                            return;
                        }
                        let suffix;
                        if (position === 2)
                            suffix = "nd";
                        else if (position === 3)
                            suffix = "rd";
                        else
                            suffix = "th";

                        document.querySelector("#pos").innerHTML = `${position}<span style="font-size: .7em;">${suffix}</span>`;
                    }
                }).catch(error => {
                    console.error('There has been a problem with your fetch operation:', error);
                });
            }, 2000);
        }).catch(error => {
            console.error('There has been a problem with your fetch operation:', error);
        });
    });

    document.querySelectorAll(".lang").forEach((lang) => {
        lang.addEventListener("click", (e) => {
            document.querySelector(".lang.active").classList.remove("active");
            lang.classList.add("active");
            document.querySelector("#languages").value = e.target.getAttribute("data-lang");
            document.cookie = `language=${e.target.getAttribute("data-lang")}`;
            editor.session.setMode(getEditorMode(e.target.getAttribute("data-lang").value));
        });
    });
});
