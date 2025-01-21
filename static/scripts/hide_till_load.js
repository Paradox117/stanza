const everything = document.getElementsByTagName("body");

for (let i = 0; i < everything.length; i++) {
    everything[i].style.display = "none";
};

document.addEventListener("DOMContentLoaded", () => {
    for (let i = 0; i < everything.length; i++) {
        everything[i].style.display = "block";
    };
});