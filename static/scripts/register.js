const passwd = document.getElementById("passwd");
const re_passwd = document.getElementById("re-passwd");
const msg = document.getElementById("message");


if (msg.innerHTML != "<h2>placeholder</h2>") {
    msg.style.color = "var(--color-red-old)";
}


function validate_pass() {
    if (re_passwd.value.length > 0) {
        if (passwd.value == re_passwd.value) {
            passwd.style.borderColor = "var(--color-green)";
            re_passwd.style.borderColor = "var(--color-green)";
            msg.style.color = "var(--color-white)";
        } else {
            passwd.style.borderColor = "var(--color-red-old)";
            re_passwd.style.borderColor = "var(--color-red-old)";
            msg.innerHTML = "<h2>Passwords do not match</h2>";
            msg.style.color = "var(--color-red-old)";
        };

    } else {
        passwd.style.borderColor = "var(--color-green)";
        re_passwd.style.borderColor = "var(--color-green)";
        msg.style.color = "var(--color-white)";
    };
};