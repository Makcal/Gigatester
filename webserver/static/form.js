var editor = ace.edit("code_space");
editor.setTheme("ace/theme/cloud9_night");
editor.session.setMode("ace/mode/java");
editor.setShowPrintMargin(false);

document.querySelector("#languages").addEventListener("change", () => {
    if (document.querySelector("#languages").value == "cpp") {
        editor.session.setMode("ace/mode/c_cpp");
    } else {
        editor.session.setMode("ace/mode/java");
    }
})

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

if (getCookie('task') !== null)
    document.querySelector('#tasks').value = getCookie('task');
if (getCookie('language') !== null)
    document.querySelector('#languages').value = getCookie('language');

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
